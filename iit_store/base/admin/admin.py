from django.contrib import admin
from base.models.profil import Profil


@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ["user", "telephone", "genre", "cree_le"]
    list_filter = ["genre"]
    search_fields = ["user__username", "user__email", "telephone"]
    readonly_fields = ["cree_le", "mis_a_jour_le"]
    raw_id_fields = ["user"]
