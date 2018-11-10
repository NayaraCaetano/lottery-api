from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import AbstractUser
from django.db import models

from authentication.managers import UserManager


class User(AbstractUser):
    # changes email to unique and blank to false
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('First Name'), max_length=20)
    last_name = models.CharField(_('Last Name'), max_length=100)

    username = None
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
