from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_manager = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')

    profile_bio = models.TextField()
    profile_photo_url = models.URLField(blank=True)
    profile_photo_key = models.CharField(max_length=500, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"this is the user profile for {self.user.first_name} {self.user.last_name}, email: {self.user.email}"


