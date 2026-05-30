from django.db import models
from django.contrib.auth.models import User


class Adresse(models.Model):
    """
    Adresses de livraison et facturation d'un client.
    """

    TYPE_CHOICES = [
        ("DOMICILE", "Domicile"),
        ("BUREAU", "Bureau"),
        ("AUTRE", "Autre"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="adresses",
        verbose_name="Client",
    )
    type_adresse = models.CharField(
        "Type d'adresse",
        max_length=10,
        choices=TYPE_CHOICES,
        default="DOMICILE",
    )
    prenom = models.CharField("Prénom", max_length=100)
    nom = models.CharField("Nom", max_length=100)
    telephone = models.CharField("Téléphone", max_length=20)
    adresse_ligne1 = models.CharField("Adresse ligne 1", max_length=255)
    adresse_ligne2 = models.CharField(
        "Adresse ligne 2", max_length=255, blank=True, null=True
    )
    ville = models.CharField("Ville", max_length=100)
    region = models.CharField("Région / État", max_length=100, blank=True, null=True)
    code_postal = models.CharField("Code postal", max_length=20, blank=True, null=True)
    pays = models.CharField("Pays", max_length=100, default="Côte d'Ivoire")
    
    # Intégration optionnelle de django-cities-light
    city = models.ForeignKey(
        "cities_light.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="adresses",
        verbose_name="Ville (Cities Light)",
    )
    region_cl = models.ForeignKey(
        "cities_light.Region",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="adresses",
        verbose_name="Région (Cities Light)",
    )
    country = models.ForeignKey(
        "cities_light.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="adresses",
        verbose_name="Pays (Cities Light)",
    )

    par_defaut = models.BooleanField("Adresse par défaut", default=False)
    cree_le = models.DateTimeField("Créé le", auto_now_add=True)

    def save(self, *args, **kwargs):
        # Une seule adresse par défaut par user
        if self.par_defaut:
            Adresse.objects.filter(user=self.user, par_defaut=True).exclude(
                pk=self.pk
            ).update(par_defaut=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prenom} {self.nom} — {self.ville}, {self.pays}"

    class Meta:
        verbose_name = "Adresse"
        verbose_name_plural = "Adresses"
        ordering = ["-par_defaut", "-cree_le"]
