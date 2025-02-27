-- IRF --
-- select *
-- from dataentry_irfcommon irf
--     left join public.dataentry_borderstation station on irf.station_id = station.id
--     left join public.dataentry_country country on station.operating_country_id = country.id
-- where date_time_entered_into_system > '2024-01-01';

-- Person who matches a profile
select count(irf.irf_number), irf.profile, country.name
from dataentry_irfcommon irf
    left join public.dataentry_borderstation station on irf.station_id = station.id
    left join public.dataentry_country country on station.operating_country_id = country.id
where date_time_entered_into_system > '2024-01-01'
group by country.name, irf.profile
order by country.name, count(irf.irf_number) desc, irf.profile;

-- Area
select count(irf.irf_number), irf.where_going_destination, country.name
from dataentry_irfcommon irf
    left join public.dataentry_borderstation station on irf.station_id = station.id
    left join public.dataentry_country country on station.operating_country_id = country.id
where date_time_entered_into_system > '2024-01-01'
group by country.name, irf.where_going_destination
order by country.name, count(irf.irf_number) desc, irf.where_going_destination


-- Without resources
-- This one works different, each checkbox stores in a different field and the other box is separate
-- Let me know if you also need the counts for the other checkboxes, I'll need to write a query for each
select count(irf.irf_number), irf.evade_signs_other, country.name
from dataentry_irfcommon irf
    left join public.dataentry_borderstation station on irf.station_id = station.id
    left join public.dataentry_country country on station.operating_country_id = country.id
where date_time_entered_into_system > '2024-01-01'
group by country.name, irf.evade_signs_other
order by country.name, count(irf.irf_number) desc, irf.evade_signs_other;


-- PVF --
-- select *
-- from dataentry_vdfcommon vdf
--     left join public.dataentry_borderstation station on vdf.station_id = station.id
--     left join public.dataentry_country country on station.operating_country_id = country.id
-- where date_time_entered_into_system > '2024-01-01'

-- How was the PV recruited?
select count(vdf.vdf_number), vdf.pv_recruited_how, country.name
from dataentry_vdfcommon vdf
    left join public.dataentry_borderstation station on vdf.station_id = station.id
    left join public.dataentry_country country on station.operating_country_id = country.id
where date_time_entered_into_system > '2024-01-01'
group by country.name, vdf.pv_recruited_how
order by country.name, count(vdf.vdf_number) desc, vdf.pv_recruited_how;

-- How was the PV released?
select count(vdf.vdf_number), vdf.how_pv_released, country.name
from dataentry_vdfcommon vdf
    left join public.dataentry_borderstation station on vdf.station_id = station.id
    left join public.dataentry_country country on station.operating_country_id = country.id
where date_time_entered_into_system > '2024-01-01'
group by country.name, vdf.how_pv_released
order by country.name, count(vdf.vdf_number) desc, vdf.how_pv_released;

-- SF --

-- select *
-- from dataentry_suspect sf
--     left join public.dataentry_borderstation station on sf.station_id = station.id
--     left join public.dataentry_country country on station.operating_country_id = country.id
--     left join public.dataentry_person suspect_person on sf.merged_person_id = suspect_person.id
-- -- Careful with these, they might duplicate the number of sf_numbers
-- --     left join public.dataentry_suspect_associated_incidents associated_incidents on sf.id = associated_incidents.suspect_id
-- --     left join public.dataentry_suspectassociation association on sf.id = association.suspect_id
-- --     left join public.dataentry_suspect_incidents incidents on sf.id = incidents.suspect_id
-- --     left join dataentry_suspectattachment on sf.id = dataentry_suspectattachment.suspect_id
-- --     left join dataentry_suspectevaluation on sf.id = dataentry_suspectevaluation.suspect_id
-- --     left join public.dataentry_suspectinformation information on sf.id = information.suspect_id
-- --     left join public.dataentry_suspectlegal legal on sf.id = legal.suspect_id
-- where date_time_entered_into_system > '2024-01-01'

-- Police are unable
select count(sf.sf_number), legal.police_unable, country.name
from dataentry_suspect sf
    left join public.dataentry_borderstation station on sf.station_id = station.id
    left join public.dataentry_country country on station.operating_country_id = country.id
    left join public.dataentry_person suspect_person on sf.merged_person_id = suspect_person.id
    left join public.dataentry_suspectlegal legal on sf.id = legal.suspect_id
-- Careful with these, they might duplicate the number of sf_numbers
--     left join public.dataentry_suspect_associated_incidents associated_incidents on sf.id = associated_incidents.suspect_id
--     left join public.dataentry_suspectassociation association on sf.id = association.suspect_id
--     left join public.dataentry_suspect_incidents incidents on sf.id = incidents.suspect_id
--     left join dataentry_suspectattachment on sf.id = dataentry_suspectattachment.suspect_id
--     left join dataentry_suspectevaluation on sf.id = dataentry_suspectevaluation.suspect_id
--     left join public.dataentry_suspectinformation information on sf.id = information.suspect_id
where date_time_entered_into_system > '2024-01-01'
group by country.name, legal.police_unable
order by country.name, count(sf.sf_number) desc, legal.police_unable;



-- LF --

-- select *
-- from dataentry_locationform lf
--     left join public.dataentry_borderstation station on lf.station_id = station.id
--     left join public.dataentry_country country on station.operating_country_id = country.id
-- -- Careful with these, they might duplicate the number of lf_numbers
-- --     left join public.dataentry_locationassociation association on lf.id = association.lf_id
-- --     left join public.dataentry_locationattachment attachment on lf.id = attachment.lf_id
-- --     left join public.dataentry_locationevaluation evaluation on lf.id = evaluation.lf_id
-- --     left join public.dataentry_locationform_associated_incidents associated_incidents on lf.id = associated_incidents.locationform_id
-- --     left join public.dataentry_locationform_incidents incidents on lf.id = incidents.locationform_id
-- --    left join public.dataentry_locationinformation location_information on lf.id = location_information.lf_id
-- where date_time_entered_into_system > '2024-01-01'


select  count(lf.lf_number), location_information.place_kind, country.name
from dataentry_locationform lf
    left join public.dataentry_borderstation station on lf.station_id = station.id
    left join public.dataentry_country country on station.operating_country_id = country.id
-- Careful with these, they might duplicate the number of lf_numbers
--     left join public.dataentry_locationassociation association on lf.id = association.lf_id
--     left join public.dataentry_locationattachment attachment on lf.id = attachment.lf_id
--     left join public.dataentry_locationevaluation evaluation on lf.id = evaluation.lf_id
--     left join public.dataentry_locationform_associated_incidents associated_incidents on lf.id = associated_incidents.locationform_id
--     left join public.dataentry_locationform_incidents incidents on lf.id = incidents.locationform_id
    left join public.dataentry_locationinformation location_information on lf.id = location_information.lf_id
where date_time_entered_into_system > '2024-01-01'
group by country.name, location_information.place_kind
order by country.name, count(lf.lf_number) desc, location_information.place_kind;