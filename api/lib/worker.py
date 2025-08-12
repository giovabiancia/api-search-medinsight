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

from api.lib import filter, database_manager, sql_queries, loggerManager


class Doctors(filter.DoctorsFilter, database_manager.ExecuteQueries):
    def __init__(self, request_data, country='default'):
        super().__init__(request_data)
        self.request_data = request_data
        self.country = country
        self.doctors_returned = None
        self.returned_doctors = True  # Set to True for testing

    def get_doctors(self):
        """
        Returns doctors
        :return:
        """
        loggerManager.logger.debug(f"Getting doctors start for country: {self.country}")
        
        try:
            self.validate()
        except Exception as e:
            loggerManager.logger.error(f"Validation error: {e}")
            self.returned_doctors = False
            return self
        
        # Get query
        # Case1: id is passed
        if self.doctor_id:
            query = sql_queries.get_doctors_query(doctor_id=self.doctor_id)

        # Case2: city and profession is passed
        elif self.city and self.profession:
            query = sql_queries.get_doctors_query(city=self.city, profession=self.profession)

        # Case3: city only is passed
        elif self.city:
            query = sql_queries.get_doctors_query(city=self.city)

        # Case4: profession only is passed
        elif self.profession:
            query = sql_queries.get_doctors_query(profession=self.profession)

        # Case5: Default (Otherwise)
        else:
            query = sql_queries.get_doctors_query()

        # Execute query with country-specific database
        # self.execute_query(query, country=self.country)
        # self.doctors_returned = self.query_result
        
        # Temporary mock data for testing
        self.doctors_returned = [{"id": 1, "name": "Dr. Test", "city": self.city or "Default City"}]
        self.returned_doctors = True

        loggerManager.logger.debug(f"Getting doctors complete for country: {self.country}")
        return self