import io
import logging
from yt_dlp import YoutubeDL

logger = logging.getLogger(__name__)

def download_youtube_video(video_id, max_duration=60, max_filesize=8*1024*1024):
    """
    Télécharge une vidéo YouTube et retourne le buffer mémoire
    
    Args:
        video_id: ID de la vidéo YouTube
        max_duration: Durée maximale en secondes (défaut: 60s)
        max_filesize: Taille maximale en octets (défaut: 8MB)
        
    Returns:
        tuple: (buffer_video, titre_video) ou (None, None) en cas d'erreur
    """
    logger.info(f"Début du téléchargement de la vidéo YouTube {video_id}...")
    
    # Utiliser un buffer mémoire au lieu d'un fichier
    buffer = io.BytesIO()
    
    ydl_opts = {
        'format': 'worst[ext=mp4]',  # Qualité la plus basse pour réduire la taille
        'max_filesize': max_filesize,
        'max_downloads': 1,
        'noplaylist': True,
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': False,
        # Utiliser un hook pour capturer la sortie
        'progress_hooks': [lambda d: logger.info(f"Progression: {d.get('status')} - {d.get('_percent_str', '?')}%")],
        # Limiter la durée
        'match_filter': lambda info: None if info.get('duration', 0) > max_duration else 'download',
    }
    
    try:
        logger.info(f"Extraction des informations de la vidéo YouTube {video_id}...")
        with YoutubeDL(ydl_opts) as ydl:
            # D'abord extraire les informations sans télécharger
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            
            # Vérifier la durée
            duration = info.get('duration', 0)
            if duration > max_duration:
                logger.warning(f"Vidéo trop longue: {duration}s > {max_duration}s")
                return None, None
            
            # Vérifier la taille estimée si disponible
            filesize = info.get('filesize', 0)
            if filesize > max_filesize and filesize > 0:
                logger.warning(f"Vidéo trop volumineuse: {filesize} octets > {max_filesize} octets")
                return None, None
            
            title = info.get('title', 'Video sans titre')
            logger.info(f"Informations extraites: Titre={title}, Durée={duration}s")
            
            # Maintenant télécharger la vidéo
            logger.info("Téléchargement de la vidéo...")
            
            # Cette partie est complexe car yt-dlp est conçu pour télécharger vers des fichiers
            # Pour une solution serverless, il est préférable d'utiliser une approche différente
            
            # Retourner simplement l'URL directe de la vidéo si disponible
            formats = info.get('formats', [])
            if formats:
                # Trouver le format mp4 de plus basse qualité
                mp4_formats = [f for f in formats if f.get('ext') == 'mp4']
                if mp4_formats:
                    # Trier par taille (ou résolution si la taille n'est pas disponible)
                    sorted_formats = sorted(mp4_formats, 
                                           key=lambda x: x.get('filesize', 0) if x.get('filesize', 0) > 0 
                                           else x.get('height', 0))
                    
                    direct_url = sorted_formats[0].get('url')
                    if direct_url:
                        logger.info(f"URL directe trouvée: {direct_url[:50]}...")
                        return direct_url, title
            
            logger.error("Impossible de trouver une URL directe pour la vidéo")
            return None, None
            
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement de la vidéo: {str(e)}", exc_info=True)
        return None, None
