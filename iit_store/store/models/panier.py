from django.db import models
from django.contrib.auth.models import User
from vendor.models.produit import Produit


class Panier(models.Model):
    """
    Panier d'achat — supporte les utilisateurs connectés et les guests (session).
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="panier",
        verbose_name="Utilisateur",
    )
    session_key = models.CharField(
        "Clé de session (guest)",
        max_length=40,
        null=True,
        blank=True,
        db_index=True,
    )
    cree_le = models.DateTimeField("Créé le", auto_now_add=True)
    mis_a_jour_le = models.DateTimeField("Mis à jour le", auto_now=True)

    @property
    def total(self):
        return sum(item.sous_total for item in self.items.all())

    @property
    def nombre_articles(self):
        return sum(item.quantite for item in self.items.all())

    def __str__(self):
        owner = self.user.username if self.user else f"Guest ({self.session_key})"
        return f"Panier de {owner}"

    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"
        ordering = ["-mis_a_jour_le"]


class PanierItem(models.Model):
    """
    Article dans un panier.
    """

    panier = models.ForeignKey(
        Panier,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Panier",
    )
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name="panier_items",
        verbose_name="Produit",
    )
    quantite = models.PositiveIntegerField("Quantité", default=1)
    prix_unitaire = models.DecimalField(
        "Prix unitaire (au moment de l'ajout)",
        max_digits=12,
        decimal_places=2,
    )
    ajoute_le = models.DateTimeField("Ajouté le", auto_now_add=True)

    @property
    def sous_total(self):
        return self.quantite * self.produit.prix_effectif

    def save(self, *args, **kwargs):
        # Toujours actualiser avec le prix effectif actuel du produit
        self.prix_unitaire = self.produit.prix_effectif
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantite}x {self.produit.nom}"

    class Meta:
        verbose_name = "Article du panier"
        verbose_name_plural = "Articles du panier"
        unique_together = ("panier", "produit")
