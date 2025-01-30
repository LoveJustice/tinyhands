from .google_lib import DB_Conn


def get_countries():
    parameters = {}
    sql_query = """SELECT id, name FROM public.dataentry_country"""
    with DB_Conn() as dbc:
        countries = dbc.ex_query(sql_query, parameters)
    return countries


def insert_country_string(sql_query, parameters, country):
    if country:
        sql_query += " AND country.name = %(country)s"
        parameters["country"] = country
    return sql_query, parameters


def get_suspect_evaluations(country=None):
    parameters = {}

    # Base SQL query
    sql_query = """
        SELECT
            suspect.sf_number AS sf_number,
            suspectevaluation.evaluation,
            country.name AS country,
            person.id AS person_id,
            person.arrested AS arrested,
            person.master_person_id AS master_person_id,
            suspect_information.interview_date AS interview_date
        FROM public.dataentry_person person
        INNER JOIN public.dataentry_suspect suspect ON suspect.merged_person_id = person.id
        INNER JOIN public.dataentry_suspectlegal suspectlegal ON suspectlegal.suspect_id = suspect.id
        INNER JOIN public.dataentry_borderstation borderstation ON borderstation.id = suspect.station_id
        INNER JOIN public.dataentry_country country ON country.id = borderstation.operating_country_id
        INNER JOIN public.dataentry_suspectevaluation suspectevaluation ON suspectevaluation.suspect_id = suspect.id
        INNER JOIN public.dataentry_suspectinformation suspect_information ON suspect_information.suspect_id = suspect.id
        WHERE suspectevaluation.evaluator_type = 'PV'
    """

    # Add country condition to SQL query if country is provided
    sql_query, parameters = insert_country_string(sql_query, parameters, country)
    with DB_Conn() as dbc:
        suspect_evaluations = dbc.ex_query(sql_query, parameters)

    return suspect_evaluations


def get_suspects(country=None):
    parameters = {}
    sql_query = """SELECT person.full_name AS full_name \
                            ,person.phone_contact AS phone_contact \
                            ,person.address_notes AS address_notes \
                            ,person.case_filed_against AS case_filed_against \
                            ,person.social_media AS social_media \
                            ,person.arrested AS arrested \
                            ,person.id AS person_id \
                            ,person.role AS role \
                            ,person.master_person_id AS master_person_id \
                            ,person.gender AS gender \
                            ,person.age AS age \
                            ,country.name AS country \
                            ,country.id AS operating_country_id \
                            ,borderstation.station_name AS station_name \
                            ,borderstation.id AS borderstation_id \
                            ,suspect.sf_number AS sf_number \
                            ,suspectlegal.arrest_date AS arrest_date \
                            ,suspectlegal.arrested AS suspect_arrested \
                            FROM public.dataentry_person person \
                            INNER JOIN public.dataentry_suspect suspect ON suspect.merged_person_id = person.id \
                            INNER JOIN public.dataentry_suspectlegal suspectlegal ON suspectlegal.suspect_id = suspect.id \
                            INNER JOIN public.dataentry_borderstation borderstation ON borderstation.id = suspect.station_id \
                            INNER JOIN public.dataentry_country country ON country.id = borderstation.operating_country_id"""
    if country:
        sql_query += " WHERE country.name = %(country)s"
        parameters["country"] = country
    with DB_Conn() as dbc:
        suspects = dbc.ex_query(sql_query, parameters)

    return suspects
#                             # ,suspectlegal.pv_attempt AS pv_attempt \

def get_irf(country=None):
    parameters = {}
    sql_query = """SELECT irfcommon.number_of_victims AS number_of_victims \
        ,irfcommon.number_of_traffickers AS number_of_traffickers \
        ,irfcommon.where_going_destination AS where_going_destination \
        ,irfcommon.irf_number AS irf_number \
        ,intercepteecommon.person_id AS person_id \
        ,irfcommon.date_of_interception AS date_of_interception \
        ,irfcommon.case_notes AS case_notes \
        ,person.arrested AS arrested \
        ,person.master_person_id AS master_person_id \
        ,country.name AS country \
        ,country.id AS operating_country_id \
        FROM public.dataentry_irfcommon irfcommon \
        INNER JOIN public.dataentry_intercepteecommon intercepteecommon ON intercepteecommon.interception_record_id = irfcommon.id \
        INNER JOIN public.dataentry_borderstation borderstation ON borderstation.id = irfcommon.station_id \
        INNER JOIN public.dataentry_country country ON country.id = borderstation.operating_country_id \
        INNER JOIN public.dataentry_person person ON person.id = intercepteecommon.person_id"""
    if country:
        sql_query += " WHERE country.name = %(country)s"
        parameters["country"] = country
    with DB_Conn() as dbc:
        irf_common = dbc.ex_query(sql_query, parameters)

    return irf_common


def get_vdf(country=None):
    parameters = {}
    sql_query = """SELECT person.arrested AS arrested \
        ,vdfcommon.station_id AS station_id \
        ,person.id AS person_id \
        ,vdfcommon.pv_recruited_how AS pv_recruited_how \
        ,vdfcommon.pv_recruited_no AS pv_recruited_no \
        ,vdfcommon.pv_recruited_broker AS pv_recruited_broker \
        ,vdfcommon.pv_recruited_agency AS pv_recruited_agency \
        ,vdfcommon.exploit_prostitution AS exploit_prostitution \
        ,vdfcommon.exploit_forced_labor AS exploit_forced_labor \
        ,vdfcommon.exploit_physical_abuse AS exploit_physical_abuse \
        ,vdfcommon.exploit_sexual_abuse AS exploit_sexual_abuse \
        ,vdfcommon.exploit_debt_bondage AS exploit_debt_bondage \
        ,vdfcommon.pv_expenses_paid_how AS pv_expenses_paid_how \
        ,vdfcommon.job_promised_amount AS job_promised_amount \
        ,vdfcommon.vdf_number AS vdf_number \
        ,person.full_name AS full_name \
        ,person.phone_contact AS phone_contact \
        ,person.address_notes AS address_notes \
        ,person.role AS role \
        ,person.social_media AS social_media \
        ,borderstation.station_name AS station_name \
        ,country.name AS country \
        ,country.id AS operating_country_id \
        ,person.master_person_id AS master_person_id \
        FROM public.dataentry_vdfcommon vdfcommon \
        INNER JOIN public.dataentry_person person ON person.id = vdfcommon.victim_id  \
        INNER JOIN public.dataentry_borderstation borderstation ON borderstation.id = vdfcommon.station_id \
        INNER JOIN public.dataentry_country country ON country.id = borderstation.operating_country_id"""
    if country:
        sql_query += " WHERE country.name = %(country)s"
        parameters["country"] = country
    with DB_Conn() as dbc:
        vdf = dbc.ex_query(sql_query, parameters)

    return vdf
