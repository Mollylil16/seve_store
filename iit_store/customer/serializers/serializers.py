from rest_framework import serializers
from customer.models.adresse import Adresse
from customer.models.avis import Avis
from customer.models.favoris import Favoris
from customer.models.moyen_paiement import MoyenPaiement
from customer.models.paiement import Paiement


class AdresseSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(
        source="get_type_adresse_display", read_only=True
    )
    city_nom = serializers.CharField(source="city.name", read_only=True)
    region_nom = serializers.CharField(source="region_cl.name", read_only=True)
    pays_nom = serializers.CharField(source="country.name", read_only=True)

    class Meta:
        model = Adresse
        fields = [
            "id", "user",
            "type_adresse", "type_display",
            "prenom", "nom", "telephone",
            "adresse_ligne1", "adresse_ligne2",
            "ville", "region", "code_postal", "pays",
            "city", "city_nom",
            "region_cl", "region_nom",
            "country", "pays_nom",
            "par_defaut", "cree_le",
        ]
        read_only_fields = ["user", "cree_le"]


class AvisSerializer(serializers.ModelSerializer):
    user_nom = serializers.CharField(source="user.username", read_only=True)
    produit_nom = serializers.CharField(source="produit.nom", read_only=True)

    class Meta:
        model = Avis
        fields = [
            "id", "produit", "produit_nom",
            "user", "user_nom",
            "note", "titre", "commentaire",
            "approuve",
            "cree_le", "mis_a_jour_le",
        ]
        read_only_fields = ["user", "approuve", "cree_le", "mis_a_jour_le"]


class FavorisSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(source="produit.nom", read_only=True)
    produit_slug = serializers.CharField(source="produit.slug", read_only=True)
    produit_prix = serializers.DecimalField(
        source="produit.prix_effectif",
        max_digits=12, decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Favoris
        fields = [
            "id", "user", "produit",
            "produit_nom", "produit_slug", "produit_prix",
            "ajoute_le",
        ]
        read_only_fields = ["user", "ajoute_le"]


class MoyenPaiementSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(
        source="get_type_paiement_display", read_only=True
    )

    class Meta:
        model = MoyenPaiement
        fields = [
            "id", "user",
            "type_paiement", "type_display",
            "libelle", "par_defaut", "expire_le", "cree_le",
        ]
        read_only_fields = ["user", "cree_le"]
        # token_reference EXCLUT volontairement


class PaiementSerializer(serializers.ModelSerializer):
    statut_display = serializers.CharField(
        source="get_statut_display", read_only=True
    )
    commande_numero = serializers.CharField(
        source="commande.numero", read_only=True
    )

    class Meta:
        model = Paiement
        fields = [
            "id", "commande", "commande_numero",
            "moyen_paiement",
            "reference", "montant", "devise",
            "statut", "statut_display",
            "cree_le", "valide_le",
        ]
        read_only_fields = [
            "reference", "statut", "cree_le", "valide_le",
            "reponse_prestataire",
        ]
