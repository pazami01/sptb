from django.conf import settings
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.db import models


class CustomAccountManager(BaseUserManager):
    """
    Custom version of the Django User Manager.
    It handles user and superuser creation.
    It's now required to include an email, first name and last name, in addition to username and password.
    """
    def _create_new_user(self, username, email, first_name, last_name, password, **other_fields):
        """
        Creates and returns a new user account.
        """
        if not username:
            raise ValueError('A username must be provided.')
        if not email:
            raise ValueError('An email must be provided.')
        if not first_name:
            raise ValueError('A first name must be provided.')
        if not last_name:
            raise ValueError('A last name must be provided.')

        username = self.model.normalize_username(username)
        email = self.normalize_email(email)
        
        new_user = self.model(username=username, email=email, first_name=first_name, last_name=last_name, **other_fields)
        new_user.set_password(password)
        new_user.save(using=self._db)

        return new_user
    
    def create_user(self, username, email, first_name, last_name, password, **other_fields):
        """
        Creates and returns a new regular user account.
        Raises ValueError if required arguments are not provided.
        Raises ValueError if is_staff or is_superuser fields are set to true.
        """
        # Set defaults if these fields are not provided in the arguments
        other_fields.setdefault('is_staff', False)
        other_fields.setdefault('is_superuser', False)

        # Make sure these fields have the correct value when provided in the arguments
        if other_fields.get('is_staff') is True:
            raise ValueError('regular user must not have is_staff set to true.')
        if other_fields.get('is_superuser') is True:
            raise ValueError('regular user must not have is_superuser set to true.')

        return self._create_new_user(username, email, first_name, last_name, password, **other_fields)
    
    def create_superuser(self, username, email, first_name, last_name, password, **other_fields):
        """
        Creates and returns a new superuser account.
        Raises ValueError if required arguments are not provided.
        Raises ValueError if is_staff or is_superuser fields are set to false.
        """
        # Set defaults if fields are not provided in the arguments
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)

        # Make sure these fields have the correct value when provided in the arguments
        if other_fields.get('is_staff') is False:
            raise ValueError('Superuser must set is_staff to true.')
        if other_fields.get('is_superuser') is False:
            raise ValueError('Superuser must set is_superuser to true.')

        return self._create_new_user(username, email, first_name, last_name, password, **other_fields)


class Account(AbstractBaseUser, PermissionsMixin):
    """
    Custom version of the Django User model.
    Email, first name, and last name are now required when
    creating a new user, in addition to the username and password.
    """

    # Required Fields
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Custom handling of user creation
    objects = CustomAccountManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    # username and password fields are required by default
    REQUIRED_FIELDS = ['email','first_name', 'last_name']

    def __str__(self):
        return self.username

