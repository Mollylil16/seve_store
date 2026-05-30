from django.contrib import admin
from customer.models.adresse import Adresse
from customer.models.avis import Avis
from customer.models.favoris import Favoris
from customer.models.moyen_paiement import MoyenPaiement
from customer.models.paiement import Paiement


@admin.register(Adresse)
class AdresseAdmin(admin.ModelAdmin):
    list_display = [
        "user", "prenom", "nom", "type_adresse",
        "ville", "pays", "par_defaut", "cree_le",
    ]
    list_filter = ["type_adresse", "pays", "par_defaut"]
    search_fields = ["user__username", "prenom", "nom", "ville", "adresse_ligne1"]
    readonly_fields = ["cree_le"]
    raw_id_fields = ["user"]


@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = [
        "produit", "user", "note", "titre",
        "approuve", "cree_le",
    ]
    list_filter = ["approuve", "note"]
    search_fields = ["produit__nom", "user__username", "commentaire"]
    list_editable = ["approuve"]
    readonly_fields = ["cree_le", "mis_a_jour_le"]
    actions = ["approuver_avis"]

    @admin.action(description="Approuver les avis sélectionnés")
    def approuver_avis(self, request, queryset):
        count = queryset.update(approuve=True)
        self.message_user(request, f"{count} avis approuvé(s).")


@admin.register(Favoris)
class FavorisAdmin(admin.ModelAdmin):
    list_display = ["user", "produit", "ajoute_le"]
    search_fields = ["user__username", "produit__nom"]
    readonly_fields = ["ajoute_le"]
    raw_id_fields = ["user", "produit"]


@admin.register(MoyenPaiement)
class MoyenPaiementAdmin(admin.ModelAdmin):
    list_display = [
        "user", "type_paiement", "libelle",
        "par_defaut", "expire_le", "cree_le",
    ]
    list_filter = ["type_paiement", "par_defaut"]
    search_fields = ["user__username", "libelle"]
    readonly_fields = ["cree_le", "token_reference"]  # sécurité


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = [
        "reference", "commande", "montant", "devise",
        "statut", "cree_le", "valide_le",
    ]
    list_filter = ["statut", "devise"]
    search_fields = ["reference", "commande__numero"]
    readonly_fields = [
        "reference", "reponse_prestataire", "cree_le", "valide_le"
    ]
    ordering = ["-cree_le"]
