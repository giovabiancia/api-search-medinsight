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
from api.lib import error_handlers, util, worker

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

    :return:
    """
    # Get doctors data
    request_data = util.process_request(request)
    request_data = dict(request_data)

    med_worker = worker.Doctors(request_data)
    med_worker.get_doctors()
    if not med_worker.doctors_returned:
        error_message = "Could not find doctors"
        # flash(error_message, 404)
    doctors_list = med_worker.returned_doctors
    """
    if isinstance(entry_worker.returned_centres, dict):
        centres_list = [entry_worker.returned_centres]
    """

    output = {
        "doctors": "doctors"
    }
    return jsonify(output)









