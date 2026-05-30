from django.contrib import admin
from vendor.models.categorie import Categorie
from vendor.models.produit import Produit, ImageProduit


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ["nom", "parent", "ordre", "active", "cree_le"]
    list_filter = ["active", "parent"]
    search_fields = ["nom", "description"]
    prepopulated_fields = {"slug": ("nom",)}
    list_editable = ["ordre", "active"]
    ordering = ["ordre", "nom"]


class ImageProduitInline(admin.TabularInline):
    model = ImageProduit
    extra = 1
    fields = ["image", "alt_text", "ordre"]


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = [
        "nom", "categorie", "vendeur", "prix", "prix_promo",
        "stock", "actif", "featured", "cree_le",
    ]
    list_filter = ["actif", "featured", "categorie", "vendeur"]
    search_fields = ["nom", "description", "slug"]
    prepopulated_fields = {"slug": ("nom",)}
    list_editable = ["prix", "stock", "actif", "featured"]
    readonly_fields = ["cree_le", "mis_a_jour_le"]
    raw_id_fields = ["vendeur", "categorie"]
    inlines = [ImageProduitInline]
    ordering = ["-cree_le"]
