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

from flask import Flask, request, Blueprint, session, g, flash, render_template, jsonify, current_app, abort, redirect, \
    url_for, make_response
from api.lib import error_handlers, util, worker, database_manager, loggerManager, database_manager

bp = Blueprint("api", __name__)


@bp.errorhandler(error_handlers.InvalidAPIUsage)
def invalid_api_usage(ex):
    return jsonify(ex.to_dict()), ex.status_code


@bp.route('/health', methods=('GET',))
def health_check():
    """
    Health check senza connessione database
    :return: Status dell'API
    """
    output = {
        "status": "ok",
        "message": "MedInsights API is running",
        "version": "1.0.0"
    }
    return jsonify(output)


@bp.route('/test-db', methods=('GET',))
def test_database():
    """
    Test connessione database
    :return: Status delle connessioni
    """
    import os
    
    results = {
        "italy": {"status": "unknown", "error": None},
        "germany": {"status": "unknown", "error": None}
    }
    
    # Test Italia
    try:
        engine, conn, cursor = database_manager.connect_db_for_country('italy')
        results["italy"]["status"] = "connected"
        database_manager.close_db_for_country('italy')
    except Exception as e:
        results["italy"]["status"] = "error"
        results["italy"]["error"] = str(e)
    
    # Test Germania
    try:
        engine, conn, cursor = database_manager.connect_db_for_country('germany')
        results["germany"]["status"] = "connected"
        database_manager.close_db_for_country('germany')
    except Exception as e:
        results["germany"]["status"] = "error"
        results["germany"]["error"] = str(e)
    
    return jsonify({
        "databases": results,
        "config": {
            "italy_host": os.getenv('IT_DB_HOST'),
            "italy_port": os.getenv('IT_DB_PORT'),
            "italy_db": os.getenv('IT_DB_NAME'),
            "germany_host": os.getenv('DE_DB_HOST'),
            "germany_port": os.getenv('DE_DB_PORT'),
            "germany_db": os.getenv('DE_DB_NAME')
        }
    })


@bp.route('/', methods=('GET',))
def index():
    """
    :return: Return information about API
    """
    output = {
        "message": "welcome to medinsight backend",
    }
    return jsonify(output)


@bp.route('/doctors', methods=('GET', 'POST'))
def doctors():
    """
    Get doctors from default database (Italy for backward compatibility)
    :return:
    """
    try:
        request_data = util.process_request(request)
        request_data = dict(request_data)

        # Use Italy database as default
        med_worker = worker.Doctors(request_data, country='italy')
        med_worker.get_doctors()
        
        if not med_worker.returned_doctors:
            error_message = "Could not find doctors"
            loggerManager.logger.warning(error_message)

        output = {
            "doctors": med_worker.doctors_returned or "No doctors found",
            "country": "italy (default)",
            "parameters": request_data
        }
        return jsonify(output)
        
    except Exception as e:
        loggerManager.logger.error(f"Error in doctors endpoint: {e}")
        raise error_handlers.InvalidAPIUsage(
            message=f"Internal server error: {str(e)}", 
            status_code=500
        )


@bp.route('/debug/<country>/doctors', methods=('GET', 'POST'))
def debug_doctors_by_country(country):
    """
    Debug version - Get doctors from country-specific database
    :param country: country identifier (italy, germany)
    :return:
    """
    try:
        # Validate country parameter
        allowed_countries = ['italy', 'germany']
        if country not in allowed_countries:
            return jsonify({
                "error": f"Country '{country}' not supported",
                "allowed_countries": allowed_countries
            }), 400
        
        request_data = util.process_request(request)
        request_data = dict(request_data)
        
        loggerManager.logger.info(f"Debug endpoint - Country: {country}, Data: {request_data}")
        
        # Simple response without database
        output = {
            "status": "success",
            "country": country,
            "parameters": request_data,
            "doctors": [
                {
                    "id": 1,
                    "name": f"Dr. Test {country.title()}",
                    "city": request_data.get('city', 'Default City'),
                    "profession": request_data.get('profession', 'General Doctor')
                }
            ]
        }
        
        return jsonify(output)
        
    except Exception as e:
        loggerManager.logger.error(f"Debug endpoint error: {e}")
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500


@bp.route('/<country>/doctors', methods=('GET', 'POST'))
def doctors_by_country(country):
    """
    Get doctors from country-specific database
    :param country: country identifier (italy, germany)
    :return:
    """
    # Validate country parameter
    allowed_countries = ['italy', 'germany']
    if country not in allowed_countries:
        raise error_handlers.InvalidAPIUsage(
            message=f"Country '{country}' not supported. Allowed countries: {', '.join(allowed_countries)}", 
            status_code=400
        )
    
    # Connect to country-specific database
    try:
        database_manager.connect_db_for_country(country)
    except Exception as e:
        loggerManager.logger.error(f"Database connection error for {country}: {e}")
        raise error_handlers.InvalidAPIUsage(
            message=f"Could not connect to {country} database", 
            status_code=500
        )

    try:
        request_data = util.process_request(request)
        request_data = dict(request_data)

        med_worker = worker.Doctors(request_data, country=country)
        med_worker.get_doctors()
        
        if not med_worker.returned_doctors:
            error_message = "Could not find doctors"
            loggerManager.logger.warning(error_message)
        
        output = {
            "doctors": med_worker.doctors_returned or "No doctors found",
            "country": country,
            "parameters": request_data
        }
        return jsonify(output)
        
    except Exception as e:
        loggerManager.logger.error(f"Error in doctors_by_country: {e}")
        raise error_handlers.InvalidAPIUsage(
            message=f"Internal server error: {str(e)}", 
            status_code=500
        )


@bp.route('/italy/doctors', methods=('GET', 'POST'))
def doctors_italy():
    """
    Get doctors from Italy database
    :return:
    """
    return doctors_by_country('italy')


@bp.route('/germany/doctors', methods=('GET', 'POST'))
def doctors_germany():
    """
    Get doctors from Germany database
    :return:
    """
    return doctors_by_country('germany')