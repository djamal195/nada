import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
import logging
from src.config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

logger = logging.getLogger(__name__)

# Configuration de Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

def upload_video(file_path, public_id):
    """
    Télécharge une vidéo vers Cloudinary
    
    Args:
        file_path: Chemin du fichier vidéo
        public_id: ID public pour la vidéo
        
    Returns:
        dict: Informations sur la vidéo téléchargée ou None en cas d'erreur
    """
    try:
        logger.info(f"Téléchargement de la vidéo {file_path} vers Cloudinary...")
        result = cloudinary.uploader.upload(
            file_path,
            resource_type="video",
            public_id=public_id,
            overwrite=True,
            format="mp4",
            transformation=[
                {"width": 320, "crop": "scale"},
                {"quality": "auto:low"},
                {"duration": 60}  # Limiter à 60 secondes
            ]
        )
        logger.info(f"Vidéo téléchargée avec succès: {result['url']}")
        return result
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement vers Cloudinary: {str(e)}")
        return None
    finally:
        # Supprimer le fichier temporaire
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Fichier temporaire supprimé: {file_path}")