from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from vendor.models.produit import Produit
from vendor.models.categorie import Categorie


class ProduitModelTestCase(APITestCase):
    """
    Tests unitaires pour les validations et comportements du modèle Produit.
    """

    def setUp(self):
        self.vendeur = User.objects.create_user(username="vendeur_t", password="password123")
        self.categorie = Categorie.objects.create(nom="Electronique")

    def test_prix_promo_strictement_inferieur_valide(self):
        produit = Produit(
            vendeur=self.vendeur,
            categorie=self.categorie,
            nom="Smartphone Pro",
            prix=100000.00,
            prix_promo=80000.00,
            stock=10
        )
        # Ne doit pas lever d'erreur
        produit.full_clean()
        produit.save()
        self.assertEqual(produit.prix_effectif, 80000.00)

    def test_prix_promo_superieur_ou_egal_invalide(self):
        produit = Produit(
            vendeur=self.vendeur,
            categorie=self.categorie,
            nom="Smartphone Pro",
            prix=100000.00,
            prix_promo=120000.00,
            stock=10
        )
        with self.assertRaises(ValidationError):
            produit.full_clean()

    def test_automatic_slug_generation(self):
        produit = Produit.objects.create(
            vendeur=self.vendeur,
            categorie=self.categorie,
            nom="Nouvel ordi ultra portable",
            prix=450000.00,
            stock=5
        )
        self.assertEqual(produit.slug, "nouvel-ordi-ultra-portable")


class ProduitAPIFiltersTestCase(APITestCase):
    """
    Tests d'intégration de l'API REST pour les filtres prix_min, prix_max et en_stock.
    """

    def setUp(self):
        self.vendeur = User.objects.create_user(username="vendeur_api", password="password123")
        
        # Création de produits avec des prix et stocks différents
        self.p1 = Produit.objects.create(
            vendeur=self.vendeur, nom="Produit A (Cher, en stock)", prix=2000.00, stock=5
        )
        self.p2 = Produit.objects.create(
            vendeur=self.vendeur, nom="Produit B (Pas cher, en stock)", prix=500.00, stock=2
        )
        self.p3 = Produit.objects.create(
            vendeur=self.vendeur, nom="Produit C (Pas cher, hors stock)", prix=400.00, stock=0
        )

    def test_filter_prix_min(self):
        response = self.client.get("/api/produits/?prix_min=1000")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Seul le produit A à 2000.00 doit être retourné
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["nom"], self.p1.nom)

    def test_filter_prix_max(self):
        response = self.client.get("/api/produits/?prix_max=600")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Les produits B (500) et C (400) doivent être retournés
        self.assertEqual(response.data["count"], 2)

    def test_filter_en_stock(self):
        response = self.client.get("/api/produits/?en_stock=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Seuls les produits A et B (stock > 0) doivent être retournés
        self.assertEqual(response.data["count"], 2)
        names = [p["nom"] for p in response.data["results"]]
        self.assertIn(self.p1.nom, names)
        self.assertIn(self.p2.nom, names)
        self.assertNotIn(self.p3.nom, names)

    def test_api_serializer_validation(self):
        # Authentifier pour autoriser la création de produit
        self.client.force_authenticate(user=self.vendeur)
        
        payload = {
            "nom": "Produit Erreur Prix",
            "prix": "5000.00",
            "prix_promo": "6000.00",
            "stock": 10
        }
        response = self.client.post("/api/produits/", payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("prix_promo", response.data)
