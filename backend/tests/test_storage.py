"""Tests for storage service."""
import pytest
from unittest.mock import MagicMock, patch
from io import BytesIO

from app.services.storage import StorageService


@pytest.fixture
def mock_settings():
    """Mock settings."""
    with patch('app.services.storage.settings') as mock:
        mock.s3_endpoint_url = "http://localhost:9000"
        mock.s3_access_key_id = "test-access"
        mock.s3_secret_access_key = "test-secret"
        mock.s3_region = "us-east-1"
        mock.s3_bucket_name = "test-bucket"
        mock.s3_public_url = None  # Use presigned URLs, not public URLs
        mock.s3_external_endpoint_url = None  # Use same endpoint for URL generation
        yield mock


@pytest.fixture
def mock_boto_client():
    """Mock boto3 S3 client."""
    with patch('app.services.storage.boto3.client') as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture
def storage_service(mock_settings, mock_boto_client):
    """Create storage service with mocked S3 client."""
    return StorageService()


class TestStorageService:
    """Tests for StorageService."""

    def test_initialization(self, storage_service):
        """Test storage service initialization."""
        assert storage_service.bucket_name == "test-bucket"

    def test_get_object_key(self, storage_service):
        """Test object key generation."""
        key = storage_service._get_object_key("story-123", "page_1.png")
        assert key == "stories/story-123/page_1.png"

    @pytest.mark.asyncio
    async def test_upload_image(self, storage_service, mock_boto_client):
        """Test image upload."""
        file_data = BytesIO(b"test image data")
        story_id = "story-123"
        filename = "page_1.png"

        mock_boto_client.upload_fileobj = MagicMock()

        result = await storage_service.upload_image(
            story_id,
            filename,
            file_data,
            content_type="image/png"
        )

        assert result == "stories/story-123/page_1.png"
        mock_boto_client.upload_fileobj.assert_called_once()
        call_args = mock_boto_client.upload_fileobj.call_args
        assert call_args[0][1] == "test-bucket"
        assert call_args[0][2] == "stories/story-123/page_1.png"

    @pytest.mark.asyncio
    async def test_get_signed_url(self, storage_service, mock_boto_client):
        """Test presigned URL generation."""
        object_key = "stories/story-123/page_1.png"
        expected_url = "http://localhost:9000/test-bucket/stories/story-123/page_1.png?signature=xyz"

        mock_boto_client.generate_presigned_url = MagicMock(
            return_value=expected_url
        )

        result = await storage_service.get_signed_url(object_key, expiration=3600)

        assert result == expected_url
        mock_boto_client.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={'Bucket': 'test-bucket', 'Key': object_key},
            ExpiresIn=3600
        )

    @pytest.mark.asyncio
    async def test_delete_file(self, storage_service, mock_boto_client):
        """Test file deletion."""
        object_key = "stories/story-123/page_1.png"

        mock_boto_client.delete_object = MagicMock()

        await storage_service.delete_file(object_key)

        mock_boto_client.delete_object.assert_called_once_with(
            Bucket="test-bucket",
            Key=object_key
        )

    @pytest.mark.asyncio
    async def test_delete_story_files(self, storage_service, mock_boto_client):
        """Test deleting all files for a story."""
        story_id = "story-123"

        # Mock list_objects_v2 response
        mock_boto_client.list_objects_v2 = MagicMock(return_value={
            'Contents': [
                {'Key': 'stories/story-123/page_1.png'},
                {'Key': 'stories/story-123/page_2.png'},
                {'Key': 'stories/story-123/cover.png'}
            ]
        })
        mock_boto_client.delete_objects = MagicMock()

        await storage_service.delete_story_files(story_id)

        mock_boto_client.list_objects_v2.assert_called_once()
        mock_boto_client.delete_objects.assert_called_once()

        # Check that all 3 files were deleted
        delete_call_args = mock_boto_client.delete_objects.call_args
        objects_deleted = delete_call_args[1]['Delete']['Objects']
        assert len(objects_deleted) == 3

    @pytest.mark.asyncio
    async def test_delete_story_files_empty(self, storage_service, mock_boto_client):
        """Test deleting files when no files exist."""
        story_id = "story-456"

        # Mock empty list response
        mock_boto_client.list_objects_v2 = MagicMock(return_value={})

        await storage_service.delete_story_files(story_id)

        mock_boto_client.list_objects_v2.assert_called_once()
        mock_boto_client.delete_objects.assert_not_called()

    @pytest.mark.asyncio
    async def test_upload_from_bytes(self, storage_service, mock_boto_client):
        """Test upload from bytes."""
        data = b"test image bytes"
        story_id = "story-123"
        filename = "cover.png"

        mock_boto_client.upload_fileobj = MagicMock()

        result = await storage_service.upload_from_bytes(
            story_id,
            filename,
            data,
            content_type="image/png"
        )

        assert result == "stories/story-123/cover.png"
        mock_boto_client.upload_fileobj.assert_called_once()

    def test_health_check_success(self, storage_service, mock_boto_client):
        """Test health check when storage is accessible."""
        mock_boto_client.head_bucket = MagicMock(return_value={'ResponseMetadata': {'HTTPStatusCode': 200}})

        result = storage_service.health_check()

        assert result is True
        mock_boto_client.head_bucket.assert_called_once_with(Bucket='test-bucket')

    def test_health_check_failure(self, storage_service, mock_boto_client):
        """Test health check when storage is not accessible."""
        from botocore.exceptions import ClientError

        error_response = {'Error': {'Code': '403'}}
        mock_boto_client.head_bucket = MagicMock(
            side_effect=ClientError(error_response, 'head_bucket')
        )

        result = storage_service.health_check()

        assert result is False
