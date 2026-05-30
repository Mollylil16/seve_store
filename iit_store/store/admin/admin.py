from django.contrib import admin
from store.models.panier import Panier, PanierItem
from store.models.commandes import Commande, CommandeItem
from store.models.livraisons import Livraison
from store.models.mode_reglement import ModeReglement


@admin.register(ModeReglement)
class ModeReglementAdmin(admin.ModelAdmin):
    list_display = ["libelle", "nom", "actif", "ordre"]
    list_editable = ["actif", "ordre"]
    ordering = ["ordre"]


class PanierItemInline(admin.TabularInline):
    model = PanierItem
    extra = 0
    readonly_fields = ["prix_unitaire", "ajoute_le"]


@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ["user", "nombre_articles", "total", "mis_a_jour_le"]
    search_fields = ["user__username", "session_key"]
    readonly_fields = ["cree_le", "mis_a_jour_le"]
    inlines = [PanierItemInline]


class CommandeItemInline(admin.TabularInline):
    model = CommandeItem
    extra = 0
    readonly_fields = ["nom_produit", "prix_unitaire", "sous_total"]


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = [
        "numero", "user", "statut", "total",
        "mode_reglement", "cree_le",
    ]
    list_filter = ["statut", "mode_reglement"]
    search_fields = ["numero", "user__username", "user__email"]
    readonly_fields = ["numero", "sous_total", "total", "cree_le", "mis_a_jour_le"]
    list_editable = ["statut"]
    inlines = [CommandeItemInline]
    ordering = ["-cree_le"]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.calculer_total()


@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = [
        "commande", "transporteur", "numero_suivi",
        "statut", "date_estimee", "date_livraison",
    ]
    list_filter = ["statut", "transporteur"]
    search_fields = ["numero_suivi", "commande__numero"]
    readonly_fields = ["cree_le", "mis_a_jour_le"]
    list_editable = ["statut"]
