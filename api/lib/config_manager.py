#!/bash/bin
# -*- encoding: utf-8 -*-
"""
@author:        Barnabas
@email:         barnabasaugustino@gmail.com
@client:        Barnabas
@gitlab:        https://gitlab.com/projects28/medinsights-be.git
@domain name:
@Hostname:      DigitalOcean
@Description:
"""
import os
from dotenv import dotenv_values

config = dotenv_values(".env")

class Configuration(object):
    """This is a base class from all configuration classes"""
    # python -c 'import secrets; print(secrets.token_hex())'
    SECRET_KEY = os.environ.get('SECRET_KEY') if os.environ.get('SECRET_KEY') else config.get('SECRET_KEY')
    ENV = os.environ.get('ENV') if os.environ.get('ENV') else config.get('ENV')
    TEMPLATE_AUTO_RELOAD = True
    ALLOWED_PHOTO_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    ALLOWED_DOCUMENT_EXTENSIONS = {'pdf'}
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS') if os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS') else config.get('SQLALCHEMY_TRACK_MODIFICATIONS')

    # Database configurations for different countries
    DATABASES = {
        'italy': {
            'host': os.environ.get('IT_DB_HOST') if os.environ.get('IT_DB_HOST') else config.get('IT_DB_HOST'),
            'port': os.environ.get('IT_DB_PORT') if os.environ.get('IT_DB_PORT') else config.get('IT_DB_PORT'),
            'user': os.environ.get('IT_DB_USER') if os.environ.get('IT_DB_USER') else config.get('IT_DB_USER'),
            'password': os.environ.get('IT_DB_PASSWORD') if os.environ.get('IT_DB_PASSWORD') else config.get('IT_DB_PASSWORD'),
            'db_name': os.environ.get('IT_DB_NAME') if os.environ.get('IT_DB_NAME') else config.get('IT_DB_NAME')
        },
        'germany': {
            'host': os.environ.get('DE_DB_HOST') if os.environ.get('DE_DB_HOST') else config.get('DE_DB_HOST'),
            'port': os.environ.get('DE_DB_PORT') if os.environ.get('DE_DB_PORT') else config.get('DE_DB_PORT'),
            'user': os.environ.get('DE_DB_USER') if os.environ.get('DE_DB_USER') else config.get('DE_DB_USER'),
            'password': os.environ.get('DE_DB_PASSWORD') if os.environ.get('DE_DB_PASSWORD') else config.get('DE_DB_PASSWORD'),
            'db_name': os.environ.get('DE_DB_NAME') if os.environ.get('DE_DB_NAME') else config.get('DE_DB_NAME')
        }
    }

    # Default configuration uses Italy database for backward compatibility
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') if os.environ.get('DATABASE_URI') else config.get('DATABASE_URI')
    DB_SERVER = os.environ.get('DB_ENGINE') if os.environ.get('DB_ENGINE') else config.get('DB_ENGINE')
    DB_NAME = os.environ.get('IT_DB_NAME') if os.environ.get('IT_DB_NAME') else config.get('IT_DB_NAME')
    DATABASE_PARAM = {
        'postgresql': {
            'host': os.environ.get('IT_DB_HOST') if os.environ.get('IT_DB_HOST') else config.get('IT_DB_HOST'),
            'port': os.environ.get('IT_DB_PORT') if os.environ.get('IT_DB_PORT') else config.get('IT_DB_PORT'),
            'user': os.environ.get('IT_DB_USER') if os.environ.get('IT_DB_USER') else config.get('IT_DB_USER'),
            'password': os.environ.get('IT_DB_PASSWORD') if os.environ.get('IT_DB_PASSWORD') else config.get('IT_DB_PASSWORD')
        }
    }

class LocalConfiguration(Configuration):
    """Contains environmental variables for local configuration"""
    DEBUG = config.get('DEBUG')

class DevelopmentConfiguration(Configuration):
    """Contains environment variables for development configuration"""
    DEBUG = True

class TestingConfiguration(Configuration):
    """Contains environment variables for staging Configuration"""
    TESTING = True
    DEBUG = True

class StagingConfiguration(Configuration):
    """Contains environment variable for staging configuration"""
    pass

class DemoConfiguration(Configuration):
    """Contains environment variable for demo configuration"""
    pass

class ProductionConfiguration(Configuration):
    """Contains environment variables for staging configuration"""
    pass

class APIConfiguration(Configuration):
    """Contains environment variables for staging configuration"""
    pass