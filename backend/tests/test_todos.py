"""Todo tests."""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
from app.api.deps import get_redis
from app.main import app


async def get_auth_token(client: AsyncClient, email: str = "todo@example.com") -> str:
    """Helper to register and get auth token."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123"},
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_todo(client: AsyncClient):
    """Test creating a new todo."""
    token = await get_auth_token(client, "create@example.com")

    response = await client.post(
        "/api/v1/todos",
        json={"title": "Test Todo", "description": "A test todo item"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "A test todo item"
    assert data["completed"] is False


@pytest.mark.asyncio
async def test_get_todos(client: AsyncClient):
    """Test getting todo list."""
    token = await get_auth_token(client, "list@example.com")

    # Create a todo first
    await client.post(
        "/api/v1/todos",
        json={"title": "List Todo"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Get todos
    response = await client.get(
        "/api/v1/todos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_update_todo(client: AsyncClient):
    """Test updating a todo."""
    token = await get_auth_token(client, "update@example.com")

    # Create a todo
    create_response = await client.post(
        "/api/v1/todos",
        json={"title": "Update Me"},
        headers={"Authorization": f"Bearer {token}"},
    )
    todo_id = create_response.json()["id"]

    # Update it
    response = await client.put(
        f"/api/v1/todos/{todo_id}",
        json={"title": "Updated Title", "completed": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_delete_todo(client: AsyncClient):
    """Test deleting a todo."""
    token = await get_auth_token(client, "delete@example.com")

    # Create a todo
    create_response = await client.post(
        "/api/v1/todos",
        json={"title": "Delete Me"},
        headers={"Authorization": f"Bearer {token}"},
    )
    todo_id = create_response.json()["id"]

    # Delete it
    response = await client.delete(
        f"/api/v1/todos/{todo_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_single_todo(client: AsyncClient):
    """Test getting a single todo by ID."""
    token = await get_auth_token(client, "single@example.com")

    # Create a todo
    create_response = await client.post(
        "/api/v1/todos",
        json={"title": "Single Todo", "description": "Get me"},
        headers={"Authorization": f"Bearer {token}"},
    )
    todo_id = create_response.json()["id"]

    # Get it
    response = await client.get(
        f"/api/v1/todos/{todo_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Single Todo"


@pytest.mark.asyncio
async def test_user_cannot_read_another_users_todo(client: AsyncClient):
    user_a_token = await get_auth_token(client, "usera@example.com")
    user_b_token = await get_auth_token(client, "userb@example.com")

    create_response = await client.post(
        "/api/v1/todos",
        json={
            "title": "User A private todo",
            "description": "Private",
        },
        headers={"Authorization": f"Bearer {user_a_token}"},
    )

    assert create_response.status_code == 201

    todo_id = create_response.json()["id"]

    response = await client.get(
        f"/api/v1/todos/{todo_id}",
        headers={"Authorization": f"Bearer {user_b_token}"},
    )

    assert response.status_code == 404
    

@pytest.mark.asyncio
async def test_user_cannot_update_another_users_todo(client: AsyncClient):
    user_a_token = await get_auth_token(client, "update-a@example.com")
    user_b_token = await get_auth_token(client, "update-b@example.com")

    create_response = await client.post(
        "/api/v1/todos",
        json={
            "title": "User A todo",
            "description": "Original description",
        },
        headers={"Authorization": f"Bearer {user_a_token}"},
    )

    assert create_response.status_code == 201

    todo_id = create_response.json()["id"]

    response = await client.put(
        f"/api/v1/todos/{todo_id}",
        json={
            "title": "Hacked by User B",
        },
        headers={"Authorization": f"Bearer {user_b_token}"},
    )

    assert response.status_code == 404
    

@pytest.mark.asyncio
async def test_user_cannot_delete_another_users_todo(client: AsyncClient):
    user_a_token = await get_auth_token(client, "delete-a@example.com")
    user_b_token = await get_auth_token(client, "delete-b@example.com")

    create_response = await client.post(
        "/api/v1/todos",
        json={
            "title": "User A private todo",
            "description": "Must not be deleted by User B",
        },
        headers={"Authorization": f"Bearer {user_a_token}"},
    )

    assert create_response.status_code == 201

    todo_id = create_response.json()["id"]

    response = await client.delete(
        f"/api/v1/todos/{todo_id}",
        headers={"Authorization": f"Bearer {user_b_token}"},
    )

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_todo_list_cache_is_scoped_by_user(client: AsyncClient):
    user_a_token = await get_auth_token(client, "cache-a@example.com")
    user_b_token = await get_auth_token(client, "cache-b@example.com")

    mock_redis = MagicMock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock()

    app.dependency_overrides[get_redis] = lambda: mock_redis

    try:
        response_a = await client.get(
            "/api/v1/todos",
            headers={"Authorization": f"Bearer {user_a_token}"},
        )

        assert response_a.status_code == 200

        response_b = await client.get(
            "/api/v1/todos",
            headers={"Authorization": f"Bearer {user_b_token}"},
        )

        assert response_b.status_code == 200

        cache_keys = [
            call.args[0]
            for call in mock_redis.get.await_args_list
        ]

        assert len(cache_keys) == 2
        assert cache_keys[0] != cache_keys[1]

    finally:
        app.dependency_overrides.pop(get_redis, None)


@pytest.mark.asyncio
async def test_toggle_completed_from_true_to_false(client: AsyncClient):
    token = await get_auth_token(client, "toggle@example.com")

    create_response = await client.post(
        "/api/v1/todos",
        json={"title": "Toggle Todo"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]

    # true
    response = await client.put(
        f"/api/v1/todos/{todo_id}",
        json={"completed": True},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["completed"] is True

    # true -> false
    response = await client.put(
        f"/api/v1/todos/{todo_id}",
        json={"completed": False},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["completed"] is False
    
@pytest.mark.asyncio
async def test_partial_update_title_preserves_description(client: AsyncClient):
    token = await get_auth_token(client, "partial@example.com")

    create_response = await client.post(
        "/api/v1/todos",
        json={
            "title": "Original Title",
            "description": "Important description",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]

    response = await client.put(
        f"/api/v1/todos/{todo_id}",
        json={"title": "Updated Title"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Important description"