select * from dataentry_irfcommon irf_no_original
         left join public.dataentry_borderstation station on irf_no_original.station_id = station.id
         left join public.dataentry_country country on station.operating_country_id = country.id
where irf_no_original.id not in (
    select irf_has_original.id from dataentry_irfcommon irf_has_original
         left join public.dataentry_irfattachmentcommon di on irf_has_original.id = di.interception_record_id
         where di.option = 'Original Form'
)
  and date_time_entered_into_system > now() - INTERVAL '1 year'
and country.name = 'Nepal';

select * from dataentry_suspect sf_no_original
         left join public.dataentry_borderstation station on sf_no_original.station_id = station.id
         left join public.dataentry_country country on station.operating_country_id = country.id
where sf_no_original.id not in (
    select sf_has_original.id from dataentry_suspect sf_has_original
        left join public.dataentry_suspectattachment ds on sf_has_original.id = ds.suspect_id
         where ds.option = 'Original Form'
)
  and date_time_entered_into_system > now() - INTERVAL '1 year'
and country.name = 'Nepal';


select * from dataentry_vdfcommon pvf_no_original
         left join public.dataentry_borderstation station on pvf_no_original.station_id = station.id
         left join public.dataentry_country country on station.operating_country_id = country.id
where pvf_no_original.id not in (
    select pvf_has_original.id from dataentry_vdfcommon pvf_has_original
        left join public.dataentry_vdfattachmentcommon ds on pvf_has_original.id = ds.vdf_id
         where ds.option = 'Original Form'
)
  and date_time_entered_into_system > now() - INTERVAL '1 year'
and country.name = 'Nepal';

select * from dataentry_locationform lf_no_original
         left join public.dataentry_borderstation station on lf_no_original.station_id = station.id
         left join public.dataentry_country country on station.operating_country_id = country.id
where lf_no_original.id not in (
    select lf_has_original.id from dataentry_locationform lf_has_original
        left join public.dataentry_locationattachment ds on lf_has_original.id = ds.lf_id
         where ds.option = 'Original Form'
)
  and date_time_entered_into_system > now() - INTERVAL '1 year'
and country.name = 'Nepal';