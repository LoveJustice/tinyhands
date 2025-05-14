update dataentry_vdfcommon pvf_to_update set date_time_last_updated = now(), how_pv_released = 'Someone else picked up the PV from staff care'
    where pvf_to_update.id in (
        select pvf.id from dataentry_vdfcommon pvf
        left join public.dataentry_borderstation db on pvf.station_id = db.id
        left join public.dataentry_country dc on db.operating_country_id = dc.id
        where dc.name in ('Rwanda', 'South Africa', 'Sierra Leone')
        and pvf.how_pv_released = 'Someone came to station/shelter to pick up the PV'
);

update dataentry_vdfcommon pvf_to_update set date_time_last_updated = now(), how_pv_released = 'Staff arranged transport for the PV to go alone'
    where pvf_to_update.id in (
        select pvf.id from dataentry_vdfcommon pvf
        left join public.dataentry_borderstation db on pvf.station_id = db.id
        left join public.dataentry_country dc on db.operating_country_id = dc.id
        where dc.name in ('Rwanda', 'South Africa', 'Sierra Leone')
        and pvf.how_pv_released = 'Staff arranged transportation for the PV to travel alone'
);

update dataentry_vdfcommon pvf_to_update set date_time_last_updated = now(), how_pv_released = 'Staff took PV to the next place'
    where pvf_to_update.id in (
        select pvf.id from dataentry_vdfcommon pvf
        left join public.dataentry_borderstation db on pvf.station_id = db.id
        left join public.dataentry_country dc on db.operating_country_id = dc.id
        where dc.name in ('Rwanda', 'South Africa', 'Sierra Leone')
        and pvf.how_pv_released = 'Staff accompanied the PV during travel'
);


update dataentry_vdfcommon pvf_to_update set date_time_last_updated = now(), where_victim_sent = 'Home (back to permanent residence)'
    where pvf_to_update.id in (
        select pvf.id from dataentry_vdfcommon pvf
        left join public.dataentry_borderstation db on pvf.station_id = db.id
        left join public.dataentry_country dc on db.operating_country_id = dc.id
        where dc.name in ('Rwanda', 'South Africa', 'Sierra Leone')
        and pvf.where_victim_sent = 'Home to stay with guardians'
);

update dataentry_vdfcommon pvf_to_update set date_time_last_updated = now(), where_victim_sent = 'Residence of other relatives'
    where pvf_to_update.id in (
        select pvf.id from dataentry_vdfcommon pvf
        left join public.dataentry_borderstation db on pvf.station_id = db.id
        left join public.dataentry_country dc on db.operating_country_id = dc.id
        where dc.name in ('Rwanda', 'South Africa', 'Sierra Leone')
        and pvf.where_victim_sent = 'Sent to stay with other relatives'
);

update dataentry_vdfcommon pvf_to_update set date_time_last_updated = now(), where_victim_sent = 'Partner organization or another NGO'
    where pvf_to_update.id in (
        select pvf.id from dataentry_vdfcommon pvf
        left join public.dataentry_borderstation db on pvf.station_id = db.id
        left join public.dataentry_country dc on db.operating_country_id = dc.id
        where dc.name in ('Rwanda', 'South Africa', 'Sierra Leone')
        and pvf.where_victim_sent = 'Sent to Partner Organization'
);
update dataentry_vdfcommon pvf_to_update set date_time_last_updated = now(), where_victim_sent = 'Government Agency'
    where pvf_to_update.id in (
        select pvf.id from dataentry_vdfcommon pvf
        left join public.dataentry_borderstation db on pvf.station_id = db.id
        left join public.dataentry_country dc on db.operating_country_id = dc.id
        where dc.name in ('Rwanda', 'South Africa', 'Sierra Leone')
        and pvf.where_victim_sent = 'Government agency'
);

update dataentry_vdfcommon pvf_to_update set date_time_last_updated = now(), share_gospel_resource = False
    where pvf_to_update.id in (
        select pvf.share_gospel_resource, pvf.share_gospel_tract, pvf.share_gospel_film, pvf.share_gospel_oral, pvf.share_gospel_other from dataentry_vdfcommon pvf
        left join public.dataentry_borderstation db on pvf.station_id = db.id
        left join public.dataentry_country dc on db.operating_country_id = dc.id
        where dc.name in ('Rwanda', 'South Africa', 'Sierra Leone')
        and not pvf.share_gospel_film and not pvf.share_gospel_tract and pvf.share_gospel_other = '' and pvf.share_gospel_resource
);

