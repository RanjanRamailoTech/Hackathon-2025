from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="company")
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name