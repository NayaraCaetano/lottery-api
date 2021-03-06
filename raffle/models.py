from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from django.db import models

from raffle.service_api import execute_raffle


class Raffle(models.Model):
    creator = models.ForeignKey('authentication.User', on_delete=models.PROTECT)
    name = models.CharField(max_length=254)
    prize = ArrayField(models.CharField(max_length=254))
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)], help_text='Application max quantity')
    closed_in = models.DateTimeField(blank=True, null=True)

    @property
    def raffled(self):
        return True if self.closed_in else False

    @property
    def winners(self):
        return self.raffleapplication_set.filter(winner=True)

    def execute_raffle(self):
        items = self.raffleapplication_set.exclude(winner=True).values_list('id', flat=True)
        if not items:
            raise RuntimeError('There are no options to draw')
        response = execute_raffle(list(items))
        items.filter(id=response['result']).update(winner=True)


class RaffleApplication(models.Model):
    raffle = models.ForeignKey(Raffle, on_delete=models.PROTECT)
    buyer_cpf = models.CharField(max_length=11)
    buyer_email = models.EmailField()
    winner = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.raffle.raffled:
            raise RuntimeError('This raffle is already closed')
        if self.raffle.quantity <= self.raffle.raffleapplication_set.count():
            raise RuntimeError('The maximum applications was reached')
        super().save(*args, **kwargs)
