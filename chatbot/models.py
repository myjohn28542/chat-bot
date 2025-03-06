from django.db import models
import uuid

class ChatHistory(models.Model):
    user_id = models.CharField(max_length=255)
    platform = models.CharField(max_length=50, choices=[('LINE', 'LINE'), ('Telegram', 'Telegram'), ('Facebook', 'Facebook')])
    message = models.TextField()
    response = models.TextField()
    sentiment = models.CharField(max_length=50, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id} - {self.platform}"


class Partner(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    api_key = models.CharField(max_length=64, unique=True, default=uuid.uuid4().hex, editable=False)
    fine_tuned_model = models.CharField(max_length=255, blank=True, null=True)  # เก็บโมเดลที่ Fine-Tune แล้ว

    def __str__(self):
        return self.name

class TrainingData(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="training_data")
    question = models.TextField()
    answer = models.TextField()

    class Meta:
        unique_together = ('partner', 'question')

    def __str__(self):
        return f"{self.partner.name}: {self.question}"


