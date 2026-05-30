from rest_framework import serializers
from store.models.panier import Panier, PanierItem
from store.models.commandes import Commande, CommandeItem
from store.models.livraisons import Livraison
from store.models.mode_reglement import ModeReglement
from vendor.models.produit import Produit


class ModeReglementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModeReglement
        fields = ["id", "nom", "libelle", "description", "actif", "ordre", "icone"]


class PanierItemSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(source="produit.nom", read_only=True)
    produit_slug = serializers.CharField(source="produit.slug", read_only=True)
    prix_unitaire = serializers.DecimalField(
        source="produit.prix_effectif", max_digits=12, decimal_places=2, read_only=True
    )
    sous_total = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True
    )

    class Meta:
        model = PanierItem
        fields = [
            "id", "produit", "produit_nom", "produit_slug",
            "quantite", "prix_unitaire", "sous_total", "ajoute_le",
        ]
        read_only_fields = ["ajoute_le"]


class PanierSerializer(serializers.ModelSerializer):
    items = PanierItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True
    )
    nombre_articles = serializers.IntegerField(read_only=True)

    class Meta:
        model = Panier
        fields = [
            "id", "user", "session_key", "items",
            "total", "nombre_articles",
            "cree_le", "mis_a_jour_le",
        ]
        read_only_fields = ["user", "cree_le", "mis_a_jour_le"]


class CommandeItemSerializer(serializers.ModelSerializer):
    sous_total = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True
    )

    class Meta:
        model = CommandeItem
        fields = [
            "id", "produit", "nom_produit",
            "quantite", "prix_unitaire", "sous_total",
        ]
        read_only_fields = ["nom_produit", "prix_unitaire"]


class CommandeSerializer(serializers.ModelSerializer):
    items = CommandeItemSerializer(many=True, read_only=True)
    statut_display = serializers.CharField(
        source="get_statut_display", read_only=True
    )
    mode_reglement_nom = serializers.CharField(
        source="mode_reglement.libelle", read_only=True
    )

    class Meta:
        model = Commande
        fields = [
            "id", "numero", "user",
            "statut", "statut_display",
            "mode_reglement", "mode_reglement_nom",
            "adresse_livraison_texte",
            "sous_total", "frais_livraison", "total",
            "note_client",
            "items",
            "cree_le", "mis_a_jour_le",
        ]
        read_only_fields = [
            "numero", "user", "sous_total", "total",
            "cree_le", "mis_a_jour_le",
        ]


class LivraisonSerializer(serializers.ModelSerializer):
    statut_display = serializers.CharField(
        source="get_statut_display", read_only=True
    )

    class Meta:
        model = Livraison
        fields = [
            "id", "commande",
            "transporteur", "numero_suivi", "url_suivi",
            "statut", "statut_display",
            "date_estimee", "date_livraison",
            "note",
            "cree_le", "mis_a_jour_le",
        ]
        read_only_fields = ["cree_le", "mis_a_jour_le"]
