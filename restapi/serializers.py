from rest_framework import serializers
from main.models import *

class CamerasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = (
            'id',
            'name',
            'url',
            'user',
            'description',
            'creationDate',
            'direction',
            'line_place',
            'line_width',
            'model',
            'pid',
            'status',
            'current_counter',
            'sample_image',
        )