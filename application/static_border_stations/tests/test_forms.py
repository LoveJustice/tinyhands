from django.test import TestCase
from static_border_stations.forms import PersonForm
from factories import BorderStationFactory


class PersonFormTests(TestCase):

    def test_person_form_when_no_email_given_and_receives_money_distribution_form_is_true_should_have_error(self):
        border_station = BorderStationFactory.create()
        data = {'first_name': u'Andrew',
                'last_name': u'Smith',
                'receives_money_distribution_form': True,
                'email': u'',
                'border_station': border_station.id,
                u'id': None}

        form = PersonForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'][0], 'Email cannot be blank when receives money distribution form is checked.')
