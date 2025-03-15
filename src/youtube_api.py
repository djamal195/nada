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
        
        # Créer un service YouTube
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        # Effectuer la recherche
        search_response = youtube.search().list(
            q=query,
            part='snippet',
            maxResults=5,
            type='video'
        ).execute()
        
        # Formater les résultats
        videos = []
        for item in search_response.get('items', []):
            videos.append({
                'title': item['snippet']['title'],
                'thumbnail': item['snippet']['thumbnails']['default']['url'],
                'videoId': item['id']['videoId']
            })
        
        logger.info(f"Résultat de la recherche YouTube: {len(videos)} vidéos trouvées")
        return videos
    except Exception as e:
        logger.error(f"Erreur détaillée lors de la recherche YouTube: {str(e)}")
        raise e