from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from customer.models.adresse import Adresse
from cities_light.models import Country, Region, City


class AdresseTestCase(APITestCase):
    """
    Tests unitaires et d'intégration pour les adresses et l'intégration cities_light.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="client_adresse", password="password123")
        self.client.force_authenticate(user=self.user)
        
        # Création des entités géographiques minimales cities_light
        self.country = Country.objects.create(name="Côte d'Ivoire", code2="CI")
        self.region = Region.objects.create(name="Lagunes", country=self.country)
        self.city = City.objects.create(name="Abidjan", country=self.country, region=self.region)

    def test_single_default_address_constraint(self):
        # Création de deux adresses par défaut
        a1 = Adresse.objects.create(
            user=self.user,
            prenom="Jean",
            nom="Dupont",
            telephone="01020304",
            adresse_ligne1="Plateau",
            ville="Abidjan",
            par_defaut=True
        )
        a2 = Adresse.objects.create(
            user=self.user,
            prenom="Marie",
            nom="Curie",
            telephone="05060708",
            adresse_ligne1="Cocody",
            ville="Abidjan",
            par_defaut=True
        )
        
        # a1 doit avoir par_defaut désactivé automatiquement
        a1.refresh_from_db()
        self.assertFalse(a1.par_defaut)
        self.assertTrue(a2.par_defaut)

    def test_cities_light_relations_and_serialization(self):
        adresse = Adresse.objects.create(
            user=self.user,
            prenom="Jean",
            nom="Dupont",
            telephone="01020304",
            adresse_ligne1="Plateau",
            ville="Abidjan",
            city=self.city,
            region_cl=self.region,
            country=self.country,
            par_defaut=True
        )
        
        # Test de l'endpoint d'API pour vérifier la sérialisation des nouveaux champs
        response = self.client.get(f"/api/adresses/{adresse.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérification des relations imbriquées cities_light
        self.assertEqual(response.data["city"], self.city.id)
        self.assertEqual(response.data["city_nom"], "Abidjan")
        self.assertEqual(response.data["region_nom"], "Lagunes")
        self.assertEqual(response.data["pays_nom"], "Côte d'Ivoire")
