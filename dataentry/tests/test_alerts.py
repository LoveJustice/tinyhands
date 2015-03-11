from django_webtest import WebTest
from django.core.urlresolvers import reverse
from django.core import mail
from dataentry.models import VictimInterview
from accounts.tests.factories import SuperUserFactory
import datetime

import ipdb

class VIFAlertCheckerTests(WebTest):
	
    fixtures = ['geo-code-locations.json', "alerts/alerts.json"]
    
    def setUp(self):
        self.x = 1
        self.superuser = SuperUserFactory.create()
		
    def test_alert_sent_when_fir_filed_against(self):
        response = self.app.get(reverse('victiminterview_create'), user=self.superuser)
        form = response.form
        form.set('vif_number', 'CND2')
        form.set('date', datetime.datetime.now().strftime("%m/%d/%Y"))
        form.set('interviewer', "johnny be good")
        form.set('statement_read_before_beginning', True);
        form.set('victim_gender', "male")
        form.set('victim_name', "Sally Sue")
        form.set('victim_address_district', "Dhanusa")
        form.set('victim_address_vdc', 'Chalsa')
        form.set('migration_plans_education', True)
        form.set('primary_motivation_support_myself', True)
        form.set('victim_primary_means_of_travel_local_bus', True)
        form.set('victim_guardian_address_district', "Dhanusa")
        form.set('victim_guardian_address_vdc', "Chalsa")
        form.fields['victim_recruited_in_village'][0].checked = True
        form.fields['victim_stayed_somewhere_between'][0].checked = True
        form.set('meeting_at_border_yes', True)
        form.fields['victim_knew_details_about_destination'][0].checked = True
        form.set('awareness_before_interception_had_heard_not_how_bad', True)
        form.set('legal_action_against_traffickers_no', True)
        form.set('attitude_towards_tiny_hands_thankful', True)
        form.set('victim_heard_gospel_no', True)
        form.set('has_signature', True)
        #Fir filed against
        form.set('legal_action_against_traffickers_fir_filed', True)
        form.set('legal_action_fir_against_value', "Case 1")
        
        form_response = form.submit()
        field_errors = form_response.context['form'].errors
        form_2 = form_response.form
        form_2.set('ignore_warnings', True)
        form_response_2 = form_2.submit()
        
        ipdb.set_trace();
        self.assertEquals(form_response_2.status_code, 302)

        