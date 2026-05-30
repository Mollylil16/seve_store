from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from base.helpers import generate_unique_slug, format_price
from base.models.profil import Profil
from vendor.models.produit import Produit


class HelperFunctionsTestCase(TestCase):
    """
    Tests unitaires pour les fonctions d'aide globales.
    """

    def test_format_price(self):
        self.assertEqual(format_price(1500), "1 500 FCFA")
        self.assertEqual(format_price(1250.50), "1 250.50 FCFA")
        self.assertEqual(format_price(None), "0 FCFA")
        self.assertEqual(format_price("invalid"), "invalid FCFA")

    def test_generate_unique_slug(self):
        # Créer un vendeur pour pouvoir créer des produits
        vendeur = User.objects.create_user(username="vendeur_test", password="password123")
        Produit.objects.create(nom="Ordinateur", prix=50000, vendeur=vendeur)
        
        # Générer un slug pour un nouveau produit de même nom
        slug = generate_unique_slug(Produit, "Ordinateur")
        self.assertEqual(slug, "ordinateur-1")


class UserProfileUpdateAPITestCase(APITestCase):
    """
    Tests d'intégration de l'API REST pour la mise à jour utilisateur + profil.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="client_test",
            email="client@test.com",
            first_name="Jean",
            last_name="Dupont",
            password="password123"
        )
        self.profil, _ = Profil.objects.get_or_create(user=self.user)
        self.profil.telephone = "22501020304"
        self.profil.bio = "Ancienne bio"
        self.profil.save()
        self.user.refresh_from_db()
        self.client.force_authenticate(user=self.user)

    def test_get_current_user_me(self):
        response = self.client.get("/api/users/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "client_test")
        self.assertEqual(response.data["profil"]["telephone"], "22501020304")

    def test_patch_current_user_me_with_nested_profil(self):
        payload = {
            "first_name": "Jean-Pierre",
            "profil": {
                "telephone": "22509090909",
                "bio": "Nouvelle bio mise à jour !"
            }
        }
        response = self.client.patch("/api/users/me/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifications de la réponse
        self.assertEqual(response.data["first_name"], "Jean-Pierre")
        self.assertEqual(response.data["profil"]["telephone"], "22509090909")
        self.assertEqual(response.data["profil"]["bio"], "Nouvelle bio mise à jour !")
        
        # Vérification en base de données
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Jean-Pierre")
        self.assertEqual(self.user.profil.telephone, "22509090909")
        self.assertEqual(self.user.profil.bio, "Nouvelle bio mise à jour !")
