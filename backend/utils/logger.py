# Simple logging utility for SocialFlow AI
import logging

def get_logger(name: str):
    """Get a configured logger instance"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )
    return logger