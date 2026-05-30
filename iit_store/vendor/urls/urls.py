from django.urls import path, include
from rest_framework.routers import DefaultRouter
from vendor.viewsets.viewsets import CategorieViewSet, ProduitViewSet

router = DefaultRouter()
router.register(r"categories", CategorieViewSet, basename="categorie")
router.register(r"produits", ProduitViewSet, basename="produit")

urlpatterns = [
    path("", include(router.urls)),
]
