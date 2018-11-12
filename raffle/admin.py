from django.contrib import admin

from raffle.models import RaffleApplication, Raffle

admin.site.register(Raffle)
admin.site.register(RaffleApplication)
