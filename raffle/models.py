from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from django.db import models


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


class RaffleApplication(models.Model):
    raffle = models.ForeignKey(Raffle, on_delete=models.PROTECT)
    buyer_cpf = models.CharField(max_length=11)
    buyer_email = models.EmailField()
    winner = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.raffle.raffled:
            raise RuntimeError('This raffle is already closed')
        super().save(*args, **kwargs)
