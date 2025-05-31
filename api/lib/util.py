#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author:        barnabas
@email:         barnabasaugustino@gmail.com
@github:        https://gitlab.com/barnabasaugustino/entry_requirements.git
@Domain name
@Hostname
@Description:   This document contains database utilities for entry_requirements project
"""
import os
from flask import current_app, g
from api.lib import error_handlers, loggerManager
from datetime import datetime
import json
import jwt


class InputValidator(object):
    def __init__(self, input_data=None, _type=None):
        """This object is responsible for all input validations"""
        self.input_data = input_data
        self._type = _type
        self.passed_test = False

    def string_validator(self):
        try:
            self.input_data.strip()
        except Exception as e:
            access_error = f'Invalid input, {self.input_data} is not a string: {e}'
            # logger_manager.log_to_app(msg=access_error, level='error')
            raise error_handlers.InvalidAPIUsage(message=access_error, status_code=400)
        return self

    def int_validator(self):
        try:
            int(self.input_data)
        except Exception as e:
            access_error = f'Invalid input, {self.input_data} is not a integer: {e}'
            # logger_manager.log_to_app(msg=access_error, level='error')
            raise error_handlers.InvalidAPIUsage(message=access_error, status_code=400)
        return self

    def float_validator(self):
        try:
            float(self.input_data)
        except Exception as e:
            access_error = f'Invalid input, {self.input_data} is not a float: {e}'
            # logger_manager.log_to_app(msg=access_error, level='error')
            raise error_handlers.InvalidAPIUsage(message=access_error, status_code=400)

        return self

    def date_validator(self):
        try:
            datetime.fromisoformat(self.input_data)
            self.passed_test = True
        except Exception as e:
            access_error = f'Invalid input, {self.input_data} is not a date'
            # logger_manager.log_to_app(msg=access_error, level='error')
            raise error_handlers.InvalidAPIUsage(message=access_error, status_code=400)
        return self

    def dict_validator(self):
        try:
            self.input_data.get('value')
            self.passed_test = True
        except Exception as e:
            access_error = f'Invalid input, {self.input_data} is not a dictionary'
            # logger_manager.log_to_app(msg=access_error, level='error')
            raise error_handlers.InvalidAPIUsage(message=access_error, status_code=400)
        return self

    def boolean_validator(self):
        try:
            if int(self.input_data) in [0, 1]:
                self.passed_test = True
        except Exception as e:
            access_error = f'Invalid input, {self.input_data} is not a dictionary'
            # logger_manager.log_to_app(msg=access_error, level='error')
            raise error_handlers.InvalidAPIUsage(message=access_error, status_code=400)
        return self

    def range_validator(self):
        return self

    def file_type_validator(self):
        return self

    def memory_validator(self):
        return self

def process_request(request):
    if request.is_json:
        request_data = request.json
    else:
        request_data = request.form

    if not bool(request_data):
        request_data = request.args
    return request_data
