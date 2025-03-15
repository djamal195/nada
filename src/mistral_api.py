import re
import requests
import json
import logging
import signal
from src.config import MISTRAL_API_KEY

logger = logging.getLogger(__name__)

def check_creator_question(prompt):
    """
    Vérifie si la question concerne le créateur du bot
    """
    prompt = prompt.lower()
    patterns = [
        r"qui (t'a|ta|t as) (créé|cree|construit|développé|developpe|conçu|concu|fabriqué|fabrique|inventé|invente)",
        r"par qui as[- ]?tu (été|ete) (créé|cree|développé|developpe|construit|conçu|concu)",
        r"qui est (ton|responsable de|derrière|derriere) (créateur|createur|développeur|developpeur|toi)",
        r"d['oòo]u viens[- ]?tu"
    ]
    
    for pattern in patterns:
        if re.search(pattern, prompt):
            return True
    
    return False

def generate_mistral_response(prompt):
    """
    Génère une réponse en utilisant l'API Mistral
    """
    logger.info(f"Début de generate_mistral_response pour prompt: {prompt}")
    
    # Vérifier si la question concerne le créateur
    if check_creator_question(prompt):
        logger.info("Question sur le créateur détectée. Réponse personnalisée envoyée.")
        return "J'ai été créé par Djamaldine Montana avec l'aide de Mistral. C'est un développeur talentueux qui m'a conçu pour aider les gens comme vous !"
    
    # Vérifier si la clé API est définie
    if not MISTRAL_API_KEY:
        logger.error("Erreur: MISTRAL_API_KEY n'est pas définie")
        return "Je suis désolé, mais je ne peux pas répondre pour le moment car ma configuration n'est pas complète. Veuillez contacter l'administrateur."
    
    try:
        logger.info("Envoi de la requête à l'API Mistral...")
        
        # Utiliser requests avec timeout au lieu de signal (qui peut ne pas fonctionner sur Vercel)
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {MISTRAL_API_KEY}"
            },
            json={
                "model": "mistral-large-latest",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000
            },
            timeout=45  # 45 secondes de timeout
        )
        
        logger.info(f"Réponse reçue de l'API Mistral. Status: {response.status_code}")
        
        # Log du corps de la réponse pour le débogage
        response_text = response.text
        logger.info(f"Corps de la réponse: {response_text[:500]}...")
        
        if response.status_code != 200:
            logger.error(f"Erreur API Mistral: {response.status_code} - {response_text}")
            return f"Désolé, l'API Mistral a retourné une erreur (code {response.status_code}). Veuillez réessayer plus tard."
        
        try:
            data = response.json()
            logger.info("Réponse JSON analysée avec succès")
            
            if 'choices' not in data or len(data['choices']) == 0:
                logger.error(f"Format de réponse inattendu: {data}")
                return "Désolé, j'ai reçu une réponse dans un format inattendu. Veuillez réessayer."
            
            generated_response = data['choices'][0]['message']['content']
            
            if len(generated_response) > 4000:
                generated_response = generated_response[:4000] + "... (réponse tronquée)"
            
            logger.info(f"Réponse générée: {generated_response[:100]}...")
            return generated_response
        except ValueError as e:
            logger.error(f"Erreur lors de l'analyse JSON: {str(e)}")
            return "Désolé, j'ai rencontré une erreur lors du traitement de la réponse. Veuillez réessayer."
            
    except requests.exceptions.Timeout:
        logger.error("Timeout lors de la requête à l'API Mistral")
        return "Désolé, la génération de la réponse a pris trop de temps. Veuillez réessayer avec une question plus courte ou plus simple."
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur de requête HTTP: {str(e)}")
        return "Désolé, je n'ai pas pu me connecter à l'API Mistral. Veuillez vérifier votre connexion et réessayer."
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}", exc_info=True)
        return "Je suis désolé, mais j'ai rencontré une erreur inattendue. Veuillez réessayer plus tard."
