from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from currencies.models import Currency

class MyUserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    email = models.EmailField(unique=True, null=True)
    is_staff = models.BooleanField('staff status',default=False,help_text='Is the user allowed to have access to the admin')
    is_active = models.BooleanField('active',default=True,help_text= 'Is the user account currently active')
    USERNAME_FIELD = 'email'
    objects = MyUserManager()

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)

    binance_api_key = models.CharField(max_length=300,default="",blank=True)
    binance_secret_key = models.CharField(max_length=300,default="",blank=True)

    hitbtc_api_key = models.CharField(max_length=300,default="",blank=True)
    hitbtc_secret_key = models.CharField(max_length=300,default="",blank=True)

    poloniex_api_key = models.CharField(max_length=300,default="",blank=True)
    poloniex_secret_key = models.CharField(max_length=300,default="",blank=True)

    coinbase_api_key = models.CharField(max_length=300,default="",blank=True)
    coinbase_secret_key = models.CharField(max_length=300,default="",blank=True)

    def __str__(self):
        return self.first_name[0].upper() + self.first_name[1:] + " " + self.last_name[0].upper() + self.last_name[1:]
