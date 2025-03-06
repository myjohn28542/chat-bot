from rest_framework import serializers
from .models import ChatHistory, Partner, TrainingData

class ChatHistorySerializer(serializers.ModelSerializer):
    response = serializers.CharField(required=False)

    class Meta:
        model = ChatHistory
        fields = '__all__'



class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = '__all__'

class TrainingDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingData
        fields = '__all__'
