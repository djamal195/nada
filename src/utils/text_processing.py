import re

def clean_text(text):
    """
    Nettoie le texte en supprimant les caractères spéciaux et les espaces multiples
    """
    # Supprimer les caractères spéciaux
    text = re.sub(r'[^\w\s]', '', text)
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    # Supprimer les espaces au début et à la fin
    text = text.strip()
    return text

def extract_keywords(text):
    """
    Extrait les mots-clés d'un texte
    """
    # Liste de mots vides en français
    stop_words = ['le', 'la', 'les', 'un', 'une', 'des', 'et', 'ou', 'de', 'du', 'ce', 'cette', 'ces', 'mon', 'ma', 'mes', 'ton', 'ta', 'tes', 'son', 'sa', 'ses']
    
    # Nettoyer le texte
    text = clean_text(text.lower())
    
    # Diviser le texte en mots
    words = text.split()
    
    # Filtrer les mots vides
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    return keywords