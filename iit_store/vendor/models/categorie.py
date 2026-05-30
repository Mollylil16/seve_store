from django.db import models
from django.utils.text import slugify


class Categorie(models.Model):
    """
    Catégorie de produits — supporte les sous-catégories via self-reference.
    """

    nom = models.CharField("Nom", max_length=100)
    description = models.TextField("Description", blank=True, null=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    image = models.ImageField(
        "Image",
        upload_to="categories/",
        blank=True,
        null=True,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sous_categories",
        verbose_name="Catégorie parente",
    )
    ordre = models.PositiveIntegerField("Ordre d'affichage", default=0)
    active = models.BooleanField("Active", default=True)
    cree_le = models.DateTimeField("Créé le", auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.parent:
            return f"{self.parent.nom} > {self.nom}"
        return self.nom

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ["ordre", "nom"]
