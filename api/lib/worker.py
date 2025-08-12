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

from flask import g
from api.lib import filter, database_manager, sql_queries, loggerManager
from collections import defaultdict


class Doctors(filter.DoctorsFilter, database_manager.ExecuteQueries):
    def __init__(self, request_data, country_code='IT'):
        super().__init__(request_data)
        self.request_data = request_data
        self.country_code = country_code.upper()
        self.doctors_returned = None
        self.returned_doctors = False

    def get_doctors(self):
        """
        Returns doctors from specific country database
        :return:
        """
        loggerManager.logger.debug(f"Getting doctors start for country: {self.country_code}")
        self.validate()
        
        # Get query
        if self.doctor_id:
            query = sql_queries.get_doctors_query(doctor_id=self.doctor_id, country_code=self.country_code)
        elif self.city and self.profession:
            query = sql_queries.get_doctors_query(city=self.city, profession=self.profession, country_code=self.country_code)
        elif self.city:
            query = sql_queries.get_doctors_query(city=self.city, country_code=self.country_code)
        elif self.profession:
            query = sql_queries.get_doctors_query(profession=self.profession, country_code=self.country_code)
        else:
            query = sql_queries.get_doctors_query(country_code=self.country_code)

        # Execute query using country-specific database connection
        try:
            self.execute_query(query, country_code=self.country_code)
            raw_data = self.query_result
            
            if raw_data:
                # Transform raw data to match original API structure
                self.doctors_returned = self._transform_to_api_structure(raw_data)
                self.returned_doctors = True
            else:
                self.doctors_returned = []
                self.returned_doctors = False
                
        except Exception as e:
            loggerManager.logger.error(f"Error executing query for country {self.country_code}: {e}")
            self.returned_doctors = False
            self.doctors_returned = []

        loggerManager.logger.debug(f"Getting doctors complete for country: {self.country_code}")
        return self

    def _transform_to_api_structure(self, raw_data):
        """
        Transform raw database results to match the original API structure
        """
        if not raw_data:
            return []

        # Handle single record
        if isinstance(raw_data, dict):
            raw_data = [raw_data]

        # Group data by doctor_id
        doctors_dict = defaultdict(lambda: {
            'details': {},
            'clinics': {},
            'specializations': {}
        })

        for record in raw_data:
            doctor_id = record['doctor_id']
            
            # Extract doctor details
            if not doctors_dict[doctor_id]['details']:
                doctors_dict[doctor_id]['details'] = {
                    'doctor_id': record['doctor_id'],
                    'salutation': record.get('salutation'),
                    'given_name': record.get('given_name'),
                    'surname': record.get('surname'),
                    'full_name': record.get('full_name'),
                    'gender': record.get('gender'),
                    'rate': record.get('rate', 0),
                    'branding': record.get('branding'),
                    'has_slots': record.get('has_slots', False),
                    'allow_questions': record.get('allow_questions', False),
                    'url': record.get('url')
                }

            # Extract clinic details
            if record.get('clinic_id') and record['clinic_id'] not in doctors_dict[doctor_id]['clinics']:
                doctors_dict[doctor_id]['clinics'][record['clinic_id']] = {
                    'clinic_id': record['clinic_id'],
                    'clinic_name': record.get('clinic_name'),
                    'street': record.get('street'),
                    'city_name': record.get('city_name'),
                    'post_code': record.get('post_code'),
                    'province': record.get('province'),
                    'latitude': record.get('latitude'),
                    'longitude': record.get('longitude'),
                    'calendar_active': record.get('calendar_active', False),
                    'online_payment': record.get('online_payment', False),
                    'non_doctor': record.get('non_doctor', False),
                    'default_fee': record.get('default_fee'),
                    'fee': record.get('fee'),
                    'doctor_id': record['doctor_id'],
                    'responsibilities': []  # Empty array as per original structure
                }

            # Extract specialization details
            if record.get('specialization_name') and record['specialization_name'] not in doctors_dict[doctor_id]['specializations']:
                doctors_dict[doctor_id]['specializations'][record['specialization_name']] = {
                    'doctor_id': record['doctor_id'],
                    'specialization_name': record['specialization_name'],
                    'name_plural': record.get('name_plural'),
                    'is_popular': record.get('is_popular', False),
                    'count': record.get('count', 1)
                }

        # Convert to final API structure
        items = []
        for doctor_id, doctor_data in doctors_dict.items():
            item = {
                'details': doctor_data['details'],
                'clinics': list(doctor_data['clinics'].values()),
                'specializations': list(doctor_data['specializations'].values())
            }
            items.append(item)

        return items

    def execute_query(self, query, country_code=None):
        """
        Execute query using country-specific database connection
        :param query: SQL query to execute
        :param country_code: Country code (DE, IT)
        :return: Query results
        """
        try:
            if query and country_code:
                # Get country-specific cursor
                cursor_attr = f'cursor_{country_code.lower()}'
                if hasattr(g, cursor_attr):
                    cursor = getattr(g, cursor_attr)
                    cursor.execute(query)
                    self.query_result = cursor.fetchall()
                    
                    if len(self.query_result) == 1:
                        self.query_result = dict(self.query_result[0])
                    elif len(self.query_result) > 1:
                        self.query_result = [dict(record) for record in self.query_result]
                    else:
                        self.query_result = None
                else:
                    raise Exception(f"No database connection available for country: {country_code}")
                    
        except Exception as e:
            err_msg = f'Error in execute_query for {country_code}: {query}: {e}'
            loggerManager.logger.error(err_msg)
            raise e
        
        return self