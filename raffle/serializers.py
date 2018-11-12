from rest_framework import serializers

from raffle.models import Raffle


class RaffleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Raffle
        fields = '__all__'
        read_only_fields = ('id', 'creator', 'closed_in')

    def validate(self, data):
        if self.instance and self.instance.closed_in:
            raise serializers.ValidationError(
                "You can't change a raffle that has already been closed")
        return data
