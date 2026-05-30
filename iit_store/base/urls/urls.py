from django.urls import path, include
from rest_framework.routers import DefaultRouter
from base.viewsets.viewsets import UserViewSet, ProfilViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"profils", ProfilViewSet, basename="profil")

urlpatterns = [
    path("", include(router.urls)),
]
