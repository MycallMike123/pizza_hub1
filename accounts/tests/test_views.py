from django.urls import reverse
from django.test.client import Client
from accounts.models import PendingUser, User, Token, TokenType
from django.contrib.auth.hashers import check_password
from django.contrib.messages import get_messages
from django.contrib.auth import get_user
from datetime import datetime, timezone

from conftest import auth_user_password


def test_register_user(db, client: Client):
    """
    Test the user registration view.
    """
    url = reverse('register')
    request_data = {
        'email': 'test@example.com',
        'password': 'testpassword',
    }
    response = client.post(url, request_data)
    assert response.status_code == 200
    pending_user = PendingUser.objects.filter(email=request_data['email']).first()
    assert pending_user
    assert check_password(request_data['password'], pending_user.password)

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == "success"
    assert "Verification email sent. Please check your inbox" in str(messages[0])

def test_register_user_already_exists(client: Client, user_instance):
    """
    Test the user registration view when the email already exists.
    """
    url = reverse('register')
    request_data = {
        'email': user_instance.email,
        'password': 'testpassword',
    }
    response = client.post(url, request_data)
    assert response.status_code == 302
    assert response.url == reverse('register')
    # Check if the message is an error about email already existing
    messages = list(get_messages(response.wsgi_request))
    assert messages[0].level_tag == "error"
    assert "Email already registered." in str(messages[0])


def test_verify_account(db, client: Client):
    """
    Test the account verification view.
    """
    pending_user = PendingUser.objects.create(
        email="test2@example.com",
        verification_code="testcode",
        password=("testpassword")
    )
    url = reverse('verify_account')
    request_data = {
        'code': pending_user.verification_code,
        'email': pending_user.email,
    }
    response = client.post(url, data=request_data)
    assert response.status_code == 302
    assert response.url == reverse('home')
    user = get_user(response.wsgi_request)
    assert user.is_authenticated


def test_verify_account_invalid_code(db, client: Client):
    """
    Test the user registration view when the email already exists.
    """
    pending_user = PendingUser.objects.create(
        email="test2@example.com",
        verification_code="testcode",
        password=("testpassword")
    )
    url = reverse('verify_account')
    request_data = {
        'code': "invalidcode",
        'email': pending_user.email,
    }
    response = client.post(url, request_data)
    assert response.status_code == 400
    assert User.objects.count() == 0

    # Check if the message is an error about invalid verification code
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == "error"
    assert "Invalid or expired verification code." in str(messages[0])


def test_login_valid_credentials(client: Client, user_instance, auth_user_password):
    """
    Test the login view with valid credentials.
    """
    url = reverse('login')
    request_data = {
        'email': user_instance.email,
        'password': auth_user_password
    }
    response = client.post(url, request_data)
    assert response.status_code == 302  # Should redirect to home page
    assert response.url == reverse('home')

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == "success"
    assert "Login successful." in str(messages[0])

def test_login_invalid_credentials(client: Client, user_instance):
    """
    Test the login view with invalid credentials.
    """
    url = reverse('login')
    request_data = {
        'email': user_instance.email,
        'password': 'wrongpassword'
    }
    response = client.post(url, request_data)
    assert response.status_code == 302  # Should return to login page
    assert response.url == reverse('login')

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == "error"
    assert "Invalid email or password." in str(messages[0])


def test_password_reset_request_using_registered_email(client: Client, user_instance):
    """
    Test the password reset request view using a registered email.
    """
    url = reverse('password_reset')
    request_data = {
        'email': user_instance.email,
    }
    response = client.post(url, request_data)
    assert response.status_code == 302  # Should redirect to password reset link page
    assert Token.objects.get(user__email=request_data['email'], token_type=TokenType.PASSWORD_RESET)

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == "success"
    assert "Password reset link sent to your email." in str(messages[0])


def test_password_reset_request_using_unregistered_email(db, client: Client):
    """
    Test the password reset request view using an unregistered email.
    """
    url = reverse('password_reset')
    request_data = {
        'email': 'unregistered@example.com'
    }
    response = client.post(url, request_data)
    assert response.status_code == 302  # Should redirect to password reset link page

    assert not Token.objects.filter(user__email=request_data['email'], token_type=TokenType.PASSWORD_RESET).first()
    # Check if the message is an error about email not found

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == "error"
    assert "Email not found." in str(messages[0])


def test_verify_password_reset_link_valid_token(db, client: Client, user_instance):
    """
    Test the password reset link verification with a valid token.
    """
    url = reverse('set_new_password')
    # Create a token for the user
    reset_token = Token.objects.create(
        user=user_instance,
        token_type=TokenType.PASSWORD_RESET,
        token="validtoken",
        created_at=datetime.now(timezone.utc)

    )
    request_data = {
        'password1': 'newpassword123',
        'password2': 'newpassword123',
        'email': user_instance.email,
        'token': reset_token.token,
    }

    response = client.post(url, request_data)
    assert response.status_code == 302 # Should redirect to login page
    assert response.url == reverse('login')
    assert Token.objects.count() == 0  # Token should be deleted after use

    user_instance.refresh_from_db()
    assert user_instance.check_password(request_data['password1'])

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == "success"
    assert "Your password has been reset successfully. You can now log in." in str(messages[0])


def test_verify_password_reset_link_invalid_token(db, client: Client, user_instance):
    """
    Test the password reset link verification with an invalid token.
    """
    url = reverse('set_new_password')

    # Create a token for the user
    reset_token = Token.objects.create(
        user=user_instance,
        token_type=TokenType.PASSWORD_RESET,
        token="validtoken",
        created_at=datetime.now(timezone.utc)
     )

    request_data = {
        'password1': 'newpassword123',
        'password2': 'newpassword123',
        'email': 'user_instance.email',
        'token': 'invalidtoken',
    }

    response = client.post(url, request_data)
    assert response.status_code == 302 # Should redirect to password reset page
    assert response.url == reverse('password_reset')
    assert Token.objects.count() == 1  # Token should not be deleted

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == "error"
    assert "Invalid or expired password reset link." in str(messages[0])
