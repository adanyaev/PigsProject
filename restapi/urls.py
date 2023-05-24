from django.urls import path
from . import views

urlpatterns = [
    path("register_user", views.RegisterUserApiView.as_view()),
    path("login_user", views.LoginUserApiView.as_view()),
    path("camera", views.CameraListApiView.as_view()),
    path("camera/<int:id>", views.CameraDetailApiView.as_view()),
    path("setup_line_settings", views.LineSettingsApiView.as_view()),
    path("reset_counter/<int:id>", views.ResetCounterApiView.as_view()),
    path("get_counter/<int:id>", views.GetCounterApiView.as_view()),
]