# Dans src/cloudinary_service.py
def upload_video_with_auto_delete(video_data, public_id):
    """
    Télécharge une vidéo vers Cloudinary avec suppression automatique après 1 heure
    """
    try:
        logger.info(f"Téléchargement de la vidéo vers Cloudinary...")
        
        # Convertir en BytesIO si nécessaire
        if isinstance(video_data, bytes):
            video_data = io.BytesIO(video_data)
        
        # Télécharger avec un tag pour la suppression automatique
        result = cloudinary.uploader.upload(
            video_data,
            resource_type="video",
            public_id=public_id,
            overwrite=True,
            format="mp4",
            tags=["auto_delete"],
            transformation=[
                {"width": 320, "crop": "scale"},
                {"quality": "auto:low"},
                {"duration": 60}  # Limiter à 60 secondes
            ]
        )
        
        logger.info(f"Vidéo téléchargée avec succès: {result['url']}")
        
        # Programmer la suppression après 1 heure
        import threading
        def delete_after_delay():
            import time
            time.sleep(3600)  # 1 heure
            try:
                cloudinary.uploader.destroy(public_id, resource_type="video")
                logger.info(f"Vidéo {public_id} supprimée automatiquement")
            except Exception as e:
                logger.error(f"Erreur lors de la suppression automatique: {str(e)}")
        
        threading.Thread(target=delete_after_delay).start()
        
        return result
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement vers Cloudinary: {str(e)}")
        return None
