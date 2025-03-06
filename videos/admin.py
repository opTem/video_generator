from django.contrib import admin
from .models import Video

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Video._meta.fields]

