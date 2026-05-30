from django.db import models


class ModeReglement(models.Model):
    """
    Modes de règlement acceptés sur la plateforme.
    Ex : Carte bancaire, Mobile Money, Virement, Cash à la livraison.
    """

    NOM_CHOICES = [
        ("CARTE", "Carte bancaire"),
        ("MOBILE_MONEY", "Mobile Money"),
        ("VIREMENT", "Virement bancaire"),
        ("CASH", "Cash à la livraison"),
        ("CRYPTO", "Crypto-monnaie"),
    ]

    nom = models.CharField(
        "Nom", max_length=50, choices=NOM_CHOICES, unique=True
    )
    libelle = models.CharField("Libellé affiché", max_length=100)
    description = models.TextField("Description", blank=True, null=True)
    actif = models.BooleanField("Actif", default=True)
    ordre = models.PositiveIntegerField("Ordre", default=0)
    icone = models.CharField(
        "Nom de l'icône", max_length=50, blank=True, null=True
    )

    def __str__(self):
        return self.libelle

    class Meta:
        verbose_name = "Mode de règlement"
        verbose_name_plural = "Modes de règlement"
        ordering = ["ordre"]
