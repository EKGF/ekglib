import logging
import sys
import time
import traceback
import typing
from base64 import b64encode
from datetime import datetime
from io import BytesIO
from typing import Any

import ldap3
import rdflib
import stringcase
from botocore.exceptions import EndpointConnectionError
from ldap3 import Connection, Entry, SchemaInfo, set_config_parameter
from ldap3.core.exceptions import (
    LDAPBindError,
    LDAPExtensionError,
    LDAPOperationResult,
    LDAPResponseTimeoutError,
    LDAPSocketOpenError,
    LDAPSocketReceiveError,
    LDAPUnavailableCriticalExtensionResult,
)
from ldap3.utils.log import (
    EXTENDED,
    set_library_log_activation_level,
    set_library_log_detail_level,
)
from pyasn1.error import PyAsn1Error
from rdflib import OWL, PROV, RDF, RDFS, XSD, Literal, URIRef, plugin

from ..dataset.various import export_graph
from ..exceptions import CannotCapture, PagingNotSupported
from ..kgiri import EKG_NS, kgiri_random, parse_identity_key_with_prefix
from ..log import error, log, log_dump, log_error, log_exception, log_item, warning
from ..main import dump_as_ttl_to_stdout
from ..namespace import DATAOPS, LDAP, RAW
from ..s3 import S3ObjectStore
from ..string import str_to_binary

# logging.basicConfig(filename='ldap.log', level=logging.DEBUG)
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# set_library_log_activation_level(EXTENDED)
# set_library_log_detail_level(EXTENDED)

skip_naming_contexts = (
    'cn=schema',
    'cn=localhost',
    'cn=ibmpolicies',
    'cn=virtual access controls',
)


def parse_ldap_domain(domain: str):
    x = domain.strip('\n').rsplit('.', 1)  # TODO: Support multiple levels of domains
    if len(x) < 2:
        error(f'Invalid LDAP domain {domain}')
    return f'dc={x[0]},dc={x[1]}'


def _log_who_am_i(conn):
    try:
        iam = conn.extend.standard.who_am_i()
        log_item('Who am I', iam)
    except LDAPExtensionError:
        log(
            "Could not get an answer to 'who am i' because the server does not support that LDAP extension"
        )
    except Exception as e:
        log_error("Couldn't get who_am_i" + str(e))


class LdapParser:
    skip_rdf_generation = False  # set to true to test/debug the overall flow of the app

    def __init__(self, args, stream: typing.BinaryIO | None = None):
        self.processed_entries = 0
        self.returned_entries = 0
        logging.info('Starting LDAP parser')
        self.args = args
        self.verbose = args.verbose
        self.ldap_log = args.ldap_log
        self.naming_context = args.ldap_naming_context
        self.data_source_code = args.data_source_code
        self.g = rdflib.Graph()
        self.add_namespaces()
        self.bind_dn = args.ldap_bind_dn
        self.bind_auth = args.ldap_bind_auth
        self.paged_size: int | None = 250
        self.search_filter = args.ldap_search_filter
        self.stream = stream
        self.ldap_host = args.ldap_host
        self.ldap_port = args.ldap_port
        self.ldap_host_port = f'{args.ldap_host}:{args.ldap_port}'
        self.ldap_timeout = args.ldap_timeout
        #
        # TODO: Support ldaps as well
        #

    def _check_bind_creds(self):
        if self.bind_dn == '':
            self.bind_dn = None
        if self.bind_dn is None:
            log_item('Bind DN', 'Anonymous')
            return
        if not isinstance(self.bind_dn, ldap3.STRING_TYPES):
            msg = f'The given bind DN is not valid: {self.bind_dn}'
            log_error(msg)
            raise AttributeError(msg)
        log_item('Bind DN', self.bind_dn)
        # log_item("Bind Auth", self.bind_auth)  # TODO: Remove this before production deploy!!

    def process(self) -> int:
        """The only public method of this class, call straight after construction, returns an integer that
        can/should be used for the process exit value
        """
        self._check_bind_creds()
        log_item('Connecting to LDAP Server', self.ldap_host_port)

        if self.ldap_log:
            logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
            set_library_log_activation_level(EXTENDED)
            set_library_log_detail_level(EXTENDED)

        set_config_parameter('RESPONSE_WAITING_TIMEOUT', self.ldap_timeout)
        set_config_parameter('IGNORE_MALFORMED_SCHEMA', True)

        server = ldap3.Server(
            self.ldap_host,
            port=self.ldap_port,
            connect_timeout=self.ldap_timeout,
            get_info=ldap3.ALL,
            use_ssl=False,
            tls=None,
            mode=ldap3.IP_V4_ONLY,
        )

        start = time.time()

        try:
            rc = self._process_connection(server)
        except LDAPBindError:
            log_error(f'Unable to bind using dn: {self.bind_dn} and the given password')
            rc = 3
        except LDAPResponseTimeoutError:
            log_error('Server timed out')
            rc = 4
        except LDAPSocketOpenError:
            log_error(f'Could not connect with {self.ldap_host_port}')
            rc = 5
        except PyAsn1Error as e:
            log_error(f'Could not connect with {self.ldap_host_port}: {e}')
            rc = 6
        except LDAPSocketReceiveError as e:
            log_error(f'LDAP Socket Receive Error: {e}')
            rc = 7

        log_item('Seconds', time.time() - start)
        # activity_iri = self.prov_activity_start(xlsx_iri)
        # self.prov_activity_end(activity_iri)
        log_item('Return Code', rc)
        return rc

    def _create_connection(self, server) -> ldap3.Connection:
        if self.bind_dn is None:
            log_item('Connecting as', 'Anonymous')
            return ldap3.Connection(
                server,
                auto_bind=ldap3.AUTO_BIND_NONE,
                version=3,
                authentication=ldap3.ANONYMOUS,
                client_strategy=ldap3.ASYNC,
                auto_referrals=True,
                raise_exceptions=False,
                read_only=True,
                lazy=False,
                check_names=True,
            )

        log_item('Connecting as', self.bind_dn)
        return ldap3.Connection(
            server,
            user=self.bind_dn,
            password=self.bind_auth,
            auto_bind=ldap3.AUTO_BIND_DEFAULT,
            client_strategy=ldap3.ASYNC,
            raise_exceptions=False,
            read_only=True,
            lazy=False,
            check_names=False,
        )

    def _process_connection(self, server) -> int:
        rc = 0
        with self._create_connection(server) as conn:
            log_item('Connected with', self.ldap_host_port)

            if not conn.bind():
                log_error(
                    "Can't bind to the LDAP server with the provided credentials ({})'".format(
                        self.bind_dn
                    )
                )
                return 1

            if self.verbose:
                log_item('Server Info', f'\n{server.info}')

            # log_item('Root', server.info.other['defaultNamingContext'][0])

            _log_who_am_i(conn)
            log_item('Connection', conn)

            # self.look_into_schema(conn)

            try:
                try:
                    #
                    # First try it with paging
                    #
                    rc = self._process_naming_contexts(server, conn)
                except PagingNotSupported:
                    #
                    # If that fails, try without paging and hope for the best
                    #
                    log(
                        'Since paging is not supported by the server now retrying without paging'
                    )
                    self.paged_size = None
                    rc = self._process_naming_contexts(server, conn)
            except Exception as e:
                log_error(f'Unknown exception: {e}')
                traceback.print_exc()

        if conn.last_error:
            log_item('Last error', conn.last_error)
        log_item('Total returned entries', self.returned_entries)
        log_item('Total processed entries', self.processed_entries)
        if (
            self.returned_entries == 0
        ):  # Getting nothing is probably an error so let's not return zero here.
            rc = 2
        return rc

    def _process_naming_contexts(self, server, conn):
        if self.naming_context:
            return self._process_one_naming_contexts(conn)
        return self._process_all_naming_contexts(server, conn)

    def _process_one_naming_contexts(self, conn) -> int:
        rc = 0
        try:
            log_item('Naming Context', self.naming_context)
            for entry in self._process_search(
                conn=conn, base=self.naming_context, scope=ldap3.SUBTREE
            ):
                self.process_entry(entry)
        except CannotCapture:
            log_error('Cannot capture LDAP data')
            rc = 1
        return rc

    def _process_all_naming_contexts(self, server, conn) -> int:
        rc = 0
        try:
            for naming_context in _naming_contexts(server.info):
                if not naming_context.strip():
                    continue
                log_item('Naming Context', naming_context)
                if naming_context.lower() in skip_naming_contexts:
                    log_item('Skipping', naming_context)
                    continue
                for entry in self._process_search(
                    conn=conn, base=naming_context, scope=ldap3.SUBTREE
                ):
                    self.process_entry(entry)
        except CannotCapture:
            log_error('Cannot capture LDAP data')
            rc = 1
        return rc

    def process_entry(self, entry: Entry) -> None:
        if self.skip_rdf_generation:
            return
        LdapEntry(self.args, entry, self.stream)
        self.processed_entries += 1

    @staticmethod
    def has_subordinates(entry):
        return (
            'hasSubordinates' in entry['attributes']
            and entry['attributes']['hasSubordinates'][0] == 'TRUE'
        )

    @staticmethod
    def value_of_attribute(attribute):
        return (
            attribute[0] if isinstance(attribute, ldap3.SEQUENCE_TYPES) else attribute
        )

    @staticmethod
    def value_of_attribute_with_key(entry: Entry, key: str):
        if key in entry:
            return entry[key]
        attributes = entry['attributes']
        if key in attributes:
            return LdapParser.value_of_attribute(attributes[key])
        return None

    @staticmethod
    def class_of_entry(entry):
        return LdapParser.value_of_attribute_with_key(entry, 'structuralObjectClass')

    @staticmethod
    def dn_of_entry(entry: Entry | dict[str, Any]) -> str:
        if hasattr(entry, 'entry_dn'):
            return entry.entry_dn
        return (
            entry['dn']
            if 'dn' in entry
            else LdapParser.value_of_attribute_with_key(entry, 'dn')
        )

    def log_entry(self, entry: Entry) -> None:
        class_of_entry = self.class_of_entry(entry)
        if class_of_entry:
            log_item(f'DN {class_of_entry}', self.dn_of_entry(entry))
            # log_dump('x', entry)
        else:
            if self.verbose:
                log_item('DN', self.dn_of_entry(entry))

    def _process_search_get_entries(self, conn: Connection, base, scope):
        if self.verbose:
            log_item(f'{scope}-search', base)
        if self.paged_size is not None:
            log_item('Paging enabled', True)
            log_item('Paged Size', self.paged_size)
            paged_criticality = True
        else:
            log_item('Paging enabled', False)
            paged_criticality = False

        conn.raise_exceptions = (
            True  # Only if this is True the LDAPOperationResult exception can be thrown
        )
        use_generator = True
        try:
            results = conn.extend.standard.paged_search(
                base,
                search_filter=self.search_filter,
                search_scope=scope,
                dereference_aliases=ldap3.DEREF_SEARCH,
                attributes=ldap3.ALL_ATTRIBUTES,
                # size_limit=self.paged_size,
                get_operational_attributes=True,
                paged_size=self.paged_size,
                paged_criticality=paged_criticality,
                generator=use_generator,
            )
            if not conn.listening:
                raise CannotCapture('Connection has been closed')
            if use_generator:
                return results
            return conn.entries
        except LDAPUnavailableCriticalExtensionResult as e:
            log_exception(e)
            raise PagingNotSupported(e.message)
        except LDAPOperationResult as e:
            raise CannotCapture(e.message)

    def _process_search(self, conn: Connection, base, scope):
        entries = self._process_search_get_entries(conn, base, scope)
        yield from self._process_entries(conn, base, scope, entries)

    def _process_entries(self, conn: Connection, base, scope, entries):
        returned_entries = 0
        try:
            for entry in entries:
                returned_entries += 1
                self.returned_entries += 1
                yield from self._process_entry(entry)
        except LDAPUnavailableCriticalExtensionResult as e:
            log_exception(e)
            raise PagingNotSupported(e.message)
        except LDAPOperationResult as e:
            raise CannotCapture(e.message)
        if self.verbose:
            log_item('Returned Entries', returned_entries)
        if returned_entries == 1 and scope is ldap3.BASE:
            yield from self._process_search(conn, base, ldap3.SUBTREE)

    def _process_entry(self, entry: Entry):
        if self.verbose:
            log_dump(f'Entry {self.returned_entries}', entry)
        if 'dn' in entry:
            self.log_entry(entry)
            # has_subordinates = self.has_subordinates(entry)
            # log_item("Has Subordinates", has_subordinates)
            # if has_subordinates:
            yield entry
        elif hasattr(entry, 'entry_dn'):
            self.log_entry(entry)
            yield entry
        else:
            log_dump('entry_dn', entry.entry_dn)
            log_error(f'Entry without dn: {entry}')

    def add_namespaces(self) -> None:
        self.g.base = EKG_NS['KGIRI']
        self.g.namespace_manager.bind('prov', PROV)
        self.g.namespace_manager.bind('raw', RAW)
        self.g.namespace_manager.bind('dataops', DATAOPS)

    def prov_activity_start(self):
        activity_iri = kgiri_random()
        self.g.add((activity_iri, RDF.type, PROV.Activity))
        self.g.add((activity_iri, PROV.startedAtTime, Literal(datetime.utcnow())))
        return activity_iri

    def prov_activity_end(self, activity_iri):
        self.g.add((activity_iri, PROV.endedAtTime, Literal(datetime.utcnow())))

    @staticmethod
    def _look_into_schema(conn: Connection):
        schema: SchemaInfo = conn.server.schema
        if schema is None:
            error('Could not access LDAP schema')
        if not schema.is_valid():
            error('LDAP Schema is not valid')
        log_item('DSA Schema from', schema.schema_entry)
        # if isinstance(schema.attribute_types, ldap3.SEQUENCE_TYPES):
        for s in schema.attribute_types:
            log_item(s, schema.attribute_types[s].description)

    def dump_as_ttl_to_stdout(self) -> int:
        dump_as_ttl_to_stdout(self.g)
        return 0

    def dump(self, output_file: str | Path | None) -> int:
        if not output_file:
            warning('You did not specify an output file, no output file created')
            return 1
        self.g.serialize(destination=output_file, encoding='UTF-8', format='ttl')
        log_item('Created', output_file)
        return 0

    def s3_file_name(self) -> str:
        return f'raw-data-transform-rules-{self.data_source_code}.ttl.gz'

    #
    # TODO: Not done yet
    #
    def export(self):
        try:
            s3os = S3ObjectStore(self.args)
            result = export_graph(
                graph=self.g,
                s3_file_name=self.s3_file_name(),
                s3_endpoint=s3os,
                data_source_code=self.data_source_code,  # TODO: Fix export_dataset to become export_graph
            )
            # log_item('result', result)
        except EndpointConnectionError:
            log_error('Could not connect to S3 s3_endpoint')
            return False
        return result


def _naming_contexts(info):
    if info.naming_contexts:
        if isinstance(info.naming_contexts, ldap3.SEQUENCE_TYPES):
            yield from info.naming_contexts
        else:
            yield str(info.naming_contexts)


_substitution_iri_map = {
    # replace the 'placeholder' IRI in the serialized stream with the desired one
    rdflib.term.URIRef(
        'http://www.w3.org/2001/XMLSchema#base64BinaryString'
    ).toPython(): XSD.base64Binary.toPython()
}


def _substitute_iris(serialized_graph):
    bts = BytesIO(b'')
    for frm, to in _substitution_iri_map.items():
        bts.write(serialized_graph.getvalue().decode().replace(frm, to).encode())
    return bts


class LdapEntry:
    """One LdapEntry represents, as the name suggests, one entry in LDAP, for which this class generates the
    RDF representation in one Graph that gets streamed to the given output stream.
    """

    entry: Entry

    def __init__(self, args, entry, stream):
        self.args = args
        self.verbose = args.verbose
        self.g = rdflib.Graph()
        self._add_namespaces()
        self.stream = stream
        self.entry = entry
        if isinstance(self.entry, dict):
            self.dn = self.entry['dn']
            self.attributes = self.entry['attributes']
        else:
            self.dn = self.entry.entry_dn
            self.attributes = self.entry.entry_attributes_as_dict()
        self.entry_iri = self._parse_entry_dn(self.dn)
        self._parse_other()
        self._graph_to_stream()

    def _add_namespaces(self):
        """Define the @base and @prefix to be used when we would dump the graph for one entry as turtle.
        In production though we would always be streaming this as N-Triples so there's no real need
        for doing this in that case.
        """
        self.g.base = EKG_NS['KGIRI']
        self.g.namespace_manager.bind('prov', PROV)
        self.g.namespace_manager.bind('raw', RAW)
        self.g.namespace_manager.bind('dataops', DATAOPS)

    def _add(self, triple: tuple[Any, Any, Any]) -> None:
        if self.verbose:
            s, p, o = triple
            log(f'<{s}> <{p}> {o}')
        self.g.add(triple)

    def _parse_entry_dn(self, dn) -> URIRef:
        entry_iri = EKG_NS['KGIRI'].term(
            parse_identity_key_with_prefix('ldap-term', dn)
        )
        self._add((entry_iri, RDF.type, LDAP.Term))
        return entry_iri

    def _parse_other(self):
        self._parse_entry_status()
        for key, values in self.attributes.items():
            if isinstance(values, ldap3.SEQUENCE_TYPES):
                self._parse_attribute(key, values)
            else:
                self._parse_attribute(key, [values])

    def _parse_attribute(self, key, values):
        if key == 'objectClass' or key == 'structuralObjectClass':
            self._parse_object_class(values)
        elif key == 'cn':
            self.parse_common_name(values)
        elif key == 'creatorsName':
            self._parse_creator(values)
        elif key == 'modifiersName':
            self._parse_modifier(values)
        elif key == 'hasSubordinates':
            self._parse_has_subordinates(values)
        elif (
            key == 'entryCSN'
        ):  # Not really useful, more or less same as createTimestamp
            return
        elif key == 'entryUUID':
            self._parse_entry_uuid(values)
        elif key == 'jpegPhoto':
            self.parse_binary_content(key, values)
        else:
            for value in values:
                self._add((self.entry_iri, LDAP.term(key), Literal(value)))

    def parse_binary_content(self, key, values):
        """Binary content is transformed into a Literal with base64 encoding"""
        for value in values:
            base64_bytes = b64encode(str_to_binary(value)).decode('ascii')

            # @LAP: assume this is handy in the UI?
            base64_url = 'data:image/jpeg;base64,' + base64_bytes
            self._add((
                self.entry_iri,
                LDAP.term(key + 'IRI'),
                Literal(base64_url, datatype=XSD.anyURI),
            ))

            # NB: Can't use rdflib.Literal with the correct datatype xsd:base64Binary,
            # as it messes with the value (decodes it), using a placeholder xsd:base64BinaryString
            # which gets replaced in the output stream, see _substitute_iris
            self._add((
                self.entry_iri,
                LDAP.term(key),
                Literal(base64_bytes, datatype=XSD.term('base64BinaryString')),
            ))

    def parse_common_name(self, values):
        """Translate cn i.e. CommonName (in X.500 terms) to RDFS.label"""
        for value in values:
            self._add((self.entry_iri, RDFS.label, Literal(value)))

    def register_person(self, entry_iri: URIRef) -> None:
        self._add((entry_iri, RDF.type, PROV.Person))
        self._add((entry_iri, RDF.type, PROV.Agent))

    def _attribute(self, key):
        for value in self.attributes[key]:
            return value

    def _create_activity(self):
        """Create a prov:Activity for the 'create' action, generate an IRI for the Activity that will be the same
        for each run (not a random one), based on 'entryUUID' or else 'dn'.
        """
        if 'entryUUID' in self.entry:
            guid = self._attribute('entryUUID')
            activity_iri = EKG_NS['KGIRI'].term(f'create-activity-{guid}')
        else:
            activity_iri = EKG_NS['KGIRI'].term(
                parse_identity_key_with_prefix('create-activity', self.dn)
            )
        self._add((activity_iri, RDF.type, PROV.Activity))
        self._add((activity_iri, PROV.generated, self.entry_iri))
        if 'createTimestamp' in self.entry:
            self._add((
                activity_iri,
                PROV.startedAtTime,
                Literal(self._attribute('createTimestamp')),
            ))
        return activity_iri

    def _parse_creator(self, values):
        activity_iri = self._create_activity()
        for value in values:
            prov_agent_iri = self._parse_entry_dn(value)
            self.register_person(prov_agent_iri)
            self._add((self.entry_iri, PROV.wasAttributedTo, prov_agent_iri))
            self._add((activity_iri, PROV.wasStartedBy, prov_agent_iri))

    def _parse_modifier(self, values):
        for value in values:
            prov_agent_iri = self._parse_entry_dn(value)
            self.register_person(prov_agent_iri)
            self._add((self.entry_iri, PROV.wasAttributedTo, prov_agent_iri))

    def _parse_entry_uuid(self, values):
        """Use the GUID specified with 'entryUUID' as an alternative KGIRI for the given entry.
        Even though the name suggests it's a standard UUID, it's actually a "legacy Microsoft UUID" based
        in RFC 4122. Which is why we're using the prefix 'guid:' in this case and not 'uuid:'.
        """
        for value in values:
            other_kgiri = EKG_NS['KGIRI'].term(f'guid:{value}')
            self._add((self.entry_iri, OWL.sameAs, other_kgiri))

    def _parse_has_subordinates(self, values):
        """Since we're scanning all entries we don't need to generate clutter saying that there are sub-entries"""
        #
        # TODO: When objectClass is a person and hasSubordinates is true can we
        #       then always conclude its a LineManager?
        #
        pass

    def _parse_object_class(self, values):
        """Translate object class to an RDF type"""
        for value in values:
            self._add((self.entry_iri, RDF.type, self._parse_value_to_rdf_type(value)))  # noqa: E501

    @staticmethod
    def _parse_value_to_rdf_type(value):
        value = stringcase.alphanumcase(value)
        return LDAP.term(stringcase.capitalcase(value))

    def _parse_entry_status(self):
        if isinstance(
            self.entry, dict
        ):  # No status when entry is a 'searchResEntry' # noqa: E501
            return
        status = self.entry.entry_status
        self._add((self.entry_iri, LDAP.entryStatus, Literal(status)))

    def _graph_to_stream(self):
        str_stream = BytesIO(b'')
        serializer = plugin.get('ntriples', plugin.Serializer)(self.g)
        serializer.serialize(str_stream)
        self.stream.write(_substitute_iris(str_stream).getvalue())
