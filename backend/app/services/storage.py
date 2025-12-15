"""File storage service for managing images and assets."""
import io
from typing import Optional, BinaryIO
from datetime import timedelta
import boto3
from botocore.exceptions import ClientError
from loguru import logger

from app.core.config import settings


class StorageService:
    """
    S3/MinIO storage service for managing story images and assets.

    Handles:
    - Uploading images (page illustrations, cover images)
    - Generating signed URLs for client access
    - Deleting files
    - Organizing files by story ID
    """

    def __init__(self):
        """Initialize S3 client."""
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
            region_name=settings.s3_region,
        )
        self.bucket_name = settings.s3_bucket_name

    def _get_object_key(self, story_id: str, filename: str) -> str:
        """
        Generate S3 object key for a file.

        Format: stories/{story_id}/{filename}
        """
        return f"stories/{story_id}/{filename}"

    async def upload_image(
        self,
        story_id: str,
        filename: str,
        file_data: BinaryIO,
        content_type: str = "image/png",
    ) -> str:
        """
        Upload an image file to S3/MinIO.

        Args:
            story_id: Story ID for organizing files
            filename: File name (e.g., 'page_1.png', 'cover.png')
            file_data: File data as binary stream
            content_type: MIME type of the file

        Returns:
            Object key of the uploaded file
        """
        object_key = self._get_object_key(story_id, filename)

        try:
            self.client.upload_fileobj(
                file_data,
                self.bucket_name,
                object_key,
                ExtraArgs={
                    "ContentType": content_type,
                    "CacheControl": "max-age=31536000",  # 1 year cache
                },
            )
            logger.info(f"Uploaded {object_key} to {self.bucket_name}")
            return object_key

        except ClientError as e:
            logger.error(f"Failed to upload {object_key}: {e}")
            raise

    async def get_signed_url(
        self,
        object_key: str,
        expiration: int = 3600,
    ) -> str:
        """
        Generate a signed URL for accessing a file.

        Args:
            object_key: S3 object key
            expiration: URL expiration in seconds (default: 1 hour)

        Returns:
            Signed URL string
        """
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": object_key,
                },
                ExpiresIn=expiration,
            )
            return url

        except ClientError as e:
            logger.error(f"Failed to generate signed URL for {object_key}: {e}")
            raise

    async def delete_file(self, object_key: str) -> None:
        """
        Delete a file from S3/MinIO.

        Args:
            object_key: S3 object key to delete
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key,
            )
            logger.info(f"Deleted {object_key} from {self.bucket_name}")

        except ClientError as e:
            logger.error(f"Failed to delete {object_key}: {e}")
            raise

    async def delete_story_files(self, story_id: str) -> None:
        """
        Delete all files associated with a story.

        Args:
            story_id: Story ID
        """
        prefix = f"stories/{story_id}/"

        try:
            # List all objects with the prefix
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
            )

            if "Contents" not in response:
                logger.info(f"No files found for story {story_id}")
                return

            # Delete all objects
            objects_to_delete = [{"Key": obj["Key"]} for obj in response["Contents"]]

            self.client.delete_objects(
                Bucket=self.bucket_name,
                Delete={"Objects": objects_to_delete},
            )

            logger.info(f"Deleted {len(objects_to_delete)} files for story {story_id}")

        except ClientError as e:
            logger.error(f"Failed to delete files for story {story_id}: {e}")
            raise

    async def upload_from_bytes(
        self,
        story_id: str,
        filename: str,
        data: bytes,
        content_type: str = "image/png",
    ) -> str:
        """
        Upload an image from bytes.

        Args:
            story_id: Story ID
            filename: File name
            data: Image data as bytes
            content_type: MIME type

        Returns:
            Object key of the uploaded file
        """
        file_obj = io.BytesIO(data)
        return await self.upload_image(story_id, filename, file_obj, content_type)

    def health_check(self) -> bool:
        """
        Check if storage service is accessible.

        Returns:
            True if accessible, False otherwise
        """
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            logger.error(f"Storage health check failed: {e}")
            return False


# Singleton instance
storage_service = StorageService()
