import os

class ProductionConfig:
    DEBUG = False
    TESTING = False
    # Ensure static files are served correctly
    STATIC_FOLDER = 'static'
    STATIC_URL_PATH = '/static'
    # Add security headers
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year cache for static files

class DevelopmentConfig:
    DEBUG = True
    TESTING = False
    STATIC_FOLDER = 'static'
    STATIC_URL_PATH = '/static'

# Get configuration based on environment
config = ProductionConfig if os.environ.get('FLASK_ENV') == 'production' else DevelopmentConfig 