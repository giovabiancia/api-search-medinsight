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

from flask import Flask, request, Blueprint, session, g, flash, render_template, jsonify, current_app
from api.lib import database_manager, error_handlers, loggerManager
from datetime import datetime

bp = Blueprint("pre_post", __name__)


@bp.errorhandler(error_handlers.InvalidAPIUsage)
def invalid_api_usage(ex):
    return jsonify(ex.to_dict()), ex.status_code


@bp.before_app_request
def print_info_before():
    loggerManager.logger.info("---------------- Request start---------------------")
    loggerManager.logger.info(f'Start time {datetime.now()}')
    loggerManager.logger.info(f'url_rule: {request.url_rule} ')
    loggerManager.logger.debug(f'headers: {request.headers}')
    loggerManager.logger.info(f'args: {request.args} ')
    loggerManager.logger.debug(f'content_length {request.content_length} ')
    loggerManager.logger.info(f'query_string: {request.query_string}')
    loggerManager.logger.info(f'remote_addr: {request.remote_addr}')
    loggerManager.logger.debug(f'scheme: {request.scheme}')
    loggerManager.logger.debug(f"-------------------------------------")
    loggerManager.logger.debug(f"Browser: {request.environ.get('HTTP_SEC_CH_UA')} ")
    loggerManager.logger.debug(f"Mobile: {request.environ.get('HTTP_SEC_CH_UA_MOBILE')}")
    loggerManager.logger.debug(f"Platform: {request.environ.get('HTTP_SEC_CH_UA_PLATFORM')}")
    loggerManager.logger.debug(f"Language: {request.environ.get('HTTP_ACCEPT_LANGUAGE')}")
    loggerManager.logger.info(f"-------------------------------------")


@bp.after_app_request
def print_info_after(response):
    loggerManager.logger.info("---------------- Request end---------------------")
    return response


@bp.before_app_request
def connect_to_db():
    """Connect to all country databases"""
    loggerManager.logger.info("Connecting to databases")
    
    # Try to connect to all country databases
    connections = database_manager.connect_all_country_dbs()
    
    # Store connections in Flask's g object
    for country, conn_data in connections.items():
        setattr(g, f'engine_{country}', conn_data['engine'])
        setattr(g, f'conn_{country}', conn_data['conn'])
        setattr(g, f'cursor_{country}', conn_data['cursor'])
        loggerManager.logger.info(f"Connected to {country} database")
    
    # Set default connection (first available)
    if connections:
        first_country = list(connections.keys())[0]
        g.engine = getattr(g, f'engine_{first_country}')
        g.conn = getattr(g, f'conn_{first_country}')
        g.cursor = getattr(g, f'cursor_{first_country}')
        loggerManager.logger.info(f"Set default connection to: {first_country}")
    else:
        # No country databases available - this is OK, will handle in routes
        loggerManager.logger.warning("No country databases configured or available")
        g.engine = None
        g.conn = None
        g.cursor = None
    
    g.db_connected = bool(connections)


@bp.after_app_request
def close_db_if_open(response):
    """Close all database connections"""
    connected = g.get("db_connected")
    if connected:
        loggerManager.logger.info("Closing databases")
        database_manager.close_all_db_connections()
    return response