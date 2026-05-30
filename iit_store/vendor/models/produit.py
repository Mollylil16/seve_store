from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from base.helpers import generate_unique_slug
from .categorie import Categorie


class Produit(models.Model):
    """
    Produit mis en vente sur la plateforme.
    """

    vendeur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="produits",
        verbose_name="Vendeur",
    )
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="produits",
        verbose_name="Catégorie",
    )
    nom = models.CharField("Nom du produit", max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField("Description", blank=True, null=True)
    description_courte = models.CharField(
        "Description courte", max_length=500, blank=True, null=True
    )
    prix = models.DecimalField(
        "Prix (FCFA)",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    prix_promo = models.DecimalField(
        "Prix promotionnel",
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    stock = models.PositiveIntegerField("Stock disponible", default=0)
    actif = models.BooleanField("Actif / En vente", default=True)
    featured = models.BooleanField("Mis en avant", default=False)
    cree_le = models.DateTimeField("Créé le", auto_now_add=True)
    mis_a_jour_le = models.DateTimeField("Mis à jour le", auto_now=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.prix_promo is not None and self.prix is not None:
            if self.prix_promo >= self.prix:
                raise ValidationError(
                    {"prix_promo": "Le prix promotionnel doit être strictement inférieur au prix normal."}
                )
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.slug:
            self.slug = generate_unique_slug(Produit, self.nom)
        super().save(*args, **kwargs)

    @property
    def prix_effectif(self):
        """Retourne le prix promo s'il existe, sinon le prix normal."""
        return self.prix_promo if self.prix_promo else self.prix

    @property
    def en_stock(self):
        return self.stock > 0

    @property
    def image_principale(self):
        img = self.images.filter(ordre=0).first() or self.images.first()
        return img

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ["-cree_le"]


class ImageProduit(models.Model):
    """
    Images associées à un produit (galerie).
    """

    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Produit",
    )
    image = models.ImageField("Image", upload_to="produits/")
    alt_text = models.CharField(
        "Texte alternatif", max_length=255, blank=True, null=True
    )
    ordre = models.PositiveIntegerField("Ordre", default=0)

    def __str__(self):
        return f"Image #{self.ordre} — {self.produit.nom}"

    class Meta:
        verbose_name = "Image Produit"
        verbose_name_plural = "Images Produits"
        ordering = ["ordre"]
