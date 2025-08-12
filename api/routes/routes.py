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
from api.lib import error_handlers, util, worker, database_manager

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
    }
    return jsonify(output)


@bp.route('/doctors', methods=('GET', 'POST'))
def doctors():
    """
    Get doctors from default database (backward compatibility)
    :return:
    """
    request_data = util.process_request(request)
    request_data = dict(request_data)

    med_worker = worker.Doctors(request_data)
    med_worker.get_doctors()
    if not med_worker.doctors_returned:
        error_message = "Could not find doctors"

    output = {
        "doctors": "doctors"
    }
    return jsonify(output)


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
        raise error_handlers.InvalidAPIUsage(
            message=f"Could not connect to {country} database", 
            status_code=500
        )

    request_data = util.process_request(request)
    request_data = dict(request_data)

    med_worker = worker.Doctors(request_data, country=country)
    med_worker.get_doctors()
    if not med_worker.doctors_returned:
        error_message = "Could not find doctors"

    output = {
        "doctors": "doctors"
    }
    return jsonify(output)


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