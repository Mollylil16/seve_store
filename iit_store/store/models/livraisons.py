from django.db import models
from store.models.commandes import Commande


class Livraison(models.Model):
    """
    Informations de livraison liées à une commande.
    """

    STATUT_CHOICES = [
        ("EN_ATTENTE", "En attente d'expédition"),
        ("EN_TRANSIT", "En transit"),
        ("EN_COURS", "En cours de livraison"),
        ("LIVREE", "Livrée"),
        ("ECHOUEE", "Échec de livraison"),
        ("RETOURNEE", "Retournée"),
    ]

    commande = models.OneToOneField(
        Commande,
        on_delete=models.CASCADE,
        related_name="livraison",
        verbose_name="Commande",
    )
    transporteur = models.CharField(
        "Transporteur", max_length=100, blank=True, null=True
    )
    numero_suivi = models.CharField(
        "Numéro de suivi", max_length=100, blank=True, null=True, db_index=True
    )
    url_suivi = models.URLField(
        "URL de suivi", blank=True, null=True
    )
    statut = models.CharField(
        "Statut",
        max_length=20,
        choices=STATUT_CHOICES,
        default="EN_ATTENTE",
        db_index=True,
    )
    date_estimee = models.DateField(
        "Date de livraison estimée", blank=True, null=True
    )
    date_livraison = models.DateTimeField(
        "Date de livraison réelle", blank=True, null=True
    )
    note = models.TextField("Note transporteur", blank=True, null=True)
    cree_le = models.DateTimeField("Créé le", auto_now_add=True)
    mis_a_jour_le = models.DateTimeField("Mis à jour le", auto_now=True)

    def __str__(self):
        return f"Livraison #{self.commande.numero} — {self.get_statut_display()}"

    class Meta:
        verbose_name = "Livraison"
        verbose_name_plural = "Livraisons"
        ordering = ["-cree_le"]
