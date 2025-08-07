import pytest
from django.test.client import Client
from django.contrib.auth.hashers import make_password, check_password

from accounts.models import User

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def user_instance(db):
    return User.objects.create(
        email="test1@example.com",
        password=make_password("testpassword")
    )

@pytest.fixture
def auth_user_password(db) -> str:
    """Return the password used for authentication in tests."""
    return "testpassword"

@pytest.fixture
def authenticate_user(client: Client, user_instance: User,
                      auth_user_password: str) -> tuple[Client, User]:
    """
    Authenticate a user for testing purposes.
    """
    client.login(email=user_instance.email, password=auth_user_password)
    return client, user_instance
