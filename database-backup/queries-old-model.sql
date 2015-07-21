----------------------------------------------------------------
--- Model: Interceptee

-- START-QUERY
SELECT id, kind, interception_record_id,
	   full_name, trim(district) as district, trim(vdc) as vdc
FROM dataentry_interceptee
ORDER BY id;
-- END-QUERY interceptee

-- START-QUERY
select id
from dataentry_interceptee
order by id;
-- END-QUERY interceptee-ids

----------------------------------------------------------------
-- Model: VictimInterview

-- START-QUERY
SELECT vif_number,
	   victim_address_district,
	   victim_address_vdc
FROM dataentry_victiminterview
order by vif_number;
-- END-QUERY victim-address

-- START-QUERY
SELECT vif_number,
	   victim_guardian_address_district
	   victim_guardian_address_vdc
FROM dataentry_victiminterview
order by vif_number;
-- END-QUERY victim-guardian-address

-- START-QUERY
select vif_number as id
from dataentry_victiminterview
order by vif_number;
-- END-QUERY victim-interview-ids

----------------------------------------------------------------
-- Model: VictimInterviewPersonBox

-- START-QUERY
select id,
	   victim_interview_id,
	   address_district,
	   address_vdc
from dataentry_victiminterviewpersonbox
order by id;
-- END-QUERY person-box

-- START-QUERY
select id
from dataentry_victiminterviewpersonbox
order by id;
-- END-QUERY person-box-ids

----------------------------------------------------------------
-- Model: VictimInterviewLocationBox

-- START-QUERY
select id,
	   victim_interview_id,
	   district,
	   vdc
from dataentry_victiminterviewlocationbox
order by id;
-- END-QUERY location-box

-- START-QUERY
select id
from dataentry_victiminterviewlocationbox
order by id;
-- END-QUERY location-box-ids


