import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from accounts.manager import UserManager
from common.models import BaseModel
from datetime import datetime, timezone


# Create your models here.
class TokenType(models.TextChoices):
    PASSWORD_RESET = ('PASSWORD_RESET')


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

class PendingUser(BaseModel):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    verification_code = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def is_valid(self) -> bool:
        """
        Check if the pending user is still valid based on the verification code.
        """

        lifespan = 20 * 60  # 20 minutes in seconds
        now = datetime.now(timezone.utc)
        timediff = (now - self.created_at).total_seconds()
        if timediff > lifespan:
            return False
        return True
    

class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    token_type = models.CharField(max_length=100, choices=TokenType.choices)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.token}"
    
    def is_valid(self) -> bool:
        """ Check if the token is still valid based on its creation time.
        """
        lifespan = 20 * 60  # 20 minutes in seconds
        now = datetime.now(timezone.utc)
        timediff = (now - self.created_at).total_seconds()
        if timediff > lifespan:
            return False
        return True
    
    def reset_user_password(self, raw_password: str):
        """ Reset the user's password using the token.
        """
        self.user: User
        self.user.set_password(raw_password)
        self.user.save()
