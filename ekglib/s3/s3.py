import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, EndpointConnectionError

from ..kgiri import parse_identity_key
from ..log import log_item, error
from ..mime import MIME_NTRIPLES


def s3_object_full_name(object_):
    return None if object_ is None else f"{object_.bucket_name}/{object_.key}"


class S3ObjectStore:

    def __init__(self, args=None):
        self.args = args
        self.verbose = args.verbose
        self.s3_endpoint = args.s3_endpoint
        self.s3_bucket_name = args.s3_bucket
        self.git_branch = args.git_branch
        self.create_bucket = args.s3_create_bucket

        self.s3 = boto3.resource(
            's3',
            endpoint_url=self.s3_endpoint,
            aws_access_key_id=args.aws_access_key_id,
            aws_secret_access_key=args.aws_secret_access_key,
            config=Config(
                region_name=args.aws_region,
                signature_version='s3v4',
                connect_timeout=5,
                retries={
                    'total_max_attempts': 1,
                    'max_attempts': 0
                }
            ),
            region_name=args.aws_region
        )
        # Get the client from the resource
        self.s3_client = self.s3.meta.client
        self.__check_bucket()

    def __check_bucket(self):
        if self.s3_bucket_name is None:
            # Print out all bucket names
            for bucket in self.s3.buckets.all():
                log_item("Found Bucket", bucket.name)
        else:
            log_item('Check Bucket', self.s3_bucket_name)
            if self.does_bucket_exist(self.s3_bucket_name):
                log_item("Bucket " + self.s3_bucket_name, "Exists")
            elif self.create_bucket:
                self.__create_bucket()
            else:
                error("Bucket " + self.s3_bucket_name + " does not exist.")

    def __create_bucket(self):
        log_item('Creating Bucket', self.s3_bucket_name)
        try:
            location = {'LocationConstraint': self.args.aws_region}
            self.s3_client.create_bucket(Bucket=self.s3_bucket_name, CreateBucketConfiguration=location)
        except ClientError as e:
            error(e)
            return False
        return True

    def __check_dataset_directory(self, dataset_code: str):
        root_object = self.root_folder(dataset_code)
        log_item("Root", s3_object_full_name(root_object))

    def does_bucket_exist(self, bucket_name):
        try:
            return self.bucket(bucket_name).creation_date is not None
        except EndpointConnectionError as e:
            error(e)

    def object(self, key):
        bucket = self.bucket(self.s3_bucket_name)
        return None if bucket is None else bucket.Object(key)

    def does_object_exist(self, key):
        return self.object(key)

    def root_folder(self, dataset_code: str):
        root_key = self.dataset_root(dataset_code)
        return None if root_key is None else self.object(root_key)

    #
    # Return the name of the root directory in the default bucket that's
    # used for the configured dataset.
    #
    def dataset_root(self, dataset_code: str) -> str:
        return f"{parse_identity_key(self.git_branch)}/{dataset_code}"

    def bucket(self, bucket_name):
        return self.s3.Bucket(bucket_name)

    def file_key_in_dataset_folder(self, dataset_code, key):
        return "{}/{}".format(self.dataset_root(dataset_code), key)

    def uploader_for(
            self,
            key,
            mime=MIME_NTRIPLES,
            content_encoding: str = None,
            dataset_code: str = None
    ):
        return S3Uploader(
            self,
            key=self.file_key_in_dataset_folder(dataset_code, key),
            mime=mime,
            content_encoding=content_encoding,
            dataset_code=dataset_code
        )


class S3Uploader:

    def __init__(
            self, s3_object_store, key,
            mime=MIME_NTRIPLES,
            content_encoding=None,
            dataset_code: str = None
    ):
        self.args = s3_object_store.args
        self.verbose = self.args.verbose
        self.object_store = s3_object_store
        self.key = key
        log_item('Key', self.key)
        self.object = self.object_store.object(key)
        log_item('Object', self.object)
        self.e_tag = None
        log_item("Creating MPU for", key)
        log_item("MIME", mime)
        log_item("Content Encoding", content_encoding)
        self.mpu = self.object.initiate_multipart_upload(
            # ContentType=mime,
            ContentType="application/x-gzip",
            # ContentEncoding=content_encoding,
            Metadata={
                'dataset-code': dataset_code
            }
        )
        self.id = self.mpu.id
        log_item("Multipart Upload Id", self.mpu.id)
        self.parts = []

    def part(self, chunk: bytes):
        part = S3Part(self, len(self.parts) + 1)
        self.parts.append(part)
        part.upload(chunk)
        return part

    def parts_dict(self):
        for part in self.parts:
            yield part.dict()

    def complete(self) -> bool:
        if len(self.parts) == 0:
            error("Cannot complete multipart upload because there were no parts")
        log_item("Completing upload", self.key)
        parts_dict = {
            'Parts': list(self.parts_dict())
        }
        # print(json.dumps(parts_dict))
        # boto3.set_stream_logger(name='botocore')
        response = self.object_store.s3_client.complete_multipart_upload(
            Bucket=self.object_store.s3_bucket_name,
            Key=self.key,
            UploadId=self.id,
            MultipartUpload=parts_dict
        )
        http_status = response['ResponseMetadata']['HTTPStatusCode']
        if http_status == 200:
            log_item("Upload Status", "Complete")
            return True
        else:
            log_item("Status", http_status)
            log_item("Completed Object", response)
            return False


class S3Part:

    def __init__(self, s3_uploader, part_number):
        self.verbose = s3_uploader.args.verbose
        self.uploader = s3_uploader
        self.number = part_number
        self.e_tag = None

        log_item("Created Part", "{}: {}".format(self.uploader.key, self.number))

    def dict(self):
        return {
            'ETag': self.e_tag,  # self.part.e_tag,
            'PartNumber': self.number
        }

    def upload(self, chunk: bytes):
        log_item("Type of chunk", type(chunk))
        log_item("Uploading Part", f"size={len(chunk)} last 10 bytes={chunk[-10:]}")
        response = self.uploader.object_store.s3_client.upload_part(
            Body=chunk,
            Bucket=self.uploader.object_store.s3_bucket_name,
            Key=self.uploader.key,
            PartNumber=self.number,
            UploadId=self.uploader.id
        )
        # log_item("Uploaded Part Response", response)
        for key, value in response.items():
            if key == 'ResponseMetadata':
                for key2, value2 in value.items():
                    if key2 == 'HTTPHeaders':
                        for key3, value3 in value2.items():
                            log_item(key3, value3)
                    else:
                        if value2:
                            log_item(key2, value2)
            else:
                if value and value != '0':
                    log_item(key, value)
        self.e_tag = response['ETag']
