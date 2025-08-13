#!/bash/bin
# -*- encoding: utf-8 -*-
"""
@author:        Barnabas
@email:         barnabasaugustino@gmail.com
@client:        Barnabas
@gitlab:        https://gitlab.com/projects28/medinsights-be.git
@domain name:
@Hostname:      DigitalOcean
@Description:   Route aggiuntive per MedInsights API
"""

from flask import Flask, request, Blueprint, session, g, flash, render_template, jsonify, current_app, abort, redirect, \
    url_for, make_response
from api.lib import error_handlers, util, worker, loggerManager

# Blueprint per le route aggiuntive
enhanced_bp = Blueprint("enhanced_api", __name__)


@enhanced_bp.errorhandler(error_handlers.InvalidAPIUsage)
def invalid_api_usage(ex):
    return jsonify(ex.to_dict()), ex.status_code


def validate_country_and_connection(country):
    """Valida il paese e controlla la connessione database"""
    country = country.upper()
    if country not in ['DE', 'IT']:
        error_message = "Invalid country. Supported countries: DE, IT"
        raise error_handlers.InvalidAPIUsage(message=error_message, status_code=400)
    
    # Controlla connessione database
    if not g.get('db_connected', False):
        error_message = "Database not available"
        raise error_handlers.InvalidAPIUsage(message=error_message, status_code=503)
    
    # Controlla connessione specifica per paese
    country_cursor_attr = f'cursor_{country.lower()}'
    if not hasattr(g, country_cursor_attr):
        error_message = f"Database for country {country} not available"
        raise error_handlers.InvalidAPIUsage(message=error_message, status_code=503)
    
    return country


# ====================== SPECIALIZATIONS ENDPOINTS ======================

@enhanced_bp.route('/specializations', methods=('GET',))
def get_specializations():
    """Ottieni tutte le specializzazioni"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    # Per ora usiamo la query base specializations - da implementare nel sql_queries.py
    output = {
        "message": "Specializations endpoint - to be implemented",
        "country": country,
        "items": []
    }
    return jsonify(output)


@enhanced_bp.route('/<country>/specializations', methods=('GET',))
def get_specializations_by_country(country):
    """Ottieni specializzazioni per paese specifico"""
    country = validate_country_and_connection(country)
    
    output = {
        "message": "Specializations by country endpoint - to be implemented", 
        "country": country,
        "items": []
    }
    return jsonify(output)


@enhanced_bp.route('/specializations/popular', methods=('GET',))
def get_popular_specializations():
    """Ottieni specializzazioni più popolari"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    limit = int(request_data.get('limit', 10))
    
    output = {
        "message": "Popular specializations endpoint - to be implemented",
        "country": country,
        "limit": limit,
        "items": []
    }
    return jsonify(output)


# ====================== CITIES ENDPOINTS ======================

@enhanced_bp.route('/cities', methods=('GET',))
def get_cities():
    """Ottieni tutte le città con dottori"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    output = {
        "message": "Cities endpoint - to be implemented",
        "country": country,
        "items": []
    }
    return jsonify(output)


@enhanced_bp.route('/<country>/cities', methods=('GET',))
def get_cities_by_country(country):
    """Ottieni città per paese specifico"""
    country = validate_country_and_connection(country)
    
    output = {
        "message": "Cities by country endpoint - to be implemented",
        "country": country,
        "items": []
    }
    return jsonify(output)


# ====================== DOCTORS ADVANCED ENDPOINTS ======================

@enhanced_bp.route('/doctors/search', methods=('GET', 'POST'))
def search_doctors_advanced():
    """Ricerca avanzata dottori"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    # Usa il worker esistente per ora
    med_worker = worker.Doctors(request_data, country_code=country)
    med_worker.get_doctors()
    
    output = {
        "items": med_worker.doctors_returned if med_worker.doctors_returned else [],
        "country": country,
        "filters": {
            "search_term": request_data.get('search_term'),
            "city": request_data.get('city'),
            "profession": request_data.get('profession'),
            "min_rate": request_data.get('min_rate'),
            "max_rate": request_data.get('max_rate'),
            "has_slots": request_data.get('has_slots'),
            "allow_questions": request_data.get('allow_questions')
        },
        "total": len(med_worker.doctors_returned) if med_worker.doctors_returned else 0
    }
    return jsonify(output)


@enhanced_bp.route('/<country>/doctors/search', methods=('GET', 'POST'))
def search_doctors_advanced_by_country(country):
    """Ricerca avanzata dottori per paese"""
    country = validate_country_and_connection(country)
    request_data = util.process_request(request)
    
    # Usa il worker esistente per ora
    med_worker = worker.Doctors(request_data, country_code=country)
    med_worker.get_doctors()
    
    output = {
        "items": med_worker.doctors_returned if med_worker.doctors_returned else [],
        "country": country,
        "filters": {
            "search_term": request_data.get('search_term'),
            "city": request_data.get('city'),
            "profession": request_data.get('profession'),
            "min_rate": request_data.get('min_rate'),
            "max_rate": request_data.get('max_rate'),
            "has_slots": request_data.get('has_slots'),
            "allow_questions": request_data.get('allow_questions')
        },
        "total": len(med_worker.doctors_returned) if med_worker.doctors_returned else 0
    }
    return jsonify(output)


@enhanced_bp.route('/doctors/top-rated', methods=('GET',))
def get_top_rated_doctors():
    """Ottieni dottori con rating più alto"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    limit = int(request_data.get('limit', 20))
    min_rate = int(request_data.get('min_rate', 4))
    
    # Per ora usa il worker esistente con filtro per rating
    med_worker = worker.Doctors(request_data, country_code=country)
    med_worker.get_doctors()
    
    # Filtra per rating se ci sono risultati
    filtered_results = []
    if med_worker.doctors_returned:
        for item in med_worker.doctors_returned:
            if item.get('details', {}).get('rate', 0) >= min_rate:
                filtered_results.append(item)
        # Ordina per rating decrescente e limita
        filtered_results = sorted(filtered_results, 
                                key=lambda x: x.get('details', {}).get('rate', 0), 
                                reverse=True)[:limit]
    
    output = {
        "items": filtered_results,
        "country": country,
        "limit": limit,
        "min_rate": min_rate,
        "total": len(filtered_results)
    }
    return jsonify(output)


@enhanced_bp.route('/<country>/doctors/top-rated', methods=('GET',))
def get_top_rated_doctors_by_country(country):
    """Ottieni dottori top rated per paese"""
    country = validate_country_and_connection(country)
    request_data = util.process_request(request)
    limit = int(request_data.get('limit', 20))
    min_rate = int(request_data.get('min_rate', 4))
    
    # Per ora usa il worker esistente con filtro per rating
    med_worker = worker.Doctors(request_data, country_code=country)
    med_worker.get_doctors()
    
    # Filtra per rating se ci sono risultati
    filtered_results = []
    if med_worker.doctors_returned:
        for item in med_worker.doctors_returned:
            if item.get('details', {}).get('rate', 0) >= min_rate:
                filtered_results.append(item)
        # Ordina per rating decrescente e limita
        filtered_results = sorted(filtered_results, 
                                key=lambda x: x.get('details', {}).get('rate', 0), 
                                reverse=True)[:limit]
    
    output = {
        "items": filtered_results,
        "country": country,
        "limit": limit,
        "min_rate": min_rate,
        "total": len(filtered_results)
    }
    return jsonify(output)


@enhanced_bp.route('/doctors/available', methods=('GET', 'POST'))
def get_doctors_with_slots():
    """Ottieni dottori con slot disponibili"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    # Usa il worker esistente e filtra per has_slots
    med_worker = worker.Doctors(request_data, country_code=country)
    med_worker.get_doctors()
    
    # Filtra per has_slots se ci sono risultati
    filtered_results = []
    if med_worker.doctors_returned:
        for item in med_worker.doctors_returned:
            if item.get('details', {}).get('has_slots', False):
                filtered_results.append(item)
    
    output = {
        "items": filtered_results,
        "country": country,
        "filters": {
            "city": request_data.get('city'),
            "profession": request_data.get('profession')
        },
        "total": len(filtered_results)
    }
    return jsonify(output)


@enhanced_bp.route('/<country>/doctors/available', methods=('GET', 'POST'))
def get_doctors_with_slots_by_country(country):
    """Ottieni dottori con slot per paese"""
    country = validate_country_and_connection(country)
    request_data = util.process_request(request)
    
    # Usa il worker esistente e filtra per has_slots
    med_worker = worker.Doctors(request_data, country_code=country)
    med_worker.get_doctors()
    
    # Filtra per has_slots se ci sono risultati
    filtered_results = []
    if med_worker.doctors_returned:
        for item in med_worker.doctors_returned:
            if item.get('details', {}).get('has_slots', False):
                filtered_results.append(item)
    
    output = {
        "items": filtered_results,
        "country": country,
        "filters": {
            "city": request_data.get('city'),
            "profession": request_data.get('profession')
        },
        "total": len(filtered_results)
    }
    return jsonify(output)


# ====================== PLACEHOLDER ENDPOINTS ======================
# Questi endpoint sono placeholder per funzionalità future

@enhanced_bp.route('/doctors/<int:doctor_id>/opinions', methods=('GET',))
def get_doctor_opinions(doctor_id):
    """Ottieni recensioni per un dottore (placeholder)"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    output = {
        "message": "Doctor opinions endpoint - to be implemented",
        "doctor_id": doctor_id,
        "country": country,
        "items": []
    }
    return jsonify(output)


@enhanced_bp.route('/<country>/doctors/<int:doctor_id>/opinions', methods=('GET',))
def get_doctor_opinions_by_country(country, doctor_id):
    """Ottieni recensioni dottore per paese (placeholder)"""
    country = validate_country_and_connection(country)
    
    output = {
        "message": "Doctor opinions by country endpoint - to be implemented",
        "doctor_id": doctor_id,
        "country": country,
        "items": []
    }
    return jsonify(output)


@enhanced_bp.route('/doctors/<int:doctor_id>/opinion-stats', methods=('GET',))
def get_doctor_opinion_stats(doctor_id):
    """Ottieni statistiche recensioni per un dottore (placeholder)"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    output = {
        "message": "Doctor opinion stats endpoint - to be implemented",
        "doctor_id": doctor_id,
        "country": country,
        "data": {}
    }
    return jsonify(output)


@enhanced_bp.route('/clinics/<int:clinic_id>/telephones', methods=('GET',))
def get_clinic_telephones(clinic_id):
    """Ottieni numeri di telefono per una clinica (placeholder)"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    output = {
        "message": "Clinic telephones endpoint - to be implemented",
        "clinic_id": clinic_id,
        "country": country,
        "items": []
    }
    return jsonify(output)


@enhanced_bp.route('/clinics/<int:clinic_id>/services', methods=('GET',))
def get_clinic_services(clinic_id):
    """Ottieni servizi per una clinica (placeholder)"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    output = {
        "message": "Clinic services endpoint - to be implemented", 
        "clinic_id": clinic_id,
        "country": country,
        "items": []
    }
    return jsonify(output)


@enhanced_bp.route('/stats', methods=('GET',))
def get_database_stats():
    """Ottieni statistiche database (placeholder)"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    output = {
        "message": "Database stats endpoint - to be implemented",
        "country": country,
        "stats": {}
    }
    return jsonify(output)


@enhanced_bp.route('/<country>/stats', methods=('GET',))
def get_database_stats_by_country(country):
    """Ottieni statistiche per paese (placeholder)"""
    country = validate_country_and_connection(country)
    
    output = {
        "message": "Database stats by country endpoint - to be implemented",
        "country": country,
        "stats": {}
    }
    return jsonify(output)


# ====================== INFO ENDPOINTS ======================

@enhanced_bp.route('/info', methods=('GET',))
def api_info():
    """Informazioni complete sull'API"""
    output = {
        "message": "MedInsights API - Enhanced Version",
        "version": "2.0",
        "countries": ["DE", "IT"],
        "endpoints": {
            "doctors": {
                "basic": "/doctors?country=<DE|IT>",
                "by_country": "/<country>/doctors",
                "search": "/doctors/search",
                "top_rated": "/doctors/top-rated",
                "available": "/doctors/available"
            },
            "specializations": {
                "all": "/specializations?country=<DE|IT>",
                "by_country": "/<country>/specializations",
                "popular": "/specializations/popular"
            },
            "cities": {
                "all": "/cities?country=<DE|IT>",
                "by_country": "/<country>/cities"
            },
            "opinions": {
                "doctor_opinions": "/doctors/<doctor_id>/opinions",
                "opinion_stats": "/doctors/<doctor_id>/opinion-stats"
            },
            "clinics": {
                "telephones": "/clinics/<clinic_id>/telephones",
                "services": "/clinics/<clinic_id>/services"
            },
            "stats": {
                "database": "/stats?country=<DE|IT>",
                "by_country": "/<country>/stats"
            },
            "health": {
                "general": "/health",
                "by_country": "/<country>/health"
            }
        },
        "supported_filters": {
            "doctors": ["id", "city", "profession", "search_term", "min_rate", "max_rate", "has_slots", "allow_questions"],
            "specializations": ["limit"],
            "cities": [],
            "top_rated": ["limit", "min_rate"]
        },
        "note": "Some endpoints are placeholders and will be fully implemented in future versions"
    }
    return jsonify(output)