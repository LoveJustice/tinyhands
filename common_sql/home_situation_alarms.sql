select * from dataentry_vdfcommon;

select * from dataentry_vdfcommon
left join public.dataentry_borderstation db on dataentry_vdfcommon.station_id = db.id
left join public.dataentry_country country on db.operating_country_id = country.id
where country.name = 'Nepal';

select vdf.total_situational_alarms, vdf.where_victim_sent, vdf.why_sent_home_with_with_alarms, date_time_entered_into_system from dataentry_vdfcommon vdf
left join public.dataentry_borderstation db on vdf.station_id = db.id
left join public.dataentry_country country on db.operating_country_id = country.id
where country.name = 'Nepal'
  and vdf.where_victim_sent like 'Home%'
  and total_situational_alarms >= 10;

-- Where do we send them if they have more than 9 alarms
select 'Yes' as more_than_9_alarms, country.name, vdf.where_victim_sent, count(*) from dataentry_vdfcommon vdf
left join public.dataentry_borderstation db on vdf.station_id = db.id
left join public.dataentry_country country on db.operating_country_id = country.id
where country.name = 'Nepal'
  and total_situational_alarms > 9
group by country.name, vdf.where_victim_sent;

-- Distribution of PVFs by total number of alarms
select country.name, vdf.total_situational_alarms, count(*) from dataentry_vdfcommon vdf
left join public.dataentry_borderstation db on vdf.station_id = db.id
left join public.dataentry_country country on db.operating_country_id = country.id
where country.name = 'Nepal'
group by country.name, vdf.total_situational_alarms
order by total_situational_alarms;

-- Of all PVFs, where was the victim sent?
select country.name, vdf.where_victim_sent, count(*), count(*) filter(where vdf.total_situational_alarms > 9) as more_than_9_alarms from dataentry_vdfcommon vdf
left join public.dataentry_borderstation db on vdf.station_id = db.id
left join public.dataentry_country country on db.operating_country_id = country.id
where country.name = 'Nepal'
group by country.name, vdf.where_victim_sent
order by where_victim_sent