from django.urls import path, include
from rest_framework.routers import DefaultRouter
from store.viewsets.viewsets import (
    ModeReglementViewSet,
    PanierViewSet,
    CommandeViewSet,
    LivraisonViewSet,
)

router = DefaultRouter()
router.register(r"modes-reglement", ModeReglementViewSet, basename="mode-reglement")
router.register(r"panier", PanierViewSet, basename="panier")
router.register(r"commandes", CommandeViewSet, basename="commande")
router.register(r"livraisons", LivraisonViewSet, basename="livraison")

urlpatterns = [
    path("", include(router.urls)),
]
