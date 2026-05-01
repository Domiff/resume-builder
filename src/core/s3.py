from io import BytesIO

import aioboto3
import httpx
from botocore.exceptions import ClientError
from django.conf import settings
from ninja.errors import HttpError


class S3Client:
    def __init__(self) -> None:
        self.session = aioboto3.Session(**self._get_client_config())
        self.httpx_client = httpx.AsyncClient()

    @staticmethod
    def _get_client_config() -> dict:
        config = {
            "aws_access_key_id": settings.S3_ACCESS_KEY,
            "aws_secret_access_key": settings.S3_SECRET_KEY,
            "region_name": settings.S3_REGION,
        }
        return config

    @staticmethod
    def build_s3_public_url(
        endpoint_url: str, bucket_name: str, object_key: str
    ) -> str:
        return f"{endpoint_url.rstrip('/')}/{bucket_name}/{object_key}"

    @staticmethod
    def _to_s3_http_exception(error_code: str) -> HttpError:
        if error_code in {"NoSuchBucket", "404"}:
            return HttpError(
                status_code=404,
                message=f"S3 bucket not found or endpoint is incorrect.",
            )
        if error_code in {"403", "AccessDenied"}:
            return HttpError(status_code=403, message=f"Access denied to S3 bucket.")
        if error_code in {"InvalidAccessKeyId", "SignatureDoesNotMatch"}:
            return HttpError(status_code=401, message=f"Invalid S3 credentials.")
        return HttpError(
            status_code=502, message=f"S3 error {error_code or 'UnknownError'}."
        )

    async def upload_bytes_to_s3(
        self, file_bytes: bytes, object_key: str, content_type: str
    ) -> str:
        try:
            async with self.session.client(
                "s3", endpoint_url=settings.S3_ENDPOINT_URL
            ) as s3_client:
                await s3_client.head_bucket(Bucket=settings.S3_BUCKET_NAME)
                file_obj = BytesIO(file_bytes)
                await s3_client.upload_fileobj(
                    Fileobj=file_obj,
                    Bucket=settings.S3_BUCKET_NAME,
                    Key=object_key,
                    ExtraArgs={"ContentType": content_type},
                )
        except ClientError as error:
            error_code = error.response.get("Error", {}).get("Code", "")
            raise self._to_s3_http_exception(error_code) from error
        except Exception as error:
            raise HttpError(
                status_code=502, message=f"Failed to upload file to S3: {error}"
            ) from error

        return self.build_s3_public_url(
            settings.S3_ENDPOINT_URL, settings.S3_BUCKET_NAME, object_key
        )

    async def download_bytes_from_url(self, url: str) -> bytes:
        async with self.httpx_client as client:
            try:
                response = await client.get(url)
            except httpx.HTTPError as exc:
                raise HttpError(
                    message="Failed to download file from input link", status_code=503
                ) from exc
        if response.status_code >= 400:
            raise HttpError(
                message=f"Failed to download file",
                status_code=response.status_code,
            )
        return response.content


s3 = S3Client()
