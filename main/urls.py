from django.shortcuts import render
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('registration', views.register, name='registration'),
    path('cameras', views.cameras, name="cameras"),
    path('setLineSettings/<int:id>', views.setLineSettings, name="setLineSettings"),
    path('camera/<int:id>', views.camera, name="camera"),
    path('live_stream/<int:id>', views.live_stream, name="live_stream"),
]