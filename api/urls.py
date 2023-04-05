from django.urls import path

from . import views

urlpatterns = [
    path('loginUser', views.loginUser, name='loginUser'),
    path('regUser', views.regUser, name='regUser'),
    path('createCamera', views.create_camera, name='create_camera'),
    path('deleteCamera', views.delete_camera, name='delete_camera'),
    path('editCamera', views.edit_camera, name="edit_camera")
]