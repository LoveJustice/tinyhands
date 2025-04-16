select * from legal_legalchargesuspectcharge sc;

select legal_status, count(*) from legal_legalchargesuspectcharge sc
    group by legal_status;

select legal_status, verdict, count(*) from legal_legalchargesuspectcharge sc
    group by legal_status, verdict;

select legal_status, verdict, to_char(date_trunc('year', sc.verdict_date), 'YYYY'), count(*) from legal_legalchargesuspectcharge sc
    group by legal_status, verdict, to_char(date_trunc('year', sc.verdict_date), 'YYYY');

select legal_status, verdict, to_char(date_trunc('year', sc.verdict_date), 'YYYY') as year_of_verdict, count(*)
from legal_legalchargesuspectcharge sc
    where verdict = 'Conviction'
    group by legal_status, verdict, to_char(date_trunc('year', sc.verdict_date), 'YYYY')
    order by year_of_verdict;

select legal_status, verdict, country.name as country_name, to_char(date_trunc('year', sc.verdict_date), 'YYYY') as year_of_verdict, count(*)
from legal_legalchargesuspectcharge sc
left join public.legal_legalcharge ll on sc.legal_charge_id = ll.id
left join public.dataentry_borderstation db on ll.station_id = db.id
left join dataentry_country country on db.operating_country_id = country.id
    where verdict = 'Conviction' and country.name = 'Nepal'
    group by legal_status, verdict, country.name, to_char(date_trunc('year', sc.verdict_date), 'YYYY')
    order by year_of_verdict;


-- convictions by year in Nepal
select legal_status, verdict, country.name as country_name, to_char(date_trunc('year', sc.verdict_date), 'YYYY') as year_of_verdict, count(*)
from legal_legalchargesuspectcharge sc
left join public.legal_legalcharge ll on sc.legal_charge_id = ll.id
left join public.dataentry_borderstation db on ll.station_id = db.id
left join dataentry_country country on db.operating_country_id = country.id
    where verdict = 'Conviction' and country.name = 'Nepal'
    group by legal_status, verdict, country.name, to_char(date_trunc('year', sc.verdict_date), 'YYYY')
    order by year_of_verdict;

-- Blank verdict date in Nepal
select ll.legal_charge_number, legal_status, verdict, country.name as country_name, sc.verdict_date as year_of_verdict
from legal_legalchargesuspectcharge sc
left join public.legal_legalcharge ll on sc.legal_charge_id = ll.id
left join public.dataentry_borderstation db on ll.station_id = db.id
left join dataentry_country country on db.operating_country_id = country.id
    where verdict = 'Conviction' and country.name = 'Nepal'
    and sc.verdict_date is null;

-- Average convictions in Nepal
select legal_status, verdict, country.name as country_name, to_char(date_trunc('year', sc.verdict_date), 'YYYY') as year_of_verdict, count(*)
from legal_legalchargesuspectcharge sc
left join public.legal_legalcharge ll on sc.legal_charge_id = ll.id
left join public.dataentry_borderstation db on ll.station_id = db.id
left join dataentry_country country on db.operating_country_id = country.id
    where verdict = 'Conviction' and country.name = 'Nepal'
    group by legal_status, verdict, country.name, to_char(date_trunc('year', sc.verdict_date), 'YYYY')
    order by year_of_verdict;

-- Straight average of convictions
select country.name as country_name, avg(sc.imprisonment_total_days) /365 as years
from legal_legalchargesuspectcharge sc
left join public.legal_legalcharge ll on sc.legal_charge_id = ll.id
left join public.dataentry_borderstation db on ll.station_id = db.id
left join dataentry_country country on db.operating_country_id = country.id
    where verdict = 'Conviction' and country.name = 'Nepal'
    group by country.name;

select country.name as country_name, sc.imprisonment_years, sc.imprisonment_days, count(*)
from legal_legalchargesuspectcharge sc
left join public.legal_legalcharge ll on sc.legal_charge_id = ll.id
left join public.dataentry_borderstation db on ll.station_id = db.id
left join dataentry_country country on db.operating_country_id = country.id
    where verdict = 'Conviction' and country.name = 'Nepal'
    group by country.name, sc.imprisonment_years, sc.imprisonment_days
    order by sc.imprisonment_years desc NULLS LAST, sc.imprisonment_days desc NULLS LAST;