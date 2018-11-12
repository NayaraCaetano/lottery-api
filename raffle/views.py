from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView

from raffle.serializers import RaffleSerializer


class RaffleListCreateAPIView(ListCreateAPIView):
    serializer_class = RaffleSerializer

    def get_queryset(self):
        return self.request.user.raffle_set.all()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class RaffleRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = RaffleSerializer

    def get_queryset(self):
        return self.request.user.raffle_set.all()

    def perform_destroy(self, instance):
        if instance.raffleapplication_set.exists():
            raise ValidationError("You can not delete a raffle that has already been purchased")
        instance.delete()
