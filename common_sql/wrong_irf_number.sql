WITH constants as ( select 'BUS811' as correct_irf_number, 'BUS8111' as wrong_irf_number)
select irf.* from dataentry_irfcommon irf, constants where irf.irf_number = constants.wrong_irf_number;

WITH constants as ( select 'BUS811' as correct_irf_number, 'BUS8111' as wrong_irf_number)
select incident.* from dataentry_incident incident, constants where incident.incident_number = constants.wrong_irf_number;

update dataentry_irfcommon set irf_number = 'BUS811' where irf_number = 'BUS8111';

update dataentry_incident set incident_number = 'BUS811' where incident_number = 'BUS8111';