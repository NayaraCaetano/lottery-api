from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView, GenericAPIView
from rest_framework.response import Response

from raffle.serializers import RaffleSerializer
from raffle.service_api import ServiceLotteryException


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


class ExecuteRaffleAPIView(GenericAPIView):
    serializer_class = RaffleSerializer

    def get_queryset(self):
        return self.request.user.raffle_set.all()

    def get(self, *args, **kwargs):
        obj = self.get_object()

        try:
            obj.execute_raffle()
        except RuntimeError as e:
            raise ValidationError(str(e))
        except ServiceLotteryException as e:
            raise ValidationError(
                'The lottery service is experiencing problems, please try again later')

        serializer = self.get_serializer(instance=obj)
        return Response(serializer.data)
