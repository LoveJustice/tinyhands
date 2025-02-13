select
	irf.irf_number,
	case
		when irf.computed_total_red_flags is null and irf.control_reported_total_red_flags is null then 0
		when irf.computed_total_red_flags is null then irf.control_reported_total_red_flags
		else irf.computed_total_red_flags
	end as red_flags,
	irf.how_sure_was_trafficking,
	irf.verified_evidence_categorization,
	irf.date_of_interception
from
	dataentry_irfcommon irf join
	dataentry_borderstation bs on bs.id = irf.station_id join
	dataentry_country c on c.id = bs.operating_country_id
where
	c.name = 'Malawi' and
	irf.verified_date >= '2024-08-01' and
	irf.verified_date < '2025-02-01' and
	irf.verified_evidence_categorization like '%Trafficking' and
	bs.station_code != 'MNZ'