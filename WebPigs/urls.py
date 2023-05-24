from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from WebPigs.settings import MEDIA_ROOT


urlpatterns = [
    path('', include('main.urls')),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),

    path('restapi/', include('restapi.urls'))
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)