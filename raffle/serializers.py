from django.utils import timezone
from rest_framework import serializers

from raffle.models import Raffle, RaffleApplication


class RaffleApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = RaffleApplication
        exclude = ('raffle',)


class RaffleSerializer(serializers.ModelSerializer):
    close_raffle = serializers.BooleanField(default=False)
    winners = RaffleApplicationSerializer(read_only=True, many=True)

    class Meta:
        model = Raffle
        fields = '__all__'
        read_only_fields = ('id', 'creator', 'closed_in', 'close', 'winners')

    def validate(self, data):
        if self.instance and self.instance.closed_in:
            raise serializers.ValidationError(
                "You can't change a raffle that has already been closed")
        return data

    def create(self, validated_data):
        validated_data.pop('close_raffle', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        close_raffle = validated_data.pop('close_raffle', False)
        if close_raffle:
            instance.closed_in = timezone.now()
        return super().update(instance, validated_data)
