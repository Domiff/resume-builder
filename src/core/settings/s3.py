"""
S3 storage settings (aioboto3).
https://aioboto3.readthedocs.io/
"""

from .env import env

S3_REGION = env("S3_REGION")
S3_ENDPOINT_URL = env("S3_ENDPOINT_URL")
S3_ACCESS_KEY = env("S3_ACCESS_KEY")
S3_SECRET_KEY = env("S3_SECRET_KEY")
S3_BUCKET_NAME = env("S3_BUCKET_NAME")
