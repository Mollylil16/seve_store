import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iit_store.settings')
django.setup()

from django.contrib.auth.models import User
from vendor.models.categorie import Categorie
from vendor.models.produit import Produit

# 1. Get or create seller
vendeur = User.objects.filter(is_staff=True).first()
if not vendeur:
    vendeur = User.objects.create_superuser('admin', 'admin@seve.com', 'adminpass')
    print("Superuser created!")

# 2. Clear old products
Produit.objects.all().delete()
Categorie.objects.all().delete()
print("Cleared old data.")

# 3. Create Categories
cats = {
    "savons": Categorie.objects.create(nom="Savons", slug="savons"),
    "cremes": Categorie.objects.create(nom="Crèmes & Pommades", slug="cremes-pommades"),
    "laits": Categorie.objects.create(nom="Laits & Lotions", slug="laits-lotions"),
}
print("Created categories.")

# 4. Products list
products_data = [
    {
        "nom": "sève. Savon Doux Bébé & Maman",
        "description_courte": "Savon surgras saponifié à froid au beurre de karité bio et calendula apaisant.",
        "description": "Formulé spécifiquement pour l'épiderme extrêmement fragile des nourrissons, des jeunes enfants et des femmes enceintes. Ce savon surgras nettoie en douceur sans altérer le film hydrolipidique de la peau. Sans parfum de synthèse ni huiles essentielles.",
        "prix": 3500,
        "stock": 120,
        "categorie": cats["savons"],
    },
    {
        "nom": "sève. Pommade Cacao Intense",
        "description_courte": "Soin corporel réparateur au pur beurre de cacao pour peaux très sèches et tous teints.",
        "description": "Une texture riche et fondante formulée à base de pur beurre de cacao brut d'Afrique de l'Ouest. Elle nourrit en profondeur, prévient la déshydratation cutanée et redonne de la souplesse aux peaux agressées. Idéal pour toute la famille, des adolescents aux personnes âgées.",
        "prix": 6500,
        "stock": 85,
        "categorie": cats["cremes"],
    },
    {
        "nom": "sève. Crème Hydra-Teint Universelle",
        "description_courte": "Crème visage hydratante protectrice révélatrice d'éclat pour tous types de teints.",
        "description": "Une émulsion fine et légère qui pénètre instantanément pour hydrater et illuminer le teint de façon naturelle. Enrichie en aloé vera et huile de jojoba, elle convient à tous les types de peau (hommes, femmes, ados) et sublime l'éclat de tous les teints.",
        "prix": 8000,
        "stock": 150,
        "featured": True,
        "categorie": cats["cremes"],
    },
    {
        "nom": "sève. Lotion Purifiante Ado & Jeune",
        "description_courte": "Lotion tonique assainissante aux actifs d'eucalyptus et zinc pour réguler le sébum.",
        "description": "Idéale pour lutter contre les imperfections des adolescents et jeunes adultes. Cette lotion purifie en profondeur, resserre les pores et réduit les excès de sébum sans dessécher l'épiderme.",
        "prix": 4500,
        "stock": 90,
        "categorie": cats["laits"],
    },
    {
        "nom": "sève. Lait Corporel Éclat Famille",
        "description_courte": "Lait de corps fluide hydratant et unifiant pour un teint soyeux au quotidien.",
        "description": "Un lait de toilette fluide, ultra-nourrissant pour le corps de toute la famille. Grâce à l'huile d'avocat et de carotte, il laisse le teint naturellement éclatant, unifié et d'une douceur absolue.",
        "prix": 7500,
        "stock": 200,
        "categorie": cats["laits"],
    },
    {
        "nom": "sève. Baume Protecteur Senior",
        "description_courte": "Soin anti-âge restructurant riche en huile d'argan pour peaux matures.",
        "description": "Conçu spécialement pour répondre aux besoins des peaux matures et des personnes âgées. Ce baume protecteur associe la puissance nutritive de l'huile d'argan sauvage au rétinol végétal pour lisser les rides, raffermir et redonner du tonus à l'épiderme.",
        "prix": 12000,
        "stock": 60,
        "categorie": cats["cremes"],
    },
    {
        "nom": "sève. Savon Noir Purifiant Homme",
        "description_courte": "Savon exfoliant doux au charbon actif et arbre à thé pour l'homme actif.",
        "description": "Un savon d'excellence pour l'hygiène quotidienne masculine. Le charbon actif absorbe les impuretés et toxines, tandis que l'huile essentielle d'arbre à thé purifie et prévient les irritations dues au rasage.",
        "prix": 3000,
        "stock": 110,
        "categorie": cats["savons"],
    },
    {
        "nom": "sève. Crème Douceur Bébé",
        "description_courte": "Soin protecteur apaisant pour le visage et le change du nourrisson à l'amande douce.",
        "description": "Protège efficacement les fesses et le visage des bébés des rougeurs et de l'humidité. Formulé avec de l'huile d'amande douce protectrice et de l'oxyde de zinc naturel.",
        "prix": 5000,
        "stock": 95,
        "categorie": cats["cremes"],
    },
    {
        "nom": "sève. Lotion Capillaire Fortifiante",
        "description_courte": "Lotion stimulante aux extraits d'ortie et de romarin pour tous âges.",
        "description": "Une formule botanique stimulante pour revitaliser le cuir chevelu, stimuler la pousse des cheveux et limiter leur chute. Convient à toute la famille, y compris les enfants.",
        "prix": 5500,
        "stock": 130,
        "categorie": cats["laits"],
    },
    {
        "nom": "sève. Savon Exfoliant Café Éclat",
        "description_courte": "Savon tonique aux grains de café bio pour affiner le grain de peau et tous teints.",
        "description": "Active la microcirculation cutanée grâce aux grains de café bio moulus. Il exfolie en douceur les cellules mortes pour redonner éclat et douceur à tous les teints de peau.",
        "prix": 3500,
        "stock": 140,
        "categorie": cats["savons"],
    },
    {
        "nom": "sève. Pommade Apaisante Karité",
        "description_courte": "Soin ancestral revisité au karité brut et camomille pour peaux sensibles.",
        "description": "Notre pommade culte. Un concentré de beurre de karité brut non raffiné et de camomille matricaire pour soulager immédiatement les peaux sèches, irritées ou échauffées chez l'enfant et l'adulte.",
        "prix": 6000,
        "stock": 100,
        "featured": True,
        "categorie": cats["cremes"],
    },
    {
        "nom": "sève. Lait Démaquillant Velours",
        "description_courte": "Lait fluide onctueux éliminant le maquillage et les impuretés en douceur.",
        "description": "Nettoie en profondeur les impuretés quotidiennes et élimine le maquillage (même waterproof) sans agresser les yeux ni la barrière cutanée. Laisse la peau veloutée et respirante.",
        "prix": 5800,
        "stock": 75,
        "categorie": cats["laits"],
    },
    {
        "nom": "sève. Lotion Matifiante Anti-Brillance",
        "description_courte": "Lotion astringente à la menthe poivrée et argile blanche pour peaux jeunes.",
        "description": "Idéale pour les adolescents et peaux mixtes à grasses. Elle matifie instantanément, régule la brillance de la zone T du visage et procure une fraîcheur stimulante au réveil.",
        "prix": 4800,
        "stock": 115,
        "categorie": cats["laits"],
    },
    {
        "nom": "sève. Crème Mains & Pieds Réparatrice",
        "description_courte": "Soin ultra-nourrissant pour les zones sèches et abîmées aux actifs botaniques.",
        "description": "Répare et apaise les mains et les talons fendillés. Une barrière protectrice riche qui nourrit intensément les peaux sèches des adultes et des seniors confrontés aux travaux manuels.",
        "prix": 4000,
        "stock": 105,
        "categorie": cats["cremes"],
    },
    {
        "nom": "sève. Savon d'Alep Douceur Olive",
        "description_courte": "Savon ancestral à l'huile d'olive et de baies de laurier pour peaux sensibles.",
        "description": "Un savon surgras ultra-doux formulé à base d'huile d'olive de première pression et de 20% d'huile de baies de laurier. Idéal pour apaiser les peaux sensibles ou sujettes au dessèchement.",
        "prix": 4200,
        "stock": 90,
        "categorie": cats["savons"],
    }
]

for p_item in products_data:
    p = Produit.objects.create(
        vendeur=vendeur,
        nom=p_item["nom"],
        description_courte=p_item["description_courte"],
        description=p_item["description"],
        prix=p_item["prix"],
        stock=p_item["stock"],
        featured=p_item.get("featured", False),
        categorie=p_item["categorie"],
        actif=True
    )
    print(f"Created Product: {p.nom}")

print("Seeding completed successfully!")
