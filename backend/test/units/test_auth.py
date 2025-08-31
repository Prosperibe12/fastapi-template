import pytest
from unittest.mock import AsyncMock, MagicMock

from backend.api.auth.crud import UserService
from backend.core.custom_exceptions import ServiceError
from backend.api.auth.schema import RegisterSchema
from backend.models.tables import User

@pytest.mark.asyncio
async def test_get_user_by_email_returns_user():
    
    fake_user = User(id=1, email="test@example.com", full_name="Tester", hashed_password="hashed")
    fake_scalars = MagicMock()
    fake_scalars.first.return_value = fake_user

    fake_result = MagicMock()
    fake_result.scalars.return_value = fake_scalars

    fake_session = AsyncMock()
    fake_session.execute.return_value = fake_result

    user = await UserService.get_user_by_email(fake_session, "test@example.com")

    assert user == fake_user
    fake_session.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_user_by_email_raises_service_error_on_failure():
    fake_session = AsyncMock()
    fake_session.execute.side_effect = Exception("DB boom")

    with pytest.raises(ServiceError):
        await UserService.get_user_by_email(fake_session, "fail@example.com")

@pytest.mark.asyncio
async def test_user_exist_true_if_user_found():
    fake_user = User(id=1, email="test@example.com", full_name="Tester", hashed_password="hashed")

    fake_session = AsyncMock()
    UserService.get_user_by_email = AsyncMock(return_value=fake_user)

    exists = await UserService.user_exist(fake_session, "test@example.com")

    assert exists is True
    UserService.get_user_by_email.assert_awaited_once_with(fake_session, "test@example.com")

@pytest.mark.asyncio
async def test_user_exist_false_if_no_user():
    fake_session = AsyncMock()
    UserService.get_user_by_email = AsyncMock(return_value=None)

    exists = await UserService.user_exist(fake_session, "nouser@example.com")

    assert exists is False

@pytest.mark.asyncio
async def test_create_user_success():
    fake_session = AsyncMock()
    request = RegisterSchema(email="test@example.com", full_name="Tester", password="pwd12345678")

    user = await UserService.create_user(fake_session, request)

    assert isinstance(user, User)
    assert user.email == "test@example.com"
    fake_session.add.assert_called_once()
    fake_session.commit.assert_awaited_once()
    fake_session.refresh.assert_awaited_once()

@pytest.mark.asyncio
async def test_create_user_rollback_on_failure():
    fake_session = AsyncMock()
    fake_session.commit.side_effect = Exception("commit failed")

    request = RegisterSchema(email="testfail@example.com", full_name="Tester", password="pwd12345678")

    with pytest.raises(ServiceError):
        await UserService.create_user(fake_session, request)

    fake_session.rollback.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_user_success():
    fake_session = AsyncMock()
    user = User(id=1, email="up@example.com", full_name="Old Name", hashed_password="pwd")
    update_data = {"full_name": "New Name"}

    updated_user = await UserService.update_user(user, update_data, fake_session)

    assert updated_user.full_name == "New Name"
    fake_session.add.assert_called_once_with(user)
    fake_session.commit.assert_awaited_once()
    fake_session.refresh.assert_awaited_once_with(user)

@pytest.mark.asyncio
async def test_update_user_raises_on_failure():
    fake_session = AsyncMock()
    fake_session.commit.side_effect = Exception("fail commit")

    user = User(id=1, email="up@example.com", full_name="Old Name", hashed_password="pwd")
    update_data = {"full_name": "New Name"}

    with pytest.raises(ServiceError):
        await UserService.update_user(user, update_data, fake_session)
