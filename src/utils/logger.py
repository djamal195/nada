import logging
import os
import sys

def setup_logger():
    """
    Configure le logger pour l'application
    """
    # Créer le logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Vérifier si des handlers existent déjà
    if not logger.handlers:
        # Créer un handler pour la console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Définir le format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # Ajouter le handler au logger
        logger.addHandler(console_handler)
        
        # Désactiver la propagation pour éviter les doublons
        logger.propagate = False
    
    return logger

# Initialiser le logger
logger = setup_logger()