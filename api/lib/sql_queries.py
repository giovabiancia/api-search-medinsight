#!/usr/bin/env
"""
@author:        Barnabas
@email:         barnabasaugustino@gmail.com
@website:       http://www.barnabasmatonya.com
@client:        Barnabas
@gitlab:
@domain name:
@Hostname:      DigitalOcean
@Description:

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
                    -- Clinic details
                    c.clinic_id, c.clinic_name, c.street, c.city_name, c.post_code, c.province,
                    c.latitude, c.longitude, c.calendar_active, c.online_payment, c.non_doctor,
                    c.default_fee, c.fee,
                    -- Specialization details
                    s.specialization_name, s.name_plural, s.is_popular, s.count
                FROM doctors.doctors d
                LEFT JOIN doctors.clinics c ON d.doctor_id = c.doctor_id
                LEFT JOIN doctors.specializations s ON d.doctor_id = s.doctor_id
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
                    -- Clinic details
                    c.clinic_id, c.clinic_name, c.street, c.city_name, c.post_code, c.province,
                    c.latitude, c.longitude, c.calendar_active, c.online_payment, c.non_doctor,
                    c.default_fee, c.fee,
                    -- Specialization details
                    s.specialization_name, s.name_plural, s.is_popular, s.count
                FROM doctors.doctors d
                LEFT JOIN doctors.clinics c ON d.doctor_id = c.doctor_id
                LEFT JOIN doctors.specializations s ON d.doctor_id = s.doctor_id
                WHERE UPPER(c.city_name) = '{city}' AND UPPER(s.specialization_name) = '{profession}'
                ORDER BY d.rate DESC, d.doctor_id, c.clinic_id, s.specialization_name
                LIMIT 50
                """

    elif profession:
        # Retrieve all practitioners matching the profession
        profession = profession.upper()
        query = f"""
                SELECT 
                    -- Doctor details
                    d.doctor_id, d.salutation, d.given_name, d.surname, d.full_name, d.gender, 
                    d.rate, d.branding, d.has_slots, d.allow_questions, d.url,
                    -- Clinic details
                    c.clinic_id, c.clinic_name, c.street, c.city_name, c.post_code, c.province,
                    c.latitude, c.longitude, c.calendar_active, c.online_payment, c.non_doctor,
                    c.default_fee, c.fee,
                    -- Specialization details
                    s.specialization_name, s.name_plural, s.is_popular, s.count
                FROM doctors.doctors d
                LEFT JOIN doctors.clinics c ON d.doctor_id = c.doctor_id
                LEFT JOIN doctors.specializations s ON d.doctor_id = s.doctor_id
                WHERE UPPER(s.specialization_name) = '{profession}'
                ORDER BY d.rate DESC, d.doctor_id, c.clinic_id, s.specialization_name
                LIMIT 50
                """

    elif city:
        # Retrieve all practitioners from the specified city
        city = city.upper()
        query = f"""
                SELECT 
                    -- Doctor details
                    d.doctor_id, d.salutation, d.given_name, d.surname, d.full_name, d.gender, 
                    d.rate, d.branding, d.has_slots, d.allow_questions, d.url,
                    -- Clinic details
                    c.clinic_id, c.clinic_name, c.street, c.city_name, c.post_code, c.province,
                    c.latitude, c.longitude, c.calendar_active, c.online_payment, c.non_doctor,
                    c.default_fee, c.fee,
                    -- Specialization details
                    s.specialization_name, s.name_plural, s.is_popular, s.count
                FROM doctors.doctors d
                LEFT JOIN doctors.clinics c ON d.doctor_id = c.doctor_id
                LEFT JOIN doctors.specializations s ON d.doctor_id = s.doctor_id
                WHERE UPPER(c.city_name) = '{city}'
                ORDER BY d.rate DESC, d.doctor_id, c.clinic_id, s.specialization_name
                LIMIT 50
                """
    else:
        # Default: Retrieve sample practitioners for demo
        query = f"""
                SELECT 
                    -- Doctor details
                    d.doctor_id, d.salutation, d.given_name, d.surname, d.full_name, d.gender, 
                    d.rate, d.branding, d.has_slots, d.allow_questions, d.url,
                    -- Clinic details
                    c.clinic_id, c.clinic_name, c.street, c.city_name, c.post_code, c.province,
                    c.latitude, c.longitude, c.calendar_active, c.online_payment, c.non_doctor,
                    c.default_fee, c.fee,
                    -- Specialization details
                    s.specialization_name, s.name_plural, s.is_popular, s.count
                FROM doctors.doctors d
                LEFT JOIN doctors.clinics c ON d.doctor_id = c.doctor_id
                LEFT JOIN doctors.specializations s ON d.doctor_id = s.doctor_id
                ORDER BY d.rate DESC, d.doctor_id, c.clinic_id, s.specialization_name
                LIMIT 20
                """
    
    loggerManager.logger.info(f"Query for country {country_code}: {query}")
    return query