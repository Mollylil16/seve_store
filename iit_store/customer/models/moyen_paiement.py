from django.db import models
from django.contrib.auth.models import User


class MoyenPaiement(models.Model):
    """
    Moyen de paiement enregistré par un client.
    Les données sensibles (numéro de carte) ne sont JAMAIS stockées ici,
    uniquement un token/référence fourni par le prestataire de paiement.
    """

    TYPE_CHOICES = [
        ("CARTE", "Carte bancaire"),
        ("MOBILE_MONEY", "Mobile Money"),
        ("PAYPAL", "PayPal"),
        ("VIREMENT", "Virement bancaire"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="moyens_paiement",
        verbose_name="Client",
    )
    type_paiement = models.CharField(
        "Type", max_length=20, choices=TYPE_CHOICES
    )
    libelle = models.CharField(
        "Libellé (ex: Visa se terminant par 4242)",
        max_length=150,
    )
    token_reference = models.CharField(
        "Token / Référence prestataire",
        max_length=255,
        blank=True,
        null=True,
    )
    par_defaut = models.BooleanField("Par défaut", default=False)
    expire_le = models.DateField("Expire le", blank=True, null=True)
    cree_le = models.DateTimeField("Créé le", auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.par_defaut:
            MoyenPaiement.objects.filter(
                user=self.user, par_defaut=True
            ).exclude(pk=self.pk).update(par_defaut=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_type_paiement_display()} — {self.libelle}"

    class Meta:
        verbose_name = "Moyen de paiement"
        verbose_name_plural = "Moyens de paiement"
        ordering = ["-par_defaut", "-cree_le"]
