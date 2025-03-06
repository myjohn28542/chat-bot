from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatbotViewSet, FineTuneAPIView, PartnerViewSet, TrainingDataViewSet

router = DefaultRouter()
router.register(r'chatbot', ChatbotViewSet, basename='chatbot')
router.register(r'partners', PartnerViewSet, basename='partners')
router.register(r'training_data', TrainingDataViewSet, basename='training_data')

urlpatterns = [
    path('', include(router.urls)),
    path('fine_tune/<int:partner_id>/', FineTuneAPIView.as_view(), name='fine_tune')
]
