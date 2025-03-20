-- Get the IRF based on the number in the screenshot
select irf_number, date_time_entered_into_system, * from dataentry_irfcommon
    where irf_number = 'DAC3088';

-- Verify that an incident was created around the same time, but has the wrong number
select incident_number, * from dataentry_incident
    where date_time_entered_into_system > '2025-02-25 09:26:13' and date_time_entered_into_system < '2025-02-25 09:26:14'
    --where dataentry_incident.incident_number like 'DAC308%'

-- Verify that no IRF has been created with that incident number
select irf_number, date_time_entered_into_system, * from dataentry_irfcommon
    where irf_number = 'DAC3089';

-- An IRF has been created with that incident number?
-- copy all the fields from the already used incident to one that has the right number
insert into dataentry_incident (incident_number, status, date_time_entered_into_system, date_time_last_updated, form_version, incident_date, summary, form_entered_by_id, station_id)
    select 'DAC3088', existing_incident.status, existing_incident.date_time_entered_into_system, existing_incident.date_time_last_updated, existing_incident.form_version,  existing_incident.incident_date, existing_incident.summary, existing_incident.form_entered_by_id, existing_incident.station_id
    from dataentry_incident existing_incident
    where existing_incident.incident_number = 'DAC3089'

-- Verify that the new incident exists
select incident_number, * from dataentry_incident
    where dataentry_incident.incident_number like 'DAC3088'