from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    """
    Custom manager for User model where email is the unique identifier.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and return a user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        user = self.model(email=(email), **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('The Staff field must be set to True for superusers.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('The Superuser field must be set to True for superusers.')

        user = self.create_user(email, password, **extra_fields)
        user.save()
        