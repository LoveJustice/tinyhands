----------------------------------------------------------------
--- Model: Interceptee

SELECT id, kind, interception_record_id, full_name, trim(district), trim(vdc)
FROM dataentry_interceptee
ORDER BY id
limit 10;

----------------------------------------------------------------
-- Model: VictimInterview
-- District only

SELECT vif_number, victim_address_district
FROM dataentry_victiminterview
order by vif_number
limit 10;

-- VDC only
SELECT vif_number, victim_address_vdc
FROM dataentry_victiminterview
order by vif_number
limit 10;

-- District and VDC
SELECT vif_number, victim_address_district, victim_address_vdc
FROM dataentry_victiminterview
order by vif_number
limit 10;

----------------------------------------------------------------
-- Model: VictimInterviewPersonBox

select id, victim_interview_id, address_district, address_vdc
from dataentry_victiminterviewpersonbox
order by id
limit 10;

----------------------------------------------------------------
-- Model: VictimInterviewLocationBox

select id, victim_interview_id, district, vdc
from dataentry_victiminterviewlocationbox
order by id
limit 10;

