#!/bash/bin
# -*- encoding: utf-8 -*-
"""
@author:        Barnabas
@email:         barnabasaugustino@gmail.com
@client:        Barnabas
@gitlab:        https://gitlab.com/projects28/medinsights-be.git
@domain name:
@Hostname:      DigitalOcean
@Description:   Route aggiuntive per MedInsights API - IMPLEMENTATE
"""

from flask import Flask, request, Blueprint, session, g, flash, render_template, jsonify, current_app, abort, redirect, \
    url_for, make_response
from api.lib import error_handlers, util, worker, sql_queries, database_manager, loggerManager

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


def execute_query_for_country(query, country_code):
    """Esegue una query per un paese specifico"""
    try:
        cursor_attr = f'cursor_{country_code.lower()}'
        if hasattr(g, cursor_attr):
            cursor = getattr(g, cursor_attr)
            cursor.execute(query)
            result = cursor.fetchall()
            
            if len(result) == 1:
                return dict(result[0])
            elif len(result) > 1:
                return [dict(record) for record in result]
            else:
                return None
        else:
            raise Exception(f"No database connection available for country: {country_code}")
    except Exception as e:
        loggerManager.logger.error(f"Error executing query for {country_code}: {e}")
        raise e


# ====================== SPECIALIZATIONS ENDPOINTS ======================

@enhanced_bp.route('/specializations', methods=('GET',))
def get_specializations():
    """Ottieni tutte le specializzazioni"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    try:
        query = sql_queries.get_specializations_query(country_code=country)
        result = execute_query_for_country(query, country)
        
        output = {
            "items": result if result else [],
            "country": country,
            "total": len(result) if result else 0
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_specializations: {e}")
        output = {
            "error": "Error retrieving specializations",
            "country": country,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/<country>/specializations', methods=('GET',))
def get_specializations_by_country(country):
    """Ottieni specializzazioni per paese specifico"""
    country = validate_country_and_connection(country)
    
    try:
        query = sql_queries.get_specializations_query(country_code=country)
        result = execute_query_for_country(query, country)
        
        output = {
            "items": result if result else [],
            "country": country,
            "total": len(result) if result else 0
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_specializations_by_country: {e}")
        output = {
            "error": "Error retrieving specializations",
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
    
    try:
        query = sql_queries.get_popular_specializations_query(limit=limit, country_code=country)
        result = execute_query_for_country(query, country)
        
        output = {
            "items": result if result else [],
            "country": country,
            "limit": limit,
            "total": len(result) if result else 0
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_popular_specializations: {e}")
        output = {
            "error": "Error retrieving popular specializations",
            "country": country,
            "limit": limit,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/<country>/specializations/popular', methods=('GET',))
def get_popular_specializations_by_country(country):
    """Ottieni specializzazioni popolari per paese specifico"""
    country = validate_country_and_connection(country)
    request_data = util.process_request(request)
    limit = int(request_data.get('limit', 10))
    
    try:
        query = sql_queries.get_popular_specializations_query(limit=limit, country_code=country)
        result = execute_query_for_country(query, country)
        
        output = {
            "items": result if result else [],
            "country": country,
            "limit": limit,
            "total": len(result) if result else 0
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_popular_specializations_by_country: {e}")
        output = {
            "error": "Error retrieving popular specializations",
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
    
    try:
        query = sql_queries.get_cities_query(country_code=country)
        result = execute_query_for_country(query, country)
        
        output = {
            "items": result if result else [],
            "country": country,
            "total": len(result) if result else 0
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_cities: {e}")
        output = {
            "error": "Error retrieving cities",
            "country": country,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/<country>/cities', methods=('GET',))
def get_cities_by_country(country):
    """Ottieni città per paese specifico"""
    country = validate_country_and_connection(country)
    
    try:
        query = sql_queries.get_cities_query(country_code=country)
        result = execute_query_for_country(query, country)
        
        output = {
            "items": result if result else [],
            "country": country,
            "total": len(result) if result else 0
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_cities_by_country: {e}")
        output = {
            "error": "Error retrieving cities",
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
    
    try:
        # Estrai parametri di ricerca
        search_term = request_data.get('search_term')
        city = request_data.get('city')
        profession = request_data.get('profession')
        min_rate = request_data.get('min_rate')
        max_rate = request_data.get('max_rate')
        has_slots = request_data.get('has_slots')
        allow_questions = request_data.get('allow_questions')
        
        # Converti parametri boolean
        if has_slots is not None:
            has_slots = str(has_slots).lower() in ['true', '1', 'yes']
        if allow_questions is not None:
            allow_questions = str(allow_questions).lower() in ['true', '1', 'yes']
        if min_rate is not None:
            min_rate = int(min_rate)
        if max_rate is not None:
            max_rate = int(max_rate)
        
        query = sql_queries.search_doctors_advanced_query(
            search_term=search_term,
            city=city,
            profession=profession,
            min_rate=min_rate,
            max_rate=max_rate,
            has_slots=has_slots,
            allow_questions=allow_questions,
            country_code=country
        )
        
        raw_data = execute_query_for_country(query, country)
        
        # Trasforma i dati nella struttura API usando il worker esistente
        if raw_data:
            med_worker = worker.Doctors({}, country_code=country)
            transformed_data = med_worker._transform_to_api_structure(raw_data)
        else:
            transformed_data = []
        
        output = {
            "items": transformed_data,
            "country": country,
            "filters": {
                "search_term": search_term,
                "city": city,
                "profession": profession,
                "min_rate": min_rate,
                "max_rate": max_rate,
                "has_slots": has_slots,
                "allow_questions": allow_questions
            },
            "total": len(transformed_data)
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in search_doctors_advanced: {e}")
        output = {
            "error": "Error in advanced search",
            "country": country,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/<country>/doctors/search', methods=('GET', 'POST'))
def search_doctors_advanced_by_country(country):
    """Ricerca avanzata dottori per paese"""
    country = validate_country_and_connection(country)
    request_data = util.process_request(request)
    
    try:
        # Estrai parametri di ricerca
        search_term = request_data.get('search_term')
        city = request_data.get('city')
        profession = request_data.get('profession')
        min_rate = request_data.get('min_rate')
        max_rate = request_data.get('max_rate')
        has_slots = request_data.get('has_slots')
        allow_questions = request_data.get('allow_questions')
        
        # Converti parametri boolean
        if has_slots is not None:
            has_slots = str(has_slots).lower() in ['true', '1', 'yes']
        if allow_questions is not None:
            allow_questions = str(allow_questions).lower() in ['true', '1', 'yes']
        if min_rate is not None:
            min_rate = int(min_rate)
        if max_rate is not None:
            max_rate = int(max_rate)
        
        query = sql_queries.search_doctors_advanced_query(
            search_term=search_term,
            city=city,
            profession=profession,
            min_rate=min_rate,
            max_rate=max_rate,
            has_slots=has_slots,
            allow_questions=allow_questions,
            country_code=country
        )
        
        raw_data = execute_query_for_country(query, country)
        
        # Trasforma i dati nella struttura API
        if raw_data:
            med_worker = worker.Doctors({}, country_code=country)
            transformed_data = med_worker._transform_to_api_structure(raw_data)
        else:
            transformed_data = []
        
        output = {
            "items": transformed_data,
            "country": country,
            "filters": {
                "search_term": search_term,
                "city": city,
                "profession": profession,
                "min_rate": min_rate,
                "max_rate": max_rate,
                "has_slots": has_slots,
                "allow_questions": allow_questions
            },
            "total": len(transformed_data)
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in search_doctors_advanced_by_country: {e}")
        output = {
            "error": "Error in advanced search",
            "country": country,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/doctors/top-rated', methods=('GET',))
def get_top_rated_doctors():
    """Ottieni dottori con rating più alto"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    limit = int(request_data.get('limit', 20))
    min_rate = int(request_data.get('min_rate', 4))
    
    try:
        query = sql_queries.get_top_rated_doctors_query(limit=limit, min_rate=min_rate, country_code=country)
        result = execute_query_for_country(query, country)
        
        output = {
            "items": result if result else [],
            "country": country,
            "limit": limit,
            "min_rate": min_rate,
            "total": len(result) if result else 0
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_top_rated_doctors: {e}")
        output = {
            "error": "Error retrieving top rated doctors",
            "country": country,
            "limit": limit,
            "min_rate": min_rate,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/<country>/doctors/top-rated', methods=('GET',))
def get_top_rated_doctors_by_country(country):
    """Ottieni dottori top rated per paese"""
    country = validate_country_and_connection(country)
    request_data = util.process_request(request)
    limit = int(request_data.get('limit', 20))
    min_rate = int(request_data.get('min_rate', 4))
    
    try:
        query = sql_queries.get_top_rated_doctors_query(limit=limit, min_rate=min_rate, country_code=country)
        result = execute_query_for_country(query, country)
        
        output = {
            "items": result if result else [],
            "country": country,
            "limit": limit,
            "min_rate": min_rate,
            "total": len(result) if result else 0
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_top_rated_doctors_by_country: {e}")
        output = {
            "error": "Error retrieving top rated doctors",
            "country": country,
            "limit": limit,
            "min_rate": min_rate,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/doctors/available', methods=('GET', 'POST'))
def get_doctors_with_slots():
    """Ottieni dottori con slot disponibili"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    try:
        city = request_data.get('city')
        profession = request_data.get('profession')
        
        query = sql_queries.get_doctors_with_slots_query(
            city=city,
            profession=profession,
            country_code=country
        )
        
        raw_data = execute_query_for_country(query, country)
        
        # Trasforma i dati nella struttura API
        if raw_data:
            med_worker = worker.Doctors({}, country_code=country)
            transformed_data = med_worker._transform_to_api_structure(raw_data)
        else:
            transformed_data = []
        
        output = {
            "items": transformed_data,
            "country": country,
            "filters": {
                "city": city,
                "profession": profession
            },
            "total": len(transformed_data)
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_doctors_with_slots: {e}")
        output = {
            "error": "Error retrieving doctors with available slots",
            "country": country,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/<country>/doctors/available', methods=('GET', 'POST'))
def get_doctors_with_slots_by_country(country):
    """Ottieni dottori con slot per paese"""
    country = validate_country_and_connection(country)
    request_data = util.process_request(request)
    
    try:
        city = request_data.get('city')
        profession = request_data.get('profession')
        
        query = sql_queries.get_doctors_with_slots_query(
            city=city,
            profession=profession,
            country_code=country
        )
        
        raw_data = execute_query_for_country(query, country)
        
        # Trasforma i dati nella struttura API
        if raw_data:
            med_worker = worker.Doctors({}, country_code=country)
            transformed_data = med_worker._transform_to_api_structure(raw_data)
        else:
            transformed_data = []
        
        output = {
            "items": transformed_data,
            "country": country,
            "filters": {
                "city": city,
                "profession": profession
            },
            "total": len(transformed_data)
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_doctors_with_slots_by_country: {e}")
        output = {
            "error": "Error retrieving doctors with available slots",
            "country": country,
            "items": []
        }
    
    return jsonify(output)


# ====================== OPINIONS ENDPOINTS ======================

@enhanced_bp.route('/doctors/<int:doctor_id>/opinions', methods=('GET',))
def get_doctor_opinions(doctor_id):
    """Ottieni recensioni per un dottore"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    try:
        query = sql_queries.get_doctor_opinions_query(doctor_id, country_code=country)
        result = execute_query_for_country(query, country)
        
        output = {
            "items": result if result else [],
            "doctor_id": doctor_id,
            "country": country,
            "total": len(result) if result else 0
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_doctor_opinions: {e}")
        output = {
            "error": "Error retrieving doctor opinions",
            "doctor_id": doctor_id,
            "country": country,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/<country>/doctors/<int:doctor_id>/opinions', methods=('GET',))
def get_doctor_opinions_by_country(country, doctor_id):
    """Ottieni recensioni dottore per paese"""
    country = validate_country_and_connection(country)
    
    try:
        query = sql_queries.get_doctor_opinions_query(doctor_id, country_code=country)
        result = execute_query_for_country(query, country)
        
        output = {
            "items": result if result else [],
            "doctor_id": doctor_id,
            "country": country,
            "total": len(result) if result else 0
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_doctor_opinions_by_country: {e}")
        output = {
            "error": "Error retrieving doctor opinions",
            "doctor_id": doctor_id,
            "country": country,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/doctors/<int:doctor_id>/opinion-stats', methods=('GET',))
def get_doctor_opinion_stats(doctor_id):
    """Ottieni statistiche recensioni per un dottore"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    try:
        query = sql_queries.get_doctor_opinion_stats_query(doctor_id, country_code=country)
        result = execute_query_for_country(query, country)
        
        output = {
            "data": result if result else {},
            "doctor_id": doctor_id,
            "country": country
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_doctor_opinion_stats: {e}")
        output = {
            "error": "Error retrieving doctor opinion stats",
            "doctor_id": doctor_id,
            "country": country,
            "data": {}
        }
    
    return jsonify(output)


@enhanced_bp.route('/<country>/doctors/<int:doctor_id>/opinion-stats', methods=('GET',))
def get_doctor_opinion_stats_by_country(country, doctor_id):
    """Ottieni statistiche recensioni dottore per paese"""
    country = validate_country_and_connection(country)
    
    try:
        query = sql_queries.get_doctor_opinion_stats_query(doctor_id, country_code=country)
        result = execute_query_for_country(query, country)
        
        output = {
            "data": result if result else {},
            "doctor_id": doctor_id,
            "country": country
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_doctor_opinion_stats_by_country: {e}")
        output = {
            "error": "Error retrieving doctor opinion stats",
            "doctor_id": doctor_id,
            "country": country,
            "data": {}
        }
    
    return jsonify(output)


# ====================== CLINICS ENDPOINTS ======================

@enhanced_bp.route('/clinics/<int:clinic_id>/telephones', methods=('GET',))
def get_clinic_telephones(clinic_id):
    """Ottieni numeri di telefono per una clinica"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    try:
        query = sql_queries.get_clinic_telephones_query(clinic_id, country_code=country)
        result = execute_query_for_country(query, country)
        
        output = {
            "items": result if result else [],
            "clinic_id": clinic_id,
            "country": country,
            "total": len(result) if result else 0
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_clinic_telephones: {e}")
        output = {
            "error": "Error retrieving clinic telephones",
            "clinic_id": clinic_id,
            "country": country,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/<country>/clinics/<int:clinic_id>/telephones', methods=('GET',))
def get_clinic_telephones_by_country(country, clinic_id):
    """Ottieni telefoni clinica per paese"""
    country = validate_country_and_connection(country)
    
    try:
        query = sql_queries.get_clinic_telephones_query(clinic_id, country_code=country)
        result = execute_query_for_country(query, country)
        
        output = {
            "items": result if result else [],
            "clinic_id": clinic_id,
            "country": country,
            "total": len(result) if result else 0
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_clinic_telephones_by_country: {e}")
        output = {
            "error": "Error retrieving clinic telephones",
            "clinic_id": clinic_id,
            "country": country,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/clinics/<int:clinic_id>/services', methods=('GET',))
def get_clinic_services(clinic_id):
    """Ottieni servizi per una clinica"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    try:
        query = sql_queries.get_clinic_services_query(clinic_id, country_code=country)
        result = execute_query_for_country(query, country)
        
        output = {
            "items": result if result else [],
            "clinic_id": clinic_id,
            "country": country,
            "total": len(result) if result else 0
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_clinic_services: {e}")
        output = {
            "error": "Error retrieving clinic services",
            "clinic_id": clinic_id,
            "country": country,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/<country>/clinics/<int:clinic_id>/services', methods=('GET',))
def get_clinic_services_by_country(country, clinic_id):
    """Ottieni servizi clinica per paese"""
    country = validate_country_and_connection(country)
    
    try:
        query = sql_queries.get_clinic_services_query(clinic_id, country_code=country)
        result = execute_query_for_country(query, country)
        
        output = {
            "items": result if result else [],
            "clinic_id": clinic_id,
            "country": country,
            "total": len(result) if result else 0
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_clinic_services_by_country: {e}")
        output = {
            "error": "Error retrieving clinic services",
            "clinic_id": clinic_id,
            "country": country,
            "items": []
        }
    
    return jsonify(output)


# ====================== STATISTICS ENDPOINTS ======================

@enhanced_bp.route('/stats', methods=('GET',))
def get_database_stats():
    """Ottieni statistiche database"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    try:
        query = sql_queries.get_database_stats_query(country_code=country)
        result = execute_query_for_country(query, country)
        
        # Trasforma array di stats in dizionario
        stats_dict = {}
        if result:
            for stat in result:
                stats_dict[stat['table_name']] = stat['total_count']
        
        output = {
            "stats": stats_dict,
            "country": country,
            "raw_data": result if result else []
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_database_stats: {e}")
        output = {
            "error": "Error retrieving database stats",
            "country": country,
            "stats": {},
            "raw_data": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/<country>/stats', methods=('GET',))
def get_database_stats_by_country(country):
    """Ottieni statistiche per paese"""
    country = validate_country_and_connection(country)
    
    try:
        query = sql_queries.get_database_stats_query(country_code=country)
        result = execute_query_for_country(query, country)
        
        # Trasforma array di stats in dizionario
        stats_dict = {}
        if result:
            for stat in result:
                stats_dict[stat['table_name']] = stat['total_count']
        
        output = {
            "stats": stats_dict,
            "country": country,
            "raw_data": result if result else []
        }
    except Exception as e:
        loggerManager.logger.error(f"Error in get_database_stats_by_country: {e}")
        output = {
            "error": "Error retrieving database stats",
            "country": country,
            "stats": {},
            "raw_data": []
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
        "status": "All endpoints implemented",
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
                "doctor_opinions": "/doctors/<doctor_id>/opinions?country=<DE|IT>",
                "doctor_opinions_by_country": "/<country>/doctors/<doctor_id>/opinions",
                "opinion_stats": "/doctors/<doctor_id>/opinion-stats?country=<DE|IT>",
                "opinion_stats_by_country": "/<country>/doctors/<doctor_id>/opinion-stats"
            },
            "clinics": {
                "telephones": "/clinics/<clinic_id>/telephones?country=<DE|IT>",
                "telephones_by_country": "/<country>/clinics/<clinic_id>/telephones",
                "services": "/clinics/<clinic_id>/services?country=<DE|IT>",
                "services_by_country": "/<country>/clinics/<clinic_id>/services"
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
            "top_rated": ["limit", "min_rate"],
            "available": ["city", "profession"],
            "advanced_search": ["search_term", "city", "profession", "min_rate", "max_rate", "has_slots", "allow_questions"]
        },
        "examples": {
            "basic_doctors": "/doctors?country=IT&city=Roma",
            "advanced_search": "/doctors/search?country=DE&search_term=Schmidt&min_rate=4",
            "top_rated": "/doctors/top-rated?country=IT&limit=10&min_rate=4",
            "specializations": "/specializations/popular?country=DE&limit=5",
            "cities": "/cities?country=IT",
            "opinions": "/doctors/123/opinions?country=IT",
            "stats": "/stats?country=DE"
        },
        "note": "All endpoints are now fully implemented with proper database queries"
    }
    return jsonify(output)