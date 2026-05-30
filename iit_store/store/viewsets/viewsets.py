from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from store.models.panier import Panier, PanierItem
from store.models.commandes import Commande, CommandeItem
from store.models.livraisons import Livraison
from store.models.mode_reglement import ModeReglement
from store.serializers.serializers import (
    PanierSerializer,
    PanierItemSerializer,
    CommandeSerializer,
    CommandeItemSerializer,
    LivraisonSerializer,
    ModeReglementSerializer,
)
from vendor.models.produit import Produit


class ModeReglementViewSet(viewsets.ReadOnlyModelViewSet):
    """Liste des modes de règlement actifs (lecture seule publique)."""

    serializer_class = ModeReglementSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ModeReglement.objects.filter(actif=True).order_by("ordre")


class PanierViewSet(viewsets.GenericViewSet):
    """
    Gestion du panier utilisateur.
    - GET  /api/panier/mon-panier/ → panier courant
    - POST /api/panier/ajouter/    → ajouter un produit
    - POST /api/panier/vider/      → vider le panier
    """

    serializer_class = PanierSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Panier.objects.filter(user=self.request.user).prefetch_related(
            "items__produit"
        )

    @action(detail=False, methods=["get"], url_path="mon-panier")
    def mon_panier(self, request):
        """Retourne ou crée le panier de l'utilisateur courant en synchronisant les prix."""
        panier, _ = Panier.objects.get_or_create(user=request.user)
        # Synchronisation dynamique des prix en base de données
        for item in panier.items.all():
            if item.prix_unitaire != item.produit.prix_effectif:
                item.prix_unitaire = item.produit.prix_effectif
                item.save(update_fields=["prix_unitaire"])
        serializer = PanierSerializer(panier, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="ajouter")
    def ajouter(self, request):
        """Ajoute un produit au panier ou augmente sa quantité."""
        produit_id = request.data.get("produit_id")
        quantite = int(request.data.get("quantite", 1))

        try:
            produit = Produit.objects.get(pk=produit_id, actif=True)
        except Produit.DoesNotExist:
            return Response(
                {"detail": "Produit introuvable."}, status=status.HTTP_404_NOT_FOUND
            )

        if produit.stock < quantite:
            return Response(
                {"detail": f"Stock insuffisant. Disponible : {produit.stock}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        panier, _ = Panier.objects.get_or_create(user=request.user)
        item, created = PanierItem.objects.get_or_create(
            panier=panier,
            produit=produit,
            defaults={"prix_unitaire": produit.prix_effectif, "quantite": quantite},
        )
        if not created:
            item.quantite += quantite
            item.save()

        serializer = PanierSerializer(panier, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="retirer")
    def retirer(self, request):
        """Retire un article du panier."""
        item_id = request.data.get("item_id")
        try:
            panier = Panier.objects.get(user=request.user)
            item = PanierItem.objects.get(pk=item_id, panier=panier)
            item.delete()
        except (Panier.DoesNotExist, PanierItem.DoesNotExist):
            return Response(
                {"detail": "Article introuvable."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = PanierSerializer(panier, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="vider")
    def vider(self, request):
        """Vide entièrement le panier."""
        try:
            panier = Panier.objects.get(user=request.user)
            panier.items.all().delete()
        except Panier.DoesNotExist:
            pass
        return Response({"detail": "Panier vidé."})


class CommandeViewSet(viewsets.ModelViewSet):
    """
    Gestion des commandes.
    """

    serializer_class = CommandeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["statut"]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        qs = Commande.objects.select_related(
            "user", "mode_reglement"
        ).prefetch_related("items__produit", "livraison")
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs.order_by("-cree_le")

    def perform_create(self, serializer):
        """Crée la commande depuis le panier de l'utilisateur avec contrôle et décrément de stock."""
        from django.db import transaction
        from rest_framework.exceptions import ValidationError

        with transaction.atomic():
            try:
                panier = Panier.objects.get(user=self.request.user)
                items = list(panier.items.select_related("produit").all())
                if not items:
                    raise ValidationError("Votre panier est vide.")

                # Vérification préalable du stock pour TOUS les produits
                for item in items:
                    if item.produit.stock < item.quantite:
                        raise ValidationError(
                            f"Stock insuffisant pour '{item.produit.nom}'. Restant: {item.produit.stock} (demandé: {item.quantite})"
                        )

                # Création de la commande
                commande = serializer.save(user=self.request.user)

                # Transfert et décrémentation du stock
                for item in items:
                    produit = item.produit
                    produit.stock -= item.quantite
                    produit.save(update_fields=["stock"])

                    CommandeItem.objects.create(
                        commande=commande,
                        produit=produit,
                        nom_produit=produit.nom,
                        quantite=item.quantite,
                        prix_unitaire=item.prix_unitaire,
                    )

                commande.calculer_total()
                # Vider le panier après commande
                panier.items.all().delete()
            except Panier.DoesNotExist:
                raise ValidationError("Aucun panier trouvé pour cet utilisateur.")

    @action(detail=True, methods=["patch"], url_path="statut",
            permission_classes=[permissions.IsAdminUser])
    def changer_statut(self, request, pk=None):
        """Change le statut d'une commande (admin uniquement)."""
        commande = self.get_object()
        nouveau_statut = request.data.get("statut")
        statuts_valides = [s[0] for s in Commande.STATUT_CHOICES]
        if nouveau_statut not in statuts_valides:
            return Response(
                {"detail": f"Statut invalide. Valeurs acceptées : {statuts_valides}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        commande.statut = nouveau_statut
        commande.save(update_fields=["statut"])
        serializer = CommandeSerializer(commande, context={"request": request})
        return Response(serializer.data)


class LivraisonViewSet(viewsets.ModelViewSet):
    """Gestion des livraisons."""

    serializer_class = LivraisonSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["statut"]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Livraison.objects.select_related("commande").all()
        return Livraison.objects.filter(
            commande__user=self.request.user
        ).select_related("commande")
