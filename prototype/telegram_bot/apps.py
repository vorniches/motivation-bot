from django.apps import AppConfig

class TelegramBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prototype.telegram_bot'  # Updated to use full path
