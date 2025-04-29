select irf.verified_evidence_categorization, sum(irf.number_of_victims) as pv_count
from dataentry_irfcommon irf
where staff_name like '%CJ%'
and date_time_entered_into_system < '2019-10-01'
group by irf.verified_evidence_categorization
