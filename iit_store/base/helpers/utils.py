from django.utils.text import slugify

def generate_unique_slug(model_class, text, slug_field="slug"):
    """
    Génère un slug unique pour un modèle Django donné et une chaîne de caractères.
    """
    base_slug = slugify(text)
    slug = base_slug
    n = 1
    # On cherche s'il existe déjà un objet avec ce slug
    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{n}"
        n += 1
    return slug

def format_price(amount, currency="FCFA"):
    """
    Formate un montant décimal ou numérique sous forme de chaîne monétaire propre.
    """
    if amount is None:
        return f"0 {currency}"
    try:
        # Formatage avec espace de séparation de milliers
        formatted_amount = f"{float(amount):,.2f}".replace(",", " ").replace(".00", "")
        return f"{formatted_amount} {currency}"
    except (ValueError, TypeError):
        return f"{amount} {currency}"
