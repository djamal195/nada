from googleapiclient.discovery import build
import os
import logging
from src.config import YOUTUBE_API_KEY

logger = logging.getLogger(__name__)

def search_youtube(query):
    """
    Recherche des vidéos sur YouTube
    """
    try:
        logger.info(f"Début de la recherche YouTube pour: {query}")
        
        # Vérifier si la clé API est définie
        if not YOUTUBE_API_KEY:
            logger.error("Erreur: YOUTUBE_API_KEY n'est pas définie")
            raise Exception("Clé API YouTube non configurée")
        
        logger.info("Création du service YouTube API...")
        try:
            # Créer un service YouTube
            youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
            logger.info("Service YouTube créé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la création du service YouTube: {str(e)}")
            raise Exception(f"Impossible de créer le service YouTube: {str(e)}")
        
        logger.info("Envoi de la requête de recherche YouTube...")
        try:
            # Effectuer la recherche
            search_response = youtube.search().list(
                q=query,
                part='snippet',
                maxResults=5,
                type='video'
            ).execute()
            logger.info("Requête de recherche YouTube exécutée avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la recherche YouTube: {str(e)}")
            raise Exception(f"Échec de la recherche YouTube: {str(e)}")
        
        # Vérifier la structure de la réponse
        if 'items' not in search_response:
            logger.error(f"Format de réponse YouTube inattendu: {search_response}")
            raise Exception("Format de réponse YouTube inattendu")
        
        # Formater les résultats
        videos = []
        for item in search_response.get('items', []):
            try:
                video_data = {
                    'title': item['snippet']['title'],
                    'thumbnail': item['snippet']['thumbnails']['default']['url'],
                    'videoId': item['id']['videoId']
                }
                videos.append(video_data)
                logger.info(f"Vidéo trouvée: {video_data['title']}")
            except KeyError as e:
                logger.warning(f"Données manquantes dans l'élément de recherche: {str(e)}")
                # Continuer avec les autres vidéos
        
        if not videos:
            logger.warning("Aucune vidéo trouvée pour cette recherche")
            return []
        
        logger.info(f"Résultat de la recherche YouTube: {len(videos)} vidéos trouvées")
        return videos
    except Exception as e:
        logger.error(f"Erreur détaillée lors de la recherche YouTube: {str(e)}", exc_info=True)
        raise e
