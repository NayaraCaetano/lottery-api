from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse_lazy
from django.utils import timezone
from model_mommy import mommy
from parameterized import parameterized
from rest_framework.test import APIClient

from authentication.models import User
from raffle.models import Raffle, RaffleApplication
from raffle.service_api import ServiceLotteryException


def data_raffle():
    return {
        "name": "Test One",
        "prize": [
            "roast chicken",
            "bike"
        ],
        "quantity": 5,
    }


def data_apply():
    return {
        "buyer_cpf": "11111111111",
        "buyer_email": "bruce@batman.com"
    }


class RaffleListCreateAPIViewTestCase(TestCase):
    url = reverse_lazy('raffles')

    def setUp(self):
        self.client = APIClient()
        self.user = mommy.make(User)

    def test_only_authenticated_users(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_list_only_user_raffles(self):
        self.client.force_authenticate(self.user)
        mommy.make(Raffle, creator=self.user)
        mommy.make(Raffle, creator=self.user)
        mommy.make(Raffle, creator=self.user)
        mommy.make(Raffle)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 3)

    def test_create_new_raffle(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, data=data_raffle())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Raffle.objects.count(), 1)

    @parameterized.expand([
        ('name',),
        ('prize',),
        ('quantity',)
    ])
    def test_required_fields(self, field):
        self.client.force_authenticate(self.user)
        data = data_raffle()
        del data[field]
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Raffle.objects.count(), 0)
        self.assertEqual(len(response.json()[field]), 1)

    def test_raffle_creator_is_the_request_user(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, data=data_raffle())
        self.assertEqual(response.json()['creator'], self.user.pk)


class RaffleRetrieveUpdateDestroyAPIViewTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = mommy.make(User)
        self.obj = mommy.make(Raffle, creator=self.user, quantity=99)
        self.url = reverse_lazy('raffle_details', kwargs={'pk': self.obj.pk})

    def test_only_authenticated_users(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_see_only_user_raffles(self):
        self.client.force_authenticate(self.user)
        other = mommy.make(Raffle)
        url = reverse_lazy('raffle_details', kwargs={'pk': other.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_edit_raffle(self):
        self.client.force_authenticate(self.user)
        response = self.client.put(self.url, data=data_raffle())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Raffle.objects.count(), 1)
        self.assertEqual(response.json()['name'], data_raffle()['name'])

    @parameterized.expand([
        ('name',),
        ('prize',),
        ('quantity',)
    ])
    def test_required_fields(self, field):
        self.client.force_authenticate(self.user)
        data = data_raffle()
        del data[field]
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(response.json()[field]), 1)

    def test_alterady_closed(self):
        self.obj.closed_in = timezone.now()
        self.obj.save()
        self.client.force_authenticate(self.user)
        response = self.client.put(self.url, data=data_raffle())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Raffle.objects.count(), 1)
        self.assertEqual(len(response.json()['non_field_errors']), 1)

    @parameterized.expand([
        ('name',),
        ('prize',),
        ('quantity',)
    ])
    def test_patch_raffle(self, field):
        self.client.force_authenticate(self.user)
        data = data_raffle()
        del data[field]
        response = self.client.patch(self.url, data=data)
        self.assertEqual(response.status_code, 200)

    def test_delete_raffle(self):
        self.client.force_authenticate(self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Raffle.objects.count(), 0)

    def test_cant_delete_with_applications(self):
        self.client.force_authenticate(self.user)
        mommy.make(RaffleApplication, raffle=self.obj)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Raffle.objects.count(), 1)

    def test_close_raffle(self):
        self.client.force_authenticate(self.user)
        data = data_raffle()
        data['close_raffle'] = True
        response = self.client.patch(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.obj.refresh_from_db()
        self.assertIsNotNone(self.obj.closed_in)


class ExecuteRaffleAPIViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = mommy.make(User)
        self.obj = mommy.make(Raffle, creator=self.user, quantity=99)
        self.url = reverse_lazy('raffle_execute', kwargs={'pk': self.obj.pk})

    def test_only_authenticated_users(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_execute_only_user_raffles(self):
        self.client.force_authenticate(self.user)
        other = mommy.make(Raffle)
        url = reverse_lazy('raffle_execute', kwargs={'pk': other.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @patch('raffle.models.execute_raffle', side_effect=ServiceLotteryException())
    def test_return_if_service_error(self, mock_execution):
        self.client.force_authenticate(self.user)
        mommy.make(RaffleApplication, raffle=self.obj)
        response = self.client.get(self.url)
        mock_execution.assert_called()
        self.assertEqual(response.status_code, 400)

    def test_return_if_none_applicatinos(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)

    @patch('raffle.models.execute_raffle')
    def test_return_if_ok(self, mock_execution):
        self.client.force_authenticate(self.user)
        obj = mommy.make(RaffleApplication, raffle=self.obj)
        mock_execution.return_value = {'result': obj.id}
        mommy.make(RaffleApplication, raffle=self.obj)
        mommy.make(RaffleApplication, raffle=self.obj)
        mommy.make(RaffleApplication, raffle=self.obj)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        mock_execution.assert_called()
        self.assertEqual(len(response.json()['winners']), 1)


class RaffleApplicationAPIViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = mommy.make(User)
        self.obj = mommy.make(Raffle, creator=self.user, quantity=1)
        self.url = reverse_lazy('raffle_apply', kwargs={'pk': self.obj.pk})

    def test_apply(self):
        response = self.client.put(self.url, data=data_apply())
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.obj.raffleapplication_set.count(), 1)

    def test_cant_apply_more_than_quantity(self):
        mommy.make(RaffleApplication, raffle=self.obj)
        response = self.client.put(self.url, data=data_apply())
        self.assertEqual(400, response.status_code)

    def test_closed_raffles_arent_a_option(self):
        self.obj.closed_in = timezone.now()
        self.obj.save()
        response = self.client.put(self.url, data=data_apply())
        self.assertEqual(404, response.status_code)
