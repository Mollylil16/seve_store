from django.db import models
from django.core.validators import MinValueValidator
from store.models.commandes import Commande
from customer.models.moyen_paiement import MoyenPaiement
import uuid


class Paiement(models.Model):
    """
    Enregistrement d'un paiement effectué pour une commande.
    """

    STATUT_CHOICES = [
        ("EN_ATTENTE", "En attente"),
        ("INITIE", "Initié"),
        ("VALIDE", "Validé"),
        ("ECHEC", "Échec"),
        ("ANNULE", "Annulé"),
        ("REMBOURSE", "Remboursé"),
    ]

    commande = models.ForeignKey(
        Commande,
        on_delete=models.PROTECT,
        related_name="paiements",
        verbose_name="Commande",
    )
    moyen_paiement = models.ForeignKey(
        MoyenPaiement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paiements",
        verbose_name="Moyen de paiement",
    )
    reference = models.CharField(
        "Référence de transaction",
        max_length=255,
        unique=True,
        default=uuid.uuid4,
    )
    montant = models.DecimalField(
        "Montant",
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    devise = models.CharField("Devise", max_length=10, default="XOF")
    statut = models.CharField(
        "Statut",
        max_length=20,
        choices=STATUT_CHOICES,
        default="EN_ATTENTE",
        db_index=True,
    )
    reponse_prestataire = models.JSONField(
        "Réponse prestataire (JSON)",
        blank=True,
        null=True,
    )
    cree_le = models.DateTimeField("Créé le", auto_now_add=True)
    valide_le = models.DateTimeField("Validé le", blank=True, null=True)

    def __str__(self):
        return f"Paiement {self.reference} — {self.get_statut_display()} ({self.montant} {self.devise})"

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ["-cree_le"]
