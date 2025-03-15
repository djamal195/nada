import os
import tempfile
from yt_dlp import YoutubeDL
import logging

logger = logging.getLogger(__name__)

def download_youtube_video(video_id, max_duration=60, max_filesize=8*1024*1024):
    """
    Télécharge une vidéo YouTube et retourne le chemin du fichier temporaire
    
    Args:
        video_id: ID de la vidéo YouTube
        max_duration: Durée maximale en secondes (défaut: 60s)
        max_filesize: Taille maximale en octets (défaut: 8MB)
        
    Returns:
        tuple: (chemin_fichier, titre_video) ou (None, None) en cas d'erreur
    """
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
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }
    
    try:
        logger.info(f"Téléchargement de la vidéo YouTube {video_id}...")
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
            
            # Vérifier la durée
            duration = info.get('duration', 0)
            if duration > max_duration:
                logger.warning(f"Vidéo trop longue: {duration}s > {max_duration}s")
                return None, None
                
            title = info.get('title', 'Video sans titre')
            logger.info(f"Vidéo téléchargée: {title}")
            
            return output_path, title
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement de la vidéo: {str(e)}")
        return None, None