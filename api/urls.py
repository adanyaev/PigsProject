from django.urls import path

from . import views

urlpatterns = [
    path('loginUser', views.loginUser, name='loginUser'),
    path('regUser', views.regUser, name='regUser'),
    path('createCamera', views.create_camera, name='create_camera'),
    path('deleteCamera', views.delete_camera, name='delete_camera'),
    path('editCamera', views.edit_camera, name="edit_camera"),
    path('setLineSettings', views.setLineSettings, name="setLineSettings"),
    path('resetCounter', views.reset_counter, name="reset_counter"),
    path('launchCameraProcess', views.launch_camera_process, name="launch_camera_process"),
    path('stopCameraProcess', views.stop_camera_process, name="stop_camera_process")
]