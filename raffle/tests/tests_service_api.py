from datetime import date
from unittest.mock import patch, MagicMock

from django.test import TestCase

from raffle.service_api import (
    execute_raffle, RAFFLE_URL, ServiceLotteryException, get_raffles_executions_at_date)


def response_mock(status=200):
    response = MagicMock()
    response.status_code = status
    return response


class LotteryServiceAPITestCase(TestCase):

    @patch('requests.post', return_value=response_mock())
    def test_params_sended_execute(self, mock_post):
        execute_raffle(['a', 'b', 'c'])
        mock_post.assert_called_with(RAFFLE_URL, json={'items': ['a', 'b', 'c']})

    @patch('requests.post', return_value=response_mock(400))
    def test_check_response_execute(self, mock_post):
        with self.assertRaises(ServiceLotteryException):
            execute_raffle(['a', 'b', 'c'])

    @patch('requests.get', return_value=response_mock())
    def test_params_sended_get(self, mock_post):
        data = date(2011,1,1)
        get_raffles_executions_at_date(data)
        mock_post.assert_called_with(
            RAFFLE_URL,
            data={
                'executed_at_after': data,
                'executed_at_before': date(2011,1,2)}
        )

    @patch('requests.get', return_value=response_mock(400))
    def test_check_response_get(self, mock_post):
        with self.assertRaises(ServiceLotteryException):
            data = date(2011, 1, 1)
            get_raffles_executions_at_date(data)
