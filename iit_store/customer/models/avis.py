from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from vendor.models.produit import Produit


class Avis(models.Model):
    """
    Avis et note d'un client sur un produit.
    """

    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name="avis",
        verbose_name="Produit",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="avis",
        verbose_name="Client",
    )
    note = models.PositiveSmallIntegerField(
        "Note (1 à 5)",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    titre = models.CharField("Titre", max_length=150, blank=True, null=True)
    commentaire = models.TextField("Commentaire", blank=True, null=True)
    approuve = models.BooleanField("Approuvé", default=False)
    cree_le = models.DateTimeField("Créé le", auto_now_add=True)
    mis_a_jour_le = models.DateTimeField("Mis à jour le", auto_now=True)

    def __str__(self):
        return f"Avis {self.note}★ de {self.user.username} sur {self.produit.nom}"

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        unique_together = ("produit", "user")   # 1 seul avis par client/produit
        ordering = ["-cree_le"]
