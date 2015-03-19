import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyInteger
from accounts.tests.factories import SuperUserFactory
from dataentry.models import *
from datetime import date
import ipdb

class IrfFactory(DjangoModelFactory):
    class Meta:
        model = InterceptionRecord

    form_entered_by = factory.SubFactory(SuperUserFactory)
    date_form_received = date(2012,1,1)

    irf_number = factory.Sequence(lambda n: 'ABC{0}'.format(n))
    date_time_of_interception = date(2011,12,12)

    location = "Nepal"
    staff_name = "Joe Test"

    how_sure_was_trafficking = 5


class IntercepteeFactory(DjangoModelFactory):
    class Meta:
        model = Interceptee

    full_name = factory.Sequence(lambda n: 'John Doe {0}'.format(n))
    age = FuzzyInteger(20,40)
    phone_contact = str(FuzzyInteger(100000000000,999999999999).fuzz())
    photo = ''
    gender = 'm'
    interception_record = factory.SubFactory(IrfFactory)
    kind = 't'
