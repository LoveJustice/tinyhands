-- Used with monitoring get_monitoring_time_for_staff to populate Monitor IBR
select
	bs.station_code,
	irf.staff_who_noticed,
	irf.number_of_victims,
	irf.verified_evidence_categorization
from
	dataentry_irfcommon irf join
	dataentry_borderstation bs on bs.id = irf.station_id join
	dataentry_country c on c.id = bs.operating_country_id
where
	irf.verified_date >= '2024-07-01' and
	irf.verified_date < '2025-01-01' and
	irf.verified_evidence_categorization like '%Trafficking'