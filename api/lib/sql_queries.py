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


def get_doctors_query(doctor_id=None, city=None, profession=None):
    """

    :param doctor_id: int doctor id
    :param city: string city name
    :param profession: string, profession
    :return:
    """
    if doctor_id:
        # Retrieve doctor's information
        query = f"""
                SELECT 
                    doctor_id, salutation, given_name, surname, full_name, gender, 
                    rate, branding, has_slots, allow_questions, url
                FROM doctors.doctors 
                WHERE doctor_id = {doctor_id}
                """

    elif city and profession:
        # Retrieve practitioners form the city
        profession = profession.upper()
        city = city.upper()
        query = f"""
                Retrieve practitioners form the city: {profession}, {city}
                """

    elif profession:
        # Retrieve all practitioner matching the profession
        profession = profession.upper()
        query = f"""
                Retrieve all practitioner matching the profession: {profession}
                """

    elif city:
        # Retrieve all practitioners of the specified city
        city = city.upper()
        query = f"""
                Retrieve all practitioners of the specified city: {city}
                """
    else:
        query = f"""
                Demo: Retrieve only few practitioners for demo
                """
    loggerManager.logger.info(query)
    return query





