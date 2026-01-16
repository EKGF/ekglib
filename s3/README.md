# s3

Helpers for interacting with Amazon S3, including convenience wrappers and utility functions.

These functions are used by other components (such as export and parser tools) to persist data in S3.

## Main Classes

- `S3ObjectStore` - Main interface for S3 operations
- `S3Part` - Represents a part of a multipart upload
- `S3Uploader` - Handles multipart uploads to S3

## Main Functions

### CLI Integration

- `set_cli_params(parser: ArgumentParser) -> Any` - Add S3-related CLI arguments

The CLI parameters include:
- `--s3-endpoint` - The S3 endpoint URL (env: `S3_ENDPOINT_URL`)
- `--s3-bucket` - The S3 bucket name (env: `S3_BUCKET_NAME`)
- `--s3-create-bucket` - Create the bucket if it doesn't exist
- `--aws-region` - AWS region (env: `AWS_REGION`)
- `--aws-access-key-id` - AWS access key (env: `AWS_ACCESS_KEY_ID`)
- `--aws-secret-access-key` - AWS secret key (env: `AWS_SECRET_ACCESS_KEY`)

### Utility Functions

- `s3_object_full_name(...)` - Construct full S3 object name/path

## Usage

```python
from ekg_lib.s3 import S3ObjectStore, set_cli_params
from argparse import ArgumentParser

# Set up CLI
parser = ArgumentParser()
set_cli_params(parser)
args = parser.parse_args()

# Create S3 object store
s3_store = S3ObjectStore(
    endpoint_url=args.s3_endpoint,
    bucket_name=args.s3_bucket,
    region=args.aws_region,
    access_key_id=args.aws_access_key_id,
    secret_access_key=args.aws_secret_access_key
)

# Use uploader for multipart uploads
uploader = s3_store.uploader_for(
    key="path/to/file.ttl.gz",
    mime="text/turtle",
    content_encoding="gzip"
)
uploader.part(data_chunk)
uploader.complete()
```

## Links

- [ekg_lib](../)
- [EKGF](https://ekgf.org)
