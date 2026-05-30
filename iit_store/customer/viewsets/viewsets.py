from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from customer.models.adresse import Adresse
from customer.models.avis import Avis
from customer.models.favoris import Favoris
from customer.models.moyen_paiement import MoyenPaiement
from customer.models.paiement import Paiement
from customer.serializers.serializers import (
    AdresseSerializer,
    AvisSerializer,
    FavorisSerializer,
    MoyenPaiementSerializer,
    PaiementSerializer,
)


class AdresseViewSet(viewsets.ModelViewSet):
    """Gestion des adresses du client connecté."""

    serializer_class = AdresseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Adresse.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="definir-par-defaut")
    def definir_par_defaut(self, request, pk=None):
        """Définit cette adresse comme adresse par défaut."""
        adresse = self.get_object()
        adresse.par_defaut = True
        adresse.save()
        return Response({"detail": "Adresse définie comme adresse par défaut."})


class AvisViewSet(viewsets.ModelViewSet):
    """
    Gestion des avis produits.
    - Lecture publique des avis approuvés
    - Création réservée aux utilisateurs authentifiés
    - Modération réservée aux admins
    """

    serializer_class = AvisSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["produit", "approuve", "note"]

    def get_queryset(self):
        qs = Avis.objects.select_related("user", "produit")
        if not self.request.user.is_authenticated:
            return qs.filter(approuve=True)
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user) | qs.filter(approuve=True)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="approuver",
            permission_classes=[permissions.IsAdminUser])
    def approuver(self, request, pk=None):
        """Approuve un avis (admin uniquement)."""
        avis = self.get_object()
        avis.approuve = True
        avis.save(update_fields=["approuve"])
        return Response({"detail": "Avis approuvé."})


class FavorisViewSet(viewsets.ModelViewSet):
    """Liste de souhaits du client connecté."""

    serializer_class = FavorisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favoris.objects.filter(user=self.request.user).select_related(
            "produit"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="toggle")
    def toggle(self, request):
        """Ajoute ou retire un produit des favoris."""
        produit_id = request.data.get("produit_id")
        from vendor.models.produit import Produit
        try:
            produit = Produit.objects.get(pk=produit_id)
        except Produit.DoesNotExist:
            return Response(
                {"detail": "Produit introuvable."}, status=status.HTTP_404_NOT_FOUND
            )
        favori, created = Favoris.objects.get_or_create(
            user=request.user, produit=produit
        )
        if not created:
            favori.delete()
            return Response({"detail": "Retiré des favoris.", "favori": False})
        return Response({"detail": "Ajouté aux favoris.", "favori": True})


class MoyenPaiementViewSet(viewsets.ModelViewSet):
    """Gestion des moyens de paiement du client."""

    serializer_class = MoyenPaiementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MoyenPaiement.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="definir-par-defaut")
    def definir_par_defaut(self, request, pk=None):
        moyen = self.get_object()
        moyen.par_defaut = True
        moyen.save()
        return Response({"detail": "Moyen de paiement défini par défaut."})


class PaiementViewSet(viewsets.ModelViewSet):
    """
    Gestion des paiements.
    - Lecture : client voit ses paiements, admin voit tout
    - Création : client uniquement
    - Modification statut : admin uniquement
    """

    serializer_class = PaiementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["statut", "devise"]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        qs = Paiement.objects.select_related("commande", "moyen_paiement")
        if self.request.user.is_staff:
            return qs
        return qs.filter(commande__user=self.request.user)
