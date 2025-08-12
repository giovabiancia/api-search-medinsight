#!/bash/bin
# -*- encoding: utf-8 -*-
"""
@author:        Barnabas
@email:         barnabasaugustino@gmail.com
@client:        Barnabas
@gitlab:        https://gitlab.com/projects28/medinsights-be.git
@domain name:
@Hostname:      DigitalOcean
@Description:   Configurazione semplificata per database multipli
"""
import os
from dotenv import dotenv_values

config = dotenv_values(".env")

class Configuration(object):
    """Classe base per tutte le configurazioni"""
    SECRET_KEY = os.environ.get('SECRET_KEY') if os.environ.get('SECRET_KEY') else config.get('SECRET_KEY')
    ENV = os.environ.get('ENV') if os.environ.get('ENV') else config.get('ENV')
    TEMPLATE_AUTO_RELOAD = True
    ALLOWED_PHOTO_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    ALLOWED_DOCUMENT_EXTENSIONS = {'pdf'}
    MAX_CONTENT_LENGTH = 20 * 1000 * 1000

    # Database Germania
    DE_DATABASE = {
        'host': os.environ.get('DE_DB_HOST') or config.get('DE_DB_HOST', 'localhost'),
        'port': os.environ.get('DE_DB_PORT') or config.get('DE_DB_PORT', '5433'),
        'user': os.environ.get('DE_DB_USER') or config.get('DE_DB_USER', 'user'),
        'password': os.environ.get('DE_DB_PASSWORD') or config.get('DE_DB_PASSWORD', 'password'),
        'name': os.environ.get('DE_DB_NAME') or config.get('DE_DB_NAME', 'medinsights_de')
    }

    # Database Italia
    IT_DATABASE = {
        'host': os.environ.get('IT_DB_HOST') or config.get('IT_DB_HOST', 'localhost'),
        'port': os.environ.get('IT_DB_PORT') or config.get('IT_DB_PORT', '5433'),
        'user': os.environ.get('IT_DB_USER') or config.get('IT_DB_USER', 'user'),
        'password': os.environ.get('IT_DB_PASSWORD') or config.get('IT_DB_PASSWORD', 'password'),
        'name': os.environ.get('IT_DB_NAME') or config.get('IT_DB_NAME', 'medinsights_it')
    }

    @staticmethod
    def get_db_config(country):
        if country.upper() == 'DE':
            return Configuration.DE_DATABASE
        else:  # Default IT
            return Configuration.IT_DATABASE

class LocalConfiguration(Configuration):
    DEBUG = config.get('DEBUG')

class DevelopmentConfiguration(Configuration):
    DEBUG = True

class TestingConfiguration(Configuration):
    TESTING = True
    DEBUG = True

class StagingConfiguration(Configuration):
    pass

class DemoConfiguration(Configuration):
    pass

class ProductionConfiguration(Configuration):
    pass

class APIConfiguration(Configuration):
    pass