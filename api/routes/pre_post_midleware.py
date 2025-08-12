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
    loggerManager.logger.info("Connecting to default db")
    g.engine, g.conn, g.cursor = database_manager.connect_db()
    g.db_connected = True


@bp.after_app_request
def close_db_if_open(response):
    # Close default database connection
    connected = g.get("db_connected")
    if connected:
        loggerManager.logger.info("Closing default db")
        database_manager.close_db(g.engine, g.conn, g.cursor)
        g.db_connected = False
    
    # Close country-specific database connections
    for country in ['italy', 'germany']:
        if g.get(f"db_connected_{country}"):
            loggerManager.logger.info(f"Closing {country} db")
            database_manager.close_db_for_country(country)
            setattr(g, f'db_connected_{country}', False)
    
    return response