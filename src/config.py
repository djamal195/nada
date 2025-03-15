import os
from flask import Response
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Variables d'environnement Messenger
MESSENGER_VERIFY_TOKEN = os.getenv('MESSENGER_VERIFY_TOKEN')
MESSENGER_PAGE_ACCESS_TOKEN = os.getenv('MESSENGER_PAGE_ACCESS_TOKEN')

# Variables d'environnement Mistral
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')

# Variables d'environnement YouTube
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# Variables d'environnement Cloudinary
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

# Variables d'environnement MongoDB
MONGODB_URI = os.getenv('MONGODB_URI')

def verify_webhook(request):
    """
    Vérifie le webhook avec le token fourni par Facebook
    """
    print("Requête de vérification reçue avec les paramètres:", request.args)
    
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    print(f"Mode: {mode}")
    print(f"Token reçu: {token}")
    print(f"Challenge: {challenge}")
    print(f"Token attendu: {MESSENGER_VERIFY_TOKEN}")
    print(f"Page Access Token: {'Défini' if MESSENGER_PAGE_ACCESS_TOKEN else 'Non défini'}")
    
    if mode and token:
        if mode == 'subscribe' and token == MESSENGER_VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return Response(challenge, status=200)
        else:
            print("Vérification échouée - Token incorrect ou mode invalide")
            print(f"Mode reçu: {mode}, Mode attendu: subscribe")
            print(f"Token reçu: {token}, Token attendu: {MESSENGER_VERIFY_TOKEN}")
            return Response(status=403)
    else:
        print("Paramètres manquants dans la requête")
        return Response(status=400)