from django.contrib.auth.models import AbstractUser
from django.db import models
# from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    otp_secret = models.CharField(max_length=16, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    is_authority = models.BooleanField(default=False)
    authority_level = models.IntegerField(null=True, blank=True) 
    


