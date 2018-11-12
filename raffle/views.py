from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView, GenericAPIView, \
    CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from raffle.models import Raffle
from raffle.serializers import RaffleSerializer, RaffleApplicationSerializer
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


class RaffleApplicationAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    queryset = Raffle.objects.filter(closed_in__isnull=True)
    serializer_class = RaffleApplicationSerializer

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save(raffle=self.get_object())
        except RuntimeError as e:
            raise ValidationError(str(e))
        return Response(serializer.data)


