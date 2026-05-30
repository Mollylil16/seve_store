from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from vendor.models.categorie import Categorie
from vendor.models.produit import Produit, ImageProduit
from vendor.filters import ProduitFilter
from vendor.serializers.serializers import (
    CategorieSerializer,
    ProduitSerializer,
    ProduitListSerializer,
    ImageProduitSerializer,
)


class CategorieViewSet(viewsets.ModelViewSet):
    """
    CRUD catégories.
    - Lecture publique
    - Écriture réservée aux admins
    """

    serializer_class = CategorieSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["active", "parent"]
    search_fields = ["nom", "description"]
    ordering_fields = ["nom", "ordre", "cree_le"]
    ordering = ["ordre"]

    def get_queryset(self):
        qs = Categorie.objects.prefetch_related("sous_categories")
        if not self.request.user.is_staff:
            qs = qs.filter(active=True)
        # Racines uniquement par défaut
        if self.request.query_params.get("racines", None) == "true":
            qs = qs.filter(parent__isnull=True)
        return qs

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class ProduitViewSet(viewsets.ModelViewSet):
    """
    CRUD produits.
    - Lecture publique
    - Création/modification réservée aux vendeurs/admins
    """

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProduitFilter
    search_fields = ["nom", "description", "description_courte"]
    ordering_fields = ["prix", "cree_le", "nom", "stock"]
    ordering = ["-cree_le"]

    def get_queryset(self):
        qs = Produit.objects.select_related(
            "categorie", "vendeur"
        ).prefetch_related("images", "avis")

        if not self.request.user.is_authenticated or not self.request.user.is_staff:
            qs = qs.filter(actif=True)

        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return ProduitListSerializer
        return ProduitSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(vendeur=self.request.user)

    @action(detail=True, methods=["post"], url_path="images",
            permission_classes=[permissions.IsAuthenticated])
    def upload_image(self, request, pk=None):
        """Upload d'une image pour ce produit."""
        produit = self.get_object()
        serializer = ImageProduitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(produit=produit)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="avis",
            permission_classes=[permissions.AllowAny])
    def get_avis(self, request, pk=None):
        """Retourne les avis approuvés d'un produit."""
        from customer.models.avis import Avis
        from customer.serializers.serializers import AvisSerializer
        produit = self.get_object()
        avis = Avis.objects.filter(produit=produit, approuve=True).select_related("user")
        serializer = AvisSerializer(avis, many=True, context={"request": request})
        return Response(serializer.data)
