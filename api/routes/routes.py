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
from api.lib import error_handlers, util, worker, loggerManager

bp = Blueprint("api", __name__)


@bp.errorhandler(error_handlers.InvalidAPIUsage)
def invalid_api_usage(ex):
    return jsonify(ex.to_dict()), ex.status_code


@bp.route('/', methods=('GET',))
def index():
    """
    :return: Return information about API
    """
    output = {
        "message": "welcome to medinsight backend",
        "countries": ["DE", "IT"],
        "endpoints": {
            "doctors": "/doctors?country=<DE|IT>",
            "doctors_de": "/de/doctors",
            "doctors_it": "/it/doctors"
        }
    }
    return jsonify(output)


@bp.route('/doctors', methods=('GET', 'POST'))
def doctors():
    """
    Get doctors with optional country parameter
    :return: JSON response with doctors data matching original API structure
    """
    # Get request data
    request_data = util.process_request(request)
    request_data = dict(request_data)
    
    # Get country parameter (default to IT for backward compatibility)
    country = request_data.get('country', 'IT').upper()
    
    # Validate country
    if country not in ['DE', 'IT']:
        error_message = "Invalid country. Supported countries: DE, IT"
        raise error_handlers.InvalidAPIUsage(message=error_message, status_code=400)
    
    # Check if we have database connections
    if not g.get('db_connected', False):
        error_message = "Database not available"
        raise error_handlers.InvalidAPIUsage(message=error_message, status_code=503)
    
    # Check if specific country database is available
    country_cursor_attr = f'cursor_{country.lower()}'
    if not hasattr(g, country_cursor_attr):
        error_message = f"Database for country {country} not available"
        raise error_handlers.InvalidAPIUsage(message=error_message, status_code=503)
    
    # Get doctors data
    med_worker = worker.Doctors(request_data, country_code=country)
    med_worker.get_doctors()
    
    if not med_worker.returned_doctors:
        loggerManager.logger.warning("Could not find doctors")
        
    # Return response in original API format
    output = {
        "items": med_worker.doctors_returned if med_worker.doctors_returned else []
    }
    return jsonify(output)


@bp.route('/<country>/doctors', methods=('GET', 'POST'))
def doctors_by_country(country):
    """
    Get doctors for specific country via URL path
    :param country: Country code (de, it)
    :return: JSON response with doctors data matching original API structure
    """
    # Validate and normalize country
    country = country.upper()
    if country not in ['DE', 'IT']:
        error_message = "Invalid country. Supported countries: DE, IT"
        raise error_handlers.InvalidAPIUsage(message=error_message, status_code=404)
    
    # Check if we have database connections
    if not g.get('db_connected', False):
        error_message = "Database not available"
        raise error_handlers.InvalidAPIUsage(message=error_message, status_code=503)
    
    # Check if specific country database is available
    country_cursor_attr = f'cursor_{country.lower()}'
    if not hasattr(g, country_cursor_attr):
        error_message = f"Database for country {country} not available"
        raise error_handlers.InvalidAPIUsage(message=error_message, status_code=503)
    
    # Get request data
    request_data = util.process_request(request)
    request_data = dict(request_data)
    
    # Get doctors data
    med_worker = worker.Doctors(request_data, country_code=country)
    med_worker.get_doctors()
    
    if not med_worker.returned_doctors:
        loggerManager.logger.warning("Could not find doctors")
        
    # Return response in original API format
    output = {
        "items": med_worker.doctors_returned if med_worker.doctors_returned else []
    }
    return jsonify(output)


# Country-specific endpoints for backward compatibility and ease of use
@bp.route('/de/doctors', methods=('GET', 'POST'))
def doctors_germany():
    """Get doctors from Germany database"""
    return doctors_by_country('DE')


@bp.route('/it/doctors', methods=('GET', 'POST'))
def doctors_italy():
    """Get doctors from Italy database"""
    return doctors_by_country('IT')


# Health check endpoints for each country
@bp.route('/health', methods=('GET',))
def health_check():
    """General health check"""
    try:
        output = {
            "status": "healthy",
            "countries": {
                "DE": bool(hasattr(g, 'engine_de') and g.engine_de),
                "IT": bool(hasattr(g, 'engine_it') and g.engine_it)
            }
        }
        return jsonify(output)
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


@bp.route('/<country>/health', methods=('GET',))
def health_check_country(country):
    """Health check for specific country"""
    country = country.upper()
    if country not in ['DE', 'IT']:
        return jsonify({"status": "error", "message": "Invalid country"}), 404
    
    try:
        engine_attr = f'engine_{country.lower()}'
        is_connected = bool(hasattr(g, engine_attr) and getattr(g, engine_attr))
        
        output = {
            "status": "healthy" if is_connected else "disconnected",
            "country": country,
            "database_connected": is_connected
        }
        return jsonify(output)
    except Exception as e:
        return jsonify({"status": "unhealthy", "country": country, "error": str(e)}), 500