-- Useful to find IRFs that are causing errors on the data collection indicators page because they don't have associated incident
select *
from  (
	select
		c.name,
		irf.irf_number,
		inc.incident_number,
		irf.date_of_interception
	from
		dataentry_irfcommon irf join
		dataentry_borderstation bs on bs.id = irf.station_id join
		dataentry_country c on c.id = bs.operating_country_id left join
		dataentry_incident inc on inc.incident_number = irf.irf_number
	)
where incident_number is null;
