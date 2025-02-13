select
	lc.legal_charge_number,
	ls.arrest_date,
	lc."location",
	p.full_name,
	lc.station_id,
	ls.arrest_submitted_date,
	ls.verified_date
from
	legal_legalcharge lc join
	legal_legalchargesuspect ls on ls.legal_charge_id = lc.id join
	dataentry_suspect s on s.id = ls.sf_id join
	dataentry_person p on p.id = s.merged_person_id join
	dataentry_borderstation bs on bs.id = lc.station_id join
	dataentry_country c on c.id = bs.operating_country_id
where
	c.name = 'Uganda' and
	ls.verified_date > '2024-12-01'