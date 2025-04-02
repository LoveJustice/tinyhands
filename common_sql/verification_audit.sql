WITH myconstants (country_name, start_date, end_date) as
             (values ('Liberia', date '2024-04-01', date '2025-03-31')),
     all_irfs_for_country_in_range as
         (select irf.irf_number,
                 irf.computed_total_red_flags,
                 irf.control_reported_total_red_flags,
                 irf.how_sure_was_trafficking,
                 irf.verified_evidence_categorization,
                 irf.date_of_interception,
                 irf.verified_date,
                 '' as spot_check,
                 '' as status,
                 '' as reason_for_suggested_change,
                 irf.case_notes as case_narrative,
                 irf.logbook_notes as compliance_notes
          from dataentry_irfcommon irf
                   left join public.dataentry_borderstation station on irf.station_id = station.id
                   left join public.dataentry_country country
                             on station.operating_country_id = country.id,
               myconstants
          where country.name = myconstants.country_name
            and irf.verified_date > myconstants.start_date
            and irf.verified_date < myconstants.end_date)
-- Use this to determine what the percentage is of the total
-- select count(*)
-- from all_irfs_for_country_in_range;

select '1 - Low Risk High Risk' as reason_for_picking,
       all_irfs_for_country_in_range.*
from all_irfs_for_country_in_range
where (all_irfs_for_country_in_range.computed_total_red_flags = 0
    OR (all_irfs_for_country_in_range.computed_total_red_flags IS NULL and
        all_irfs_for_country_in_range.control_reported_total_red_flags = 0))
    AND all_irfs_for_country_in_range.how_sure_was_trafficking >= 1
    AND all_irfs_for_country_in_range.how_sure_was_trafficking <= 3
UNION
select '2 - Low Flag Evidence' as reason_for_picking,
       all_irfs_for_country_in_range.*
from all_irfs_for_country_in_range
where (all_irfs_for_country_in_range.computed_total_red_flags < 10
    OR (all_irfs_for_country_in_range.computed_total_red_flags IS NULL and
        all_irfs_for_country_in_range.control_reported_total_red_flags < 10))
    and all_irfs_for_country_in_range.verified_evidence_categorization = 'Evidence of Trafficking'
UNION
select '3 - Remaining High Risk' as reason_for_picking,
       all_irfs_for_country_in_range.*
from all_irfs_for_country_in_range
where (all_irfs_for_country_in_range.verified_evidence_categorization = 'High Risk of Trafficking')
UNION
select '4 - Remaining Evidence' as reason_for_picking,
       all_irfs_for_country_in_range.*
from all_irfs_for_country_in_range
where (all_irfs_for_country_in_range.verified_evidence_categorization = 'Evidence of Trafficking')
UNION
select '5 - Should Not Count' as reason_for_picking,
       all_irfs_for_country_in_range.*
from all_irfs_for_country_in_range
where (all_irfs_for_country_in_range.verified_evidence_categorization = 'Should not count as an Intercept')
order by reason_for_picking