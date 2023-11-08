from rest_framework import serializers

from .models import Appointment


class AppointmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Appointment
        depth = 1
        field = '__all__'
