#!/usr/bin/env
"""
@author:        Barnabas
@email:         barnabasaugustino@gmail.com
@website:       http://www.barnabasmatonya.com
@client:        Barnabas
@gitlab:        https://gitlab.com/projects28/medinsights-be.git
@domain name:
@Hostname:      DigitalOcean
@Description:   SQL queries per MedInsights API - supporto multi-paese con servizi (UPDATED)

"""

from api.lib import loggerManager


def get_doctors_query(doctor_id=None, city=None, profession=None, country_code='IT'):
    """
    Get doctors query for specific country database with services and enrichment status including attempts
    :param doctor_id: int doctor id
    :param city: string city name
    :param profession: string, profession
    :param country_code: string, country code (DE, IT)
    :return: SQL query string
    """
    
    if doctor_id:
        # Retrieve doctor's complete information by ID including services and enrichment status
        query = f"""
                SELECT 
                    -- Doctor details
                    d.doctor_id, d.salutation, d.given_name, d.surname, d.full_name, d.gender, 
                    d.rate, d.branding, d.has_slots, d.allow_questions, d.url,
                    -- Clinic details via mapping table
                    c.clinic_id, c.clinic_name, c.street, c.city_name, c.post_code, c.province,
                    c.latitude, c.longitude, c.calendar_active, c.online_payment, c.non_doctor,
                    c.default_fee, c.fee,
                    -- Specialization details via mapping table
                    s.specialization_name, s.name_plural, s.is_popular, 1 as count,
                    -- Service details
                    so.service_id, so.option_name as service_name, so.description as service_description,
                    csom.service_price, csom.service_price_decimal, csom.is_price_from, csom.is_default as is_default_service,
                    -- Google Places enrichment status
                    CASE 
                        WHEN gpd.google_place_id IS NOT NULL THEN 'enriched'
                        WHEN ea.id IS NOT NULL AND ea.attempt_status = 'success' THEN 'enriched'
                        WHEN ea.id IS NOT NULL AND ea.attempt_status IN ('failed', 'error', 'no_results') THEN 'attempted_failed'
                        WHEN ea.id IS NOT NULL THEN 'attempted'
                        ELSE 'never_attempted'
                    END as enrichment_status,
                    gpd.google_place_id,
                    gpd.enriched_at,
                    gpd.updated_at as last_enrichment_update,
                    gpd.business_name as google_business_name,
                    gpd.rating as google_rating,
                    gpd.reviews_count as google_reviews_count,
                    -- Enrichment attempts information
                    ea.attempt_status as last_attempt_status,
                    ea.attempted_at as last_attempt_date,
                    ea.error_message as last_attempt_error,
                    ea.search_query as last_search_query,
                    ea.processing_time_ms as last_processing_time,
                    ea.attempted_by as last_attempted_by,
                    CASE 
                        WHEN ea.id IS NOT NULL THEN true
                        ELSE false
                    END as has_enrichment_attempts,
                    CASE 
                        WHEN gpd.google_place_id IS NOT NULL THEN true
                        ELSE false
                    END as has_google_places_data
                FROM doctors.doctors d
                LEFT JOIN doctors.doctors_clinics_map dcm ON d.doctor_id = dcm.doctor_id
                LEFT JOIN doctors.clinics c ON dcm.clinic_id = c.clinic_id
                LEFT JOIN doctors.doctors_specializations_map dsm ON d.doctor_id = dsm.doctor_id
                LEFT JOIN doctors.specializations s ON dsm.specialization_id = s.specialization_id
                LEFT JOIN doctors.clinics_service_options_map csom ON (c.clinic_id = csom.clinic_id AND d.doctor_id = csom.doctor_id)
                LEFT JOIN doctors.service_options so ON csom.service_id = so.service_id
                LEFT JOIN doctors.google_places_data gpd ON d.doctor_id = gpd.doctor_id
                LEFT JOIN doctors.enrichment_attempts ea ON (d.doctor_id = ea.doctor_id AND ea.country_code = '{country_code}' AND ea.enrichment_source = 'google_places')
                WHERE d.doctor_id = {doctor_id}
                ORDER BY d.doctor_id, c.clinic_id, s.specialization_name, csom.is_default DESC, so.option_name
                """

    elif city and profession:
        # Retrieve practitioners from the city with specific profession including services and enrichment status
        profession = profession.upper()
        city = city.upper()
        query = f"""
                SELECT 
                    -- Doctor details
                    d.doctor_id, d.salutation, d.given_name, d.surname, d.full_name, d.gender, 
                    d.rate, d.branding, d.has_slots, d.allow_questions, d.url,
                    -- Clinic details via mapping table
                    c.clinic_id, c.clinic_name, c.street, c.city_name, c.post_code, c.province,
                    c.latitude, c.longitude, c.calendar_active, c.online_payment, c.non_doctor,
                    c.default_fee, c.fee,
                    -- Specialization details via mapping table
                    s.specialization_name, s.name_plural, s.is_popular, 1 as count,
                    -- Service details
                    so.service_id, so.option_name as service_name, so.description as service_description,
                    csom.service_price, csom.service_price_decimal, csom.is_price_from, csom.is_default as is_default_service,
                    -- Google Places enrichment status
                    CASE 
                        WHEN gpd.google_place_id IS NOT NULL THEN 'enriched'
                        WHEN ea.id IS NOT NULL AND ea.attempt_status = 'success' THEN 'enriched'
                        WHEN ea.id IS NOT NULL AND ea.attempt_status IN ('failed', 'error', 'no_results') THEN 'attempted_failed'
                        WHEN ea.id IS NOT NULL THEN 'attempted'
                        ELSE 'never_attempted'
                    END as enrichment_status,
                    gpd.google_place_id,
                    gpd.enriched_at,
                    gpd.updated_at as last_enrichment_update,
                    gpd.business_name as google_business_name,
                    gpd.rating as google_rating,
                    gpd.reviews_count as google_reviews_count,
                    -- Enrichment attempts information
                    ea.attempt_status as last_attempt_status,
                    ea.attempted_at as last_attempt_date,
                    ea.error_message as last_attempt_error,
                    ea.search_query as last_search_query,
                    ea.processing_time_ms as last_processing_time,
                    ea.attempted_by as last_attempted_by,
                    CASE 
                        WHEN ea.id IS NOT NULL THEN true
                        ELSE false
                    END as has_enrichment_attempts,
                    CASE 
                        WHEN gpd.google_place_id IS NOT NULL THEN true
                        ELSE false
                    END as has_google_places_data
                FROM doctors.doctors d
                LEFT JOIN doctors.doctors_clinics_map dcm ON d.doctor_id = dcm.doctor_id
                LEFT JOIN doctors.clinics c ON dcm.clinic_id = c.clinic_id
                LEFT JOIN doctors.doctors_specializations_map dsm ON d.doctor_id = dsm.doctor_id
                LEFT JOIN doctors.specializations s ON dsm.specialization_id = s.specialization_id
                LEFT JOIN doctors.clinics_service_options_map csom ON (c.clinic_id = csom.clinic_id AND d.doctor_id = csom.doctor_id)
                LEFT JOIN doctors.service_options so ON csom.service_id = so.service_id
                LEFT JOIN doctors.google_places_data gpd ON d.doctor_id = gpd.doctor_id
                LEFT JOIN doctors.enrichment_attempts ea ON (d.doctor_id = ea.doctor_id AND ea.country_code = '{country_code}' AND ea.enrichment_source = 'google_places')
                WHERE UPPER(c.city_name) = '{city}' AND UPPER(s.specialization_name) = '{profession}'
                ORDER BY d.rate DESC, d.doctor_id, c.clinic_id, s.specialization_name, csom.is_default DESC, so.option_name
                """

    elif profession:
        # Retrieve all practitioners matching the profession including services and enrichment status
        profession = profession.upper()
        query = f"""
                SELECT 
                    -- Doctor details
                    d.doctor_id, d.salutation, d.given_name, d.surname, d.full_name, d.gender, 
                    d.rate, d.branding, d.has_slots, d.allow_questions, d.url,
                    -- Clinic details via mapping table
                    c.clinic_id, c.clinic_name, c.street, c.city_name, c.post_code, c.province,
                    c.latitude, c.longitude, c.calendar_active, c.online_payment, c.non_doctor,
                    c.default_fee, c.fee,
                    -- Specialization details via mapping table
                    s.specialization_name, s.name_plural, s.is_popular, 1 as count,
                    -- Service details
                    so.service_id, so.option_name as service_name, so.description as service_description,
                    csom.service_price, csom.service_price_decimal, csom.is_price_from, csom.is_default as is_default_service,
                    -- Google Places enrichment status
                    CASE 
                        WHEN gpd.google_place_id IS NOT NULL THEN 'enriched'
                        WHEN ea.id IS NOT NULL AND ea.attempt_status = 'success' THEN 'enriched'
                        WHEN ea.id IS NOT NULL AND ea.attempt_status IN ('failed', 'error', 'no_results') THEN 'attempted_failed'
                        WHEN ea.id IS NOT NULL THEN 'attempted'
                        ELSE 'never_attempted'
                    END as enrichment_status,
                    gpd.google_place_id,
                    gpd.enriched_at,
                    gpd.updated_at as last_enrichment_update,
                    gpd.business_name as google_business_name,
                    gpd.rating as google_rating,
                    gpd.reviews_count as google_reviews_count,
                    -- Enrichment attempts information
                    ea.attempt_status as last_attempt_status,
                    ea.attempted_at as last_attempt_date,
                    ea.error_message as last_attempt_error,
                    ea.search_query as last_search_query,
                    ea.processing_time_ms as last_processing_time,
                    ea.attempted_by as last_attempted_by,
                    CASE 
                        WHEN ea.id IS NOT NULL THEN true
                        ELSE false
                    END as has_enrichment_attempts,
                    CASE 
                        WHEN gpd.google_place_id IS NOT NULL THEN true
                        ELSE false
                    END as has_google_places_data
                FROM doctors.doctors d
                LEFT JOIN doctors.doctors_clinics_map dcm ON d.doctor_id = dcm.doctor_id
                LEFT JOIN doctors.clinics c ON dcm.clinic_id = c.clinic_id
                LEFT JOIN doctors.doctors_specializations_map dsm ON d.doctor_id = dsm.doctor_id
                LEFT JOIN doctors.specializations s ON dsm.specialization_id = s.specialization_id
                LEFT JOIN doctors.clinics_service_options_map csom ON (c.clinic_id = csom.clinic_id AND d.doctor_id = csom.doctor_id)
                LEFT JOIN doctors.service_options so ON csom.service_id = so.service_id
                LEFT JOIN doctors.google_places_data gpd ON d.doctor_id = gpd.doctor_id
                LEFT JOIN doctors.enrichment_attempts ea ON (d.doctor_id = ea.doctor_id AND ea.country_code = '{country_code}' AND ea.enrichment_source = 'google_places')
                WHERE UPPER(s.specialization_name) = '{profession}'
                ORDER BY d.rate DESC, d.doctor_id, c.clinic_id, s.specialization_name, csom.is_default DESC, so.option_name
                """

    elif city:
        # Retrieve all practitioners from the specified city including services and enrichment status
        city = city.upper()
        query = f"""
                SELECT 
                    -- Doctor details
                    d.doctor_id, d.salutation, d.given_name, d.surname, d.full_name, d.gender, 
                    d.rate, d.branding, d.has_slots, d.allow_questions, d.url,
                    -- Clinic details via mapping table
                    c.clinic_id, c.clinic_name, c.street, c.city_name, c.post_code, c.province,
                    c.latitude, c.longitude, c.calendar_active, c.online_payment, c.non_doctor,
                    c.default_fee, c.fee,
                    -- Specialization details via mapping table
                    s.specialization_name, s.name_plural, s.is_popular, 1 as count,
                    -- Service details
                    so.service_id, so.option_name as service_name, so.description as service_description,
                    csom.service_price, csom.service_price_decimal, csom.is_price_from, csom.is_default as is_default_service,
                    -- Google Places enrichment status
                    CASE 
                        WHEN gpd.google_place_id IS NOT NULL THEN 'enriched'
                        WHEN ea.id IS NOT NULL AND ea.attempt_status = 'success' THEN 'enriched'
                        WHEN ea.id IS NOT NULL AND ea.attempt_status IN ('failed', 'error', 'no_results') THEN 'attempted_failed'
                        WHEN ea.id IS NOT NULL THEN 'attempted'
                        ELSE 'never_attempted'
                    END as enrichment_status,
                    gpd.google_place_id,
                    gpd.enriched_at,
                    gpd.updated_at as last_enrichment_update,
                    gpd.business_name as google_business_name,
                    gpd.rating as google_rating,
                    gpd.reviews_count as google_reviews_count,
                    -- Enrichment attempts information
                    ea.attempt_status as last_attempt_status,
                    ea.attempted_at as last_attempt_date,
                    ea.error_message as last_attempt_error,
                    ea.search_query as last_search_query,
                    ea.processing_time_ms as last_processing_time,
                    ea.attempted_by as last_attempted_by,
                    CASE 
                        WHEN ea.id IS NOT NULL THEN true
                        ELSE false
                    END as has_enrichment_attempts,
                    CASE 
                        WHEN gpd.google_place_id IS NOT NULL THEN true
                        ELSE false
                    END as has_google_places_data
                FROM doctors.doctors d
                LEFT JOIN doctors.doctors_clinics_map dcm ON d.doctor_id = dcm.doctor_id
                LEFT JOIN doctors.clinics c ON dcm.clinic_id = c.clinic_id
                LEFT JOIN doctors.doctors_specializations_map dsm ON d.doctor_id = dsm.doctor_id
                LEFT JOIN doctors.specializations s ON dsm.specialization_id = s.specialization_id
                LEFT JOIN doctors.clinics_service_options_map csom ON (c.clinic_id = csom.clinic_id AND d.doctor_id = csom.doctor_id)
                LEFT JOIN doctors.service_options so ON csom.service_id = so.service_id
                LEFT JOIN doctors.google_places_data gpd ON d.doctor_id = gpd.doctor_id
                LEFT JOIN doctors.enrichment_attempts ea ON (d.doctor_id = ea.doctor_id AND ea.country_code = '{country_code}' AND ea.enrichment_source = 'google_places')
                WHERE UPPER(c.city_name) = '{city}'
                ORDER BY d.rate DESC, d.doctor_id, c.clinic_id, s.specialization_name, csom.is_default DESC, so.option_name
                """
    else:
        # Demo: Retrieve only few practitioners for demo including services and enrichment status
        query = f"""
                SELECT 
                    -- Doctor details
                    d.doctor_id, d.salutation, d.given_name, d.surname, d.full_name, d.gender, 
                    d.rate, d.branding, d.has_slots, d.allow_questions, d.url,
                    -- Clinic details via mapping table
                    c.clinic_id, c.clinic_name, c.street, c.city_name, c.post_code, c.province,
                    c.latitude, c.longitude, c.calendar_active, c.online_payment, c.non_doctor,
                    c.default_fee, c.fee,
                    -- Specialization details via mapping table
                    s.specialization_name, s.name_plural, s.is_popular, 1 as count,
                    -- Service details
                    so.service_id, so.option_name as service_name, so.description as service_description,
                    csom.service_price, csom.service_price_decimal, csom.is_price_from, csom.is_default as is_default_service,
                    -- Google Places enrichment status
                    CASE 
                        WHEN gpd.google_place_id IS NOT NULL THEN 'enriched'
                        WHEN ea.id IS NOT NULL AND ea.attempt_status = 'success' THEN 'enriched'
                        WHEN ea.id IS NOT NULL AND ea.attempt_status IN ('failed', 'error', 'no_results') THEN 'attempted_failed'
                        WHEN ea.id IS NOT NULL THEN 'attempted'
                        ELSE 'never_attempted'
                    END as enrichment_status,
                    gpd.google_place_id,
                    gpd.enriched_at,
                    gpd.updated_at as last_enrichment_update,
                    gpd.business_name as google_business_name,
                    gpd.rating as google_rating,
                    gpd.reviews_count as google_reviews_count,
                    -- Enrichment attempts information
                    ea.attempt_status as last_attempt_status,
                    ea.attempted_at as last_attempt_date,
                    ea.error_message as last_attempt_error,
                    ea.search_query as last_search_query,
                    ea.processing_time_ms as last_processing_time,
                    ea.attempted_by as last_attempted_by,
                    CASE 
                        WHEN ea.id IS NOT NULL THEN true
                        ELSE false
                    END as has_enrichment_attempts,
                    CASE 
                        WHEN gpd.google_place_id IS NOT NULL THEN true
                        ELSE false
                    END as has_google_places_data
                FROM doctors.doctors d
                LEFT JOIN doctors.doctors_clinics_map dcm ON d.doctor_id = dcm.doctor_id
                LEFT JOIN doctors.clinics c ON dcm.clinic_id = c.clinic_id
                LEFT JOIN doctors.doctors_specializations_map dsm ON d.doctor_id = dsm.doctor_id
                LEFT JOIN doctors.specializations s ON dsm.specialization_id = s.specialization_id
                LEFT JOIN doctors.clinics_service_options_map csom ON (c.clinic_id = csom.clinic_id AND d.doctor_id = csom.doctor_id)
                LEFT JOIN doctors.service_options so ON csom.service_id = so.service_id
                LEFT JOIN doctors.google_places_data gpd ON d.doctor_id = gpd.doctor_id
                LEFT JOIN doctors.enrichment_attempts ea ON (d.doctor_id = ea.doctor_id AND ea.country_code = '{country_code}' AND ea.enrichment_source = 'google_places')
                ORDER BY d.rate DESC, d.doctor_id, c.clinic_id, s.specialization_name, csom.is_default DESC, so.option_name
                LIMIT 50
                """
    
    loggerManager.logger.info(f"Query for country {country_code}: {query}")
    return query


def search_doctors_advanced_query(search_term=None, city=None, profession=None, 
                                 min_rate=None, max_rate=None, has_slots=None, 
                                 allow_questions=None, limit=None, country_code='IT'):
    """
    Advanced search for doctors with multiple filters including services and enrichment status with attempts
    :param search_term: string, search in doctor name
    :param city: string, city name
    :param profession: string, profession/specialization
    :param min_rate: int, minimum rating
    :param max_rate: int, maximum rating
    :param has_slots: boolean, has available slots
    :param allow_questions: boolean, allows questions
    :param limit: int, maximum number of results
    :param country_code: string, country code (DE, IT)
    :return: SQL query string
    """
    
    base_query = f"""
            SELECT 
                -- Doctor details
                d.doctor_id, d.salutation, d.given_name, d.surname, d.full_name, d.gender, 
                d.rate, d.branding, d.has_slots, d.allow_questions, d.url,
                -- Clinic details via mapping table
                c.clinic_id, c.clinic_name, c.street, c.city_name, c.post_code, c.province,
                c.latitude, c.longitude, c.calendar_active, c.online_payment, c.non_doctor,
                c.default_fee, c.fee,
                -- Specialization details via mapping table
                s.specialization_name, s.name_plural, s.is_popular, 1 as count,
                -- Service details
                so.service_id, so.option_name as service_name, so.description as service_description,
                csom.service_price, csom.service_price_decimal, csom.is_price_from, csom.is_default as is_default_service,
                -- Google Places enrichment status
                CASE 
                    WHEN gpd.google_place_id IS NOT NULL THEN 'enriched'
                    WHEN ea.id IS NOT NULL AND ea.attempt_status = 'success' THEN 'enriched'
                    WHEN ea.id IS NOT NULL AND ea.attempt_status IN ('failed', 'error', 'no_results') THEN 'attempted_failed'
                    WHEN ea.id IS NOT NULL THEN 'attempted'
                    ELSE 'never_attempted'
                END as enrichment_status,
                gpd.google_place_id,
                gpd.enriched_at,
                gpd.updated_at as last_enrichment_update,
                gpd.business_name as google_business_name,
                gpd.rating as google_rating,
                gpd.reviews_count as google_reviews_count,
                -- Enrichment attempts information
                ea.attempt_status as last_attempt_status,
                ea.attempted_at as last_attempt_date,
                ea.error_message as last_attempt_error,
                ea.search_query as last_search_query,
                ea.processing_time_ms as last_processing_time,
                ea.attempted_by as last_attempted_by,
                CASE 
                    WHEN ea.id IS NOT NULL THEN true
                    ELSE false
                END as has_enrichment_attempts,
                CASE 
                    WHEN gpd.google_place_id IS NOT NULL THEN true
                    ELSE false
                END as has_google_places_data
            FROM doctors.doctors d
            LEFT JOIN doctors.doctors_clinics_map dcm ON d.doctor_id = dcm.doctor_id
            LEFT JOIN doctors.clinics c ON dcm.clinic_id = c.clinic_id
            LEFT JOIN doctors.doctors_specializations_map dsm ON d.doctor_id = dsm.doctor_id
            LEFT JOIN doctors.specializations s ON dsm.specialization_id = s.specialization_id
            LEFT JOIN doctors.clinics_service_options_map csom ON (c.clinic_id = csom.clinic_id AND d.doctor_id = csom.doctor_id)
            LEFT JOIN doctors.service_options so ON csom.service_id = so.service_id
            LEFT JOIN doctors.google_places_data gpd ON d.doctor_id = gpd.doctor_id
            LEFT JOIN doctors.enrichment_attempts ea ON (d.doctor_id = ea.doctor_id AND ea.country_code = '{country_code}' AND ea.enrichment_source = 'google_places')
            WHERE 1=1
            """
    
    conditions = []
    
    if search_term:
        search_term = search_term.replace("'", "''")  # Escape single quotes
        conditions.append(f"(UPPER(d.full_name) LIKE UPPER('%{search_term}%') OR UPPER(d.given_name) LIKE UPPER('%{search_term}%') OR UPPER(d.surname) LIKE UPPER('%{search_term}%'))")
    
    if city:
        city = city.upper().replace("'", "''")
        conditions.append(f"UPPER(c.city_name) = '{city}'")
    
    if profession:
        profession = profession.upper().replace("'", "''")
        conditions.append(f"UPPER(s.specialization_name) = '{profession}'")
    
    if min_rate is not None:
        conditions.append(f"d.rate >= {min_rate}")
    
    if max_rate is not None:
        conditions.append(f"d.rate <= {max_rate}")
    
    if has_slots is not None:
        conditions.append(f"d.has_slots = {has_slots}")
    
    if allow_questions is not None:
        conditions.append(f"d.allow_questions = {allow_questions}")
    
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    base_query += " ORDER BY d.rate DESC, d.doctor_id, c.clinic_id, s.specialization_name, csom.is_default DESC, so.option_name"
    
    # Add LIMIT only if specified
    if limit is not None:
        base_query += f" LIMIT {limit}"
    
    loggerManager.logger.info(f"Advanced search query for country {country_code}: {base_query}")
    return base_query


def get_doctors_with_slots_query(city=None, profession=None, country_code='IT'):
    """
    Get doctors with available slots including services and enrichment status
    :param city: string, city name (optional)
    :param profession: string, profession/specialization (optional)
    :param country_code: string, country code (DE, IT)
    :return: SQL query string
    """
    base_query = """
            SELECT 
                -- Doctor details
                d.doctor_id, d.salutation, d.given_name, d.surname, d.full_name, d.gender, 
                d.rate, d.branding, d.has_slots, d.allow_questions, d.url,
                -- Clinic details via mapping table
                c.clinic_id, c.clinic_name, c.street, c.city_name, c.post_code, c.province,
                c.latitude, c.longitude, c.calendar_active, c.online_payment, c.non_doctor,
                c.default_fee, c.fee, c.has_slots as clinic_has_slots, c.nearest_slot_date,
                -- Specialization details via mapping table
                s.specialization_name, s.name_plural, s.is_popular, 1 as count,
                -- Service details
                so.service_id, so.option_name as service_name, so.description as service_description,
                csom.service_price, csom.service_price_decimal, csom.is_price_from, csom.is_default as is_default_service,
                -- Google Places enrichment status
                CASE 
                    WHEN gpd.google_place_id IS NOT NULL THEN 'enriched'
                    ELSE 'not_enriched'
                END as enriched_status,
                gpd.google_place_id,
                gpd.enriched_at,
                gpd.updated_at as last_enrichment_update,
                gpd.business_name as google_business_name,
                gpd.rating as google_rating,
                gpd.reviews_count as google_reviews_count
            FROM doctors.doctors d
            LEFT JOIN doctors.doctors_clinics_map dcm ON d.doctor_id = dcm.doctor_id
            LEFT JOIN doctors.clinics c ON dcm.clinic_id = c.clinic_id
            LEFT JOIN doctors.doctors_specializations_map dsm ON d.doctor_id = dsm.doctor_id
            LEFT JOIN doctors.specializations s ON dsm.specialization_id = s.specialization_id
            LEFT JOIN doctors.clinics_service_options_map csom ON (c.clinic_id = csom.clinic_id AND d.doctor_id = csom.doctor_id)
            LEFT JOIN doctors.service_options so ON csom.service_id = so.service_id
            LEFT JOIN doctors.google_places_data gpd ON d.doctor_id = gpd.doctor_id
            WHERE (d.has_slots = true OR c.has_slots = true)
            """
    
    conditions = []
    
    if city:
        city = city.upper().replace("'", "''")
        conditions.append(f"UPPER(c.city_name) = '{city}'")
    
    if profession:
        profession = profession.upper().replace("'", "''")
        conditions.append(f"UPPER(s.specialization_name) = '{profession}'")
    
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    base_query += " ORDER BY d.rate DESC, c.nearest_slot_date ASC NULLS LAST, csom.is_default DESC, so.option_name"
    
    loggerManager.logger.info(f"Doctors with slots query for country {country_code}: {base_query}")
    return base_query

# Keep all other existing functions unchanged...
def get_specializations_query(country_code='IT'):
    """
    Get all specializations for a specific country
    :param country_code: string, country code (DE, IT)
    :return: SQL query string
    """
    query = """
            SELECT 
                s.specialization_id,
                s.specialization_name,
                s.name_plural,
                s.name_female,
                s.is_popular,
                COUNT(DISTINCT dsm.doctor_id) as doctor_count
            FROM doctors.specializations s
            LEFT JOIN doctors.doctors_specializations_map dsm ON s.specialization_id = dsm.specialization_id
            GROUP BY s.specialization_id, s.specialization_name, s.name_plural, s.name_female, s.is_popular
            ORDER BY s.is_popular DESC, doctor_count DESC, s.specialization_name
            """
    
    loggerManager.logger.info(f"Specializations query for country {country_code}: {query}")
    return query


def get_cities_query(country_code='IT'):
    """
    Get all cities with doctors for a specific country
    :param country_code: string, country code (DE, IT)
    :return: SQL query string
    """
    query = """
            SELECT 
                c.city_name,
                c.province,
                COUNT(DISTINCT dcm.doctor_id) as doctor_count,
                COUNT(DISTINCT c.clinic_id) as clinic_count
            FROM doctors.clinics c
            LEFT JOIN doctors.doctors_clinics_map dcm ON c.clinic_id = dcm.clinic_id
            WHERE c.city_name IS NOT NULL AND c.city_name != ''
            GROUP BY c.city_name, c.province
            HAVING COUNT(DISTINCT dcm.doctor_id) > 0
            ORDER BY doctor_count DESC, c.city_name
            """
    
    loggerManager.logger.info(f"Cities query for country {country_code}: {query}")
    return query


def get_doctor_opinions_query(doctor_id, country_code='IT'):
    """
    Get opinions/reviews for a specific doctor
    :param doctor_id: int, doctor ID
    :param country_code: string, country code (DE, IT)
    :return: SQL query string
    """
    query = f"""
            SELECT 
                o.opinion_id,
                o.doctor_id,
                o.rate,
                o.is_anonymous,
                o.photo_url,
                o.client_message,
                o.doctor_response,
                o.created_at,
                d.full_name as doctor_name
            FROM doctors.opinions o
            LEFT JOIN doctors.doctors d ON o.doctor_id = d.doctor_id
            WHERE o.doctor_id = {doctor_id}
            ORDER BY o.created_at DESC
            """
    
    loggerManager.logger.info(f"Doctor opinions query for doctor {doctor_id} in country {country_code}: {query}")
    return query


def get_doctor_opinion_stats_query(doctor_id, country_code='IT'):
    """
    Get opinion statistics for a specific doctor
    :param doctor_id: int, doctor ID
    :param country_code: string, country code (DE, IT)
    :return: SQL query string
    """
    query = f"""
            SELECT 
                os.doctor_id,
                os.positive,
                os.neutral,
                os.negative,
                os.total,
                CASE 
                    WHEN os.total > 0 THEN ROUND((os.positive::DECIMAL / os.total * 100), 2)
                    ELSE 0 
                END as positive_percentage,
                d.full_name as doctor_name,
                d.rate
            FROM doctors.opinions_stats os
            LEFT JOIN doctors.doctors d ON os.doctor_id = d.doctor_id
            WHERE os.doctor_id = {doctor_id}
            """
    
    loggerManager.logger.info(f"Doctor opinion stats query for doctor {doctor_id} in country {country_code}: {query}")
    return query


def get_clinic_telephones_query(clinic_id, country_code='IT'):
    """
    Get telephone numbers for a specific clinic
    :param clinic_id: int, clinic ID
    :param country_code: string, country code (DE, IT)
    :return: SQL query string
    """
    query = f"""
            SELECT 
                t.telephone_id,
                t.clinic_id,
                t.phone_number,
                c.clinic_name
            FROM doctors.telephones t
            LEFT JOIN doctors.clinics c ON t.clinic_id = c.clinic_id
            WHERE t.clinic_id = {clinic_id}
            ORDER BY t.telephone_id
            """
    
    loggerManager.logger.info(f"Clinic telephones query for clinic {clinic_id} in country {country_code}: {query}")
    return query


def get_clinic_services_query(clinic_id, country_code='IT'):
    """
    Get services for a specific clinic
    :param clinic_id: int, clinic ID
    :param country_code: string, country code (DE, IT)
    :return: SQL query string
    """
    query = f"""
            SELECT 
                csom.id as mapping_id,
                csom.clinic_id,
                csom.doctor_id,
                csom.service_price,
                csom.service_price_decimal,
                csom.is_price_from,
                csom.is_default,
                so.service_id,
                so.option_name,
                so.description,
                c.clinic_name,
                d.full_name as doctor_name
            FROM doctors.clinics_service_options_map csom
            LEFT JOIN doctors.service_options so ON csom.service_id = so.service_id
            LEFT JOIN doctors.clinics c ON csom.clinic_id = c.clinic_id
            LEFT JOIN doctors.doctors d ON csom.doctor_id = d.doctor_id
            WHERE csom.clinic_id = {clinic_id}
            ORDER BY csom.is_default DESC, so.option_name
            """
    
    loggerManager.logger.info(f"Clinic services query for clinic {clinic_id} in country {country_code}: {query}")
    return query


def get_popular_specializations_query(limit=10, country_code='IT'):
    """
    Get most popular specializations
    :param limit: int, number of results to return
    :param country_code: string, country code (DE, IT)
    :return: SQL query string
    """
    query = f"""
            SELECT 
                s.specialization_id,
                s.specialization_name,
                s.name_plural,
                s.name_female,
                s.is_popular,
                COUNT(DISTINCT dsm.doctor_id) as doctor_count
            FROM doctors.specializations s
            LEFT JOIN doctors.doctors_specializations_map dsm ON s.specialization_id = dsm.specialization_id
            WHERE s.is_popular = true
            GROUP BY s.specialization_id, s.specialization_name, s.name_plural, s.name_female, s.is_popular
            ORDER BY doctor_count DESC, s.specialization_name
            LIMIT {limit}
            """
    
    loggerManager.logger.info(f"Popular specializations query for country {country_code}: {query}")
    return query


def get_top_rated_doctors_query(limit=20, min_rate=4, country_code='IT'):
    """
    Get top rated doctors
    :param limit: int, number of results to return
    :param min_rate: int, minimum rating
    :param country_code: string, country code (DE, IT)
    :return: SQL query string
    """
    query = f"""
            SELECT DISTINCT
                -- Doctor details
                d.doctor_id, d.salutation, d.given_name, d.surname, d.full_name, d.gender, 
                d.rate, d.branding, d.has_slots, d.allow_questions, d.url,
                -- Opinion stats
                os.positive, os.neutral, os.negative, os.total as total_opinions,
                CASE 
                    WHEN os.total > 0 THEN ROUND((os.positive::DECIMAL / os.total * 100), 2)
                    ELSE 0 
                END as positive_percentage
            FROM doctors.doctors d
            LEFT JOIN doctors.opinions_stats os ON d.doctor_id = os.doctor_id
            WHERE d.rate >= {min_rate}
            ORDER BY d.rate DESC, positive_percentage DESC, os.total DESC
            LIMIT {limit}
            """
    
    loggerManager.logger.info(f"Top rated doctors query for country {country_code}: {query}")
    return query


def get_database_stats_query(country_code='IT'):
    """
    Get database statistics
    :param country_code: string, country code (DE, IT)
    :return: SQL query string
    """
    query = """
            SELECT 
                'doctors' as table_name,
                COUNT(*) as total_count
            FROM doctors.doctors
            UNION ALL
            SELECT 
                'clinics' as table_name,
                COUNT(*) as total_count
            FROM doctors.clinics
            UNION ALL
            SELECT 
                'specializations' as table_name,
                COUNT(*) as total_count
            FROM doctors.specializations
            UNION ALL
            SELECT 
                'opinions' as table_name,
                COUNT(*) as total_count
            FROM doctors.opinions
            UNION ALL
            SELECT 
                'cities' as table_name,
                COUNT(DISTINCT city_name) as total_count
            FROM doctors.clinics
            WHERE city_name IS NOT NULL AND city_name != ''
            ORDER BY table_name
            """
    
    loggerManager.logger.info(f"Database stats query for country {country_code}: {query}")
    return query



# Aggiungi queste funzioni alla fine di api/lib/sql_queries.py

def insert_google_place_data_query(place_data, country_code='IT'):
    """
    Insert Google Places data into google_places_data table
    :param place_data: dict, Google Places API data (must include doctor_id)
    :param country_code: string, country code (DE, IT)
    :return: SQL query string
    """
    
    # Validazione doctor_id obbligatorio
    if not place_data.get('doctor_id'):
        raise ValueError("doctor_id is required for Google Places data")
    
    # Escape single quotes for SQL safety
    def escape_sql(value):
        if value is None:
            return 'NULL'
        if isinstance(value, str):
            escaped = value.replace("'", "''")
            return f"'{escaped}'"
        if isinstance(value, (dict, list)):
            import json
            json_str = json.dumps(value)
            escaped = json_str.replace("'", "''")
            return f"'{escaped}'"
        return str(value)
    
    query = f"""
            INSERT INTO doctors.google_places_data (
                google_place_id,
                doctor_id,
                business_name,
                business_status,
                rating,
                reviews_count,
                phone,
                email,
                website,
                google_maps_url,
                formatted_address,
                latitude,
                longitude,
                opening_hours,
                photos,
                types,
                reviews,
                original_doctor_name,
                original_doctor_surname,
                country_code,
                enriched_at
            ) VALUES (
                {escape_sql(place_data.get('google_place_id'))},
                {place_data.get('doctor_id')},
                {escape_sql(place_data.get('business_name'))},
                {escape_sql(place_data.get('business_status'))},
                {place_data.get('rating') or 'NULL'},
                {place_data.get('reviews_count', 0)},
                {escape_sql(place_data.get('phone'))},
                {escape_sql(place_data.get('email'))},
                {escape_sql(place_data.get('website'))},
                {escape_sql(place_data.get('google_maps_url'))},
                {escape_sql(place_data.get('formatted_address'))},
                {place_data.get('location', {}).get('lat') or 'NULL'},
                {place_data.get('location', {}).get('lng') or 'NULL'},
                {escape_sql(place_data.get('opening_hours'))},
                {escape_sql(place_data.get('photos'))},
                {escape_sql(place_data.get('types'))},
                {escape_sql(place_data.get('reviews'))},
                {escape_sql(place_data.get('original_doctor', {}).get('name'))},
                {escape_sql(place_data.get('original_doctor', {}).get('surname'))},
                {escape_sql(country_code)},
                {escape_sql(place_data.get('enriched_at'))}
            )
            ON CONFLICT (google_place_id) 
            DO UPDATE SET 
                updated_at = NOW(),
                rating = EXCLUDED.rating,
                reviews_count = EXCLUDED.reviews_count,
                reviews = EXCLUDED.reviews,
                phone = EXCLUDED.phone,
                email = EXCLUDED.email,
                website = EXCLUDED.website
            RETURNING id, google_place_id, doctor_id;
            """
    
    loggerManager.logger.info(f"Insert Google Place query for doctor_id: {place_data.get('doctor_id')}, country: {country_code}")
    return query


def get_google_places_data_query(google_place_id=None, doctor_id=None, country_code='IT', limit=None):
    """
    Get Google Places data with doctor information
    :param google_place_id: string, specific Google Place ID
    :param doctor_id: int, specific doctor ID
    :param country_code: string, country code (DE, IT)
    :param limit: int, limit results
    :return: SQL query string
    """
    
    base_query = """
            SELECT 
                gpd.id,
                gpd.google_place_id,
                gpd.doctor_id,
                gpd.business_name,
                gpd.business_status,
                gpd.rating,
                gpd.reviews_count,
                gpd.phone,
                gpd.email,
                gpd.website,
                gpd.google_maps_url,
                gpd.formatted_address,
                gpd.latitude,
                gpd.longitude,
                gpd.opening_hours,
                gpd.photos,
                gpd.types,
                gpd.reviews,
                gpd.original_doctor_name,
                gpd.original_doctor_surname,
                gpd.country_code,
                gpd.enriched_at,
                gpd.created_at,
                gpd.updated_at,
                d.full_name as doctor_full_name,
                d.given_name as doctor_given_name,
                d.surname as doctor_surname,
                d.rate as doctor_rate
            FROM doctors.google_places_data gpd
            INNER JOIN doctors.doctors d ON gpd.doctor_id = d.doctor_id
            WHERE gpd.country_code = '{}'
            """.format(country_code)
    
    conditions = []
    
    if google_place_id:
        conditions.append(f"gpd.google_place_id = '{google_place_id}'")
    
    if doctor_id:
        conditions.append(f"gpd.doctor_id = {doctor_id}")
    
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    base_query += " ORDER BY gpd.created_at DESC"
    
    if limit:
        base_query += f" LIMIT {limit}"
    
    loggerManager.logger.info(f"Get Google Places query for country {country_code}, doctor_id: {doctor_id}")
    return base_query


# STEP 2: Aggiungi queste funzioni alla fine del file api/lib/sql_queries.py

# CORREGGI la funzione insert_enrichment_attempt_query in api/lib/sql_queries.py
# Il problema è che escape_sql non viene chiamato correttamente per attempted_by

def insert_enrichment_attempt_query(attempt_data, country_code='IT'):
    """
    Insert enrichment attempt record
    :param attempt_data: dict with attempt information
    :param country_code: string, country code (DE, IT)
    :return: SQL query string
    """
    
    # Escape single quotes for SQL safety
    def escape_sql(value):
        if value is None:
            return 'NULL'
        if isinstance(value, str):
            escaped = value.replace("'", "''")
            return f"'{escaped}'"
        if isinstance(value, (dict, list)):
            import json
            json_str = json.dumps(value)
            escaped = json_str.replace("'", "''")
            return f"'{escaped}'"
        return str(value)
    
    # CORREZIONE: Usa escape_sql anche per attempted_by
    attempted_by = attempt_data.get('attempted_by')
    if attempted_by is not None:
        attempted_by_sql = escape_sql(attempted_by)  # <-- QUESTO ERA IL PROBLEMA
    else:
        attempted_by_sql = 'NULL'

    query = f"""
            INSERT INTO doctors.enrichment_attempts (
                doctor_id,
                country_code,
                attempt_status,
                enrichment_source,
                search_query,
                doctor_name,
                doctor_surname,
                clinic_name,
                clinic_address,
                google_place_id,
                places_found,
                error_message,
                attempted_by,
                processing_time_ms
            ) VALUES (
                {attempt_data.get('doctor_id')},
                {escape_sql(country_code)},
                {escape_sql(attempt_data.get('attempt_status', 'attempted'))},
                {escape_sql(attempt_data.get('enrichment_source', 'google_places'))},
                {escape_sql(attempt_data.get('search_query'))},
                {escape_sql(attempt_data.get('doctor_name'))},
                {escape_sql(attempt_data.get('doctor_surname'))},
                {escape_sql(attempt_data.get('clinic_name'))},
                {escape_sql(attempt_data.get('clinic_address'))},
                {escape_sql(attempt_data.get('google_place_id'))},
                {attempt_data.get('places_found', 0)},
                {escape_sql(attempt_data.get('error_message'))},
                {attempted_by_sql},
                {attempt_data.get('processing_time_ms') or 'NULL'}
            )
            ON CONFLICT (doctor_id, country_code, enrichment_source) 
            DO UPDATE SET 
                attempt_status = EXCLUDED.attempt_status,
                search_query = EXCLUDED.search_query,
                google_place_id = EXCLUDED.google_place_id,
                places_found = EXCLUDED.places_found,
                error_message = EXCLUDED.error_message,
                attempted_by = EXCLUDED.attempted_by,
                attempted_at = NOW(),
                processing_time_ms = EXCLUDED.processing_time_ms
            RETURNING id, doctor_id, attempt_status;
            """
    
    loggerManager.logger.info(f"Insert enrichment attempt for doctor_id: {attempt_data.get('doctor_id')}, country: {country_code}")
    return query

def get_enrichment_attempts_query(doctor_id=None, country_code='IT', status=None, limit=None):
    """
    Get enrichment attempts with optional filters
    :param doctor_id: int, specific doctor ID (optional)
    :param country_code: string, country code (DE, IT)
    :param status: string, attempt status filter (optional)
    :param limit: int, limit results (optional)
    :return: SQL query string
    """
    
    base_query = """
            SELECT 
                ea.id,
                ea.doctor_id,
                ea.country_code,
                ea.attempt_status,
                ea.enrichment_source,
                ea.search_query,
                ea.doctor_name,
                ea.doctor_surname,
                ea.clinic_name,
                ea.clinic_address,
                ea.google_place_id,
                ea.places_found,
                ea.error_message,
                ea.attempted_by,
                ea.attempted_at,
                ea.processing_time_ms,
                d.full_name as current_doctor_name,
                d.rate as doctor_rate,
                -- Check if Google Place data exists
                CASE 
                    WHEN gpd.id IS NOT NULL THEN true 
                    ELSE false 
                END as has_google_place_data
            FROM doctors.enrichment_attempts ea
            INNER JOIN doctors.doctors d ON ea.doctor_id = d.doctor_id
            LEFT JOIN doctors.google_places_data gpd ON (ea.doctor_id = gpd.doctor_id AND ea.country_code = gpd.country_code)
            WHERE ea.country_code = '{}'
            """.format(country_code)
    
    conditions = []
    
    if doctor_id:
        conditions.append(f"ea.doctor_id = {doctor_id}")
    
    if status:
        conditions.append(f"ea.attempt_status = '{status}'")
    
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    base_query += " ORDER BY ea.attempted_at DESC"
    
    if limit:
        base_query += f" LIMIT {limit}"
    
    loggerManager.logger.info(f"Get enrichment attempts query for country {country_code}, doctor_id: {doctor_id}")
    return base_query


def check_doctor_enrichment_status_query(doctor_ids, country_code='IT'):
    """
    Check enrichment status for multiple doctors
    :param doctor_ids: list of doctor IDs
    :param country_code: string, country code (DE, IT)
    :return: SQL query string
    """
    
    if not doctor_ids:
        return None
    
    doctor_ids_str = ','.join(map(str, doctor_ids))
    
    query = f"""
            SELECT 
                d.doctor_id,
                d.full_name,
                ea.attempt_status,
                ea.attempted_at,
                ea.enrichment_source,
                ea.places_found,
                ea.google_place_id,
                CASE 
                    WHEN ea.id IS NULL THEN 'never_attempted'
                    WHEN ea.attempt_status = 'success' THEN 'enriched'
                    WHEN ea.attempt_status IN ('failed', 'no_results', 'error') THEN 'attempted_failed'
                    ELSE 'attempted_unknown'
                END as enrichment_status,
                CASE 
                    WHEN gpd.id IS NOT NULL THEN true 
                    ELSE false 
                END as has_saved_data
            FROM doctors.doctors d
            LEFT JOIN doctors.enrichment_attempts ea ON (
                d.doctor_id = ea.doctor_id 
                AND ea.country_code = '{country_code}'
                AND ea.enrichment_source = 'google_places'
            )
            LEFT JOIN doctors.google_places_data gpd ON (
                d.doctor_id = gpd.doctor_id 
                AND gpd.country_code = '{country_code}'
            )
            WHERE d.doctor_id IN ({doctor_ids_str})
            ORDER BY d.doctor_id
            """
    
    loggerManager.logger.info(f"Check enrichment status for {len(doctor_ids)} doctors in country {country_code}")
    return query


def get_unenriched_doctors_query(country_code='IT', limit=None, exclude_failed=False):
    """
    Get doctors that have never been enriched or need re-enrichment
    :param country_code: string, country code (DE, IT)
    :param limit: int, limit results (optional)
    :param exclude_failed: bool, exclude doctors with failed attempts
    :return: SQL query string
    """
    
    exclude_condition = ""
    if exclude_failed:
        exclude_condition = "AND ea.attempt_status NOT IN ('no_results', 'failed')"
    
    base_query = f"""
            SELECT 
                d.doctor_id,
                d.full_name,
                d.given_name,
                d.surname,
                c.clinic_name,
                c.street,
                c.city_name,
                c.post_code,
                CASE 
                    WHEN ea.id IS NULL THEN 'never_attempted'
                    ELSE ea.attempt_status
                END as enrichment_status,
                ea.attempted_at
            FROM doctors.doctors d
            LEFT JOIN doctors.doctors_clinics_map dcm ON d.doctor_id = dcm.doctor_id
            LEFT JOIN doctors.clinics c ON dcm.clinic_id = c.clinic_id
            LEFT JOIN doctors.enrichment_attempts ea ON (
                d.doctor_id = ea.doctor_id 
                AND ea.country_code = '{country_code}'
                AND ea.enrichment_source = 'google_places'
            )
            WHERE (
                ea.id IS NULL  -- Mai tentato
                OR ea.attempt_status IN ('failed', 'error')  -- Fallito, può ritentare
                {exclude_condition}
            )
            AND NOT EXISTS (
                SELECT 1 FROM doctors.google_places_data gpd 
                WHERE gpd.doctor_id = d.doctor_id 
                AND gpd.country_code = '{country_code}'
            )
            """
    
    base_query += " ORDER BY d.doctor_id"
    
    if limit:
        base_query += f" LIMIT {limit}"
    
    loggerManager.logger.info(f"Get unenriched doctors query for country {country_code}")
    return base_query


def get_complete_doctor_profile_query(doctor_id, country_code='IT'):
    """
    Ottieni TUTTI i dati disponibili per un dottore specifico con query separate e semplici
    :param doctor_id: int, ID del dottore
    :param country_code: string, codice paese (DE, IT)
    :return: dict con tutte le query necessarie
    """
    
    queries = {
        # 1. Dati base del dottore
        'doctor_base': f"""
            SELECT 
                d.id as internal_id,
                d.doctor_id,
                d.salutation,
                d.given_name,
                d.surname,
                d.full_name,
                d.gender,
                d.rate,
                d.branding,
                d.has_slots as doctor_has_slots,
                d.allow_questions,
                d.url as doctor_url,
                d.import_date,
                d.created as doctor_created,
                d.modified as doctor_modified
            FROM doctors.doctors d
            WHERE d.doctor_id = {doctor_id}
        """,
        
        # 2. Tutte le cliniche del dottore
        'clinics': f"""
            SELECT 
                c.id as clinic_internal_id,
                c.clinic_id,
                c.clinic_name,
                c.province,
                c.street,
                c.district_name,
                c.post_code,
                c.city_name,
                c.facility_id,
                c.latitude,
                c.longitude,
                c.calendar_active,
                c.calendar_guid,
                c.has_slots as clinic_has_slots,
                c.nearest_slot_date,
                c.online_payment,
                c.fee,
                c.default_fee,
                c.non_doctor,
                c.is_commercial_from_deal,
                c.is_commercial_from_saas,
                c.booking_extra_fields,
                c.created as clinic_created,
                c.modified as clinic_modified,
                dcm.created as mapping_created
            FROM doctors.doctors d
            JOIN doctors.doctors_clinics_map dcm ON d.doctor_id = dcm.doctor_id
            JOIN doctors.clinics c ON dcm.clinic_id = c.clinic_id
            WHERE d.doctor_id = {doctor_id}
            ORDER BY c.clinic_id
        """,
        
        # 3. Tutte le specializzazioni del dottore
        'specializations': f"""
            SELECT 
                s.id as spec_internal_id,
                s.specialization_id,
                s.specialization_name,
                s.name_plural,
                s.name_female,
                s.is_popular,
                s.created as spec_created,
                s.modified as spec_modified,
                dsm.created as spec_mapping_created
            FROM doctors.doctors d
            JOIN doctors.doctors_specializations_map dsm ON d.doctor_id = dsm.doctor_id
            JOIN doctors.specializations s ON dsm.specialization_id = s.specialization_id
            WHERE d.doctor_id = {doctor_id}
            ORDER BY s.is_popular DESC, s.specialization_name
        """,
        
        # 4. Tutti i servizi del dottore (per clinica)
        'services': f"""
            SELECT 
                csom.id as service_mapping_id,
                csom.clinic_id,
                csom.service_price,
                csom.service_price_decimal,
                csom.is_price_from,
                csom.is_default as is_default_service,
                csom.import_date as service_import_date,
                csom.created as service_mapping_created,
                csom.modified as service_mapping_modified,
                so.id as service_internal_id,
                so.service_id,
                so.option_name as service_name,
                so.description as service_description,
                so.created as service_created,
                so.modified as service_modified
            FROM doctors.doctors d
            JOIN doctors.doctors_clinics_map dcm ON d.doctor_id = dcm.doctor_id
            JOIN doctors.clinics_service_options_map csom ON (dcm.clinic_id = csom.clinic_id AND d.doctor_id = csom.doctor_id)
            JOIN doctors.service_options so ON csom.service_id = so.service_id
            WHERE d.doctor_id = {doctor_id}
            ORDER BY csom.clinic_id, csom.is_default DESC, so.option_name
        """,
        
        # 5. Tutte le opinioni/recensioni del dottore
        'opinions': f"""
            SELECT 
                o.id as opinion_internal_id,
                o.opinion_id,
                o.rate as opinion_rate,
                o.is_anonymous,
                o.photo_url,
                o.client_message,
                o.doctor_response,
                o.created_at as opinion_created_at,
                o.created as opinion_created,
                o.modified as opinion_modified
            FROM doctors.opinions o
            WHERE o.doctor_id = {doctor_id}
            ORDER BY o.created DESC
        """,
        
        # 6. Statistiche delle opinioni
        'opinion_stats': f"""
            SELECT 
                os.id as stats_internal_id,
                os.positive,
                os.neutral,
                os.negative,
                os.total,
                CASE 
                    WHEN os.total > 0 THEN ROUND((os.positive::DECIMAL / os.total * 100), 2)
                    ELSE 0 
                END as positive_percentage,
                os.created as stats_created,
                os.modified as stats_modified
            FROM doctors.opinions_stats os
            WHERE os.doctor_id = {doctor_id}
        """,
        
        # 7. Dati Google Places (se disponibili)
        'google_places': f"""
            SELECT 
                gpd.id as google_internal_id,
                gpd.google_place_id,
                gpd.business_name,
                gpd.business_status,
                gpd.rating as google_rating,
                gpd.reviews_count as google_reviews_count,
                gpd.phone as google_phone,
                gpd.email as google_email,
                gpd.website as google_website,
                gpd.google_maps_url,
                gpd.formatted_address as google_address,
                gpd.latitude as google_latitude,
                gpd.longitude as google_longitude,
                gpd.opening_hours,
                gpd.photos,
                gpd.types,
                gpd.reviews as google_reviews,
                gpd.original_doctor_name,
                gpd.original_doctor_surname,
                gpd.enriched_at,
                gpd.created_at as google_created,
                gpd.updated_at as google_updated
            FROM doctors.google_places_data gpd
            WHERE gpd.doctor_id = {doctor_id} AND gpd.country_code = '{country_code}'
            ORDER BY gpd.created_at DESC
        """,
        
        # 8. Storico tentativi di arricchimento
        'enrichment_attempts': f"""
            SELECT 
                ea.id as attempt_internal_id,
                ea.attempt_status,
                ea.enrichment_source,
                ea.search_query,
                ea.doctor_name as attempted_doctor_name,
                ea.doctor_surname as attempted_doctor_surname,
                ea.clinic_name as attempted_clinic_name,
                ea.clinic_address as attempted_clinic_address,
                ea.google_place_id as attempted_google_place_id,
                ea.places_found,
                ea.error_message,
                ea.attempted_by,
                ea.attempted_at,
                ea.processing_time_ms
            FROM doctors.enrichment_attempts ea
            WHERE ea.doctor_id = {doctor_id} AND ea.country_code = '{country_code}'
            ORDER BY ea.attempted_at DESC
        """,
        
        # 9. Numeri di telefono per tutte le cliniche
        'phone_numbers': f"""
            SELECT 
                t.telephone_id,
                t.clinic_id,
                t.phone_number,
                t.created as phone_created,
                t.modified as phone_modified,
                c.clinic_name
            FROM doctors.doctors d
            JOIN doctors.doctors_clinics_map dcm ON d.doctor_id = dcm.doctor_id
            JOIN doctors.telephones t ON dcm.clinic_id = t.clinic_id
            JOIN doctors.clinics c ON t.clinic_id = c.clinic_id
            WHERE d.doctor_id = {doctor_id}
            ORDER BY t.clinic_id, t.telephone_id
        """
    }
    
    loggerManager.logger.info(f"Complete doctor profile queries for doctor_id: {doctor_id}, country: {country_code}")
    return queries
