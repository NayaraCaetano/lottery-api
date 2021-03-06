from django.conf.urls import url

from raffle.views import (
    RaffleListCreateAPIView, RaffleRetrieveUpdateDestroyAPIView, ExecuteRaffleAPIView,
    RaffleApplicationAPIView)

urlpatterns = [
    url(r'^$', RaffleListCreateAPIView.as_view(), name='raffles'),
    url(r'^(?P<pk>[0-9]+)/$', RaffleRetrieveUpdateDestroyAPIView.as_view(), name='raffle_details'),
    url(r'^(?P<pk>[0-9]+)/execute', ExecuteRaffleAPIView.as_view(),
        name='raffle_execute'),
    url(r'^(?P<pk>[0-9]+)/apply', RaffleApplicationAPIView.as_view(),
        name='raffle_apply'),

]