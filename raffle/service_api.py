from datetime import timedelta

import requests
import requests_cache
from django.conf import settings


RAFFLE_URL = f'{settings.LOTTERY_SERVICE_URL}raffle/'


requests_cache.install_cache('test_cache', backend='memory', expire_after=timedelta(weeks=1))


class ServiceLotteryException(Exception):
    pass


def _check_response(response):
    if response.status_code >= 400:
        raise ServiceLotteryException(response.json())
    return response


def execute_raffle(items):
    response = requests.post(RAFFLE_URL, json={'items': items})
    _check_response(response)
    return response.json()


def get_raffles_executions_at_date(date):
    data = {
        'executed_at_after': date,
        'executed_at_before': date + timedelta(days=1)
    }
    response = requests.get(RAFFLE_URL, data=data)
    _check_response(response)
    # Todo: Get all pagination results
    return response.json()['results']
