#!/bash/bin
# -*- encoding: utf-8 -*-
"""
@author:        Barnabas
@email:         barnabasaugustino@gmail.com
@client:        Barnabas
@gitlab:        https://gitlab.com/projects28/medinsights-be.git
@domain name:
@Hostname:      DigitalOcean
@Description:   Worker esteso per MedInsights API con supporto completo e servizi
"""

from flask import g
from api.lib import filter, database_manager, sql_queries, loggerManager
from collections import defaultdict
from datetime import datetime


class EnhancedMedicalWorker(filter.DoctorsFilter, database_manager.ExecuteQueries):
    """Worker esteso per gestire tutte le funzionalità dell'API medica"""
    
    def __init__(self, request_data=None, country_code='IT'):
        super().__init__(request_data or {})
        self.request_data = request_data or {}
        self.country_code = country_code.upper()
        self.result_data = None
        self.operation_successful = False

    def _transform_to_api_structure(self, raw_data):
        """
        Trasforma i dati grezzi del database nella struttura API originale
        CORRETTO: Elimina duplicati di doctor_id garantendo un record unico per dottore
        """
        if not raw_data:
            return []

        # Gestisci record singolo
        if isinstance(raw_data, dict):
            raw_data = [raw_data]

        # Usa un set per tracciare doctor_id già processati
        processed_doctors = set()
        items = []

        for record in raw_data:
            doctor_id = record.get['doctor_id']
            
            # CORREZIONE: Salta se questo dottore è già stato processato
            if doctor_id in processed_doctors:
                continue
                
            processed_doctors.add(doctor_id)

            # Estrai dettagli dottore
            doctor_details = {
                'doctor_id': record.get['doctor_id'],
                'salutation': record.get('salutation'),
                'given_name': record.get('given_name'),
                'surname': record.get('surname'),
                'full_name': record.get('full_name'),
                'gender': record.get('gender'),
                'rate': record.get('rate', 0),
                'branding': record.get('branding'),
                'has_slots': record.get('has_slots', False),
                'allow_questions': record.get('allow_questions', False),
                'url': record.get('url'),
                # Informazioni enrichment Google Places
                'enriched_status': record.get('enriched_status', 'not_enriched'),
                'google_place_id': record.get('google_place_id'),
                'enriched_at': record.get('enriched_at'),
                'last_enrichment_update': record.get('last_enrichment_update'),
                'google_business_name': record.get('google_business_name'),
                'google_rating': record.get('google_rating'),
                'google_reviews_count': record.get('google_reviews_count'),
                'can_enrich': record.get('enriched_status', 'not_enriched') == 'not_enriched',
                "has_enrichment_attempts": record.get('has_enrichment_attempts'),
                "last_attempt_status": record.get('last_attempt_status'),
                "has_google_places_data": record.get('has_google_places_data'),
            }

            # Gestisci cliniche (da JSON array o record singolo)
            clinics = []
            if 'clinics' in record and record['clinics']:
                # Se clinics è già un array JSON (dalla query lite)
                if isinstance(record['clinics'], list):
                    for clinic_data in record['clinics']:
                        clinic = {
                            'clinic_id': clinic_data.get('clinic_id'),
                            'clinic_name': clinic_data.get('clinic_name'),
                            'street': clinic_data.get('street'),
                            'city_name': clinic_data.get('city_name'),
                            'post_code': clinic_data.get('post_code'),
                            'province': clinic_data.get('province'),
                            'latitude': clinic_data.get('latitude'),
                            'longitude': clinic_data.get('longitude'),
                            'calendar_active': clinic_data.get('calendar_active', False),
                            'online_payment': clinic_data.get('online_payment', False),
                            'doctor_id': doctor_id,
                            'responsibilities': []  # Popolato dopo con i servizi se disponibili
                        }
                        clinics.append(clinic)
            elif record.get('clinic_id'):
                # Fallback per record singolo
                clinic = {
                    'clinic_id': record.get('clinic_id'),
                    'clinic_name': record.get('clinic_name'),
                    'street': record.get('street'),
                    'city_name': record.get('city_name'),
                    'post_code': record.get('post_code'),
                    'province': record.get('province'),
                    'latitude': record.get('latitude'),
                    'longitude': record.get('longitude'),
                    'calendar_active': record.get('calendar_active', False),
                    'online_payment': record.get('online_payment', False),
                    'doctor_id': doctor_id,
                    'responsibilities': []
                }
                clinics.append(clinic)

            # Gestisci specializzazioni
            specializations = []
            if record.get('primary_specialization'):
                spec = {
                    'doctor_id': doctor_id,
                    'specialization_name': record['primary_specialization'],
                    'name_plural': record.get('name_plural'),
                    'is_popular': record.get('is_popular', False),
                    'count': 1
                }
                specializations.append(spec)
            elif record.get('specialization_name'):
                spec = {
                    'doctor_id': doctor_id,
                    'specialization_name': record['specialization_name'],
                    'name_plural': record.get('name_plural'),
                    'is_popular': record.get('is_popular', False),
                    'count': record.get('count', 1)
                }
                specializations.append(spec)

            # Costruisci item finale
            item = {
                'details': doctor_details,
                'clinics': clinics,
                'specializations': specializations
            }
            
            items.append(item)

        return items

    
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
    # Aggiungi questi metodi alla classe EnhancedMedicalWorker in api/lib/worker.py

    def save_google_place_data(self, place_data):
        """
        Salva dati Google Places nella tabella dedicata (doctor_id obbligatorio)
        :param place_data: dict, dati da Google Places API (deve includere doctor_id)
        :return: self
        """
        loggerManager.logger.debug(f"Saving Google Place data for country: {self.country_code}")
        
        try:
            # Validazione dati essenziali
            if not place_data.get('google_place_id'):
                raise ValueError("google_place_id is required")
            
            if not place_data.get('doctor_id'):
                raise ValueError("doctor_id is required - Google Place must be linked to a doctor")
            
            query = sql_queries.insert_google_place_data_query(place_data, country_code=self.country_code)
            self.execute_query(query, country_code=self.country_code)
            
            if self.query_result:
                self.result_data = self.query_result
                self.operation_successful = True
                doctor_id = self.query_result.get('doctor_id')
                loggerManager.logger.info(f"Successfully saved Google Place: {place_data.get('google_place_id')} for doctor_id: {doctor_id}")
            else:
                self.result_data = {}
                self.operation_successful = False
                loggerManager.logger.warning(f"Failed to save Google Place: {place_data.get('google_place_id')}")
                
        except Exception as e:
            loggerManager.logger.error(f"Error saving Google Place data for country {self.country_code}: {e}")
            self.operation_successful = False
            self.result_data = {"error": str(e)}

        return self

    def get_google_places_data(self, google_place_id=None, doctor_id=None, limit=None):
        """
        Recupera dati Google Places salvati con informazioni del dottore
        :param google_place_id: string, ID specifico (opzionale)
        :param doctor_id: int, ID dottore (opzionale)
        :param limit: int, limite risultati (opzionale)
        :return: self
        """
        loggerManager.logger.debug(f"Getting Google Places data for country: {self.country_code}")
        
        try:
            query = sql_queries.get_google_places_data_query(
                google_place_id=google_place_id,
                doctor_id=doctor_id,
                country_code=self.country_code,
                limit=limit
            )
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
            loggerManager.logger.error(f"Error getting Google Places data for country {self.country_code}: {e}")
            self.operation_successful = False
            self.result_data = []

        return self
    # STEP 3: Aggiungi questi metodi alla classe EnhancedMedicalWorker in api/lib/worker.py
    # IMPORTANTE: Aggiungi anche questo import all'inizio del file:
    # from datetime import datetime

    def save_enrichment_attempt(self, attempt_data):
        """
        Salva un tentativo di arricchimento (successo o fallimento)
        :param attempt_data: dict con i dati del tentativo
        :return: self
        """
        loggerManager.logger.debug(f"Saving enrichment attempt for country: {self.country_code}")
        
        try:
            # Validazione dati essenziali
            if not attempt_data.get('doctor_id'):
                raise ValueError("doctor_id is required for enrichment attempt")
            
            if not attempt_data.get('attempt_status'):
                raise ValueError("attempt_status is required")
            
            query = sql_queries.insert_enrichment_attempt_query(attempt_data, country_code=self.country_code)
            self.execute_query(query, country_code=self.country_code)
            
            if self.query_result:
                self.result_data = self.query_result
                self.operation_successful = True
                loggerManager.logger.info(f"Successfully saved enrichment attempt: doctor_id {attempt_data.get('doctor_id')}, status: {attempt_data.get('attempt_status')}")
            else:
                self.result_data = {}
                self.operation_successful = False
                loggerManager.logger.warning(f"Failed to save enrichment attempt: doctor_id {attempt_data.get('doctor_id')}")
                
        except Exception as e:
            loggerManager.logger.error(f"Error saving enrichment attempt for country {self.country_code}: {e}")
            self.operation_successful = False
            self.result_data = {"error": str(e)}

        return self

    def get_enrichment_attempts(self, doctor_id=None, status=None, limit=None):
        """
        Recupera tentativi di arricchimento con filtri opzionali
        :param doctor_id: int, ID dottore specifico (opzionale)
        :param status: string, stato tentativo (opzionale)
        :param limit: int, limite risultati (opzionale)
        :return: self
        """
        loggerManager.logger.debug(f"Getting enrichment attempts for country: {self.country_code}")
        
        try:
            query = sql_queries.get_enrichment_attempts_query(
                doctor_id=doctor_id,
                country_code=self.country_code,
                status=status,
                limit=limit
            )
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
            loggerManager.logger.error(f"Error getting enrichment attempts for country {self.country_code}: {e}")
            self.operation_successful = False
            self.result_data = []

        return self

    def check_doctors_enrichment_status(self, doctor_ids):
        """
        Controlla lo stato di arricchimento per una lista di dottori
        :param doctor_ids: list di doctor ID
        :return: self
        """
        loggerManager.logger.debug(f"Checking enrichment status for {len(doctor_ids)} doctors in country: {self.country_code}")
        
        try:
            if not doctor_ids:
                self.result_data = []
                self.operation_successful = True
                return self
            
            query = sql_queries.check_doctor_enrichment_status_query(
                doctor_ids=doctor_ids,
                country_code=self.country_code
            )
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
            loggerManager.logger.error(f"Error checking enrichment status for country {self.country_code}: {e}")
            self.operation_successful = False
            self.result_data = []

        return self

    def get_unenriched_doctors(self, limit=None, exclude_failed=False):
        """
        Ottieni dottori che non sono mai stati arricchiti o che necessitano di re-arricchimento
        :param limit: int, limite risultati (opzionale)
        :param exclude_failed: bool, escludi dottori con tentativi falliti
        :return: self
        """
        loggerManager.logger.debug(f"Getting unenriched doctors for country: {self.country_code}")
        
        try:
            query = sql_queries.get_unenriched_doctors_query(
                country_code=self.country_code,
                limit=limit,
                exclude_failed=exclude_failed
            )
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
            loggerManager.logger.error(f"Error getting unenriched doctors for country {self.country_code}: {e}")
            self.operation_successful = False
            self.result_data = []

        return self

    def save_google_place_data_with_attempt(self, place_data, attempt_data=None):
        """
        Salva dati Google Places E traccia il tentativo di arricchimento
        :param place_data: dict, dati da Google Places API
        :param attempt_data: dict, dati del tentativo (opzionale, generato automaticamente)
        :return: self
        """
        loggerManager.logger.debug(f"Saving Google Place data with attempt tracking for country: {self.country_code}")
        
        start_time = datetime.now()
        
        try:
            # Validazione dati essenziali
            if not place_data.get('doctor_id'):
                raise ValueError("doctor_id is required")
            
            # Salva prima il tentativo di arricchimento
            if not attempt_data:
                attempt_data = {
                    'doctor_id': place_data.get('doctor_id'),
                    'attempt_status': 'success' if place_data.get('google_place_id') else 'no_results',
                    'enrichment_source': 'google_places',
                    'search_query': place_data.get('search_query'),
                    'doctor_name': place_data.get('original_doctor', {}).get('name'),
                    'doctor_surname': place_data.get('original_doctor', {}).get('surname'),
                    'clinic_name': place_data.get('business_name'),
                    'clinic_address': place_data.get('formatted_address'),
                    'google_place_id': place_data.get('google_place_id'),
                    'places_found': 1 if place_data.get('google_place_id') else 0,
                    'attempted_by': place_data.get('attempted_by'),
                    'processing_time_ms': int((datetime.now() - start_time).total_seconds() * 1000)
                }
            
            # Salva il tentativo
            attempt_worker = EnhancedMedicalWorker(country_code=self.country_code)
            attempt_worker.save_enrichment_attempt(attempt_data)
            
            # Se abbiamo dati validi, salva anche i Google Places
            google_place_result = None
            if place_data.get('google_place_id'):
                self.save_google_place_data(place_data)
                google_place_result = self.result_data if self.operation_successful else None
            
            # Combina i risultati
            self.result_data = {
                'attempt_saved': attempt_worker.operation_successful,
                'attempt_data': attempt_worker.result_data,
                'google_place_saved': google_place_result is not None,
                'google_place_data': google_place_result,
                'doctor_id': place_data.get('doctor_id'),
                'status': attempt_data.get('attempt_status')
            }
            self.operation_successful = attempt_worker.operation_successful
            
            loggerManager.logger.info(f"Completed enrichment with attempt tracking: doctor_id {place_data.get('doctor_id')}, status: {attempt_data.get('attempt_status')}")
            
        except Exception as e:
            # Salva il tentativo fallito
            try:
                failed_attempt_data = {
                    'doctor_id': place_data.get('doctor_id'),
                    'attempt_status': 'error',
                    'enrichment_source': 'google_places',
                    'error_message': str(e),
                    'attempted_by': place_data.get('attempted_by'),
                    'processing_time_ms': int((datetime.now() - start_time).total_seconds() * 1000)
                }
                
                attempt_worker = EnhancedMedicalWorker(country_code=self.country_code)
                attempt_worker.save_enrichment_attempt(failed_attempt_data)
                
            except Exception as attempt_error:
                loggerManager.logger.error(f"Failed to save failed attempt: {attempt_error}")
            
            loggerManager.logger.error(f"Error in save_google_place_data_with_attempt for country {self.country_code}: {e}")
            self.operation_successful = False
            self.result_data = {"error": str(e), "doctor_id": place_data.get('doctor_id')}

        return self
    def get_complete_doctor_profile(self, doctor_id):
        """
        Ottieni profilo completo del dottore con TUTTI i dati disponibili
        :param doctor_id: int, ID del dottore
        :return: self
        """
        loggerManager.logger.debug(f"Getting complete profile for doctor {doctor_id} in country: {self.country_code}")
        
        try:
            # Ottieni tutte le query
            queries = sql_queries.get_complete_doctor_profile_query(doctor_id, country_code=self.country_code)
            
            # Esegui ogni query e raccogli i risultati
            complete_data = {}
            
            for section_name, query in queries.items():
                try:
                    self.execute_query(query, country_code=self.country_code)
                    
                    if self.query_result:
                        if isinstance(self.query_result, list):
                            complete_data[section_name] = self.query_result
                        else:
                            complete_data[section_name] = [self.query_result]
                    else:
                        complete_data[section_name] = []
                        
                    loggerManager.logger.debug(f"Section {section_name}: {len(complete_data[section_name])} records")
                    
                except Exception as e:
                    loggerManager.logger.error(f"Error executing query for section {section_name}: {e}")
                    complete_data[section_name] = []
            
            # Verifica che il dottore esista
            if not complete_data.get('doctor_base'):
                self.result_data = None
                self.operation_successful = False
                loggerManager.logger.warning(f"Doctor {doctor_id} not found in country {self.country_code}")
                return self
            
            # Organizza i dati in una struttura logica
            organized_data = self._organize_complete_doctor_data(complete_data, doctor_id)
            
            self.result_data = organized_data
            self.operation_successful = True
            loggerManager.logger.info(f"Successfully retrieved complete profile for doctor {doctor_id}")
            
        except Exception as e:
            loggerManager.logger.error(f"Error getting complete doctor profile for doctor {doctor_id} in country {self.country_code}: {e}")
            self.operation_successful = False
            self.result_data = None

        return self

    def _organize_complete_doctor_data(self, data_sections, doctor_id):
        """
        Organizza i dati del dottore in una struttura logica e ben organizzata
        :param data_sections: dict con tutti i dati dalle query
        :param doctor_id: int, ID del dottore
        :return: dizionario organizzato
        """
        
        # Dati base del dottore
        doctor_base = data_sections['doctor_base'][0] if data_sections['doctor_base'] else {}
        
        # Organizza cliniche con i loro servizi e telefoni
        clinics_data = []
        for clinic in data_sections['clinics']:
            clinic_id = clinic['clinic_id']
            
            # Servizi per questa clinica
            clinic_services = [
                service for service in data_sections['services'] 
                if service['clinic_id'] == clinic_id
            ]
            
            # Telefoni per questa clinica
            clinic_phones = [
                {
                    'telephone_id': phone['telephone_id'],
                    'phone_number': phone['phone_number'],
                    'phone_created': phone['phone_created'],
                    'phone_modified': phone['phone_modified']
                }
                for phone in data_sections['phone_numbers'] 
                if phone['clinic_id'] == clinic_id
            ]
            
            # Componi dati clinica completi
            clinic_data = dict(clinic)
            clinic_data['services'] = clinic_services
            clinic_data['phone_numbers'] = clinic_phones
            clinic_data['total_services'] = len(clinic_services)
            clinic_data['total_phones'] = len(clinic_phones)
            
            clinics_data.append(clinic_data)
        
        # Calcola alcuni totali e statistiche
        total_services = len(data_sections['services'])
        total_opinions = len(data_sections['opinions'])
        total_phone_numbers = len(data_sections['phone_numbers'])
        
        # Calcola rating medio dalle opinioni
        opinions_with_rating = [op for op in data_sections['opinions'] if op.get('opinion_rate')]
        avg_opinion_rating = None
        if opinions_with_rating:
            total_rating = sum(op['opinion_rate'] for op in opinions_with_rating)
            avg_opinion_rating = round(total_rating / len(opinions_with_rating), 2)
        
        # Determina stato arricchimento
        enrichment_status = 'never_attempted'
        if data_sections['google_places']:
            enrichment_status = 'enriched'
        elif data_sections['enrichment_attempts']:
            last_attempt = data_sections['enrichment_attempts'][0]  # Ordinato per data DESC
            if last_attempt['attempt_status'] == 'success':
                enrichment_status = 'enriched'
            elif last_attempt['attempt_status'] in ['failed', 'error', 'no_results']:
                enrichment_status = 'attempted_failed'
            else:
                enrichment_status = 'attempted'
        
        # Struttura finale organizzata
        organized_profile = {
            # Informazioni base
            'doctor_id': doctor_id,
            'profile_retrieved_at': datetime.now().isoformat(),
            'country_code': self.country_code,
            
            # Dati personali del dottore
            'personal_info': {
                'internal_id': doctor_base.get('internal_id'),
                'salutation': doctor_base.get('salutation'),
                'given_name': doctor_base.get('given_name'),
                'surname': doctor_base.get('surname'),
                'full_name': doctor_base.get('full_name'),
                'gender': doctor_base.get('gender'),
                'doctor_url': doctor_base.get('doctor_url'),
                'import_date': doctor_base.get('import_date'),
                'created': doctor_base.get('doctor_created'),
                'modified': doctor_base.get('doctor_modified')
            },
            
            # Valutazioni e disponibilità
            'ratings_and_availability': {
                'rate': doctor_base.get('rate'),
                'doctor_has_slots': doctor_base.get('doctor_has_slots'),
                'allow_questions': doctor_base.get('allow_questions'),
                'branding': doctor_base.get('branding'),
                'avg_opinion_rating': avg_opinion_rating,
                'total_opinions_count': total_opinions
            },
            
            # Specializzazioni
            'specializations': {
                'items': data_sections['specializations'],
                'total': len(data_sections['specializations']),
                'popular_specializations': [
                    spec for spec in data_sections['specializations'] 
                    if spec.get('is_popular')
                ]
            },
            
            # Cliniche con servizi e telefoni
            'clinics': {
                'items': clinics_data,
                'total': len(clinics_data),
                'total_services_across_clinics': total_services,
                'total_phone_numbers': total_phone_numbers
            },
            
            # Opinioni e recensioni
            'opinions': {
                'items': data_sections['opinions'],
                'total': total_opinions,
                'statistics': data_sections['opinion_stats'][0] if data_sections['opinion_stats'] else None,
                'average_rating': avg_opinion_rating
            },
            
            # Dati Google Places
            'google_places': {
                'items': data_sections['google_places'],
                'total': len(data_sections['google_places']),
                'has_google_data': len(data_sections['google_places']) > 0
            },
            
            # Storico arricchimento
            'enrichment_history': {
                'status': enrichment_status,
                'attempts': data_sections['enrichment_attempts'],
                'total_attempts': len(data_sections['enrichment_attempts']),
                'last_attempt': data_sections['enrichment_attempts'][0] if data_sections['enrichment_attempts'] else None
            },
            
            # Sommario generale
            'summary': {
                'total_clinics': len(clinics_data),
                'total_specializations': len(data_sections['specializations']),
                'total_services': total_services,
                'total_opinions': total_opinions,
                'total_phone_numbers': total_phone_numbers,
                'has_google_places_data': len(data_sections['google_places']) > 0,
                'enrichment_status': enrichment_status,
                'profile_completeness': self._calculate_profile_completeness(doctor_base, data_sections)
            }
        }
        
        return organized_profile

    def _calculate_profile_completeness(self, doctor_base, data_sections):
        """
        Calcola una percentuale di completezza del profilo
        :param doctor_base: dati base del dottore
        :param data_sections: tutte le sezioni dati
        :return: percentuale di completezza (0-100)
        """
        score = 0
        max_score = 100
        
        # Dati base (30 punti)
        if doctor_base.get('full_name'): score += 5
        if doctor_base.get('gender'): score += 5
        if doctor_base.get('rate'): score += 10
        if doctor_base.get('doctor_url'): score += 5
        if doctor_base.get('salutation'): score += 5
        
        # Specializzazioni (15 punti)
        if data_sections['specializations']: 
            score += 15
        
        # Cliniche (20 punti)
        if data_sections['clinics']: 
            score += 10
            # Bonus per cliniche con dati completi
            complete_clinics = sum(1 for c in data_sections['clinics'] 
                                if c.get('latitude') and c.get('longitude') and c.get('street'))
            if complete_clinics > 0:
                score += 10
        
        # Servizi (10 punti)
        if data_sections['services']: score += 10
        
        # Opinioni (15 punti)
        if data_sections['opinions']: score += 15
        
        # Google Places (10 punti)
        if data_sections['google_places']: score += 10
        
        return min(score, max_score)


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
    
