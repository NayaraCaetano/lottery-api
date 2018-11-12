from django.conf.urls import url

from raffle.views import RaffleListCreateAPIView, RaffleRetrieveUpdateDestroyAPIView


urlpatterns = [
    url(r'^$', RaffleListCreateAPIView.as_view(), name='raffles'),
    url(r'^(?P<pk>[0-9]+)', RaffleRetrieveUpdateDestroyAPIView.as_view(), name='raffle_details'),
]