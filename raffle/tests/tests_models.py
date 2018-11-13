from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from model_mommy import mommy

from raffle.models import Raffle, RaffleApplication


class RaffleTestCase(TestCase):

    def test_property_raffled(self):
        raffle_1 = mommy.make(Raffle, closed_in=timezone.now())
        raffle_2 = mommy.make(Raffle, closed_in=None)
        self.assertTrue(raffle_1.raffled)
        self.assertFalse(raffle_2.raffled)

    def test_property_winners(self):
        raffle = mommy.make(Raffle, quantity=99)
        mommy.make(RaffleApplication, raffle=raffle)
        mommy.make(RaffleApplication, raffle=raffle, winner=True)
        raffle.refresh_from_db()
        self.assertEqual(raffle.winners.count(), 1)

    def test_cant_apply_in_raffled_application(self):
        raffle = mommy.make(Raffle, closed_in=timezone.now())
        with self.assertRaises(RuntimeError):
            mommy.make(RaffleApplication, raffle=raffle)

    @patch('raffle.models.execute_raffle', return_value={'result': '1'})
    def test_execute_raffle(self, mock_execute):
        raffle = mommy.make(Raffle, quantity=99)
        apl = mommy.make(RaffleApplication, raffle=raffle)
        raffle.execute_raffle()
        mock_execute.assert_called()
        apl.refresh_from_db()
        self.assertTrue(apl.winner)

    def test_execute_raffle_raises_if_none_applications(self):
        raffle = mommy.make(Raffle)
        with self.assertRaises(RuntimeError):
            raffle.execute_raffle()
