from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from rest_framework.test import APITestCase
from rest_framework import status
from vendor.models.produit import Produit
from store.models.panier import Panier, PanierItem
from store.models.commandes import Commande, CommandeItem
from store.admin.admin import CommandeAdmin


class PanierDynamicPricingTestCase(APITestCase):
    """
    Tests de la dynamisation des prix du panier.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="client_panier", password="password123")
        self.vendeur = User.objects.create_user(username="vendeur_panier", password="password123")
        self.client.force_authenticate(user=self.user)
        
        self.produit = Produit.objects.create(
            vendeur=self.vendeur, nom="Produit Test", prix=1000.00, stock=20
        )
        self.panier, _ = Panier.objects.get_or_create(user=self.user)
        self.item = PanierItem.objects.create(
            panier=self.panier, produit=self.produit, quantite=2, prix_unitaire=1000.00
        )

    def test_dynamic_cart_total_and_price_sync(self):
        # Modifier le prix du produit
        self.produit.prix = 1200.00
        self.produit.save()
        
        # Le total du panier doit refléter le prix mis à jour (1200 * 2 = 2400)
        self.assertEqual(self.panier.total, 2400.00)
        self.assertEqual(self.item.sous_total, 2400.00)
        
        # Appel de l'action mon-panier pour synchroniser la base de données
        response = self.client.get("/api/panier/mon-panier/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data["total"]), 2400.00)
        
        # Vérification en base de données
        self.item.refresh_from_db()
        self.assertEqual(self.item.prix_unitaire, 1200.00)


class CommandeAndStockTestCase(APITestCase):
    """
    Tests du recalcul de commande, décrémentation stock, et blocage CRUD panier.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="client_commande", password="password123")
        self.vendeur = User.objects.create_user(username="vendeur_commande", password="password123")
        self.client.force_authenticate(user=self.user)
        
        self.produit = Produit.objects.create(
            vendeur=self.vendeur, nom="Produit Stock", prix=500.00, stock=10
        )
        self.panier, _ = Panier.objects.get_or_create(user=self.user)
        self.item = PanierItem.objects.create(
            panier=self.panier, produit=self.produit, quantite=3, prix_unitaire=500.00
        )

    def test_order_creation_decrements_stock(self):
        payload = {
            "adresse_livraison_texte": "Abidjan, Cocody",
            "note_client": "Livrer le soir"
        }
        
        # Création de la commande
        response = self.client.post("/api/commandes/", payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Le stock du produit doit être décrémenté de 3 (10 - 3 = 7)
        self.produit.refresh_from_db()
        self.assertEqual(self.produit.stock, 7)
        
        # Le panier doit être vidé
        self.assertEqual(self.panier.items.count(), 0)

    def test_insufficient_stock_raises_validation_error(self):
        # Augmenter la quantité demandée au-delà du stock dispo
        self.item.quantite = 15
        self.item.save()
        
        payload = {
            "adresse_livraison_texte": "Abidjan, Cocody"
        }
        response = self.client.post("/api/commandes/", payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Stock intact
        self.produit.refresh_from_db()
        self.assertEqual(self.produit.stock, 10)

    def test_recalculate_on_item_save_and_delete(self):
        commande = Commande.objects.create(user=self.user, sous_total=0, total=0)
        item1 = CommandeItem.objects.create(
            commande=commande, produit=self.produit, nom_produit=self.produit.nom, quantite=2, prix_unitaire=500.00
        )
        
        # Total initial : 1000
        commande.refresh_from_db()
        self.assertEqual(commande.total, 1000.00)
        
        # Modification quantité
        item1.quantite = 4
        item1.save()
        
        # Nouveau total : 2000
        commande.refresh_from_db()
        self.assertEqual(commande.total, 2000.00)
        
        # Suppression de l'item
        item1.delete()
        commande.refresh_from_db()
        self.assertEqual(commande.total, 0.00)

    def test_stock_restored_on_cancellation(self):
        # Créer une commande avec un item
        commande = Commande.objects.create(user=self.user, sous_total=500, total=500)
        CommandeItem.objects.create(
            commande=commande, produit=self.produit, nom_produit=self.produit.nom, quantite=2, prix_unitaire=500.00
        )
        
        # Simuler le changement de statut à ANNULEE
        commande.statut = "ANNULEE"
        commande.save()
        
        # Le stock initial était 10. Avec 2 restitués, il doit être à 12
        self.produit.refresh_from_db()
        self.assertEqual(self.produit.stock, 12)

    def test_panier_crud_disabled_in_router(self):
        # Les routes CRUD standard sur /api/panier/ ne doivent pas exister (405 ou 404)
        response_list = self.client.get("/api/panier/")
        self.assertIn(response_list.status_code, [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_404_NOT_FOUND])
        
        response_detail = self.client.get(f"/api/panier/{self.panier.id}/")
        self.assertIn(response_detail.status_code, [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_404_NOT_FOUND])
