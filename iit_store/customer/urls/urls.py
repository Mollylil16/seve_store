from django.urls import path, include
from rest_framework.routers import DefaultRouter
from customer.viewsets.viewsets import (
    AdresseViewSet,
    AvisViewSet,
    FavorisViewSet,
    MoyenPaiementViewSet,
    PaiementViewSet,
)

router = DefaultRouter()
router.register(r"adresses", AdresseViewSet, basename="adresse")
router.register(r"avis", AvisViewSet, basename="avis")
router.register(r"favoris", FavorisViewSet, basename="favoris")
router.register(r"moyens-paiement", MoyenPaiementViewSet, basename="moyen-paiement")
router.register(r"paiements", PaiementViewSet, basename="paiement")

urlpatterns = [
    path("", include(router.urls)),
]
