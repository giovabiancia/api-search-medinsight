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
        # Retrieve doctor's information by ID
        query = f"""
                SELECT 
                    doctor_id, salutation, given_name, surname, full_name, gender, 
                    rate, branding, has_slots, allow_questions, url
                FROM doctors.doctors 
                WHERE doctor_id = {doctor_id}
                """

    elif city and profession:
        # Retrieve practitioners from the city with specific profession
        profession = profession.upper()
        city = city.upper()
        query = f"""
                SELECT 
                    doctor_id, salutation, given_name, surname, full_name, gender, 
                    rate, branding, has_slots, allow_questions, url
                FROM doctors.doctors 
                WHERE UPPER(city) = '{city}' AND UPPER(profession) = '{profession}'
                ORDER BY rate DESC
                LIMIT 50
                """

    elif profession:
        # Retrieve all practitioners matching the profession
        profession = profession.upper()
        query = f"""
                SELECT 
                    doctor_id, salutation, given_name, surname, full_name, gender, 
                    rate, branding, has_slots, allow_questions, url
                FROM doctors.doctors 
                WHERE UPPER(profession) = '{profession}'
                ORDER BY rate DESC
                LIMIT 50
                """

    elif city:
        # Retrieve all practitioners from the specified city
        city = city.upper()
        query = f"""
                SELECT 
                    doctor_id, salutation, given_name, surname, full_name, gender, 
                    rate, branding, has_slots, allow_questions, url
                FROM doctors.doctors 
                WHERE UPPER(city) = '{city}'
                ORDER BY rate DESC
                LIMIT 50
                """
    else:
        # Default: Retrieve sample practitioners for demo
        query = f"""
                SELECT 
                    doctor_id, salutation, given_name, surname, full_name, gender, 
                    rate, branding, has_slots, allow_questions, url
                FROM doctors.doctors 
                ORDER BY rate DESC
                LIMIT 20
                """
    
    loggerManager.logger.info(f"Query for country {country_code}: {query}")
    return query