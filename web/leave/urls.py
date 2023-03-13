from django.conf import settings
from django.conf.urls.static import static
import os

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path(f'{os.environ.get("ADMIN")}/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('accounts.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
