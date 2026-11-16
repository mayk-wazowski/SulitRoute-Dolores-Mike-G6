from django.conf import settings
from django.db import models


class Profile(models.Model):
    ROLE_CHOICES = [
        ('shopper', 'Shopper'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='shopper')
    contact_number = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"