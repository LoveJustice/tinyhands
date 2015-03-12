from django_webtest import WebTest
from django.core.urlresolvers import reverse
from django.core import mail
from django.conf import settings
from dataentry.models import VictimInterview
from accounts.tests.factories import SuperUserFactory
import datetime

import ipdb

class VIFAlertCheckerTests(WebTest):
	
    fixtures = ['geo-code-locations.json', "alerts/alerts.json", "portal/border_stations.json"]
    
    def setUp(self):
        self.superuser = SuperUserFactory.create()
		
    def test_alert_sent_when_fir_filed_against(self):
        response = self.app.get(reverse('victiminterview_create'), user=self.superuser)
        form = response.form
        form.set('vif_number', 'BHD111')
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
        form_2 = form_response.form
        form_2.set('ignore_warnings', True)
        form_response_2 = form_2.submit()
        
        self.assertEquals(form_response_2.status_code, 302)
        #check for email
        self.assertEquals(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEquals(self.superuser.email, email.to[0])
        self.assertEquals(settings.ADMIN_EMAIL_SENDER, email.from_email)
        
        
    def test_alert_sent_when_dofe_filed_against(self):
        response = self.app.get(reverse('victiminterview_create'), user=self.superuser)
        form = response.form
        form.set('vif_number', 'BHD112')
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
        #Dofe filed against
        form.set('legal_action_against_traffickers_dofe_complaint', True)
        form.set('legal_action_dofe_against_value', "Case 1")
        
        form_response = form.submit()
        form_2 = form_response.form
        form_2.set('ignore_warnings', True)
        form_response_2 = form_2.submit()
        
        self.assertEquals(form_response_2.status_code, 302)
        #check for email
        self.assertEquals(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEquals(self.superuser.email, email.to[0])
        self.assertEquals(settings.ADMIN_EMAIL_SENDER, email.from_email)
        
    def test_alert_sent_when_10_strength_points_filed_against(self):
        response = self.app.get(reverse('victiminterview_create'), user=self.superuser)
        form = response.form
        form.set('vif_number', 'BHD113')
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
        #Set to increase points over 10
        form.fields['victim_place_worked_involved_sending_girls_overseas'][1].checked = True
        
        form_response = form.submit()
        form_2 = form_response.form
        form_2.set('ignore_warnings', True)
        form_response_2 = form_2.submit()
        
        self.assertEquals(form_response_2.status_code, 302)
        #check for email
        self.assertEquals(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEquals(self.superuser.email, email.to[0])
        self.assertEquals(settings.ADMIN_EMAIL_SENDER, email.from_email)
        

class IRFAlertCheckerTests(WebTest):
	
    fixtures = ['geo-code-locations.json', "alerts/alerts.json", "portal/border_stations.json"]
    
    def setUp(self):
        self.superuser = SuperUserFactory.create()
        
    def test_alert_sent_when_trafficker_name_match(self):
        return
        response = self.app.get(reverse('interceptionrecord_create'), user=self.superuser)
        form = response.form
        form.set('irf_number', 'BHD114')
        form.set('date_time_of_interception', datetime.datetime.now().strftime("%m/%d/%Y"))
        form.set('location', 'Asia')
        form.set('staff_name', "johnny be good 7")
        form.set('drugged_or_drowsy', True)
        form.set('which_contact_church_member', True)
        form.set('how_sure_was_trafficking', 5)
        form.set('contact_noticed', True)
        form.set('interceptees-0-kind', "t")
        form.set('interceptees-0-full_name', "Some Bad Guy")
        form.set('interceptees-0-gender', "m")
        form.set('interceptees-0-age', '102')
        form.set('interceptees-0-district', 'Dhanusa')
        form.set('interceptees-0-vdc', 'Chalsa')
        form.set('interceptees-0-phone_contact', '9999999999')
        form.set('has_signature', True)
        form_response = form.submit()
        field_errors = form_response.context['form'].errors
        form_2 = form_response.form
        form_2.set('ignore_warnings', True)
        form_response_2 = form_2.submit()
        self.assertEquals(form_response_2.status_code, 302)
        
        self.assertEquals(form_response_2.status_code, 302)
        #check for email
        self.assertEquals(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEquals(self.superuser.email, email.to[0])
        self.assertEquals(settings.ADMIN_EMAIL_SENDER, email.from_email)
        
    def test_alert_sent_when_identified_trafficker(self):
        return
        response = self.app.get(reverse('interceptionrecord_create'), user=self.superuser)
        form = response.form
        form.set('irf_number', 'BHD115')
        form.set('date_time_of_interception', datetime.datetime.now().strftime("%m/%d/%Y"))
        form.set('location', 'Asia')
        form.set('staff_name', "johnny be good 7")
        form.set('drugged_or_drowsy', True)
        form.set('which_contact_church_member', True)
        form.set('how_sure_was_trafficking', 5)
        form.set('contact_noticed', True)
        form.set('interceptees-0-kind', "t")
        form.set('interceptees-0-full_name', "Some Bad Guy")
        form.set('interceptees-0-gender', "m")
        form.set('interceptees-0-age', '102')
        form.set('interceptees-0-district', 'Dhanusa')
        form.set('interceptees-0-vdc', 'Chalsa')
        form.set('interceptees-0-phone_contact', '9999999999')
        form.set('has_signature', True)
        form_response = form.submit()
        field_errors = form_response.context['form'].errors
        form_2 = form_response.form
        form_2.set('ignore_warnings', True)
        form_response_2 = form_2.submit()
        self.assertEquals(form_response_2.status_code, 302)
        
        self.assertEquals(form_response_2.status_code, 302)
        #check for email
        self.assertEquals(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEquals(self.superuser.email, email.to[0])
        self.assertEquals(settings.ADMIN_EMAIL_SENDER, email.from_email)
        
    def test_alert_sent_when_trafficker_in_custody(self):
        return
        response = self.app.get(reverse('interceptionrecord_create'), user=self.superuser)
        form = response.form
        form.set('irf_number', 'BHD116')
        form.set('date_time_of_interception', datetime.datetime.now().strftime("%m/%d/%Y"))
        form.set('location', 'Asia')
        form.set('staff_name', "johnny be good 7")
        form.set('drugged_or_drowsy', True)
        form.set('which_contact_church_member', True)
        form.set('how_sure_was_trafficking', 5)
        form.set('contact_noticed', True)
        form.set('interceptees-0-kind', "t")
        form.set('interceptees-0-full_name', "Some Bad Guy")
        form.set('interceptees-0-gender', "m")
        form.set('interceptees-0-age', '102')
        form.set('interceptees-0-district', 'Dhanusa')
        form.set('interceptees-0-vdc', 'Chalsa')
        form.set('interceptees-0-phone_contact', '9999999999')
        form.set('has_signature', True)
        form_response = form.submit()
        field_errors = form_response.context['form'].errors
        form_2 = form_response.form
        form_2.set('ignore_warnings', True)
        form_response_2 = form_2.submit()
        self.assertEquals(form_response_2.status_code, 302)
        
        self.assertEquals(form_response_2.status_code, 302)
        #check for email
        self.assertEquals(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEquals(self.superuser.email, email.to[0])
        self.assertEquals(settings.ADMIN_EMAIL_SENDER, email.from_email)