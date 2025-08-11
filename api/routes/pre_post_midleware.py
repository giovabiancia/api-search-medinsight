#!/bash/bin
# -*- encoding: utf-8 -*-
"""
@author:        Barnabas
@email:         barnabasaugustino@gmail.com
@client:        Barnabas
@gitlab:        https://gitlab.com/projects28/medinsights-be.git
@domain name:
@Hostname:      DigitalOcean
@Description:   Middleware semplificato
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
    loggerManager.logger.info(f'url_rule: {request.url_rule} ')
    loggerManager.logger.info(f'args: {request.args} ')
    loggerManager.logger.info(f'remote_addr: {request.remote_addr}')

@bp.after_app_request
def print_info_after(response):
    loggerManager.logger.info("---------------- Request end---------------------")
    return response

def get_country_from_request():
    """Estrae il paese dalla richiesta"""
    # Controlla parametri URL
    country = request.args.get('country')
    if country:
        return country.upper()
    
    # Controlla JSON
    if request.is_json and request.json:
        country = request.json.get('country')
        if country:
            return country.upper()
    
    # Controlla form
    if request.form:
        country = request.form.get('country')
        if country:
            return country.upper()
    
    # Default Italia
    return 'IT'

@bp.before_app_request
def connect_to_db():
    """Connette al database giusto in base al paese"""
    try:
        # Ottieni paese dalla richiesta
        country = get_country_from_request()
        
        # Valida paese (solo DE o IT)
        if country not in ['DE', 'IT']:
            country = 'IT'  # Default
        
        g.country = country
        
        # Connetti al database del paese
        g.engine, g.conn, g.cursor = database_manager.connect_db(country)
        g.db_connected = True
        
        loggerManager.logger.info(f"Connesso al database: {country}")
        
    except Exception as e:
        loggerManager.logger.error(f"Errore connessione database: {e}")
        g.db_connected = False

@bp.after_app_request
def close_db_if_open(response):
    """Chiude connessione database"""
    if g.get("db_connected"):
        database_manager.close_db(g.engine, g.conn, g.cursor)
        g.db_connected = False
        loggerManager.logger.info("Database disconnesso")
    return response