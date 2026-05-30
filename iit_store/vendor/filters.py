import django_filters
from vendor.models.produit import Produit

class ProduitFilter(django_filters.FilterSet):
    prix_min = django_filters.NumberFilter(field_name="prix", lookup_expr="gte", label="Prix minimum")
    prix_max = django_filters.NumberFilter(field_name="prix", lookup_expr="lte", label="Prix maximum")
    en_stock = django_filters.BooleanFilter(method="filter_en_stock", label="En stock uniquement")

    class Meta:
        model = Produit
        fields = ["categorie", "actif", "featured", "vendeur", "prix_min", "prix_max", "en_stock"]

    def filter_en_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset
