#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author:        Barnabas
@email:         barnabasaugustino@gmail.com
@client:        Barnabas
@gitlab:        https://gitlab.com/projects28/medinsights-be.git
@domain name:
@Hostname:      DigitalOcean
@Description:
"""

from flask import Flask, request, g, render_template_string
from flask_cors import CORS
import os
from api.lib import config_manager, database_manager, loggerManager


def create_app(test_config=None):
    """This function creates and returns app instance"""
    app = Flask(__name__, instance_relative_config=True, static_folder='base/static')
    CORS(app, supports_credentials=True)

    # Load configuration
    app = load_configuration(app)


    # Database
    database_manager.init_app(app=app)

    # Create instance folder
    app = create_instance_directory(app)


    # Register Blueprints
    app = register_blueprints(app)

    return app


def load_configuration(app=None):
    """returns configured app instance"""
    env = os.environ.get('ENV')
    if env == 'TESTING':
        # Load test configuration
        app.config.from_object(config_manager.TestingConfiguration)
    elif env == 'DEVELOPMENT':
        # Load development configuration
        app.config.from_object(config_manager.DevelopmentConfiguration)
    elif env == 'STAGING':
        # Load staging configuration
        app.config.from_object(config_manager.StagingConfiguration)

    elif env == 'DEMO':
        # Load development configuration
        app.config.from_object(config_manager.DemoConfiguration)

    elif env == 'PRODUCTION':
        # Load production environment
        app.config.from_object(config_manager.ProductionConfiguration)

    elif env == 'API':
        # Load development configuration
        app.config.from_object(config_manager.APIConfiguration)

    else:  # local
        # Load local configuration
        app.config.from_object(config_manager.LocalConfiguration)

    return app


def create_instance_directory(app=None):
    """Create instance folder if it does not exist"""
    path = os.path.join(app.instance_path)
    app = create_directory(app, path)
    return app


def register_blueprints(app=None):
    """Register blueprints to application instance"""
    # Register base blueprints (required for static directory)
    from .base import routes
    app.register_blueprint(routes.bp)

    # Register routes
    from .routes import pre_post_midleware, routes
    app.register_blueprint(pre_post_midleware.bp)
    app.register_blueprint(routes.bp)

    # Define the rule
    app.add_url_rule('/', endpoint='index')

    return app


def create_directory(app=None, path=None):
    """Creates instance directory"""
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as e:
        loggerManager.logger.warn(f"Could not create an instance directory")
    return app



