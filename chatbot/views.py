import json

from .serializers import PartnerSerializer, TrainingDataSerializer, ChatHistorySerializer
from .serializers import PartnerSerializer
from rest_framework.views import APIView
import openai
import requests

from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Partner, ChatHistory, TrainingData
from .serializers import ChatHistorySerializer
import os

class ChatbotViewSet(viewsets.GenericViewSet):
    http_method_names = ['post']

    def get_serializer_class(self):
        return ChatHistorySerializer

    def create(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data["user_id"]
            message = serializer.validated_data["message"]
            platform = serializer.validated_data.get("platform", "Unknown")
            partner_id = request.data.get("partner_id")

            if not partner_id:
                return Response({"error": "Partner ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                partner = Partner.objects.get(id=partner_id)
            except Partner.DoesNotExist:
                return Response({"error": "Partner not found"}, status=status.HTTP_404_NOT_FOUND)

            fine_tuned_model = partner.fine_tuned_model or "gpt-3.5-turbo"

            if not fine_tuned_model.startswith("ft:") and fine_tuned_model != "gpt-3.5-turbo":
                return Response({"error": "Invalid fine-tuned model ID"}, status=status.HTTP_400_BAD_REQUEST)

            chat = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model=fine_tuned_model)

            response = chat([
                SystemMessage(content="คุณเป็นแชทบอทของร้าน BarberX ให้ตอบตาม Training Data เท่านั้น"),
                HumanMessage(content=message)
            ])

            bot_reply = response.content

            chat_history = ChatHistory.objects.create(
                user_id=user_id, platform=platform, message=message, response=bot_reply
            )

            return Response(ChatHistorySerializer(chat_history).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TrainingDataViewSet(viewsets.ModelViewSet):
    serializer_class = TrainingDataSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        partner_id = self.request.query_params.get('partner_id')
        if partner_id:
            return TrainingData.objects.filter(partner_id=partner_id)
        return TrainingData.objects.all()

    def create(self, request, *args, **kwargs):
        partner_id = request.data.get('partner')
        try:
            partner = Partner.objects.get(id=partner_id)
        except Partner.DoesNotExist:
            return Response({"error": "Partner not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(partner=partner)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class FineTuneAPIView(APIView):

    def post(self, request, partner_id):
        try:
            partner = Partner.objects.get(id=partner_id)
        except Partner.DoesNotExist:
            return Response({"error": "Partner not found"}, status=status.HTTP_404_NOT_FOUND)

        training_data = TrainingData.objects.filter(partner=partner)
        if not training_data.exists():
            return Response({"error": "No training data found. Please add training data before fine-tuning."}, status=status.HTTP_400_BAD_REQUEST)

        formatted_data = []
        for item in training_data:
            formatted_data.append({
                "messages": [
                    {"role": "user", "content": item.question},
                    {"role": "assistant", "content": item.answer}
                ]
            })

        file_path = f"fine_tune_partner_{partner.id}.jsonl"
        with open(file_path, "w", encoding="utf-8") as f:
            for item in formatted_data:
                f.write(json.dumps(item) + "\n")

        openai.api_key = os.getenv("OPENAI_API_KEY")
        with open(file_path, "rb") as file:
            response = openai.files.create(file=file, purpose="fine-tune")

        file_id = response.id
        fine_tune_response = openai.fine_tuning.jobs.create(
            training_file=file_id,
            model="gpt-3.5-turbo"
        )

        fine_tuned_model_id = fine_tune_response.id
        partner.fine_tuned_model = fine_tuned_model_id
        partner.save()

        return Response({
            "message": "Fine-Tuning started",
            "partner": partner.name,
            "model_id": fine_tuned_model_id
        }, status=status.HTTP_200_OK)

class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            partner = serializer.save()
            return Response({
                "message": "Partner created successfully",
                "partner": PartnerSerializer(partner).data,
                "api_key": partner.api_key
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

