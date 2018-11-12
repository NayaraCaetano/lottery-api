import pytest
from django.test import TestCase

from authentication.models import User


class UserObjectManagerTestCase(TestCase):

    def test_create_user(self):
        User.objects.create_user('test@test.com', '1234qwert')
        self.assertTrue(User.objects.filter(email='test@test.com', is_superuser=False))

    def test_create_super_user(self):
        User.objects.create_superuser('test@test.com', '1234qwert')
        self.assertTrue(User.objects.filter(email='test@test.com', is_superuser=True))

    def test_create_staff_user(self):
        User.objects.create_user('test@test.com', '1234qwert', is_staff=True)
        self.assertTrue(User.objects.filter(email='test@test.com', is_staff=True))

    def test_password_is_set_corretly(self):
        User.objects.create_user('test@test.com', '1234qwert')
        user = User.objects.get(email='test@test.com')
        self.assertTrue(user.check_password('1234qwert'))

    def test_tries_to_create_user_without_email(self):
        with pytest.raises(Exception) as excinfo:
            User.objects.create_user(password='1234qwert')

    def test_tries_to_create_superuser_without_staff_status(self):
        with pytest.raises(Exception) as excinfo:
            User.objects.create_superuser('test@test.com', '1234qwert', is_staff=False)

    def test_tries_to_create_superuser_without_superuser_status(self):
        with pytest.raises(Exception) as excinfo:
            User.objects.create_superuser('test@test.com', '1234qwert', is_superuser=False)
