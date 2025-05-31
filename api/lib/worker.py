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
    def __init__(self, request_data):
        super().__init__(request_data)
        self.request_data = request_data
        self.doctors_returned = None
        self.returned_doctors = False

    def get_doctors(self):
        """
        Returns doctors
        :return:
        """
        loggerManager.logger.debug(f"Getting doctors start")
        self.validate()
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

        # Todo: execute query
        # self.execute_query(query)
        # self.doctors_returned = self.query_result
        #
        # if self.doctors_returned:
        self.returned_doctors = True

        loggerManager.logger.debug(f"Getting doctors complete")
        return self









