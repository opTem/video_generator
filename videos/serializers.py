from rest_framework import serializers
from django.contrib.gis.geos import Point
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    pass