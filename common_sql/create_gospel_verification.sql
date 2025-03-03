-- For Pycharm Ultimate select datasource as prod, schema postgres.public on the top right of this box --

--insert into dataentry_gospelverification  (vdf_id, station_id, status, form_entered_by_id, date_time_entered_into_system, date_time_last_updated)
    -- Check that this is right first by running without create, then comment the insert in above
    select id, station_id, 'approved' as status, form_entered_by_id, now(), now()--, vdf_number
        from dataentry_vdfcommon
        where vdf_number in ('FIX123', 'FIX123');


-- Now check if this was created
select * from dataentry_gospelverification
    left join public.dataentry_vdfcommon dv on dataentry_gospelverification.vdf_id = dv.id
    where vdf_number in ('FIX123', 'FIX123');


-- delete from dataentry_gospelverification where id in (3698, 3699);