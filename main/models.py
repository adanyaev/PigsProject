from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

class ExtendedUser(models.Model):
    phone = models.CharField(max_length=20)
    patronymic = models.CharField(max_length=30)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key = True,
        related_name='origin_user')
    is_admin = models.BooleanField(default=False)
    creationDate = models.DateTimeField(auto_now_add=True)


class Camera(models.Model):
    url = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=400)
    creationDate = models.DateTimeField(auto_now_add=True)
    direction = models.CharField(max_length=100, null=False, blank=False)
    line_place = models.FloatField(default=0.5, blank=False)
    line_width = models.IntegerField(default=20, blank=False)
    model = models.CharField(max_length=100, blank=False)
    pid = models.IntegerField(default=None, null=True)
    status = models.IntegerField(default=0)
    current_counter = models.IntegerField(default=0)
