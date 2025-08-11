#!/usr/bin/env
"""
@author:        Barnabas
@email:         barnabasaugustino@gmail.com
@website:       http://www.barnabasmatonya.com
@client:        Barnabas
@gitlab:        https://gitlab.com/projects28/medinsights-be.git
@domain name:
@Hostname:      DigitalOcean
@Description:   Query SQL semplificate
"""

from api.lib import loggerManager

def get_doctors_query(doctor_id=None, city=None, profession=None):
    """
    Genera query SQL per ottenere informazioni dottori
    
    :param doctor_id: int doctor id
    :param city: string city name
    :param profession: string, profession
    :return: SQL query string
    """
    
    base_query = """
        SELECT 
            doctor_id, salutation, given_name, surname, full_name, gender, 
            rate, branding, has_slots, allow_questions, url
        FROM doctors.doctors 
    """
    
    if doctor_id:
        # Dottore specifico
        query = f"{base_query} WHERE doctor_id = {doctor_id}"
        loggerManager.logger.info(f"Query per doctor ID: {doctor_id}")

    elif city and profession:
        # Città e professione
        profession = profession.upper()
        city = city.upper()
        query = f"""
            {base_query}
            WHERE UPPER(city) = '{city}' 
            AND UPPER(profession) LIKE '%{profession}%'
            ORDER BY surname, given_name
            LIMIT 50
        """
        loggerManager.logger.info(f"Query per professione '{profession}' in città '{city}'")

    elif profession:
        # Solo professione
        profession = profession.upper()
        query = f"""
            {base_query}
            WHERE UPPER(profession) LIKE '%{profession}%'
            ORDER BY city, surname, given_name
            LIMIT 50
        """
        loggerManager.logger.info(f"Query per professione: '{profession}'")

    elif city:
        # Solo città
        city = city.upper()
        query = f"""
            {base_query}
            WHERE UPPER(city) = '{city}'
            ORDER BY profession, surname, given_name
            LIMIT 50
        """
        loggerManager.logger.info(f"Query per città: '{city}'")
    
    else:
        # Demo - alcuni dottori
        query = f"""
            {base_query}
            ORDER BY doctor_id
            LIMIT 10
        """
        loggerManager.logger.info("Query demo: sample doctors")
    
    loggerManager.logger.debug(f"Query generata: {query}")
    return query