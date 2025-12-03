import argparse
import csv
import urllib
from typing import Any, Optional

import requests
from requests.exceptions import StreamConsumedError
from requests.utils import iter_slices

from ..log import log_item, log_error, error, warning
from ..mime import MIME_CSV, check_sparql_mime_type, MIME_TSV

try:
    from SPARQLWrapper import SPARQLWrapper, POST, GET, URLENCODED, JSON, RDFXML
    from SPARQLWrapper.SPARQLExceptions import (
        QueryBadFormed,
        EndPointNotFound,
        Unauthorized,
    )
    from SPARQLWrapper.Wrapper import QueryResult
except ImportError:
    raise Exception(
        "SPARQLWrapper not found! install with 'pip3 install SPARQLWrapper'"
    )


def dump(obj: Any) -> None:
    for attr in dir(obj):
        print('obj.%s = %r' % (attr, getattr(obj, attr)))


def set_cli_params(parser: argparse.ArgumentParser) -> None:
    parser.add_argument_group('SPARQL')
    parser.add_argument('--sparql_endpoint-s3_endpoint', help='The SPARQL s3_endpoint')
    parser.add_argument('--sparql_endpoint-database', help='The SPARQL database')
    parser.add_argument(
        '--sparql_endpoint-userid', help='The SPARQL userid', default=None
    )
    parser.add_argument(
        '--sparql_endpoint-passwd',
        '--sparql_endpoint-password',
        help='The SPARQL password',
        default=None,
    )


# noinspection PyUnresolvedReferences
def iter_raw(r: requests.Response, chunk_size: int = 1):
    """
    Reimplementation of requests.Response.iter_content that doesn't try
    to decode zipped content
    :param chunk_size:
    :type r: requests.Response
    """

    def generate():
        while True:
            # urllib3.response.HTTPResponse.read
            chunk = r.raw.read(amt=chunk_size, decode_content=False)
            if not chunk:
                break
            log_item('Type of chunk', type(chunk))
            yield chunk

        r._content_consumed = True

    # noinspection PyProtectedMember
    if r._content_consumed and isinstance(r._content, bool):
        raise StreamConsumedError()
    elif chunk_size is not None and not isinstance(chunk_size, int):
        raise TypeError(
            'chunk_size must be an int, it is instead a %s.' % type(chunk_size)
        )
    # noinspection PyProtectedMember
    # simulate reading small chunks of the content
    reused_chunks = iter_slices(r._content, chunk_size)

    stream_chunks = generate()

    # noinspection PyProtectedMember
    chunks = reused_chunks if r._content_consumed else stream_chunks

    return chunks


class SPARQLResponse:
    sparql_endpoint: 'SPARQLEndpoint'

    def __init__(
        self, sparql_endpoint, response: requests.Response, mime: str | None = None
    ):
        self.sparql_endpoint = sparql_endpoint
        self.response = response
        self.mime = mime
        self.chunk_size = 1024
        if not self.sparql_endpoint.handle_error(self.response):
            return
        log_item('Content Encoding', self.response.headers.get('Content-Encoding'))
        if self.mime == MIME_CSV:
            self.iter_lines_generator = self._iter_lines_in_csv_format
        elif self.mime == MIME_TSV:
            self.iter_lines_generator = self._iter_lines_in_tsv_format
        else:
            self.iter_lines_generator = self._iter_lines_raw

    def _csv_iter(self):
        for line in self.response.iter_lines(
            chunk_size=self.chunk_size, decode_unicode=False, delimiter=b'\n'
        ):
            yield line.decode('utf-8')

    def _iter_lines_in_csv_format(self):
        for line in csv.DictReader(self._csv_iter()):
            yield line

    #
    # TODO: Translate each TSV row into a Python dictionary where the keys are the column names returned in row 1
    #
    def _iter_lines_in_tsv_format(self):
        first_line = True
        for line in self.response.iter_lines(
            chunk_size=self.chunk_size, decode_unicode=False, delimiter=b'\n'
        ):
            if first_line:
                first_line = False
                continue
            if len(line) == 0:
                continue
            yield line.decode('utf-8')

    def _iter_lines_raw(self):
        print('iter_lines 3')
        for line in self.response.iter_lines(
            chunk_size=self.chunk_size, decode_unicode=False, delimiter=b'\n'
        ):
            yield line.decode('utf-8')

    def iter_lines(self):
        return self.iter_lines_generator()


class SPARQLEndpoint:
    sparql_endpoint: SPARQLWrapper

    #
    #
    #
    def __init__(self, args=None):
        """
        Create a SPARQL Endpoint (an instance of the class SPARQLWrapper) given the "standard"
        command line params that we're using for most command line utilities

        :param args: the CLI args, see set_cli_params
        """
        self.args = args
        self.verbose = args.verbose
        self.data_source_code = args.data_source_code
        self.endpoint_base = args.sparql_endpoint
        self.database = args.sparql_endpoint_database
        self.sparql_endpoint = SPARQLWrapper(
            endpoint=f'{self.endpoint_url()}/query',
            updateEndpoint=f'{self.endpoint_url()}/update',
            returnFormat=JSON,
        )
        self.sparql_endpoint.setCredentials(
            args.sparql_endpoint_userid, passwd=args.sparql_endpoint_passwd
        )
        # self.s3_endpoint.addDefaultGraph(graph_iri_for_dataset(self.data_source_code))
        # self.s3_endpoint.setUseKeepAlive()

    def endpoint_url(self) -> str:
        return f'{self.endpoint_base}/{self.database}'

    def endpoint_url_for_queries(self) -> str:
        return f'{self.endpoint_base}/{self.database}/query'

    def user_id(self):
        return self.sparql_endpoint.user

    def password(self):
        return self.sparql_endpoint.passwd

    def execute_sparql_select_query(self, sparql_statement, mime_type=MIME_CSV):
        check_sparql_mime_type(mime_type)

        if self.verbose:
            log_item('Executing', sparql_statement)
        # noinspection PyProtectedMember
        log_item(
            'Statement Type', self.sparql_endpoint._parseQueryType(sparql_statement)
        )
        self.sparql_endpoint.clearCustomHttpHeader('Accept')
        self.sparql_endpoint.setRequestMethod(URLENCODED)
        self.sparql_endpoint.setMethod(GET)
        self.sparql_endpoint.addCustomHttpHeader('Accept', mime_type)
        log_item('Query', sparql_statement.lstrip())
        self.sparql_endpoint.setQuery(sparql_statement.lstrip())
        # noinspection PyProtectedMember
        request = self.sparql_endpoint._createRequest()
        for header_name, header_value in request.header_items():
            log_item(header_name, header_value)
        log_item('Is Update', self.sparql_endpoint.isSparqlUpdateRequest())
        log_item('Full URL', request.full_url)
        # with urllib.request.urlopen(request) as f:
        #     print(f.read().decode('utf-8'))
        return self._execute_query()

    def execute_csv_query(self, sparql_statement: str):
        return self.execute_sparql_query2(sparql_statement)

    def execute_sparql_query2(
        self, sparql_statement, graph_iri: str | None = None, mime: str = MIME_CSV
    ) -> Optional[SPARQLResponse]:
        if self.verbose:
            log_item('Executing', sparql_statement)

        # noinspection PyProtectedMember
        log_item(
            'Statement Type', self.sparql_endpoint._parseQueryType(sparql_statement)
        )

        endpoint_url = self.endpoint_url_for_queries()

        log_item('SPARQL Endpoint', endpoint_url)
        log_item('Accept Mime Type', mime)

        params = {
            'timeout': 10000,  # ms
            'limit': 10000,
            'charset': 'utf-8',
        }
        if graph_iri:
            params['graph'] = graph_iri
        params['reasoner'] = 'true'
        log_item('Params', params)
        #
        # Using this method: https://www.w3.org/TR/sparql11-protocol/#query-via-post-direct
        #
        r = requests.post(
            endpoint_url,
            data=sparql_statement,
            auth=(self.user_id(), self.password()),
            params=params,
            headers={
                'Accept': mime,
                'Accept-Encoding': '*;q=0, identity;q=1',
                'Accept-Charset': '*;q=0, utf-8;q=1',
                'Content-type': 'application/sparql_endpoint-query',
            },
            stream=True,
        )
        if r.status_code == 200:
            return SPARQLResponse(self, r, mime=mime)
        log_item('HTTP Status', r.status_code)
        return None

    def execute_sparql_statement(self, sparql_statement):
        if self.verbose:
            log_item('Executing', sparql_statement)
        statement_type = self.sparql_endpoint._parseQueryType(sparql_statement)
        log_item('Statement Type', statement_type)
        self.sparql_endpoint.clearCustomHttpHeader('Accept')
        self.sparql_endpoint.setMethod(POST)
        self.sparql_endpoint.setRequestMethod(URLENCODED)
        self.sparql_endpoint.addCustomHttpHeader('Accept', 'text/boolean')
        self.sparql_endpoint.addParameter('reasoner', 'true')
        log_item('Query', sparql_statement)
        self.sparql_endpoint.setQuery(sparql_statement)
        request = self.sparql_endpoint._createRequest()
        for header_name, header_value in request.header_items():
            log_item(header_name, header_value)
        log_item('Is Update', self.sparql_endpoint.isSparqlUpdateRequest())
        log_item('Full URL', request.full_url)
        # with urllib.request.urlopen(request) as f:
        #     print(f.read().decode('utf-8'))
        return self._execute_query()

    def execute_construct(
        self, sparql_construct_statement: str
    ) -> Optional[QueryResult]:
        self.sparql_endpoint.clearCustomHttpHeader('Accept')
        self.sparql_endpoint.setMethod(GET)
        self.sparql_endpoint.setReturnFormat(
            RDFXML
        )  # the call to convert() below depends on this being RDFXML
        self.sparql_endpoint.setRequestMethod(URLENCODED)
        self.sparql_endpoint.addParameter('reasoner', 'true')
        #
        # timeout higher than triple store time out
        # self.sparql_endpoint.setTimeout(10)
        #
        # millisecs. let triple store fail first so timeout earlier than HTTP
        # self.sparql_endpoint.addParameter("timeout", "2000")
        log_item('Query', sparql_construct_statement)
        self.sparql_endpoint.setQuery(sparql_construct_statement)
        # noinspection PyProtectedMember
        request = self.sparql_endpoint._createRequest()
        for header_name, header_value in request.header_items():
            log_item(header_name, header_value)
        return self._execute_query()

    def _execute_query(self):  # noqa: C901
        try:
            result = self.sparql_endpoint.query()
            response = result.response
            log_item('Response Code', response.code)
            for key, value in response.info().items():
                log_item(key, value)
            for key, value in result.info().items():
                log_item(key, value)
            if response.code in (200, 201):
                return result
        except urllib.error.HTTPError as err:
            error('{} code={}'.format(err, err.code))
        except urllib.error.URLError as err:
            error('{} reason={}'.format(err, err.reason))
        except EndPointNotFound as err:
            error('{}'.format(err))
            dump(err)
        except QueryBadFormed:
            error(f'Bad formed SPARQL statement: {self.sparql_endpoint.queryString}')
        except Unauthorized:
            error('Unauthorized to access {}'.format(self.sparql_endpoint.endpoint))
        except ConnectionRefusedError:
            error('Could not connect to {}'.format(self.sparql_endpoint.endpoint))
        return None

    def handle_error(self, r: requests.Response) -> bool:
        log_item('URL', r.url)
        for key, value in r.headers.items():
            log_item(key, value)
        if not self._handle_stardog_error(r):
            return False
        if not self._handle_ontotext_error(r):
            return False
        log_item('HTTP Status', r.status_code)
        if r.status_code == 200:
            return True
        if r.status_code == 201:
            return True
        return False

    def _handle_stardog_error(self, r: requests.Response) -> bool:
        """
        In case we detect the response header SD-Error-Code we know it's a Stardog server.
        Then handle the various errors Stardog can give.
        """
        stardog_error = r.headers.get('SD-Error-Code')
        if not stardog_error:
            return True
        if stardog_error == 'UnknownDatabase':
            log_error(f'The database {self.database} does not exist')
            return False
        warning(f'Encountered unknown Stardog error {stardog_error}')
        return True

    # noinspection PyMethodMayBeStatic
    def _handle_ontotext_error(self, r: requests.Response) -> bool:  # noqa
        return True
