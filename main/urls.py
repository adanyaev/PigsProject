from django.shortcuts import render
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('registration', views.register, name='registration'),
    path('cameras', views.cameras, name="cameras")

]