from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenVerifyView,
)
from base.viewsets.viewsets import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
)

urlpatterns = [
    # Admin Django
    path("admin/", admin.site.urls),

    # Auth JWT
    path("api/token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # Apps API
    path("api/", include("base.urls.urls")),
    path("api/", include("vendor.urls.urls")),
    path("api/", include("store.urls.urls")),
    path("api/", include("customer.urls.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)