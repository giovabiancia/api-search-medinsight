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
        enriched_only = request_data.get('enriched_only')
        limit = request_data.get('limit')
        
        # Converti parametri boolean
        if has_slots is not None:
            has_slots = str(has_slots).lower() in ['true', '1', 'yes']
        if allow_questions is not None:
            allow_questions = str(allow_questions).lower() in ['true', '1', 'yes']
      
        if enriched_only is not None:  # NUOVO
            enriched_only = str(enriched_only).lower() in ['true', '1', 'yes']
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
            limit=limit,
            enriched_only=enriched_only,
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
        enriched_only = request_data.get('enriched_only')
        limit = request_data.get('limit')
        
        # Converti parametri boolean
        if has_slots is not None:
            has_slots = str(has_slots).lower() in ['true', '1', 'yes']
        if allow_questions is not None:
            allow_questions = str(allow_questions).lower() in ['true', '1', 'yes']
        if enriched_only is not None:  # NUOVO
            enriched_only = str(enriched_only).lower() in ['true', '1', 'yes']
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
            limit=limit,
            enriched_only=enriched_only,
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

# Aggiungi questi endpoint alla fine di api/routes/enhanced_routes.py

# ====================== GOOGLE PLACES ENDPOINTS ======================

@enhanced_bp.route('/google-places/save', methods=('POST',))
def save_google_place():
    """Salva dati da Google Places API (doctor_id obbligatorio)"""
    if not request.is_json:
        raise error_handlers.InvalidAPIUsage(message="Content-Type must be application/json", status_code=400)
    
    place_data = request.json
    country = validate_country_and_connection(place_data.get('country', 'IT'))
    
    try:
        # Validazione dati essenziali
        if not place_data.get('google_place_id'):
            raise error_handlers.InvalidAPIUsage(message="google_place_id is required", status_code=400)
        
        if not place_data.get('doctor_id'):
            raise error_handlers.InvalidAPIUsage(message="doctor_id is required", status_code=400)
        
        # Salva usando il worker
        med_worker = worker.EnhancedMedicalWorker(country_code=country)
        med_worker.save_google_place_data(place_data)
        
        if med_worker.operation_successful:
            output = {
                "success": True,
                "message": "Google Place data saved successfully",
                "data": med_worker.result_data,
                "country": country
            }
            status_code = 201
        else:
            output = {
                "success": False,
                "message": "Failed to save Google Place data",
                "error": med_worker.result_data,
                "country": country
            }
            status_code = 400
            
    except Exception as e:
        loggerManager.logger.error(f"Error in save_google_place: {e}")
        output = {
            "success": False,
            "message": "Error saving Google Place data",
            "error": str(e),
            "country": country
        }
        status_code = 500
    
    return jsonify(output), status_code


@enhanced_bp.route('/<country>/google-places/save', methods=('POST',))
def save_google_place_by_country(country):
    """Salva dati Google Places per paese specifico"""
    country = validate_country_and_connection(country)
    
    if not request.is_json:
        raise error_handlers.InvalidAPIUsage(message="Content-Type must be application/json", status_code=400)
    
    place_data = request.json
    
    try:
        # Validazione dati essenziali
        if not place_data.get('google_place_id'):
            raise error_handlers.InvalidAPIUsage(message="google_place_id is required", status_code=400)
        
        if not place_data.get('doctor_id'):
            raise error_handlers.InvalidAPIUsage(message="doctor_id is required", status_code=400)
        
        # Salva usando il worker
        med_worker = worker.EnhancedMedicalWorker(country_code=country)
        med_worker.save_google_place_data(place_data)
        
        if med_worker.operation_successful:
            output = {
                "success": True,
                "message": "Google Place data saved successfully",
                "data": med_worker.result_data,
                "country": country
            }
            status_code = 201
        else:
            output = {
                "success": False,
                "message": "Failed to save Google Place data",
                "error": med_worker.result_data,
                "country": country
            }
            status_code = 400
            
    except Exception as e:
        loggerManager.logger.error(f"Error in save_google_place_by_country: {e}")
        output = {
            "success": False,
            "message": "Error saving Google Place data",
            "error": str(e),
            "country": country
        }
        status_code = 500
    
    return jsonify(output), status_code


@enhanced_bp.route('/google-places', methods=('GET',))
def get_google_places():
    """Recupera dati Google Places salvati con informazioni del dottore"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    try:
        google_place_id = request_data.get('google_place_id')
        doctor_id = request_data.get('doctor_id')
        limit = request_data.get('limit')
        
        if doctor_id:
            doctor_id = int(doctor_id)
        if limit:
            limit = int(limit)
        
        # Recupera usando il worker
        med_worker = worker.EnhancedMedicalWorker(country_code=country)
        med_worker.get_google_places_data(
            google_place_id=google_place_id,
            doctor_id=doctor_id,
            limit=limit
        )
        
        output = {
            "items": med_worker.result_data if med_worker.result_data else [],
            "country": country,
            "filters": {
                "google_place_id": google_place_id,
                "doctor_id": doctor_id,
                "limit": limit
            },
            "total": len(med_worker.result_data) if med_worker.result_data else 0
        }
        
    except Exception as e:
        loggerManager.logger.error(f"Error in get_google_places: {e}")
        output = {
            "error": "Error retrieving Google Places data",
            "country": country,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/<country>/google-places', methods=('GET',))
def get_google_places_by_country(country):
    """Recupera dati Google Places per paese specifico"""
    country = validate_country_and_connection(country)
    request_data = util.process_request(request)
    
    try:
        google_place_id = request_data.get('google_place_id')
        doctor_id = request_data.get('doctor_id')
        limit = request_data.get('limit')
        
        if doctor_id:
            doctor_id = int(doctor_id)
        if limit:
            limit = int(limit)
        
        # Recupera usando il worker
        med_worker = worker.EnhancedMedicalWorker(country_code=country)
        med_worker.get_google_places_data(
            google_place_id=google_place_id,
            doctor_id=doctor_id,
            limit=limit
        )
        
        output = {
            "items": med_worker.result_data if med_worker.result_data else [],
            "country": country,
            "filters": {
                "google_place_id": google_place_id,
                "doctor_id": doctor_id,
                "limit": limit
            },
            "total": len(med_worker.result_data) if med_worker.result_data else 0
        }
        
    except Exception as e:
        loggerManager.logger.error(f"Error in get_google_places_by_country: {e}")
        output = {
            "error": "Error retrieving Google Places data",
            "country": country,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/doctors/<int:doctor_id>/google-places', methods=('GET',))
def get_doctor_google_places(doctor_id):
    """Recupera tutti i Google Places di un dottore specifico"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    try:
        limit = request_data.get('limit')
        if limit:
            limit = int(limit)
        
        # Recupera usando il worker
        med_worker = worker.EnhancedMedicalWorker(country_code=country)
        med_worker.get_google_places_data(doctor_id=doctor_id, limit=limit)
        
        output = {
            "items": med_worker.result_data if med_worker.result_data else [],
            "doctor_id": doctor_id,
            "country": country,
            "total": len(med_worker.result_data) if med_worker.result_data else 0
        }
        
    except Exception as e:
        loggerManager.logger.error(f"Error in get_doctor_google_places: {e}")
        output = {
            "error": "Error retrieving doctor Google Places data",
            "doctor_id": doctor_id,
            "country": country,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/<country>/doctors/<int:doctor_id>/google-places', methods=('GET',))
def get_doctor_google_places_by_country(country, doctor_id):
    """Recupera Google Places di un dottore per paese specifico"""
    country = validate_country_and_connection(country)
    request_data = util.process_request(request)
    
    try:
        limit = request_data.get('limit')
        if limit:
            limit = int(limit)
        
        # Recupera usando il worker
        med_worker = worker.EnhancedMedicalWorker(country_code=country)
        med_worker.get_google_places_data(doctor_id=doctor_id, limit=limit)
        
        output = {
            "items": med_worker.result_data if med_worker.result_data else [],
            "doctor_id": doctor_id,
            "country": country,
            "total": len(med_worker.result_data) if med_worker.result_data else 0
        }
        
    except Exception as e:
        loggerManager.logger.error(f"Error in get_doctor_google_places_by_country: {e}")
        output = {
            "error": "Error retrieving doctor Google Places data",
            "doctor_id": doctor_id,
            "country": country,
            "items": []
        }
    
    return jsonify(output)

# STEP 4: Aggiungi questi endpoint alla fine del file api/routes/enhanced_routes.py

# ====================== ENRICHMENT TRACKING ENDPOINTS ======================

@enhanced_bp.route('/enrichment/attempts', methods=('GET',))
def get_enrichment_attempts():
    """Recupera tentativi di arricchimento con filtri"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    try:
        doctor_id = request_data.get('doctor_id')
        status = request_data.get('status')
        limit = request_data.get('limit')
        
        if doctor_id:
            doctor_id = int(doctor_id)
        if limit:
            limit = int(limit)
        
        # Recupera usando il worker
        med_worker = worker.EnhancedMedicalWorker(country_code=country)
        med_worker.get_enrichment_attempts(
            doctor_id=doctor_id,
            status=status,
            limit=limit
        )
        
        output = {
            "items": med_worker.result_data if med_worker.result_data else [],
            "country": country,
            "filters": {
                "doctor_id": doctor_id,
                "status": status,
                "limit": limit
            },
            "total": len(med_worker.result_data) if med_worker.result_data else 0
        }
        
    except Exception as e:
        loggerManager.logger.error(f"Error in get_enrichment_attempts: {e}")
        output = {
            "error": "Error retrieving enrichment attempts",
            "country": country,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/<country>/enrichment/attempts', methods=('GET',))
def get_enrichment_attempts_by_country(country):
    """Recupera tentativi di arricchimento per paese specifico"""
    country = validate_country_and_connection(country)
    request_data = util.process_request(request)
    
    try:
        doctor_id = request_data.get('doctor_id')
        status = request_data.get('status')
        limit = request_data.get('limit')
        
        if doctor_id:
            doctor_id = int(doctor_id)
        if limit:
            limit = int(limit)
        
        # Recupera usando il worker
        med_worker = worker.EnhancedMedicalWorker(country_code=country)
        med_worker.get_enrichment_attempts(
            doctor_id=doctor_id,
            status=status,
            limit=limit
        )
        
        output = {
            "items": med_worker.result_data if med_worker.result_data else [],
            "country": country,
            "filters": {
                "doctor_id": doctor_id,
                "status": status,
                "limit": limit
            },
            "total": len(med_worker.result_data) if med_worker.result_data else 0
        }
        
    except Exception as e:
        loggerManager.logger.error(f"Error in get_enrichment_attempts_by_country: {e}")
        output = {
            "error": "Error retrieving enrichment attempts",
            "country": country,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/<country>/enrichment/status/check', methods=('POST',))
def check_enrichment_status_by_country(country):
    """Controlla stato arricchimento per paese specifico"""
    country = validate_country_and_connection(country)
    
    if not request.is_json:
        raise error_handlers.InvalidAPIUsage(message="Content-Type must be application/json", status_code=400)
    
    data = request.json
    
    try:
        doctor_ids = data.get('doctor_ids', [])
        
        if not doctor_ids or not isinstance(doctor_ids, list):
            raise error_handlers.InvalidAPIUsage(message="doctor_ids must be a non-empty list", status_code=400)
        
        # Converti a interi
        doctor_ids = [int(doc_id) for doc_id in doctor_ids]
        
        # Controlla stato usando il worker
        med_worker = worker.EnhancedMedicalWorker(country_code=country)
        med_worker.check_doctors_enrichment_status(doctor_ids)
        
        # Raggruppa risultati per stato
        status_summary = {}
        for item in med_worker.result_data or []:
            status = item.get('enrichment_status', 'unknown')
            if status not in status_summary:
                status_summary[status] = []
            status_summary[status].append(item['doctor_id'])
        
        output = {
            "doctors_checked": len(doctor_ids),
            "country": country,
            "status_summary": status_summary,
            "details": med_worker.result_data if med_worker.result_data else [],
            "legend": {
                "never_attempted": "Mai tentato arricchimento",
                "enriched": "Arricchimento completato con successo",
                "attempted_failed": "Tentativo fallito (può ritentare)",
                "attempted_unknown": "Stato tentativo sconosciuto"
            }
        }
        
    except Exception as e:
        loggerManager.logger.error(f"Error in check_enrichment_status_by_country: {e}")
        output = {
            "error": "Error checking enrichment status",
            "country": country,
            "doctors_checked": 0,
            "details": []
        }
    
    return jsonify(output)

@enhanced_bp.route('/enrichment/status/check', methods=('POST',))
def check_enrichment_status():
    """Controlla stato arricchimento per lista di dottori"""
    if not request.is_json:
        raise error_handlers.InvalidAPIUsage(message="Content-Type must be application/json", status_code=400)
    
    data = request.json
    country = validate_country_and_connection(data.get('country', 'IT'))
    
    try:
        doctor_ids = data.get('doctor_ids', [])
        
        if not doctor_ids or not isinstance(doctor_ids, list):
            raise error_handlers.InvalidAPIUsage(message="doctor_ids must be a non-empty list", status_code=400)
        
        # Converti a interi
        doctor_ids = [int(doc_id) for doc_id in doctor_ids]
        
        # Controlla stato usando il worker
        med_worker = worker.EnhancedMedicalWorker(country_code=country)
        med_worker.check_doctors_enrichment_status(doctor_ids)
        
        # Raggruppa risultati per stato
        status_summary = {}
        for item in med_worker.result_data or []:
            status = item.get('enrichment_status', 'unknown')
            if status not in status_summary:
                status_summary[status] = []
            status_summary[status].append(item['doctor_id'])
        
        output = {
            "doctors_checked": len(doctor_ids),
            "country": country,
            "status_summary": status_summary,
            "details": med_worker.result_data if med_worker.result_data else [],
            "legend": {
                "never_attempted": "Mai tentato arricchimento",
                "enriched": "Arricchimento completato con successo",
                "attempted_failed": "Tentativo fallito (può ritentare)",
                "attempted_unknown": "Stato tentativo sconosciuto"
            }
        }
        
    except Exception as e:
        loggerManager.logger.error(f"Error in check_enrichment_status_by_country: {e}")
        output = {
            "error": "Error checking enrichment status",
            "country": country,
            "doctors_checked": 0,
            "details": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/enrichment/unenriched', methods=('GET',))
def get_unenriched_doctors():
    """Ottieni dottori non ancora arricchiti"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    try:
        limit = request_data.get('limit')
        exclude_failed = request_data.get('exclude_failed', 'false').lower() in ['true', '1', 'yes']
        
        if limit:
            limit = int(limit)
        
        # Recupera usando il worker
        med_worker = worker.EnhancedMedicalWorker(country_code=country)
        med_worker.get_unenriched_doctors(
            limit=limit,
            exclude_failed=exclude_failed
        )
        
        output = {
            "items": med_worker.result_data if med_worker.result_data else [],
            "country": country,
            "filters": {
                "limit": limit,
                "exclude_failed": exclude_failed
            },
            "total": len(med_worker.result_data) if med_worker.result_data else 0,
            "message": "Dottori che non sono mai stati arricchiti o con tentativi falliti"
        }
        
    except Exception as e:
        loggerManager.logger.error(f"Error in get_unenriched_doctors: {e}")
        output = {
            "error": "Error retrieving unenriched doctors",
            "country": country,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/<country>/enrichment/unenriched', methods=('GET',))
def get_unenriched_doctors_by_country(country):
    """Ottieni dottori non arricchiti per paese specifico"""
    country = validate_country_and_connection(country)
    request_data = util.process_request(request)
    
    try:
        limit = request_data.get('limit')
        exclude_failed = request_data.get('exclude_failed', 'false').lower() in ['true', '1', 'yes']
        
        if limit:
            limit = int(limit)
        
        # Recupera usando il worker
        med_worker = worker.EnhancedMedicalWorker(country_code=country)
        med_worker.get_unenriched_doctors(
            limit=limit,
            exclude_failed=exclude_failed
        )
        
        output = {
            "items": med_worker.result_data if med_worker.result_data else [],
            "country": country,
            "filters": {
                "limit": limit,
                "exclude_failed": exclude_failed
            },
            "total": len(med_worker.result_data) if med_worker.result_data else 0,
            "message": "Dottori che non sono mai stati arricchiti o con tentativi falliti"
        }
        
    except Exception as e:
        loggerManager.logger.error(f"Error in get_unenriched_doctors_by_country: {e}")
        output = {
            "error": "Error retrieving unenriched doctors",
            "country": country,
            "items": []
        }
    
    return jsonify(output)


@enhanced_bp.route('/enrichment/batch-attempts', methods=('POST',))
def save_batch_enrichment_attempts():
    """Salva tentativi di arricchimento in batch"""
    if not request.is_json:
        raise error_handlers.InvalidAPIUsage(message="Content-Type must be application/json", status_code=400)
    
    data = request.json
    country = validate_country_and_connection(data.get('country', 'IT'))
    
    try:
        attempts = data.get('attempts', [])
        
        if not attempts or not isinstance(attempts, list):
            raise error_handlers.InvalidAPIUsage(message="attempts must be a non-empty list", status_code=400)
        
        results = []
        successful = 0
        failed = 0
        
        # Processa ogni tentativo
        for attempt_data in attempts:
            try:
                med_worker = worker.EnhancedMedicalWorker(country_code=country)
                med_worker.save_enrichment_attempt(attempt_data)
                
                if med_worker.operation_successful:
                    successful += 1
                    results.append({
                        "doctor_id": attempt_data.get('doctor_id'),
                        "status": "saved",
                        "data": med_worker.result_data
                    })
                else:
                    failed += 1
                    results.append({
                        "doctor_id": attempt_data.get('doctor_id'),
                        "status": "failed",
                        "error": med_worker.result_data
                    })
                    
            except Exception as e:
                failed += 1
                results.append({
                    "doctor_id": attempt_data.get('doctor_id'),
                    "status": "error",
                    "error": str(e)
                })
        
        output = {
            "success": True,
            "message": f"Batch enrichment attempts processed",
            "summary": {
                "total": len(attempts),
                "successful": successful,
                "failed": failed,
                "success_rate": round((successful / len(attempts)) * 100, 2) if attempts else 0
            },
            "results": results,
            "country": country
        }
        
        status_code = 200 if successful > 0 else 400
        
    except Exception as e:
        loggerManager.logger.error(f"Error in save_batch_enrichment_attempts: {e}")
        output = {
            "success": False,
            "message": "Error processing batch enrichment attempts",
            "error": str(e),
            "country": country
        }
        status_code = 500
    
    return jsonify(output), status_code


@enhanced_bp.route('/<country>/enrichment/batch-attempts', methods=('POST',))
def save_batch_enrichment_attempts_by_country(country):
    """Salva tentativi batch per paese specifico"""
    country = validate_country_and_connection(country)
    
    if not request.is_json:
        raise error_handlers.InvalidAPIUsage(message="Content-Type must be application/json", status_code=400)
    
    data = request.json
    
    try:
        attempts = data.get('attempts', [])
        
        if not attempts or not isinstance(attempts, list):
            raise error_handlers.InvalidAPIUsage(message="attempts must be a non-empty list", status_code=400)
        
        results = []
        successful = 0
        failed = 0
        
        # Processa ogni tentativo
        for attempt_data in attempts:
            try:
                med_worker = worker.EnhancedMedicalWorker(country_code=country)
                med_worker.save_enrichment_attempt(attempt_data)
                
                if med_worker.operation_successful:
                    successful += 1
                    results.append({
                        "doctor_id": attempt_data.get('doctor_id'),
                        "status": "saved",
                        "data": med_worker.result_data
                    })
                else:
                    failed += 1
                    results.append({
                        "doctor_id": attempt_data.get('doctor_id'),
                        "status": "failed",
                        "error": med_worker.result_data
                    })
                    
            except Exception as e:
                failed += 1
                results.append({
                    "doctor_id": attempt_data.get('doctor_id'),
                    "status": "error",
                    "error": str(e)
                })
        
        output = {
            "success": True,
            "message": f"Batch enrichment attempts processed",
            "summary": {
                "total": len(attempts),
                "successful": successful,
                "failed": failed,
                "success_rate": round((successful / len(attempts)) * 100, 2) if attempts else 0
            },
            "results": results,
            "country": country
        }
        
        status_code = 200 if successful > 0 else 400
        
    except Exception as e:
        loggerManager.logger.error(f"Error in save_batch_enrichment_attempts_by_country: {e}")
        output = {
            "success": False,
            "message": "Error processing batch enrichment attempts",
            "error": str(e),
            "country": country
        }
        status_code = 500
    
    return jsonify(output), status_code
       

@enhanced_bp.route('/doctors/<int:doctor_id>/complete', methods=('GET',))
def get_complete_doctor_profile(doctor_id):
    """Ottieni profilo completo di un dottore con TUTTI i dati disponibili"""
    request_data = util.process_request(request)
    country = validate_country_and_connection(request_data.get('country', 'IT'))
    
    try:
        # Usa il worker per ottenere il profilo completo
        med_worker = worker.EnhancedMedicalWorker(country_code=country)
        med_worker.get_complete_doctor_profile(doctor_id)
        
        if med_worker.operation_successful and med_worker.result_data:
            output = {
                "success": True,
                "doctor_id": doctor_id,
                "country": country,
                "profile": med_worker.result_data
            }
            status_code = 200
        else:
            output = {
                "success": False,
                "message": f"Doctor {doctor_id} not found or no data available",
                "doctor_id": doctor_id,
                "country": country,
                "profile": None
            }
            status_code = 404
            
    except Exception as e:
        loggerManager.logger.error(f"Error in get_complete_doctor_profile: {e}")
        output = {
            "success": False,
            "message": "Error retrieving complete doctor profile",
            "error": str(e),
            "doctor_id": doctor_id,
            "country": country,
            "profile": None
        }
        status_code = 500
    
    return jsonify(output), status_code


@enhanced_bp.route('/<country>/doctors/<int:doctor_id>/complete', methods=('GET',))
def get_complete_doctor_profile_by_country(country, doctor_id):
    """Ottieni profilo completo di un dottore per paese specifico"""
    country = validate_country_and_connection(country)
    
    try:
        # Usa il worker per ottenere il profilo completo
        med_worker = worker.EnhancedMedicalWorker(country_code=country)
        med_worker.get_complete_doctor_profile(doctor_id)
        
        if med_worker.operation_successful and med_worker.result_data:
            output = {
                "success": True,
                "doctor_id": doctor_id,
                "country": country,
                "profile": med_worker.result_data
            }
            status_code = 200
        else:
            output = {
                "success": False,
                "message": f"Doctor {doctor_id} not found or no data available",
                "doctor_id": doctor_id,
                "country": country,
                "profile": None
            }
            status_code = 404
            
    except Exception as e:
        loggerManager.logger.error(f"Error in get_complete_doctor_profile_by_country: {e}")
        output = {
            "success": False,
            "message": "Error retrieving complete doctor profile",
            "error": str(e),
            "doctor_id": doctor_id,
            "country": country,
            "profile": None
        }
        status_code = 500
    
    return jsonify(output), status_code

