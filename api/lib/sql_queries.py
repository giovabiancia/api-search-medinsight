#!/usr/bin/env
"""
@author:        Barnabas
@email:         barnabasaugustino@gmail.com
@website:       http://www.barnabasmatonya.com
@client:        Barnabas
@gitlab:        https://gitlab.com/projects28/medinsights-be.git
@domain name:
@Hostname:      DigitalOcean
@Description:   SQL queries per MedInsights API - supporto multi-paese (CORRECTED)

"""

from api.lib import loggerManager


def get_doctors_query(doctor_id=None, city=None, profession=None, country_code='IT'):
    """
    Get doctors query for specific country database
    :param doctor_id: int doctor id
    :param city: string city name
    :param profession: string, profession
    :param country_code: string, country code (DE, IT)
    :return: SQL query string
    """
    
    if doctor_id:
        # Retrieve doctor's complete information by ID
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
                    s.specialization_name, s.name_plural, s.is_popular, 1 as count
                FROM doctors.doctors d
                LEFT JOIN doctors.doctors_clinics_map dcm ON d.doctor_id = dcm.doctor_id
                LEFT JOIN doctors.clinics c ON dcm.clinic_id = c.clinic_id
                LEFT JOIN doctors.doctors_specializations_map dsm ON d.doctor_id = dsm.doctor_id
                LEFT JOIN doctors.specializations s ON dsm.specialization_id = s.specialization_id
                WHERE d.doctor_id = {doctor_id}
                ORDER BY d.doctor_id, c.clinic_id, s.specialization_name
                """

    elif city and profession:
        # Retrieve practitioners from the city with specific profession
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
                    s.specialization_name, s.name_plural, s.is_popular, 1 as count
                FROM doctors.doctors d
                LEFT JOIN doctors.doctors_clinics_map dcm ON d.doctor_id = dcm.doctor_id
                LEFT JOIN doctors.clinics c ON dcm.clinic_id = c.clinic_id
                LEFT JOIN doctors.doctors_specializations_map dsm ON d.doctor_id = dsm.doctor_id
                LEFT JOIN doctors.specializations s ON dsm.specialization_id = s.specialization_id
                WHERE UPPER(c.city_name) = '{city}' AND UPPER(s.specialization_name) = '{profession}'
                ORDER BY d.rate DESC, d.doctor_id, c.clinic_id, s.specialization_name
                """

    elif profession:
        # Retrieve all practitioners matching the profession
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
                    s.specialization_name, s.name_plural, s.is_popular, 1 as count
                FROM doctors.doctors d
                LEFT JOIN doctors.doctors_clinics_map dcm ON d.doctor_id = dcm.doctor_id
                LEFT JOIN doctors.clinics c ON dcm.clinic_id = c.clinic_id
                LEFT JOIN doctors.doctors_specializations_map dsm ON d.doctor_id = dsm.doctor_id
                LEFT JOIN doctors.specializations s ON dsm.specialization_id = s.specialization_id
                WHERE UPPER(s.specialization_name) = '{profession}'
                ORDER BY d.rate DESC, d.doctor_id, c.clinic_id, s.specialization_name
                """

    elif city:
        # Retrieve all practitioners from the specified city
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
                    s.specialization_name, s.name_plural, s.is_popular, 1 as count
                FROM doctors.doctors d
                LEFT JOIN doctors.doctors_clinics_map dcm ON d.doctor_id = dcm.doctor_id
                LEFT JOIN doctors.clinics c ON dcm.clinic_id = c.clinic_id
                LEFT JOIN doctors.doctors_specializations_map dsm ON d.doctor_id = dsm.doctor_id
                LEFT JOIN doctors.specializations s ON dsm.specialization_id = s.specialization_id
                WHERE UPPER(c.city_name) = '{city}'
                ORDER BY d.rate DESC, d.doctor_id, c.clinic_id, s.specialization_name
                """
    else:
        # Demo: Retrieve only few practitioners for demo
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
                    s.specialization_name, s.name_plural, s.is_popular, 1 as count
                FROM doctors.doctors d
                LEFT JOIN doctors.doctors_clinics_map dcm ON d.doctor_id = dcm.doctor_id
                LEFT JOIN doctors.clinics c ON dcm.clinic_id = c.clinic_id
                LEFT JOIN doctors.doctors_specializations_map dsm ON d.doctor_id = dsm.doctor_id
                LEFT JOIN doctors.specializations s ON dsm.specialization_id = s.specialization_id
                ORDER BY d.rate DESC, d.doctor_id, c.clinic_id, s.specialization_name
                LIMIT 50
                """
    
    loggerManager.logger.info(f"Query for country {country_code}: {query}")
    return query


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


def search_doctors_advanced_query(search_term=None, city=None, profession=None, 
                                 min_rate=None, max_rate=None, has_slots=None, 
                                 allow_questions=None, limit=None, country_code='IT'):
    """
    Advanced search for doctors with multiple filters
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
    
    base_query = """
            SELECT 
                -- Doctor details
                d.doctor_id, d.salutation, d.given_name, d.surname, d.full_name, d.gender, 
                d.rate, d.branding, d.has_slots, d.allow_questions, d.url,
                -- Clinic details via mapping table
                c.clinic_id, c.clinic_name, c.street, c.city_name, c.post_code, c.province,
                c.latitude, c.longitude, c.calendar_active, c.online_payment, c.non_doctor,
                c.default_fee, c.fee,
                -- Specialization details via mapping table
                s.specialization_name, s.name_plural, s.is_popular, 1 as count
            FROM doctors.doctors d
            LEFT JOIN doctors.doctors_clinics_map dcm ON d.doctor_id = dcm.doctor_id
            LEFT JOIN doctors.clinics c ON dcm.clinic_id = c.clinic_id
            LEFT JOIN doctors.doctors_specializations_map dsm ON d.doctor_id = dsm.doctor_id
            LEFT JOIN doctors.specializations s ON dsm.specialization_id = s.specialization_id
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
    
    base_query += " ORDER BY d.rate DESC, d.doctor_id, c.clinic_id, s.specialization_name"
    
    # Add LIMIT only if specified
    if limit is not None:
        base_query += f" LIMIT {limit}"
    
    loggerManager.logger.info(f"Advanced search query for country {country_code}: {base_query}")
    return base_query


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


def get_doctors_with_slots_query(city=None, profession=None, country_code='IT'):
    """
    Get doctors with available slots
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
                s.specialization_name, s.name_plural, s.is_popular, 1 as count
            FROM doctors.doctors d
            LEFT JOIN doctors.doctors_clinics_map dcm ON d.doctor_id = dcm.doctor_id
            LEFT JOIN doctors.clinics c ON dcm.clinic_id = c.clinic_id
            LEFT JOIN doctors.doctors_specializations_map dsm ON d.doctor_id = dsm.doctor_id
            LEFT JOIN doctors.specializations s ON dsm.specialization_id = s.specialization_id
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
    
    base_query += " ORDER BY d.rate DESC, c.nearest_slot_date ASC NULLS LAST"
    
    loggerManager.logger.info(f"Doctors with slots query for country {country_code}: {base_query}")
    return base_query


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