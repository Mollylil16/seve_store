from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from vendor.models.produit import Produit
from store.models.mode_reglement import ModeReglement
import uuid


class Commande(models.Model):
    """
    Commande passée par un client.
    """

    STATUT_CHOICES = [
        ("EN_ATTENTE", "En attente"),
        ("CONFIRMEE", "Confirmée"),
        ("EN_PREPARATION", "En préparation"),
        ("EXPEDIEE", "Expédiée"),
        ("LIVREE", "Livrée"),
        ("ANNULEE", "Annulée"),
        ("REMBOURSEE", "Remboursée"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="commandes",
        verbose_name="Client",
    )
    numero = models.CharField(
        "Numéro de commande",
        max_length=36,
        unique=True,
        editable=False,
        default=uuid.uuid4,
    )
    statut = models.CharField(
        "Statut",
        max_length=20,
        choices=STATUT_CHOICES,
        default="EN_ATTENTE",
        db_index=True,
    )
    mode_reglement = models.ForeignKey(
        ModeReglement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commandes",
        verbose_name="Mode de règlement",
    )
    # Snapshot adresse au moment de la commande
    adresse_livraison_texte = models.TextField(
        "Adresse de livraison (snapshot)", blank=True, null=True
    )
    sous_total = models.DecimalField(
        "Sous-total",
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    frais_livraison = models.DecimalField(
        "Frais de livraison",
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    total = models.DecimalField(
        "Total",
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    note_client = models.TextField("Note du client", blank=True, null=True)
    cree_le = models.DateTimeField("Créé le", auto_now_add=True)
    mis_a_jour_le = models.DateTimeField("Mis à jour le", auto_now=True)

    def calculer_total(self):
        self.sous_total = sum(
            item.sous_total for item in self.items.all()
        )
        self.total = self.sous_total + self.frais_livraison
        self.save(update_fields=["sous_total", "total"])

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_instance = Commande.objects.get(pk=self.pk)
                if old_instance.statut != "ANNULEE" and self.statut == "ANNULEE":
                    for item in self.items.all():
                        produit = item.produit
                        produit.stock += item.quantite
                        produit.save(update_fields=["stock"])
            except Commande.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Commande #{self.numero} — {self.user.username}"

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ["-cree_le"]


class CommandeItem(models.Model):
    """
    Ligne d'article dans une commande (snapshot des prix).
    """

    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Commande",
    )
    produit = models.ForeignKey(
        Produit,
        on_delete=models.PROTECT,
        related_name="commande_items",
        verbose_name="Produit",
    )
    nom_produit = models.CharField(
        "Nom du produit (snapshot)", max_length=255
    )
    quantite = models.PositiveIntegerField("Quantité", default=1)
    prix_unitaire = models.DecimalField(
        "Prix unitaire (snapshot)", max_digits=12, decimal_places=2
    )

    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire

    def save(self, *args, **kwargs):
        if not self.nom_produit:
            self.nom_produit = self.produit.nom
        if not self.prix_unitaire:
            self.prix_unitaire = self.produit.prix_effectif
        super().save(*args, **kwargs)
        self.commande.calculer_total()

    def delete(self, *args, **kwargs):
        commande = self.commande
        super().delete(*args, **kwargs)
        commande.calculer_total()

    def __str__(self):
        return f"{self.quantite}x {self.nom_produit}"

    class Meta:
        verbose_name = "Article de commande"
        verbose_name_plural = "Articles de commande"
