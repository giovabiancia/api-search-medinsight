#!/bash/bin
# -*- encoding: utf-8 -*-
"""
@author:        Barnabas
@email:         barnabasaugustino@gmail.com
@client:        Barnabas
@gitlab:        https://gitlab.com/projects28/medinsights-be.git
@domain name:
@Hostname:      DigitalOcean
@Description:   Route semplificate con supporto multi-paese
"""

from flask import Flask, request, Blueprint, session, g, flash, render_template, jsonify, current_app, abort
from api.lib import error_handlers, util, worker

bp = Blueprint("api", __name__)

@bp.errorhandler(error_handlers.InvalidAPIUsage)
def invalid_api_usage(ex):
    return jsonify(ex.to_dict()), ex.status_code

@bp.route('/', methods=('GET',))
def index():
    """Informazioni API"""
    output = {
        "message": "MedInsight Backend API",
        "version": "2.0.0",
        "current_country": getattr(g, 'country', 'IT'),
        "supported_countries": ["DE", "IT"],
        "endpoints": {
            "/doctors": "Get doctors (country from parameter)",
            "/de/doctors": "Get doctors from Germany",
            "/it/doctors": "Get doctors from Italy"
        }
    }
    return jsonify(output)

@bp.route('/doctors', methods=('GET', 'POST'))
def doctors():
    """Ottieni dottori dal database del paese corrente"""
    country = getattr(g, 'country', 'IT')
    return get_doctors_data(country)

@bp.route('/de/doctors', methods=('GET', 'POST'))
def doctors_de():
    """Ottieni dottori dalla Germania"""
    return get_doctors_data('DE')

@bp.route('/it/doctors', methods=('GET', 'POST'))
def doctors_it():
    """Ottieni dottori dall'Italia"""
    return get_doctors_data('IT')

def get_doctors_data(country):
    """Funzione per ottenere dati dottori"""
    try:
        # Connetti al database del paese se necessario
        if getattr(g, 'country', None) != country:
            # Riconnetti al database giusto
            if g.get("db_connected"):
                from api.lib import database_manager
                database_manager.close_db(g.engine, g.conn, g.cursor)
            
            g.engine, g.conn, g.cursor = database_manager.connect_db(country)
            g.country = country
            g.db_connected = True
        
        # Ottieni parametri richiesta
        request_data = util.process_request(request)
        request_data = dict(request_data)
        
        # Crea worker
        med_worker = worker.Doctors(request_data)
        med_worker.get_doctors()
        
        if not med_worker.returned_doctors:
            output = {
                "message": f"Nessun dottore trovato in {country}",
                "country": country,
                "doctors": [],
                "total": 0
            }
            return jsonify(output), 404
        
        # Prepara risposta
        doctors_list = med_worker.doctors_returned
        if isinstance(doctors_list, dict):
            doctors_list = [doctors_list]
        
        output = {
            "success": True,
            "country": country,
            "doctors": doctors_list or [],
            "total": len(doctors_list) if doctors_list else 0,
            "filters": {
                "id": request_data.get('id'),
                "city": request_data.get('city'),
                "profession": request_data.get('profession')
            }
        }
        return jsonify(output)
        
    except Exception as e:
        loggerManager.logger.error(f"Errore ottenimento dottori {country}: {e}")
        output = {
            "error": "Errore server",
            "country": country,
            "message": "Impossibile ottenere informazioni dottori"
        }
        return jsonify(output), 500

@bp.route('/health', methods=('GET',))
def health():
    """Health check"""
    try:
        # Test connessione database corrente
        g.cursor.execute("SELECT 1")
        result = g.cursor.fetchone()
        
        output = {
            "status": "ok",
            "country": getattr(g, 'country', 'IT'),
            "database": "connected" if result else "error"
        }
        return jsonify(output)
    except Exception as e:
        output = {
            "status": "error",
            "message": str(e)
        }
        return jsonify(output), 500