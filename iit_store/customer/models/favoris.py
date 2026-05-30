from django.db import models
from django.contrib.auth.models import User
from vendor.models.produit import Produit


class Favoris(models.Model):
    """
    Liste de souhaits / favoris d'un client.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favoris",
        verbose_name="Client",
    )
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name="mis_en_favoris",
        verbose_name="Produit",
    )
    ajoute_le = models.DateTimeField("Ajouté le", auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ♥ {self.produit.nom}"

    class Meta:
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        unique_together = ("user", "produit")   # pas de doublon
        ordering = ["-ajoute_le"]
