from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profil(models.Model):
    """
    Extension du modèle User Django.
    Créé automatiquement à la création d'un User.
    """

    GENRE_CHOICES = [
        ("M", "Masculin"),
        ("F", "Féminin"),
        ("A", "Autre"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profil",
        verbose_name="Utilisateur",
    )
    telephone = models.CharField(
        "Téléphone", max_length=20, blank=True, null=True
    )
    photo = models.ImageField(
        "Photo de profil",
        upload_to="profils/",
        blank=True,
        null=True,
    )
    date_naissance = models.DateField(
        "Date de naissance", blank=True, null=True
    )
    genre = models.CharField(
        "Genre",
        max_length=1,
        choices=GENRE_CHOICES,
        blank=True,
        null=True,
    )
    bio = models.TextField("Bio", blank=True, null=True)
    cree_le = models.DateTimeField("Créé le", auto_now_add=True)
    mis_a_jour_le = models.DateTimeField("Mis à jour le", auto_now=True)

    def __str__(self):
        return f"Profil de {self.user.get_full_name() or self.user.username}"

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"
        ordering = ["-cree_le"]


# ── Signal : créer/sauvegarder le profil automatiquement ──────────────────
@receiver(post_save, sender=User)
def creer_ou_sauvegarder_profil(sender, instance, created, **kwargs):
    if created:
        Profil.objects.create(user=instance)
    else:
        instance.profil.save()
