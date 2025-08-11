#!/bash/bin
# -*- encoding: utf-8 -*-
"""
@author:        Barnabas
@email:         barnabasaugustino@gmail.com
@client:        Barnabas
@gitlab:        https://gitlab.com/projects28/medinsights-be.git
@domain name:
@Hostname:      DigitalOcean
@Description:   Worker semplificato
"""

from api.lib import filter, database_manager, sql_queries, loggerManager

class Doctors(filter.DoctorsFilter, database_manager.ExecuteQueries):
    def __init__(self, request_data):
        super().__init__(request_data)
        self.request_data = request_data
        self.doctors_returned = None
        self.returned_doctors = False

    def get_doctors(self):
        """Ottieni dottori"""
        loggerManager.logger.debug("Getting doctors start")
        
        try:
            # Valida input
            self.validate()
            
            # Ottieni query
            if self.doctor_id:
                query = sql_queries.get_doctors_query(doctor_id=self.doctor_id)
            elif self.city and self.profession:
                query = sql_queries.get_doctors_query(city=self.city, profession=self.profession)
            elif self.city:
                query = sql_queries.get_doctors_query(city=self.city)
            elif self.profession:
                query = sql_queries.get_doctors_query(profession=self.profession)
            else:
                query = sql_queries.get_doctors_query()
            
            # Esegui query
            self.execute_query(query)
            self.doctors_returned = self.query_result
            
            if self.doctors_returned:
                self.returned_doctors = True
                loggerManager.logger.info(f"Trovati dottori: {self._count_results()}")
            else:
                self.returned_doctors = False
                loggerManager.logger.info("Nessun dottore trovato")
                
        except Exception as e:
            loggerManager.logger.error(f"Errore getting doctors: {e}")
            self.returned_doctors = False
            self.doctors_returned = None
        
        loggerManager.logger.debug("Getting doctors complete")
        return self
    
    def _count_results(self):
        """Conta risultati"""
        if not self.doctors_returned:
            return 0
        elif isinstance(self.doctors_returned, list):
            return len(self.doctors_returned)
        elif isinstance(self.doctors_returned, dict):
            return 1
        else:
            return 0