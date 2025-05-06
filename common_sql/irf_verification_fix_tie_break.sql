-- BE CAREFUL IF THIS HAPPENS ON AN IRF IN A PREVIOUS MONTH

--- Get all the verifications
select * from dataentry_irfverification
left join public.dataentry_irfcommon di on dataentry_irfverification.interception_record_id = di.id
where di.irf_number = 'GAU575';

--- Find the one that had a misclick or had wrong details and change it
update dataentry_irfverification
SET evidence_categorization = 'Evidence of Trafficking'
where id = <ID FROM ABOVE>

--- Update IRF common table from above to fix some statuses, if now verified, verified_date should come from latest irfverification
update dataentry_irfcommon
SET status = 'verified', verified_date = '2025-04-11', verified_evidence_categorization = 'Evidence of Trafficking'
where irf_number = <IRF NUMBER FROM ABOVE>;
