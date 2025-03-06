from django.contrib import admin
from .models import Partner, TrainingData, ChatHistory

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)

@admin.register(TrainingData)
class TrainingDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'partner', 'question', 'answer')
    search_fields = ('question', 'answer')
    list_filter = ('partner',)

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'platform', 'message', 'response', 'timestamp')
    search_fields = ('user_id', 'message', 'response')
    list_filter = ('platform', 'timestamp')
