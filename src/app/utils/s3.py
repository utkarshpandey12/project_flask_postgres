import boto3
from botocore.client import Config
from flask import current_app

AWS_S3_SERVICE = "s3"
AWS_S3_SIGNATURE_VERSION = "s3v4"


def _get_s3_client():
    s3_client = boto3.client(
        AWS_S3_SERVICE,
        aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
        region_name=current_app.config["AWS_DEFAULT_REGION"],
        config=Config(signature_version=AWS_S3_SIGNATURE_VERSION),
    )
    return s3_client


def _get_s3_resource():
    s3_resource = boto3.resource(
        AWS_S3_SERVICE,
        aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
        region_name=current_app.config["AWS_DEFAULT_REGION"],
        config=Config(signature_version=AWS_S3_SIGNATURE_VERSION),
    )
    return s3_resource


def _get_s3_bucket_name(is_private):
    bucket_name_config = (
        "S3_BUCKET_NAME_PRIVATE" if is_private else "S3_BUCKET_NAME_PUBLIC"
    )
    return current_app.config[bucket_name_config]


def _get_s3_bucket(is_private):
    s3_resource = _get_s3_resource()
    bucket_name = _get_s3_bucket_name(is_private)
    return s3_resource.Bucket(bucket_name)


def upload_file_to_s3(key_name, file_path, is_private):
    s3_bucket = _get_s3_bucket(is_private)
    s3_bucket.upload_file(file_path, key_name)


def upload_bytes_to_s3(key_name, data, is_private, extra_args=None):
    s3_bucket = _get_s3_bucket(is_private)
    s3_bucket.upload_fileobj(data, key_name, extra_args)


CONTENT_TYPES = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
}


def upload_audio_to_s3(key_name, data, is_private):
    extra_args = {}
    ext = key_name.split(".")[-1].lower()
    extra_args["ContentType"] = CONTENT_TYPES[ext]
    extra_args["CacheControl"] = "max-age=31536000, immutable"
    upload_bytes_to_s3(key_name, data, is_private, extra_args)


def generate_url(key_name, is_private):
    bucket_name = _get_s3_bucket_name(is_private)
    return f"https://{bucket_name}.s3.amazonaws.com/{key_name}"


def generate_signed_url(key_name, is_private, expiry_in_secs=None, s3_client=None):
    bucket_name = _get_s3_bucket_name(is_private)
    if not expiry_in_secs:
        expiry_in_secs = current_app.config["S3_SIGNED_URL_EXPIRY"]
    if s3_client is None:
        s3_client = _get_s3_client()
    url = s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket_name, "Key": key_name},
        ExpiresIn=expiry_in_secs,
    )
    return url
