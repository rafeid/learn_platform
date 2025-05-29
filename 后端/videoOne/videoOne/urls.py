from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.admin import custom_admin_site

urlpatterns = [
    path('admin/', custom_admin_site.urls),
    path('api/', include('core.urls')),  # 将 api/ 路由指向 core.urls
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # 支持文件上传