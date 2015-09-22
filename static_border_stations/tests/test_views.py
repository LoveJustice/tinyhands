from django_webtest import WebTest
from django.core.urlresolvers import reverse
from datetime import date

from static_border_stations.tests.factories import BorderStationFactory
from accounts.tests.factories import SuperUserFactory

from static_border_stations.models import *
from dataentry.models import BorderStation


class TestBorderStations(WebTest):

    def setUp(self):
        self.BS = BorderStationFactory.create()
        self.superuser = SuperUserFactory.create()
        url = reverse("borderstations_update", kwargs={'pk': self.BS.id})
        self.response = self.app.get(url, user=self.superuser)
        self.form = self.response.form

    def test_border_station_create_view_should_exist(self):
        self.assertEquals(self.response.status_code, 200)

    def testUpdateStaff(self):
        form = self.form

        form.set("staff_set-0-first_name", "Joe")
        form.set("staff_set-0-last_name", "Shmo")
        form.set("staff_set-0-email", "joe@gmail.com")

        formResp = form.submit()

        self.assertEquals(302, formResp.status_code)

        bs = BorderStation.objects.get(id=self.BS.id).staff_set.get()
        self.assertEquals("Joe", bs.first_name)
        self.assertEquals("Shmo", bs.last_name)
        self.assertEquals("joe@gmail.com", bs.email)

    def testUpdateStaffWithoutEmail(self):
        form = self.form

        form.set("staff_set-0-first_name", "Joe")
        form.set("staff_set-0-last_name", "Shmo")

        formResp = form.submit()

        self.assertEquals(302, formResp.status_code)

        bs = BorderStation.objects.get(id=self.BS.id).staff_set.get()
        self.assertEquals("Joe", bs.first_name)
        self.assertEquals("Shmo", bs.last_name)

    def test_update_staff_fails_when_no_email_and_receive_money_distribution_form_checked(self):
        form = self.form

        form.set("staff_set-0-first_name", "Joe")
        form.set("staff_set-0-last_name", "Shmo")
        form.set("staff_set-0-receives_money_distribution_form", True)

        formResp = form.submit()

        self.assertEquals(200, formResp.status_code)
        self.assertEquals("Email cannot be blank when receives money distribution form is checked.", formResp.context["staff_form"].errors['__all__'][0])

    def testUpdateCommitteeMember(self):
        form = self.form

        form.set("committeemember_set-0-first_name", "bob")
        form.set("committeemember_set-0-last_name", "smith")
        form.set("committeemember_set-0-email", "bob@gmail.com")

        formResp = form.submit()

        self.assertEquals(302, formResp.status_code)

        bs = BorderStation.objects.get(id=self.BS.id).committeemember_set.get()
        self.assertEquals("bob", bs.first_name)
        self.assertEquals("smith", bs.last_name)
        self.assertEquals("bob@gmail.com", bs.email)

    def testUpdateCommitteeMemberWithoutEmail(self):
        form = self.form

        form.set("committeemember_set-0-first_name", "bob")
        form.set("committeemember_set-0-last_name", "smith")

        formResp = form.submit()

        self.assertEquals(302, formResp.status_code)

        bs = BorderStation.objects.get(id=self.BS.id).committeemember_set.get()
        self.assertEquals("bob", bs.first_name)
        self.assertEquals("smith", bs.last_name)

    def testUpdateLocation(self):
        form = self.form

        form.set("location_set-0-name", "SomeLocation")
        form.set("location_set-0-latitude", 1.23)
        form.set("location_set-0-longitude", 4.56)

        formResp = form.submit()

        self.assertEquals(302, formResp.status_code)

        bs = BorderStation.objects.get(id=self.BS.id).location_set.get()
        self.assertEquals("SomeLocation", bs.name)
        self.assertEquals(1.23, bs.latitude)
        self.assertEquals(4.56, bs.longitude)

    def testUpdateBorderStationDetails(self):
        form = self.form

        form.set("location_set-0-name", "SomeLocation")
        form.set("location_set-0-latitude", 1.23)
        form.set("location_set-0-longitude", 4.56)

        formResp = form.submit()

        self.assertEquals(302, formResp.status_code)

        bs = BorderStation.objects.get(id=self.BS.id).location_set.get()
        self.assertEquals("SomeLocation", bs.name)
        self.assertEquals(1.23, bs.latitude)
        self.assertEquals(4.56, bs.longitude)

    # TODO: Test editing borderstation info
    # TODO: Test adding/updating more Staff to borderstation
    # TODO: Test adding/updating more CommitteMembers to borderstation
    # TODO: Test adding/updating more Locations to borderstation


class BorderStationsCreationTest(WebTest):

    def setUp(self):
        self.superuser = SuperUserFactory.create()
        self.response = self.app.get(reverse('borderstations_create'), user=self.superuser)
        self.form = self.response.form
        BorderStation.objects.get_or_create(station_name="Test Station", station_code="TTT")

    def test_border_station_create_view_should_exist(self):
        self.assertEquals(self.response.status_code, 200)

    def test_border_station_create_view_form_fields_are_empty(self):
        fields = self.form.fields

        self.assertEquals('', fields['station_name'][0].value)
        self.assertEquals('', fields['station_code'][0].value)
        self.assertEquals('', fields['date_established'][0].value)
        self.assertEquals(False, fields['has_shelter'][0].checked)
        self.assertEquals('', fields['latitude'][0].value)
        self.assertEquals('', fields['longitude'][0].value)

        self.assertEquals('', fields['staff_set-0-first_name'][0].value)
        self.assertEquals('', fields['staff_set-0-last_name'][0].value)
        self.assertEquals('', fields['staff_set-0-email'][0].value)
        self.assertEquals(False, fields['staff_set-0-receives_money_distribution_form'][0].checked)

        self.assertEquals('', fields['committeemember_set-0-first_name'][0].value)
        self.assertEquals('', fields['committeemember_set-0-last_name'][0].value)
        self.assertEquals('', fields['committeemember_set-0-email'][0].value)
        self.assertEquals(False, fields['committeemember_set-0-receives_money_distribution_form'][0].checked)

        self.assertEquals('', fields['location_set-0-name'][0].value)
        self.assertEquals('', fields['location_set-0-latitude'][0].value)
        self.assertEquals('', fields['location_set-0-longitude'][0].value)

    def test_border_station_create_view_form_submission_fails_with_empty_fields(self):
        form_response = self.form.submit()

        field_errors = form_response.context['form'].errors

        self.assertEquals(200, form_response.status_code)
        self.assertEquals('This field is required.', field_errors['station_name'][0])
        self.assertEquals('This field is required.', field_errors['station_code'][0])
        self.assertEquals('This field is required.', field_errors['date_established'][0])
        self.assertEquals('This field is required.', field_errors['latitude'][0])
        self.assertEquals('This field is required.', field_errors['longitude'][0])

    def test_border_station_create_view_form_submission_fails_with_dupilicate_station_code(self):
        form = self.form

        form.set('station_name', 'Station 1')
        form.set('station_code', 'TTT')
        form.set('date_established', '1/1/11')
        form.set('longitude', '3')
        form.set('latitude', '4')
        form_response = form.submit()

        field_errors = form_response.context['form'].errors

        self.assertEquals(200, form_response.status_code)
        self.assertEquals('Border station with this Station code already exists.', field_errors['station_code'][0])

    def test_border_station_create_view_form_submission_fails_with_invalid_date(self):
        form = self.form

        form.set('station_name', 'Station A')
        form.set('station_code', 'STA')
        form.set('date_established', '1/1/1')
        form.set('longitude', '3')
        form.set('latitude', '4')
        form_response = form.submit()

        field_errors = form_response.context['form'].errors

        self.assertEquals(200, form_response.status_code)
        self.assertEquals('Enter a valid date.', field_errors['date_established'][0])

    def test_border_station_create_view_form_submission_fails_with_invalid_email(self):
        form = self.form

        form.set('station_name', 'Station B')
        form.set('station_code', 'STB')
        form.set('date_established', '1/1/11')
        form.set('longitude', '3')
        form.set('latitude', '4')

        form.set('staff_set-0-first_name', 'Bob')
        form.set('staff_set-0-last_name', 'Smith')
        form.set('staff_set-0-email', 'bobsmith')
        form.set('staff_set-0-receives_money_distribution_form', True)

        form.set('committeemember_set-0-first_name', 'Jack')
        form.set('committeemember_set-0-last_name', 'Smith')
        form.set('committeemember_set-0-email', 'jacksmith')
        form.set('committeemember_set-0-receives_money_distribution_form', True)

        form_response = form.submit()
        staff_errors = form_response.context['staff_form'].errors
        cm_errors = form_response.context['cm_form'].errors

        self.assertEquals(200, form_response.status_code)
        self.assertEquals('Enter a valid email address.', staff_errors['email'][0])
        self.assertEquals('Enter a valid email address.', cm_errors['email'][0])

    def test_border_station_create_view_form_submits_with_correct_fields(self):
        form = self.form

        form.set('station_name', 'Station C')
        form.set('station_code', 'STC')
        form.set('date_established', '1/1/11')
        form.set('longitude', '3')
        form.set('latitude', '4')
        form_response = form.submit()

        self.assertEquals(302, form_response.status_code)
        self.assertEquals('', form_response.errors)

    def test_border_station_create_view_form_submits_with_all_fields(self):
        form = self.form

        form.set('station_name', 'Station D')
        form.set('station_code', 'STD')
        form.set('date_established', '1/1/11')
        form.set('latitude', '4')
        form.set('longitude', '3')

        form.set('staff_set-0-first_name', 'Bob')
        form.set('staff_set-0-last_name', 'Smith')
        form.set('staff_set-0-email', 'bobsmith@test.org')
        form.set('staff_set-0-receives_money_distribution_form', True)

        form.set('committeemember_set-0-first_name', 'Jack')
        form.set('committeemember_set-0-last_name', 'Smith')
        form.set('committeemember_set-0-email', 'jacksmith@test.org')
        form.set('committeemember_set-0-receives_money_distribution_form', True)

        form.set('location_set-0-name', 'Nepal')
        form.set('location_set-0-latitude', '1')
        form.set('location_set-0-longitude', '2')

        form_response = form.submit()

        self.assertEquals(302, form_response.status_code)
        self.assertEquals('', form_response.errors)

        updatedStation = BorderStation.objects.get(station_name="Station D")
        self.assertEquals('Station D', updatedStation.station_name)
        self.assertEquals('STD', updatedStation.station_code)
        self.assertEquals(date(2011, 1, 1), updatedStation.date_established)
        self.assertEquals(4, updatedStation.latitude)
        self.assertEquals(3, updatedStation.longitude)

        staffMember = updatedStation.staff_set.get()
        self.assertEquals('Bob', staffMember.first_name)
        self.assertEquals('Smith', staffMember.last_name)
        self.assertEquals('bobsmith@test.org', staffMember.email)
        self.assertEquals(True, staffMember.receives_money_distribution_form)

        committeeMember = updatedStation.committeemember_set.get()
        self.assertEquals('Jack', committeeMember.first_name)
        self.assertEquals('Smith', committeeMember.last_name)
        self.assertEquals('jacksmith@test.org', committeeMember.email)
        self.assertEquals(True, committeeMember.receives_money_distribution_form)

        location = updatedStation.location_set.get()
        self.assertEquals('Nepal', location.name)
        self.assertEquals(1, location.latitude)
        self.assertEquals(2, location.longitude)

    def test_border_station_create_view_form_submits_with_no_email(self):
        form = self.form

        form.set('station_name', 'Station D')
        form.set('station_code', 'STD')
        form.set('date_established', '1/1/11')
        form.set('latitude', '4')
        form.set('longitude', '3')

        form.set('staff_set-0-first_name', 'Bob')
        form.set('staff_set-0-last_name', 'Smith')

        form.set('committeemember_set-0-first_name', 'Jack')
        form.set('committeemember_set-0-last_name', 'Smith')

        form.set('location_set-0-name', 'Nepal')
        form.set('location_set-0-latitude', '1')
        form.set('location_set-0-longitude', '2')

        form_response = form.submit()

        self.assertEquals(302, form_response.status_code)
        self.assertEquals('', form_response.errors)

        updatedStation = BorderStation.objects.get(station_name="Station D")
        self.assertEquals('Station D', updatedStation.station_name)
        self.assertEquals('STD', updatedStation.station_code)
        self.assertEquals(date(2011, 1, 1), updatedStation.date_established)
        self.assertEquals(4, updatedStation.latitude)
        self.assertEquals(3, updatedStation.longitude)

        staffMember = updatedStation.staff_set.get()
        self.assertEquals('Bob', staffMember.first_name)
        self.assertEquals('Smith', staffMember.last_name)

        committeeMember = updatedStation.committeemember_set.get()
        self.assertEquals('Jack', committeeMember.first_name)
        self.assertEquals('Smith', committeeMember.last_name)

        location = updatedStation.location_set.get()
        self.assertEquals('Nepal', location.name)
        self.assertEquals(1, location.latitude)
        self.assertEquals(2, location.longitude)
