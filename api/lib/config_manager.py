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
    # STATIC_CONTENTS_HOST = os.environ.get('entry_requirements_static_contents_host')
    # STATIC_CONTENTS_PORT = os.environ.get('entry_requirements_app_static_contents_port')
    MAX_CONTENT_LENGTH = 20 * 1000 * 1000

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') if os.environ.get('DATABASE_URI') else config.get('DATABASE_URI')
    DB_SERVER = os.environ.get('DB_ENGINE') if os.environ.get('DB_ENGINE') else config.get('DB_ENGINE')
    DB_NAME = os.environ.get('DB_NAME') if config.get('DB_NAME') else config.get('DB_NAME')
    DATABASE_PARAM = {
        'postgresql': {
            'host': os.environ.get('DATABASE_HOST') if os.environ.get('DATABASE_HOST') else config.get('DATABASE_HOST'),
            'port': os.environ.get('DATABASE_PORT') if os.environ.get('DATABASE_PORT') else config.get('DATABASE_PORT'),
            'user': os.environ.get('DATABASE_USER') if os.environ.get('DATABASE_USER') else config.get('DATABASE_USER'),
            'password': os.environ.get('DATABASE_PASSWORD') if os.environ.get('DATABASE_PASSWORD') else config.get('DATABASE_PASSWORD')
        }
    }

class LocalConfiguration(Configuration):
    """Contains environmental variables for local configuration"""
    DEBUG = config.get('DEBUG')
    # SERVER_NAME SHOULD NOT BE SET IN LOCAL
    # SERVER_NAME = os.environ.get('SERVER_NAME')
    # SESSION_COOKIE_DOMAIN = os.environ.get('SERVER_NAME')


class DevelopmentConfiguration(Configuration):
    """Contains environment variables for development configuration"""
    DEBUG = True
    # SERVER_NAME = os.environ.get('SERVER_NAME')
    # SESSION_COOKIE_DOMAIN = os.environ.get('SERVER_NAME')


class TestingConfiguration(Configuration):
    """Contains environment variables for staging Configuration"""
    TESTING = True
    DEBUG = True
    # SERVER_NAME SHOULD NOT BE SET IN LOCAL AND TESTING ENV
    # SERVER_NAME = os.environ.get('SERVER_NAME')
    # SESSION_COOKIE_DOMAIN = os.environ.get('SERVER_NAME')


class StagingConfiguration(Configuration):
    """Contains environment variable for staging configuration"""
    # It uses inherited configuration
    # SERVER_NAME = os.environ.get('SERVER_NAME')
    # SESSION_COOKIE_DOMAIN = os.environ.get('SERVER_NAME')


class DemoConfiguration(Configuration):
    """Contains environment variable for demo configuration"""
    # It uses inherited configuration
    # SERVER_NAME SHOULD NOT BE SET IN LOCAL
    # SERVER_NAME = os.environ.get('SERVER_NAME')
    # SESSION_COOKIE_DOMAIN = os.environ.get('SERVER_NAME')


class ProductionConfiguration(Configuration):
    """Contains environment variables for staging configuration"""
    # It uses inherited configuration
    # SERVER_NAME = os.environ.get('SERVER_NAME')
    # SESSION_COOKIE_DOMAIN = os.environ.get('SERVER_NAME')


class APIConfiguration(Configuration):
    """Contains environment variables for staging configuration"""
    # It uses inherited configuration
    # SERVER_NAME = os.environ.get('SERVER_NAME')
    # SESSION_COOKIE_DOMAIN = os.environ.get('SERVER_NAME')


