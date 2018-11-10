from django.test import TestCase
from model_mommy import mommy
from parameterized import parameterized
from rest_framework.reverse import reverse_lazy

from authentication.models import User


class LoginIntegrationTestCase(TestCase):
    URL = reverse_lazy('user_login')

    def _create_user(self, email, password):
        user = mommy.make(User, email=email)
        user.set_password(password)
        user.save()
        return user

    @parameterized.expand([
        ({'email': 'test@test.com', 'password': ''},),
        ({'email': '', 'password': '1234qwert'},)
    ])
    def test_user_try_log_in_without_one_of_the_required_fields(self, data):
        self._create_user('test@test.com', '1234qwert')
        response = self.client.post(self.URL, data)
        self.assertEqual(400, response.status_code)

    @parameterized.expand([
        ({'email': 'incorrect@test.com', 'password': '1234qwert'},),
        ({'email': 'test@test.com', 'password': 'incorrect'},)
    ])
    def test_user_try_log_in_with_invalid_credentials(self, data):
        self._create_user('test@test.com', '1234qwert')
        response = self.client.post(self.URL, data)
        self.assertEqual(400, response.status_code)

    def test_successful_auth_must_return_the_user_auth_token(self):
        data = {'email': 'test@test.com', 'password': '1234qwert'}
        self._create_user(**data)
        response = self.client.post(self.URL, data)
        self.assertTrue(response.json().get('token') is not None)

    def test_doesnt_need_authentication(self):
        data = {'email': 'test@test.com', 'password': '1234qwert'}
        self._create_user(**data)
        response = self.client.post(self.URL, data)
        self.assertFalse(response.status_code is 401)