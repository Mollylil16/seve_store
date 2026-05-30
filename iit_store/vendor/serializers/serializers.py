from rest_framework import serializers
from vendor.models.categorie import Categorie
from vendor.models.produit import Produit, ImageProduit


class CategorieSerializer(serializers.ModelSerializer):
    sous_categories = serializers.SerializerMethodField()

    class Meta:
        model = Categorie
        fields = [
            "id", "nom", "slug", "description", "image",
            "parent", "ordre", "active", "sous_categories", "cree_le",
        ]
        read_only_fields = ["slug", "cree_le"]

    def get_sous_categories(self, obj):
        if obj.sous_categories.exists():
            return CategorieSerializer(
                obj.sous_categories.filter(active=True), many=True, context=self.context
            ).data
        return []


class ImageProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageProduit
        fields = ["id", "image", "alt_text", "ordre"]


class ProduitSerializer(serializers.ModelSerializer):
    images = ImageProduitSerializer(many=True, read_only=True)
    categorie_nom = serializers.CharField(source="categorie.nom", read_only=True)
    vendeur_nom = serializers.CharField(source="vendeur.username", read_only=True)
    prix_effectif = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    en_stock = serializers.BooleanField(read_only=True)
    note_moyenne = serializers.SerializerMethodField()

    class Meta:
        model = Produit
        fields = [
            "id", "nom", "slug", "description", "description_courte",
            "prix", "prix_promo", "prix_effectif",
            "stock", "en_stock",
            "categorie", "categorie_nom",
            "vendeur", "vendeur_nom",
            "actif", "featured",
            "images",
            "note_moyenne",
            "cree_le", "mis_a_jour_le",
        ]
        read_only_fields = ["slug", "vendeur", "cree_le", "mis_a_jour_le"]

    def validate(self, attrs):
        prix = attrs.get("prix")
        prix_promo = attrs.get("prix_promo")
        
        # S'il s'agit d'un update partiel (PATCH), on récupère les valeurs actuelles si manquantes
        if self.instance:
            if prix is None:
                prix = self.instance.prix
            if "prix_promo" not in attrs and prix_promo is None:
                prix_promo = self.instance.prix_promo

        if prix_promo is not None and prix is not None:
            if prix_promo >= prix:
                raise serializers.ValidationError(
                    {"prix_promo": "Le prix promotionnel doit être strictement inférieur au prix normal."}
                )
        return attrs

    def get_note_moyenne(self, obj):
        avis = obj.avis.filter(approuve=True)
        if avis.exists():
            return round(sum(a.note for a in avis) / avis.count(), 2)
        return None


class ProduitListSerializer(serializers.ModelSerializer):
    """Version allégée pour les listes."""

    image_principale = serializers.SerializerMethodField()
    prix_effectif = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    en_stock = serializers.BooleanField(read_only=True)
    categorie_nom = serializers.CharField(source="categorie.nom", read_only=True)

    class Meta:
        model = Produit
        fields = [
            "id", "nom", "slug", "prix", "prix_promo", "prix_effectif",
            "en_stock", "stock", "actif", "featured",
            "image_principale", "categorie", "categorie_nom",
            "cree_le",
        ]

    def get_image_principale(self, obj):
        img = obj.image_principale
        if img:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(img.image.url)
            return img.image.url
        return None
