import os
from argparse import ArgumentParser
from typing import Any


def set_cli_params(parser: ArgumentParser) -> Any:
    s3_endpoint_url = os.getenv('S3_ENDPOINT_URL', None)
    s3_bucket_name = os.getenv('S3_BUCKET_NAME', None)
    aws_region = os.getenv('AWS_REGION', None)
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID', None)
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY', None)

    group = parser.add_argument_group('Object Store')

    if s3_endpoint_url:
        group.add_argument(
            '--s3-endpoint',
            help=f'The S3 s3_endpoint (default is S3_ENDPOINT_URL={s3_endpoint_url})',
            default=s3_endpoint_url,
            required=True,
        )
    else:
        group.add_argument(
            '--s3-endpoint',
            help='The S3 s3_endpoint, default can be set via env var S3_ENDPOINT_URL',
            required=True,
        )

    if s3_bucket_name:
        group.add_argument(
            '--s3-bucket',
            help=f'The S3  bucket name (default is S3_BUCKET_NAME={s3_bucket_name})',
            default=s3_bucket_name,
            required=True,
        )
    else:
        group.add_argument(
            '--s3-bucket',
            help='The S3  bucket name, default can be set via env var S3_BUCKET_NAME',
            required=True,
        )
    group.add_argument(
        '--s3-create-bucket',
        help="Create the bucket if it's missing",
        action='store_true',
        required=False,
        default=False,
    )
    if aws_region:
        group.add_argument(
            '--aws-region',
            help=f'The AWS region (default is AWS_REGION={aws_region})',
            default=aws_region,
            required=True,
        )
    else:
        group.add_argument(
            '--aws-region',
            help='The AWS region, default can be set via env var AWS_REGION',
            required=True,
        )

    if aws_access_key_id:
        group.add_argument(
            '--aws-access-key-id',
            help=f'The AWS access key id (default is AWS_ACCESS_KEY_ID={aws_access_key_id})',
            default=aws_region,
            required=True,
        )
    else:
        group.add_argument(
            '--aws-access-key-id',
            help='The AWS access key id, default can be set via env var AWS_ACCESS_KEY_ID',
            required=True,
        )

    if aws_secret_access_key:
        group.add_argument(
            '--aws-secret-access-key',
            help=f'The AWS secret access key (default is AWS_SECRET_ACCESS_KEY={aws_secret_access_key})',
            default=aws_region,
            required=True,
        )
    else:
        group.add_argument(
            '--aws-secret-access-key',
            help='The AWS secret access key, default can be set via env var AWS_SECRET_ACCESS_KEY',
            required=True,
        )
    return group
