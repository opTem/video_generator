from django.db import models
from django.utils.timezone import now

class Video(models.Model):
    theme = models.CharField(max_length=255, default="Нет данных")
    text = models.TextField(default="Нет данных")
    tiktok_description = models.TextField(default="")

    frame_1_text = models.TextField(default="Нет данных")
    frame_2_text = models.TextField(default="Нет данных")
    frame_3_text = models.TextField(default="Нет данных")
    frame_4_text = models.TextField(default="Нет данных")  # ✅ Добавлено
    frame_5_text = models.TextField(default="Нет данных")  # ✅ Добавлено

    frame_1_prompt = models.TextField(default="Нет данных")
    frame_2_prompt = models.TextField(default="Нет данных")
    frame_3_prompt = models.TextField(default="Нет данных")
    frame_4_prompt = models.TextField(default="Нет данных")  # ✅ Добавлено
    frame_5_prompt = models.TextField(default="Нет данных")  # ✅ Добавлено

    music_prompt = models.TextField(null=True, blank=True)

    background_image_1 = models.ImageField(upload_to="backgrounds/", null=True, blank=True)
    background_image_2 = models.ImageField(upload_to="backgrounds/", null=True, blank=True)
    background_image_3 = models.ImageField(upload_to="backgrounds/", null=True, blank=True)
    background_image_4 = models.ImageField(upload_to="backgrounds/", null=True, blank=True)  # ✅ Добавлено
    background_image_5 = models.ImageField(upload_to="backgrounds/", null=True, blank=True)  # ✅ Добавлено

    audio_file = models.FileField(upload_to="audio/", null=True, blank=True)
    music_file = models.FileField(upload_to="music/", null=True, blank=True)
    final_video = models.FileField(upload_to="videos/", null=True, blank=True)

    ssml_text = models.TextField(null=True, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"Видео ({self.theme}) - {self.created_at}"
