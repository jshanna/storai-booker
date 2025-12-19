"""Tests for story sharing and comments API."""
import pytest
from httpx import AsyncClient, ASGITransport
from beanie import PydanticObjectId

from main import app
from app.models.storybook import Storybook, GenerationInputs
from app.models.comment import Comment
from app.models.user import User
from app.services.auth import auth_service


@pytest.fixture
async def story_with_user(init_test_db):
    """Create a story with an authenticated user."""
    # Create user
    user = await auth_service.create_user(
        email="storyowner@example.com",
        password="TestPass123",
        full_name="Story Owner",
    )

    # Create story
    story = Storybook(
        user_id=str(user.id),
        title="Test Story for Sharing",
        generation_inputs=GenerationInputs(
            audience_age=7,
            topic="A brave squirrel",
            setting="Enchanted forest",
            format="storybook",
            illustration_style="watercolor",
            characters=["Hazel the squirrel"],
            page_count=10,
        ),
        status="complete",
    )
    await story.insert()

    # Get auth tokens
    tokens = auth_service.create_token_pair(user)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    return story, user, headers


@pytest.fixture
async def second_user(init_test_db):
    """Create a second user for testing permissions."""
    user = await auth_service.create_user(
        email="seconduser@example.com",
        password="TestPass123",
        full_name="Second User",
    )
    tokens = auth_service.create_token_pair(user)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    return user, headers


class TestEnableSharing:
    """Tests for POST /api/stories/{id}/share endpoint."""

    @pytest.mark.asyncio
    async def test_enable_sharing_success(self, story_with_user):
        """Test successfully enabling sharing for a story."""
        story, user, headers = story_with_user

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers=headers,
        ) as client:
            response = await client.post(f"/api/stories/{story.id}/share")

        assert response.status_code == 200
        data = response.json()
        assert data["is_shared"] is True
        assert data["share_token"] is not None
        assert len(data["share_token"]) == 32  # token_urlsafe(24) produces 32 chars
        assert data["share_url"] is not None
        assert data["shared_at"] is not None

    @pytest.mark.asyncio
    async def test_enable_sharing_requires_auth(self, story_with_user):
        """Test that enabling sharing requires authentication."""
        story, _, _ = story_with_user

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(f"/api/stories/{story.id}/share")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_enable_sharing_requires_ownership(self, story_with_user, second_user):
        """Test that only the story owner can enable sharing."""
        story, _, _ = story_with_user
        _, second_headers = second_user

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers=second_headers,
        ) as client:
            response = await client.post(f"/api/stories/{story.id}/share")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_enable_sharing_not_found(self, story_with_user):
        """Test enabling sharing for a non-existent story."""
        _, _, headers = story_with_user
        fake_id = str(PydanticObjectId())

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers=headers,
        ) as client:
            response = await client.post(f"/api/stories/{fake_id}/share")

        assert response.status_code == 404


class TestDisableSharing:
    """Tests for DELETE /api/stories/{id}/share endpoint."""

    @pytest.mark.asyncio
    async def test_disable_sharing_success(self, story_with_user):
        """Test successfully disabling sharing for a story."""
        story, user, headers = story_with_user

        # First enable sharing
        story.is_shared = True
        story.share_token = "test_token_12345678901234567890"
        await story.save()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers=headers,
        ) as client:
            response = await client.delete(f"/api/stories/{story.id}/share")

        assert response.status_code == 200
        data = response.json()
        assert data["is_shared"] is False
        assert data["share_token"] is None
        assert data["share_url"] is None

    @pytest.mark.asyncio
    async def test_disable_sharing_requires_ownership(self, story_with_user, second_user):
        """Test that only the story owner can disable sharing."""
        story, _, _ = story_with_user
        _, second_headers = second_user

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers=second_headers,
        ) as client:
            response = await client.delete(f"/api/stories/{story.id}/share")

        assert response.status_code == 403


class TestGetSharedStory:
    """Tests for GET /api/shared/{token} endpoint."""

    @pytest.mark.asyncio
    async def test_get_shared_story_success(self, story_with_user):
        """Test successfully getting a shared story."""
        story, user, _ = story_with_user

        # Enable sharing
        story.is_shared = True
        story.share_token = "test_token_abc123"
        await story.save()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/api/shared/test_token_abc123")

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Story for Sharing"
        assert data["is_shared"] is True
        assert data["owner_name"] == "Story Owner"

    @pytest.mark.asyncio
    async def test_get_shared_story_not_shared(self, story_with_user):
        """Test getting a story that is not shared returns 404."""
        story, _, _ = story_with_user

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/api/shared/nonexistent_token")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_shared_story_after_unshare(self, story_with_user):
        """Test that a story is not accessible after sharing is disabled."""
        story, _, headers = story_with_user

        # Enable sharing first
        story.is_shared = True
        story.share_token = "test_token_xyz789"
        await story.save()

        # Disable sharing
        story.is_shared = False
        await story.save()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/api/shared/test_token_xyz789")

        assert response.status_code == 404


class TestComments:
    """Tests for comment endpoints."""

    @pytest.mark.asyncio
    async def test_create_comment_success(self, story_with_user, second_user):
        """Test successfully creating a comment."""
        story, _, _ = story_with_user
        commenter, commenter_headers = second_user

        # Enable sharing
        story.is_shared = True
        story.share_token = "comment_test_token"
        await story.save()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers=commenter_headers,
        ) as client:
            response = await client.post(
                "/api/shared/comment_test_token/comments",
                json={"text": "Great story!"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["text"] == "Great story!"
        assert data["author_name"] == "Second User"
        assert data["story_id"] == str(story.id)

    @pytest.mark.asyncio
    async def test_create_comment_requires_auth(self, story_with_user):
        """Test that creating a comment requires authentication."""
        story, _, _ = story_with_user

        story.is_shared = True
        story.share_token = "auth_test_token"
        await story.save()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/api/shared/auth_test_token/comments",
                json={"text": "Great story!"},
            )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_comments_success(self, story_with_user, second_user):
        """Test listing comments on a shared story."""
        story, _, _ = story_with_user
        commenter, _ = second_user

        # Enable sharing
        story.is_shared = True
        story.share_token = "list_comments_token"
        await story.save()

        # Create some comments
        for i in range(3):
            comment = Comment(
                story_id=str(story.id),
                user_id=str(commenter.id),
                author_name="Second User",
                text=f"Comment {i}",
            )
            await comment.insert()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/api/shared/list_comments_token/comments")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["comments"]) == 3

    @pytest.mark.asyncio
    async def test_delete_comment_as_author(self, story_with_user, second_user):
        """Test deleting a comment as the comment author."""
        story, _, _ = story_with_user
        commenter, commenter_headers = second_user

        # Enable sharing
        story.is_shared = True
        story.share_token = "delete_test_token"
        await story.save()

        # Create comment
        comment = Comment(
            story_id=str(story.id),
            user_id=str(commenter.id),
            author_name="Second User",
            text="My comment to delete",
        )
        await comment.insert()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers=commenter_headers,
        ) as client:
            response = await client.delete(f"/api/comments/{comment.id}")

        assert response.status_code == 204

        # Verify comment is deleted
        deleted = await Comment.get(comment.id)
        assert deleted is None

    @pytest.mark.asyncio
    async def test_delete_comment_as_story_owner(self, story_with_user, second_user):
        """Test deleting a comment as the story owner."""
        story, owner, owner_headers = story_with_user
        commenter, _ = second_user

        # Enable sharing
        story.is_shared = True
        story.share_token = "owner_delete_token"
        await story.save()

        # Create comment by another user
        comment = Comment(
            story_id=str(story.id),
            user_id=str(commenter.id),
            author_name="Second User",
            text="Comment on owner's story",
        )
        await comment.insert()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers=owner_headers,
        ) as client:
            response = await client.delete(f"/api/comments/{comment.id}")

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_comment_forbidden(self, story_with_user, second_user, init_test_db):
        """Test that unauthorized users cannot delete comments."""
        story, owner, _ = story_with_user
        _, _ = second_user

        # Create a third user
        third_user = await auth_service.create_user(
            email="thirduser@example.com",
            password="TestPass123",
            full_name="Third User",
        )
        third_tokens = auth_service.create_token_pair(third_user)
        third_headers = {"Authorization": f"Bearer {third_tokens['access_token']}"}

        # Enable sharing
        story.is_shared = True
        story.share_token = "forbidden_delete_token"
        await story.save()

        # Create comment by owner
        comment = Comment(
            story_id=str(story.id),
            user_id=str(owner.id),
            author_name="Story Owner",
            text="Owner's comment",
        )
        await comment.insert()

        # Third user tries to delete
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers=third_headers,
        ) as client:
            response = await client.delete(f"/api/comments/{comment.id}")

        assert response.status_code == 403


class TestRateLimiting:
    """Tests for comment rate limiting."""

    @pytest.mark.asyncio
    async def test_comment_rate_limit(self, story_with_user, second_user):
        """Test that users are rate limited when posting too many comments."""
        story, _, _ = story_with_user
        commenter, commenter_headers = second_user

        # Enable sharing
        story.is_shared = True
        story.share_token = "rate_limit_token"
        await story.save()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers=commenter_headers,
        ) as client:
            # Post 10 comments (the limit)
            for i in range(10):
                response = await client.post(
                    "/api/shared/rate_limit_token/comments",
                    json={"text": f"Comment {i}"},
                )
                assert response.status_code == 201

            # 11th comment should be rate limited
            response = await client.post(
                "/api/shared/rate_limit_token/comments",
                json={"text": "One too many"},
            )
            assert response.status_code == 429
