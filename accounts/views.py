from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from accounts.models import User, PendingUser, Token, TokenType
from django.contrib import messages, auth  # Import the custom user model
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from datetime import datetime, timezone
from common.tasks import send_verification_email
from django.contrib.auth import get_user_model

from accounts.decorators import redirect_authenticated_user

# Create your views here.
def home(request: HttpRequest):
    return render(request, 'home.html')


@redirect_authenticated_user
def login(request: HttpRequest):
    if request.method == 'POST':
        email: str = request.POST.get('email')
        password: str = request.POST.get('password')
        user = auth.authenticate(request, email=email.lower(), password=password)
        
        if user is not None:
            auth.login(request, user)
            messages.success(request, "Login successful.")
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login')
        
    else:
        return render(request, 'login.html')
    
def logout(request: HttpRequest):
    auth.logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')


@redirect_authenticated_user
def register(request: HttpRequest):
    if request.method == 'POST':
        # Handle form submission logic here
        email : str = request.POST.get('email')
        password : str = request.POST.get('password')
        cleaned_email = email.lower()

        if User.objects.filter(email=cleaned_email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')
        else:
            # Verify the  email
            code = get_random_string(length=10)
            PendingUser.objects.update_or_create(
                email=cleaned_email,
                defaults={
                    'password': make_password(password),
                    'verification_code': code,
                    'created_at': datetime.now(timezone.utc)
                }
            )
            # Send verification email
            send_verification_email(
                subject="Verify your email",
                email_to=[cleaned_email],
                html_template='emails/email_verification_template.html',
                context={
                    'verification_code': code,
                }
            )
            messages.success(request, f"Verification email sent. Please check your inbox {cleaned_email}.")
            return render(request, 'verify_account.html', context={'email': cleaned_email})
    
    else:
        return render(request, 'register.html',)
    

def verify_account(request: HttpRequest):
    if request.method == 'POST':
        code: str = request.POST['code']
        email: str = request.POST['email']
        pending_user: PendingUser = PendingUser.objects.filter(
            verification_code=code, email=email
        ).first()
        if pending_user and pending_user.is_valid(): # Assuming is_valid checks if the code is still valid
            user = User.objects.create(
                email=pending_user.email, password=pending_user.password
            )
            pending_user.delete()
            auth.login(request, user)
            messages.success(request, "Account verified successfully. You are now logged in.")
            return redirect('home')
        else:
            messages.error(request, "Invalid or expired verification code.")
            return render(request, 'verify_account.html', {'email': email}, status=400)
        

def password_reset(request: HttpRequest):
    if request.method == 'POST':
        email: str = request.POST.get('email', "")
        user = get_user_model().objects.filter(email=email.lower()).first()

        if user:
            # Generate a password reset token and send it via email
            token, _ = Token.objects.update_or_create(
                user=user,
                token_type=TokenType.PASSWORD_RESET,
                defaults={
                    'token': get_random_string(length=20),
                    'created_at': datetime.now(timezone.utc)
                }
            )

            email_data = {
                'email': email.lower(),
                'token': token.token,
            }
            send_verification_email(
                subject="Password Reset Request",
                email_to=[email.lower()],
                html_template='emails/password_reset_template.html',
                context=email_data
            )
            messages.success(request, "Password reset link sent to your email.")
            return redirect('password_reset')

            
        else:
            messages.error(request, "Email not found.")
            return redirect('password_reset')
    
    return render(request, 'password_reset.html')


def verify_password_reset_link(request: HttpRequest):
    """
    Verify the password reset link and allow the user to set a new password."""
    email = request.GET.get('email')
    reset_token = request.GET.get('token')

    token = Token.objects.filter(
        user__email=email, token=reset_token, token_type=TokenType.PASSWORD_RESET
    ).first()

    if not token or not token.is_valid():
        messages.error(request, "Invalid or expired password reset link.")
        return redirect('password_reset')

    return render(
        request, 
        'set_new_password_using_reset_token.html', 
        context={'token': reset_token, 'email': email},
        )


def set_new_password(request: HttpRequest):
    """Set a new password for the user."""
    password1: str = request.POST.get('password1')
    password2: str = request.POST.get('password2')
    email: str = request.POST.get('email')
    reset_token: str = request.POST.get('token')

    if password1 != password2:
        messages.error(request, "Passwords do not match.")
        return render(
            request,
            'set_new_password_using_reset_token.html',
            context={'token': reset_token, 'email': email}
            )
    
    token: Token = Token.objects.filter(
        token=reset_token, user__email=email, token_type=TokenType.PASSWORD_RESET
    ).first()

    if not token or not token.is_valid():
        messages.error(request, "Invalid or expired password reset link.")
        return redirect('password_reset')
    
    token.reset_user_password(password1)
    token.delete()  # Optionally delete the token after use
    messages.success(request, "Your password has been reset successfully. You can now log in.")
    return redirect('login')