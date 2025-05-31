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


from markupsafe import escape
from api.lib import util


class DoctorsFilter(object):
    def __init__(self, request_data):
        self.request_data = request_data
        self.doctor_id = self.request_data.get('id')
        self.city = self.request_data.get('city')
        self.profession = self.request_data.get('profession')

        self.validation = []

    def validate(self):
        """Validate inputs"""
        if isinstance(self.city, str):
            self.city = escape(self.city)
            passed_test = validate(self.city, 'str')
            self.validation.append(passed_test)

        if isinstance(self.profession, str):
            self.profession = escape(self.profession)
            passed_test = validate(self.profession, 'str')
            self.validation.append(passed_test)


        if isinstance(self.doctor_id, str):
            self.doctor_id = int(self.doctor_id)
            passed_test = validate(self.doctor_id, 'int')
            self.validation.append(passed_test)

        return self


def validate(input_data, _type):
    # logger_manager.log_to_app(f'Validating Inputs starts')
    validator = util.InputValidator(input_data, _type)
    passed_test = None
    if _type == 'str':
        validator.string_validator()
        passed_test = validator.passed_test
    if _type == 'int':
        validator.int_validator()
        passed_test = validator.passed_test
    if _type == 'float':
        validator.float_validator()
        passed_test = validator.passed_test
    if _type == 'date':
        validator.date_validator()
        passed_test = validator.passed_test
    if _type == 'dict':
        validator.dict_validator()
        passed_test = validator.passed_test

    # if _type == 'list':
    #     validator.list_validator()
    #     passed_test = validator.passed_test

    if _type == 'bool':
        validator.boolean_validator()
        passed_test = validator.passed_test
    # logger_manager.log_to_app(f'Validating Inputs complete')
    return passed_test

