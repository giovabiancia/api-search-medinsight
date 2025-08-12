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
            self.doctors_returned = self.query_result
            if self.doctors_returned:
                self.returned_doctors = True
        except Exception as e:
            loggerManager.logger.error(f"Error executing query for country {self.country_code}: {e}")
            self.returned_doctors = False

        loggerManager.logger.debug(f"Getting doctors complete for country: {self.country_code}")
        return self

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