from flask import Flask, request, Response
import json
import os
import sys
import logging

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import verify_webhook
from src.messenger_api import handle_message
from src.utils.logger import setup_logger

# Configurer le logger
logger = setup_logger()

app = Flask(__name__)

@app.route('/api/webhook', methods=['GET'])
def webhook_verification():
    """
    Endpoint pour la vérification du webhook par Facebook
    """
    logger.info("Requête GET reçue pour la vérification du webhook")
    return verify_webhook(request)

@app.route('/api/webhook', methods=['POST'])
def webhook_handler():
    """
    Endpoint pour recevoir les événements du webhook
    """
    logger.info("Requête POST reçue du webhook")
    data = request.json
    logger.info(f"Corps de la requête: {json.dumps(data)}")
    
    if data.get('object') == 'page':
        logger.info("Événement de page reçu")
        for entry in data.get('entry', []):
            logger.info(f"Entrée reçue: {json.dumps(entry)}")
            messaging = entry.get('messaging', [])
            if messaging:
                webhook_event = messaging[0]
                logger.info(f"Événement Webhook reçu: {json.dumps(webhook_event)}")
                
                sender_id = webhook_event.get('sender', {}).get('id')
                logger.info(f"ID de l'expéditeur: {sender_id}")
                
                if webhook_event.get('message'):
                    logger.info("Message reçu, appel de handle_message")
                    try:
                        handle_message(sender_id, webhook_event.get('message'))
                        logger.info("handle_message terminé avec succès")
                    except Exception as e:
                        logger.error(f"Erreur lors du traitement du message: {str(e)}")
                elif webhook_event.get('postback'):
                    logger.info(f"Postback reçu: {json.dumps(webhook_event.get('postback'))}")
                    try:
                        handle_message(sender_id, {'postback': webhook_event.get('postback')})
                        logger.info("handle_message pour postback terminé avec succès")
                    except Exception as e:
                        logger.error(f"Erreur lors du traitement du postback: {str(e)}")
                else:
                    logger.info(f"Événement non reconnu: {webhook_event}")
            else:
                logger.info("Aucun événement de messagerie dans cette entrée")
        
        return Response("EVENT_RECEIVED", status=200)
    else:
        logger.info("Requête non reconnue reçue")
        return Response(status=404)

@app.errorhandler(Exception)
def handle_error(e):
    logger.error(f"Erreur non gérée: {str(e)}")
    return Response("Quelque chose s'est mal passé!", status=500)

if __name__ == '__main__':
    app.run(debug=True)