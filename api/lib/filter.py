#!/bash/bin
# -*- encoding: utf-8 -*-
"""
Fix per il filter.py - problema con la validazione
"""

from markupsafe import escape
from api.lib import util, loggerManager


class DoctorsFilter(object):
    def __init__(self, request_data):
        self.request_data = request_data
        self.doctor_id = self.request_data.get('id')
        self.city = self.request_data.get('city')
        self.profession = self.request_data.get('profession')
        self.validation = []

    def validate(self):
        """Validate inputs"""
        loggerManager.logger.debug(f"Validating inputs: {self.request_data}")
        
        try:
            if self.city and isinstance(self.city, str):
                self.city = escape(self.city)
                passed_test = validate(self.city, 'str')
                self.validation.append(passed_test)

            if self.profession and isinstance(self.profession, str):
                self.profession = escape(self.profession)
                passed_test = validate(self.profession, 'str')
                self.validation.append(passed_test)

            if self.doctor_id:
                if isinstance(self.doctor_id, str):
                    self.doctor_id = int(self.doctor_id)
                passed_test = validate(self.doctor_id, 'int')
                self.validation.append(passed_test)
                
            loggerManager.logger.debug(f"Validation completed successfully")
            
        except Exception as e:
            loggerManager.logger.error(f"Validation error: {e}")
            raise e

        return self


def validate(input_data, _type):
    """Simplified validation function"""
    loggerManager.logger.debug(f'Validating input: {input_data}, type: {_type}')
    
    try:
        validator = util.InputValidator(input_data, _type)
        passed_test = None
        
        if _type == 'str':
            validator.string_validator()
            passed_test = True
        elif _type == 'int':
            validator.int_validator()
            passed_test = True
        elif _type == 'float':
            validator.float_validator()
            passed_test = True
        elif _type == 'date':
            validator.date_validator()
            passed_test = validator.passed_test
        elif _type == 'dict':
            validator.dict_validator()
            passed_test = validator.passed_test
        elif _type == 'bool':
            validator.boolean_validator()
            passed_test = validator.passed_test
        else:
            passed_test = True

        loggerManager.logger.debug(f'Validation result: {passed_test}')
        return passed_test
        
    except Exception as e:
        loggerManager.logger.error(f'Validation failed for {input_data}: {e}')
        raise e