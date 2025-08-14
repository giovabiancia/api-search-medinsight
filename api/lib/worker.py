#!/bash/bin
# -*- encoding: utf-8 -*-
"""
@author:        Barnabas
@email:         barnabasaugustino@gmail.com
@client:        Barnabas
@gitlab:        https://gitlab.com/projects28/medinsights-be.git
@domain name:
@Hostname:      DigitalOcean
@Description:   Worker esteso per MedInsights API con supporto completo
"""

from flask import g
from api.lib import filter, database_manager, sql_queries, loggerManager
from collections import defaultdict


class EnhancedMedicalWorker(filter.DoctorsFilter, database_manager.ExecuteQueries):
    """Worker esteso per gestire tutte le funzionalità dell'API medica"""
    
    def __init__(self, request_data=None, country_code='IT'):
        super().__init__(request_data or {})
        self.request_data = request_data or {}
        self.country_code = country_code.upper()
        self.result_data = None
        self.operation_successful = False

    def get_specializations(self):
        """
        Ottiene tutte le specializzazioni disponibili
        :return: self
        """
        loggerManager.logger.debug(f"Getting specializations for country: {self.country_code}")
        
        try:
            query = sql_queries.get_specializations_query(country_code=self.country_code)
            self.execute_query(query, country_code=self.country_code)
            
            if self.query_result:
                if isinstance(self.query_result, dict):
                    self.result_data = [self.query_result]
                else:
                    self.result_data = self.query_result
                self.operation_successful = True
            else:
                self.result_data = []
                self.operation_successful = False
                
        except Exception as e:
            loggerManager.logger.error(f"Error getting specializations for country {self.country_code}: {e}")
            self.operation_successful = False
            self.result_data = []

        return self

    def get_cities(self):
        """
        Ottiene tutte le città con dottori disponibili
        :return: self
        """
        loggerManager.logger.debug(f"Getting cities for country: {self.country_code}")
        
        try:
            query = sql_queries.get_cities_query(country_code=self.country_code)
            self.execute_query(query, country_code=self.country_code)
            
            if self.query_result:
                if isinstance(self.query_result, dict):
                    self.result_data = [self.query_result]
                else:
                    self.result_data = self.query_result
                self.operation_successful = True
            else:
                self.result_data = []
                self.operation_successful = False
                
        except Exception as e:
            loggerManager.logger.error(f"Error getting cities for country {self.country_code}: {e}")
            self.operation_successful = False
            self.result_data = []

        return self

    def get_doctor_opinions(self, doctor_id):
        """
        Ottiene le recensioni per un dottore specifico
        :param doctor_id: int, ID del dottore
        :return: self
        """
        loggerManager.logger.debug(f"Getting opinions for doctor {doctor_id} in country: {self.country_code}")
        
        try:
            query = sql_queries.get_doctor_opinions_query(doctor_id, country_code=self.country_code)
            self.execute_query(query, country_code=self.country_code)
            
            if self.query_result:
                if isinstance(self.query_result, dict):
                    self.result_data = [self.query_result]
                else:
                    self.result_data = self.query_result
                self.operation_successful = True
            else:
                self.result_data = []
                self.operation_successful = False
                
        except Exception as e:
            loggerManager.logger.error(f"Error getting opinions for doctor {doctor_id} in country {self.country_code}: {e}")
            self.operation_successful = False
            self.result_data = []

        return self

    def get_doctor_opinion_stats(self, doctor_id):
        """
        Ottiene le statistiche delle recensioni per un dottore specifico
        :param doctor_id: int, ID del dottore
        :return: self
        """
        loggerManager.logger.debug(f"Getting opinion stats for doctor {doctor_id} in country: {self.country_code}")
        
        try:
            query = sql_queries.get_doctor_opinion_stats_query(doctor_id, country_code=self.country_code)
            self.execute_query(query, country_code=self.country_code)
            
            if self.query_result:
                self.result_data = self.query_result if isinstance(self.query_result, dict) else self.query_result[0]
                self.operation_successful = True
            else:
                self.result_data = {}
                self.operation_successful = False
                
        except Exception as e:
            loggerManager.logger.error(f"Error getting opinion stats for doctor {doctor_id} in country {self.country_code}: {e}")
            self.operation_successful = False
            self.result_data = {}

        return self

    def get_clinic_telephones(self, clinic_id):
        """
        Ottiene i numeri di telefono per una clinica specifica
        :param clinic_id: int, ID della clinica
        :return: self
        """
        loggerManager.logger.debug(f"Getting telephones for clinic {clinic_id} in country: {self.country_code}")
        
        try:
            query = sql_queries.get_clinic_telephones_query(clinic_id, country_code=self.country_code)
            self.execute_query(query, country_code=self.country_code)
            
            if self.query_result:
                if isinstance(self.query_result, dict):
                    self.result_data = [self.query_result]
                else:
                    self.result_data = self.query_result
                self.operation_successful = True
            else:
                self.result_data = []
                self.operation_successful = False
                
        except Exception as e:
            loggerManager.logger.error(f"Error getting telephones for clinic {clinic_id} in country {self.country_code}: {e}")
            self.operation_successful = False
            self.result_data = []

        return self

    def get_clinic_services(self, clinic_id):
        """
        Ottiene i servizi per una clinica specifica
        :param clinic_id: int, ID della clinica
        :return: self
        """
        loggerManager.logger.debug(f"Getting services for clinic {clinic_id} in country: {self.country_code}")
        
        try:
            query = sql_queries.get_clinic_services_query(clinic_id, country_code=self.country_code)
            self.execute_query(query, country_code=self.country_code)
            
            if self.query_result:
                if isinstance(self.query_result, dict):
                    self.result_data = [self.query_result]
                else:
                    self.result_data = self.query_result
                self.operation_successful = True
            else:
                self.result_data = []
                self.operation_successful = False
                
        except Exception as e:
            loggerManager.logger.error(f"Error getting services for clinic {clinic_id} in country {self.country_code}: {e}")
            self.operation_successful = False
            self.result_data = []

        return self

    def search_doctors_advanced(self):
        """
        Ricerca avanzata dei dottori con filtri multipli
        :return: self
        """
        loggerManager.logger.debug(f"Advanced search for doctors in country: {self.country_code}")
        
        try:
            # Estrai parametri di ricerca
            search_term = self.request_data.get('search_term')
            city = self.request_data.get('city')
            profession = self.request_data.get('profession')
            min_rate = self.request_data.get('min_rate')
            max_rate = self.request_data.get('max_rate')
            has_slots = self.request_data.get('has_slots')
            allow_questions = self.request_data.get('allow_questions')
            limit = self.request_data.get('limit')
            
            # Converti stringhe boolean
            if has_slots is not None:
                has_slots = str(has_slots).lower() in ['true', '1', 'yes']
            if allow_questions is not None:
                allow_questions = str(allow_questions).lower() in ['true', '1', 'yes']
            
            query = sql_queries.search_doctors_advanced_query(
                search_term=search_term,
                city=city,
                profession=profession,
                min_rate=min_rate,
                max_rate=max_rate,
                has_slots=has_slots,
                allow_questions=allow_questions,
                limit=limit,
                country_code=self.country_code
            )
            
            self.execute_query(query, country_code=self.country_code)
            raw_data = self.query_result
            
            if raw_data:
                # Trasforma i dati grezzi nella struttura API
                self.result_data = self._transform_to_api_structure(raw_data)
                self.operation_successful = True
            else:
                self.result_data = []
                self.operation_successful = False
                
        except Exception as e:
            loggerManager.logger.error(f"Error in advanced search for country {self.country_code}: {e}")
            self.operation_successful = False
            self.result_data = []

        return self

    def get_popular_specializations(self, limit=10):
        """
        Ottiene le specializzazioni più popolari
        :param limit: int, numero di risultati
        :return: self
        """
        loggerManager.logger.debug(f"Getting popular specializations for country: {self.country_code}")
        
        try:
            query = sql_queries.get_popular_specializations_query(limit=limit, country_code=self.country_code)
            self.execute_query(query, country_code=self.country_code)
            
            if self.query_result:
                if isinstance(self.query_result, dict):
                    self.result_data = [self.query_result]
                else:
                    self.result_data = self.query_result
                self.operation_successful = True
            else:
                self.result_data = []
                self.operation_successful = False
                
        except Exception as e:
            loggerManager.logger.error(f"Error getting popular specializations for country {self.country_code}: {e}")
            self.operation_successful = False
            self.result_data = []

        return self

    def get_top_rated_doctors(self, limit=20, min_rate=4):
        """
        Ottiene i dottori con rating più alto
        :param limit: int, numero di risultati
        :param min_rate: int, rating minimo
        :return: self
        """
        loggerManager.logger.debug(f"Getting top rated doctors for country: {self.country_code}")
        
        try:
            query = sql_queries.get_top_rated_doctors_query(limit=limit, min_rate=min_rate, country_code=self.country_code)
            self.execute_query(query, country_code=self.country_code)
            
            if self.query_result:
                if isinstance(self.query_result, dict):
                    self.result_data = [self.query_result]
                else:
                    self.result_data = self.query_result
                self.operation_successful = True
            else:
                self.result_data = []
                self.operation_successful = False
                
        except Exception as e:
            loggerManager.logger.error(f"Error getting top rated doctors for country {self.country_code}: {e}")
            self.operation_successful = False
            self.result_data = []

        return self

    def get_doctors_with_slots(self):
        """
        Ottiene i dottori con slot disponibili
        :return: self
        """
        loggerManager.logger.debug(f"Getting doctors with slots for country: {self.country_code}")
        
        try:
            city = self.request_data.get('city')
            profession = self.request_data.get('profession')
            
            query = sql_queries.get_doctors_with_slots_query(
                city=city,
                profession=profession,
                country_code=self.country_code
            )
            
            self.execute_query(query, country_code=self.country_code)
            raw_data = self.query_result
            
            if raw_data:
                # Trasforma i dati grezzi nella struttura API
                self.result_data = self._transform_to_api_structure(raw_data)
                self.operation_successful = True
            else:
                self.result_data = []
                self.operation_successful = False
                
        except Exception as e:
            loggerManager.logger.error(f"Error getting doctors with slots for country {self.country_code}: {e}")
            self.operation_successful = False
            self.result_data = []

        return self

    def get_database_stats(self):
        """
        Ottiene le statistiche del database
        :return: self
        """
        loggerManager.logger.debug(f"Getting database stats for country: {self.country_code}")
        
        try:
            query = sql_queries.get_database_stats_query(country_code=self.country_code)
            self.execute_query(query, country_code=self.country_code)
            
            if self.query_result:
                if isinstance(self.query_result, dict):
                    self.result_data = [self.query_result]
                else:
                    self.result_data = self.query_result
                self.operation_successful = True
            else:
                self.result_data = []
                self.operation_successful = False
                
        except Exception as e:
            loggerManager.logger.error(f"Error getting database stats for country {self.country_code}: {e}")
            self.operation_successful = False
            self.result_data = []

        return self

    def _transform_to_api_structure(self, raw_data):
        """
        Trasforma i dati grezzi del database nella struttura API originale
        :param raw_data: dati grezzi dal database
        :return: lista di dizionari strutturati
        """
        if not raw_data:
            return []

        # Gestisci record singolo
        if isinstance(raw_data, dict):
            raw_data = [raw_data]

        # Raggruppa dati per doctor_id
        doctors_dict = defaultdict(lambda: {
            'details': {},
            'clinics': {},
            'specializations': {}
        })

        for record in raw_data:
            doctor_id = record['doctor_id']
            
            # Estrai dettagli dottore
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

            # Estrai dettagli clinica
            if record.get('clinic_id') and record['clinic_id'] not in doctors_dict[doctor_id]['clinics']:
                clinic_data = {
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
                    'responsibilities': []  # Array vuoto come da struttura originale
                }
                
                # Aggiungi campi specifici per cliniche con slot
                if 'clinic_has_slots' in record:
                    clinic_data['has_slots'] = record.get('clinic_has_slots', False)
                if 'nearest_slot_date' in record:
                    clinic_data['nearest_slot_date'] = record.get('nearest_slot_date')
                    
                doctors_dict[doctor_id]['clinics'][record['clinic_id']] = clinic_data

            # Estrai dettagli specializzazione
            if record.get('specialization_name') and record['specialization_name'] not in doctors_dict[doctor_id]['specializations']:
                doctors_dict[doctor_id]['specializations'][record['specialization_name']] = {
                    'doctor_id': record['doctor_id'],
                    'specialization_name': record['specialization_name'],
                    'name_plural': record.get('name_plural'),
                    'is_popular': record.get('is_popular', False),
                    'count': record.get('count', 1)
                }

        # Converti nella struttura API finale
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
        Esegue query usando la connessione database specifica per paese
        :param query: query SQL da eseguire
        :param country_code: codice paese (DE, IT)
        :return: risultati query
        """
        try:
            if query and country_code:
                # Ottieni cursor specifico per paese
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
                    raise Exception(f"Nessuna connessione database disponibile per paese: {country_code}")
                    
        except Exception as e:
            err_msg = f'Errore in execute_query per {country_code}: {query}: {e}'
            loggerManager.logger.error(err_msg)
            raise e
        
        return self


# Manteniamo la classe originale per backward compatibility
class Doctors(EnhancedMedicalWorker):
    """Classe originale per backward compatibility"""
    
    def __init__(self, request_data, country_code='IT'):
        super().__init__(request_data, country_code)
        self.doctors_returned = None
        self.returned_doctors = False

    def get_doctors(self):
        """
        Metodo originale per ottenere dottori - mantiene compatibilità
        :return: self
        """
        loggerManager.logger.debug(f"Getting doctors start for country: {self.country_code}")
        self.validate()
        
        # Ottieni query
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

        # Esegui query usando connessione database specifica per paese
        try:
            self.execute_query(query, country_code=self.country_code)
            raw_data = self.query_result
            
            if raw_data:
                # Trasforma dati grezzi nella struttura API originale
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