import json
import requests
import logging
import io
import tempfile
import os
from src.config import MESSENGER_PAGE_ACCESS_TOKEN
from src.mistral_api import generate_mistral_response
from src.youtube_api import search_youtube
from src.models.video import Video
from src.database import Database

logger = logging.getLogger(__name__)

# Dictionnaire pour stocker l'état des utilisateurs
user_states = {}

def handle_message(sender_id, received_message):
    """
    Gère les messages reçus des utilisateurs
    """
    logger.info(f"Début de handle_message pour sender_id: {sender_id}")
    logger.info(f"Message reçu: {json.dumps(received_message)}")
    
    try:
        # Initialiser la base de données si nécessaire
        try:
            Database.get_instance()
        except Exception as db_error:
            logger.warning(f"Impossible de se connecter à la base de données: {str(db_error)}")
            # Continuer sans la base de données
        
        if 'text' in received_message:
            text = received_message['text'].lower()
            
            if text == '/yt':
                user_states[sender_id] = 'youtube'
                send_text_message(sender_id, "Mode YouTube activé. Donnez-moi les mots-clés pour la recherche YouTube.")
            elif text == 'yt/':
                user_states[sender_id] = 'mistral'
                send_text_message(sender_id, "Mode Mistral réactivé. Comment puis-je vous aider ?")
            elif sender_id in user_states and user_states[sender_id] == 'youtube':
                logger.info(f"Recherche YouTube pour: {received_message['text']}")
                try:
                    videos = search_youtube(received_message['text'])
                    if not videos or len(videos) == 0:
                        send_text_message(sender_id, "Aucune vidéo trouvée pour cette recherche. Essayez avec d'autres mots-clés.")
                        return
                        
                    logger.info(f"Résultats de la recherche YouTube: {json.dumps(videos)}")
                    send_youtube_results(sender_id, videos)
                except Exception as e:
                    logger.error(f"Erreur lors de la recherche YouTube: {str(e)}")
                    send_text_message(sender_id, "Désolé, je n'ai pas pu effectuer la recherche YouTube. Veuillez réessayer plus tard.")
            else:
                logger.info("Génération de la réponse Mistral...")
                try:
                    response = generate_mistral_response(received_message['text'])
                    logger.info(f"Réponse Mistral générée: {response}")
                    send_text_message(sender_id, response)
                except Exception as e:
                    logger.error(f"Erreur lors de la génération de la réponse Mistral: {str(e)}")
                    fallback_response = "Je suis désolé, je ne peux pas accéder à mon service de réponse en ce moment. Vous pouvez essayer le mode YouTube en tapant '/yt'."
                    send_text_message(sender_id, fallback_response)
            
            logger.info("Message envoyé avec succès")
        elif 'postback' in received_message:
            logger.info(f"Traitement du postback: {json.dumps(received_message['postback'])}")
            try:
                payload = json.loads(received_message['postback']['payload'])
                logger.info(f"Payload du postback: {json.dumps(payload)}")
                
                if payload.get('action') == 'watch_video':
                    logger.info(f"Action watch_video détectée pour videoId: {payload.get('videoId')}")
                    handle_watch_video(sender_id, payload.get('videoId'))
                else:
                    logger.info(f"Action de postback non reconnue: {payload.get('action')}")
            except Exception as e:
                logger.error(f"Erreur lors du traitement du postback: {str(e)}")
                send_text_message(sender_id, "Désolé, je n'ai pas pu traiter votre demande. Veuillez réessayer plus tard.")
        else:
            logger.info("Message reçu sans texte")
            send_text_message(sender_id, "Désolé, je ne peux traiter que des messages texte.")
    except Exception as e:
        logger.error(f"Erreur lors du traitement du message: {str(e)}")
        error_message = "Désolé, j'ai rencontré une erreur en traitant votre message. Veuillez réessayer plus tard."
        if "timeout" in str(e):
            error_message = "Désolé, la génération de la réponse a pris trop de temps. Veuillez réessayer avec une question plus courte ou plus simple."
        send_text_message(sender_id, error_message)
    
    logger.info("Fin de handle_message")

def send_youtube_results(recipient_id, videos):
    """
    Envoie les résultats de recherche YouTube sous forme de carrousel
    """
    elements = []
    for video in videos:
        elements.append({
            "title": video['title'],
            "image_url": video['thumbnail'],
            "buttons": [
                {
                    "type": "web_url",
                    "url": f"https://www.youtube.com/watch?v={video['videoId']}",
                    "title": "Regarder sur YouTube"
                },
                {
                    "type": "postback",
                    "title": "Télécharger MP4",
                    "payload": json.dumps({
                        "action": "watch_video",
                        "videoId": video['videoId']
                    })
                }
            ]
        })
    
    message_data = {
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": elements
                }
            }
        }
    }
    
    call_send_api(message_data)

def handle_watch_video(recipient_id, video_id):
    """
    Télécharge et envoie une vidéo YouTube en MP4
    """
    try:
        # Informer l'utilisateur que le téléchargement est en cours
        send_text_message(recipient_id, "Je télécharge votre vidéo, veuillez patienter...")
        
        # Télécharger la vidéo
        video_data, title, filename = download_youtube_video(video_id)
        
        if not video_data:
            send_text_message(recipient_id, "Désolé, je n'ai pas pu télécharger cette vidéo. Elle est peut-être trop longue ou trop volumineuse.")
            send_text_message(recipient_id, f"Voici le lien YouTube à la place: https://www.youtube.com/watch?v={video_id}")
            return
        
        # Envoyer la vidéo à l'utilisateur
        success = send_video_file(recipient_id, video_data, filename, title)
        
        if not success:
            # Fallback: envoyer le lien YouTube
            send_text_message(recipient_id, "Désolé, je n'ai pas pu envoyer la vidéo. Voici le lien YouTube à la place:")
            send_text_message(recipient_id, f"https://www.youtube.com/watch?v={video_id}")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de la vidéo: {str(e)}")
        send_text_message(recipient_id, "Désolé, je n'ai pas pu envoyer la vidéo. Veuillez réessayer plus tard.")
        send_text_message(recipient_id, f"Voici le lien YouTube à la place: https://www.youtube.com/watch?v={video_id}")

def download_youtube_video(video_id, max_duration=60, max_filesize=8*1024*1024):
    """
    Télécharge une vidéo YouTube et retourne les données binaires
    
    Args:
        video_id: ID de la vidéo YouTube
        max_duration: Durée maximale en secondes (défaut: 60s)
        max_filesize: Taille maximale en octets (défaut: 8MB)
        
    Returns:
        tuple: (données_binaires, titre_video, nom_fichier) ou (None, None, None) en cas d'erreur
    """
    logger.info(f"Début du téléchargement de la vidéo YouTube {video_id}...")
    
    try:
        from yt_dlp import YoutubeDL
        
        # Créer un dossier temporaire
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, f"{video_id}.mp4")
        
        ydl_opts = {
            'format': 'worst[ext=mp4]',  # Qualité la plus basse pour réduire la taille
            'outtmpl': output_path,
            'max_filesize': max_filesize,
            'max_downloads': 1,
            'noplaylist': True,
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': False,
        }
        
        logger.info(f"Extraction des informations de la vidéo YouTube {video_id}...")
        with YoutubeDL(ydl_opts) as ydl:
            # D'abord extraire les informations sans télécharger
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            
            # Vérifier la durée
            duration = info.get('duration', 0)
            if duration > max_duration:
                logger.warning(f"Vidéo trop longue: {duration}s > {max_duration}s")
                return None, None, None
            
            # Vérifier la taille estimée si disponible
            filesize = info.get('filesize', 0)
            if filesize > max_filesize and filesize > 0:
                logger.warning(f"Vidéo trop volumineuse: {filesize} octets > {max_filesize} octets")
                return None, None, None
            
            title = info.get('title', 'Video sans titre')
            logger.info(f"Informations extraites: Titre={title}, Durée={duration}s")
            
            # Trouver le format mp4 de plus basse qualité
            formats = info.get('formats', [])
            mp4_formats = [f for f in formats if f.get('ext') == 'mp4']
            
            if not mp4_formats:
                logger.error("Aucun format MP4 disponible")
                return None, None, None
            
            # Trier par taille/résolution
            sorted_formats = sorted(mp4_formats, 
                                   key=lambda x: x.get('filesize', 0) if x.get('filesize', 0) > 0 
                                   else x.get('height', 0))
            
            # Obtenir l'URL directe
            direct_url = sorted_formats[0].get('url')
            
            if not direct_url:
                logger.error("Impossible d'obtenir l'URL directe")
                return None, None, None
            
            # Télécharger la vidéo directement depuis l'URL
            logger.info(f"Téléchargement de la vidéo depuis l'URL directe...")
            response = requests.get(direct_url, stream=True, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Erreur lors du téléchargement: {response.status_code}")
                return None, None, None
            
            # Lire les données en mémoire
            video_data = io.BytesIO()
            for chunk in response.iter_content(chunk_size=8192):
                video_data.write(chunk)
            
            # Remettre le curseur au début du buffer
            video_data.seek(0)
            
            # Vérifier la taille
            size = video_data.getbuffer().nbytes
            if size > max_filesize:
                logger.warning(f"Vidéo téléchargée trop volumineuse: {size} octets > {max_filesize} octets")
                return None, None, None
            
            logger.info(f"Vidéo téléchargée avec succès, taille: {size} octets")
            filename = f"{video_id}.mp4"
            return video_data, title, filename
            
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement de la vidéo: {str(e)}", exc_info=True)
        return None, None, None
    finally:
        # Nettoyer le dossier temporaire
        try:
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
        except Exception as e:
            logger.warning(f"Impossible de nettoyer le dossier temporaire: {str(e)}")

def send_video_file(recipient_id, video_data, filename, title):
    """
    Envoie un fichier vidéo à l'utilisateur via l'API Messenger
    
    Args:
        recipient_id: ID du destinataire
        video_data: Données binaires de la vidéo (BytesIO)
        filename: Nom du fichier
        title: Titre de la vidéo
        
    Returns:
        bool: True si envoyé avec succès, False sinon
    """
    try:
        logger.info(f"Envoi du fichier vidéo {filename} à l'utilisateur {recipient_id}...")
        
        # L'API Messenger nécessite une URL publique pour les pièces jointes
        # Nous devons donc utiliser l'API d'upload de pièces jointes
        
        url = f"https://graph.facebook.com/v13.0/me/message_attachments?access_token={MESSENGER_PAGE_ACCESS_TOKEN}"
        
        # Préparer les données pour l'upload
        from requests_toolbelt.multipart.encoder import MultipartEncoder
        
        multipart_data = MultipartEncoder(
            fields={
                'recipient': json.dumps({"id": recipient_id}),
                'message': json.dumps({
                    "attachment": {
                        "type": "video", 
                        "payload": {
                            "is_reusable": True
                        }
                    }
                }),
                'filedata': (filename, video_data, 'video/mp4')
            }
        )
        
        # Envoyer la requête
        response = requests.post(
            url,
            data=multipart_data,
            headers={'Content-Type': multipart_data.content_type},
            timeout=60
        )
        
        if response.status_code != 200:
            logger.error(f"Erreur lors de l'upload du fichier: {response.status_code} - {response.text}")
            return False
        
        # Récupérer l'ID de la pièce jointe
        result = response.json()
        attachment_id = result.get('attachment_id')
        
        if not attachment_id:
            logger.error(f"Pas d'ID de pièce jointe dans la réponse: {result}")
            return False
        
        # Envoyer le message avec la pièce jointe
        message_data = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "attachment": {
                    "type": "video",
                    "payload": {
                        "attachment_id": attachment_id
                    }
                }
            }
        }
        
        call_send_api(message_data)
        
        # Envoyer également le titre comme message texte
        send_text_message(recipient_id, f"Titre: {title}")
        
        logger.info("Fichier vidéo envoyé avec succès")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du fichier vidéo: {str(e)}")
        return False

def send_text_message(recipient_id, message_text):
    """
    Envoie un message texte à l'utilisateur
    """
    logger.info(f"Début de send_text_message pour recipient_id: {recipient_id}")
    logger.info(f"Message à envoyer: {message_text}")
    
    # Diviser le message en chunks de 2000 caractères maximum
    chunks = [message_text[i:i+2000] for i in range(0, len(message_text), 2000)]
    
    for chunk in chunks:
        message_data = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": chunk
            }
        }
        
        try:
            call_send_api(message_data)
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message: {str(e)}")
            raise e
    
    logger.info("Fin de send_text_message")

def call_send_api(message_data):
    """
    Appelle l'API Send de Facebook pour envoyer des messages
    """
    logger.info(f"Début de call_send_api avec message_data: {json.dumps(message_data)}")
    url = f"https://graph.facebook.com/v13.0/me/messages?access_token={MESSENGER_PAGE_ACCESS_TOKEN}"
    
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=message_data,
            timeout=30
        )
        
        logger.info(f"Réponse reçue de l'API Facebook. Status: {response.status_code}")
        
        response_body = response.json()
        logger.info(f"Réponse de l'API Facebook: {json.dumps(response_body)}")
        
        if 'error' in response_body:
            logger.error(f"Erreur lors de l'appel à l'API Send: {response_body['error']}")
            raise Exception(response_body['error']['message'])
        
        logger.info("Message envoyé avec succès")
        return response_body
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à l'API Facebook: {str(e)}")
        raise e
