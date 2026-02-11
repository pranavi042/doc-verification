from rest_framework import serializers
from .models import PanCard

class PanCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = PanCard
        fields = '__all__'
