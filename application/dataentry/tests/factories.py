import datetime
import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyInteger, FuzzyFloat, FuzzyChoice, FuzzyDate, FuzzyDateTime
import pytz

from accounts.tests.factories import SuperUserFactory
from dataentry.models import *


class IrfFactory(DjangoModelFactory):
    class Meta:
        model = InterceptionRecord

    form_entered_by = factory.SubFactory(SuperUserFactory)
    date_form_received = datetime.datetime(2012, 1, 1, tzinfo=pytz.UTC)

    irf_number = factory.Sequence(lambda n: 'BHD{0}'.format(n))
    date_time_of_interception = FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=pytz.UTC), datetime.datetime(2012, 1, 1, tzinfo=pytz.UTC))

    location = "Nepal"
    staff_name = "Joe Test"

    how_sure_was_trafficking = 5

class MbzStationFactory(DjangoModelFactory):
    class Meta:
        django_get_or_create = ('station_code',)
        model = BorderStation
    
    station_code = 'MBZ'
    station_name = 'Malbazar'
    open = True
    operating_country = None
    time_zone = 'Asia/Kolkata'

    @factory.post_generation
    def mbox(self, create, extracted, **kwargs):
        self.operating_country = Country.objects.get(name='India')
        self.save()
        
    
class IrfIndiaFactory(DjangoModelFactory):
    class Meta:
        model = IrfCommon
    
    station = factory.SubFactory(MbzStationFactory)

    form_entered_by = factory.SubFactory(SuperUserFactory)

    irf_number = factory.Sequence(lambda n: 'MBZ{0}'.format(n))
    date_of_interception = FuzzyDate(datetime.datetime(2008, 1, 1, tzinfo=pytz.UTC), datetime.datetime(2012, 1, 1, tzinfo=pytz.UTC))
    logbook_submitted = datetime.datetime(2012, 1, 1, tzinfo=pytz.UTC)
    status = 'approved'

    location = "India"
    staff_name = "Joe Test"
    who_noticed = 'contact'
    which_contact = 'Bus driver'
    contact_paid = False

    how_sure_was_trafficking = 5

class MasterPersonFactory(DjangoModelFactory):
    class Meta:
        model = MasterPerson
    
    gender = 'm' 

class PersonFactory(DjangoModelFactory):
    class Meta:
        model = Person

    full_name = factory.Sequence(lambda n: 'John Doe {0}'.format(n))
    age = FuzzyInteger(20, 40)
    phone_contact = str(FuzzyInteger(100000000000, 999999999999).fuzz())
    gender = 'm'
    role = 'PVOT'
    photo = None
    master_person = factory.SubFactory(MasterPersonFactory)

class PersonWithPhotoFactory(DjangoModelFactory):
    class Meta:
        model = Person

    full_name = factory.Sequence(lambda n: 'John Doe {0}'.format(n))
    age = FuzzyInteger(20, 40)
    phone_contact = str(FuzzyInteger(100000000000, 999999999999).fuzz())
    gender = 'm'
    role = 'PVOT'
    photo = 'foo.png'
    master_person = factory.SubFactory(MasterPersonFactory)

class VifFactory(DjangoModelFactory):
    class Meta:
        model = VictimInterview

    vif_number = factory.Sequence(lambda n: 'BHD{0}'.format(n))
    interviewer = "Joe Test"

    victim = factory.SubFactory(PersonFactory)

    number_of_victims = FuzzyInteger(1, 10).fuzz()
    number_of_traffickers = FuzzyInteger(1, 10).fuzz()

    date = datetime.date(2011, 12, 12)
    date_time_entered_into_system = datetime.datetime(2011, 12, 12, tzinfo=pytz.UTC)
    date_time_last_updated = datetime.datetime(2011, 12, 12, tzinfo=pytz.UTC)

class CifIndiaFactory(DjangoModelFactory):
    class Meta:
            model = CifCommon
    
    cif_number = factory.Sequence(lambda n: 'BHD{0}'.format(n))
    date_time_entered_into_system = datetime.datetime(2011, 12, 12, tzinfo=pytz.UTC)
    date_time_last_updated = datetime.datetime(2011, 12, 12, tzinfo=pytz.UTC)
    station = factory.SubFactory(MbzStationFactory)

class VictimInterviewLocationBoxFactory(DjangoModelFactory):
    class Meta:
        model = VictimInterviewLocationBox

    victim_interview = factory.SubFactory(VifFactory)


class IntercepteeFactory(DjangoModelFactory):
    class Meta:
        model = Interceptee

    person = factory.SubFactory(PersonFactory)
    photo = 'foo.png'
    interception_record = factory.SubFactory(IrfFactory)
    kind = 'v'

class IntercepteeIndiaFactory(DjangoModelFactory):
    class Meta:
        model = IntercepteeCommon

    person = factory.SubFactory(PersonWithPhotoFactory)
    interception_record = factory.SubFactory(IrfIndiaFactory)

# Photo will cause IDManagement test to fail.  Photo is required for photo_exporter test.
class IntercepteeNoPhotoFactory(DjangoModelFactory):
    class Meta:
        model = Interceptee

    person = factory.SubFactory(PersonFactory)
    interception_record = factory.SubFactory(IrfFactory)

# Photo will cause IDManagement test to fail.  Photo is required for photo_exporter test.
class IntercepteeIndiaNoPhotoFactory(DjangoModelFactory):
    class Meta:
        model = IntercepteeCommon

    person = factory.SubFactory(PersonFactory)
    interception_record = factory.SubFactory(IrfIndiaFactory)

class SiteSettingsFactory(DjangoModelFactory):
    class Meta:
        model = SiteSettings

    data = [
        {'name': 'address1_cutoff', 'value': 70, 'description': "asdfasdf"},
        {'name': 'address1_limit', 'value': 5, 'description': "asdfasdf"},
        {'name': 'address2_cutoff', 'value': 70, 'description': "asdfasdf"},
        {'name': 'address2_limit', 'value': 5, 'description': "asdfasdf"},
        {'name': 'person_cutoff', 'value': 90, 'description': "asdfasdf"},
        {'name': 'person_limit', 'value': 10, 'description': "asdfasdf"},
    ]


class Address1Factory(DjangoModelFactory):
    class Meta:
        model = Address1

    name = factory.Sequence(lambda n: 'Address1 {0}'.format(n))



class CanonicalNameFactory(DjangoModelFactory):
    class Meta:
        model = Address2

    name = factory.Sequence(lambda n: 'Address2 cannon {0}'.format(n))
    latitude = FuzzyFloat(0, 20)
    longitude = FuzzyFloat(0, 20)
    address1 = factory.SubFactory(Address1Factory)
    canonical_name = None
    verified = FuzzyChoice([True, False])


class Address2Factory(DjangoModelFactory):
    class Meta:
        model = Address2

    name = factory.Sequence(lambda n: 'Address2 {0}'.format(n))
    latitude = FuzzyFloat(0, 20)
    longitude = FuzzyFloat(0, 20)

    address1 = factory.SubFactory(Address1Factory)
    canonical_name = factory.SubFactory(CanonicalNameFactory)
    verified = FuzzyChoice([True, False])
    
class PersonBoxFactory(DjangoModelFactory):
    class Meta:
        model = VictimInterviewPersonBox
        
    person = factory.SubFactory(PersonFactory)
    victim_interview = factory.SubFactory(VifFactory)

class PersonBoxIndiaFactory(DjangoModelFactory):
    class Meta:
        model = PersonBoxCommon
        
    person = factory.SubFactory(PersonFactory)
    cif = factory.SubFactory(CifIndiaFactory)  

class AliasGroupFactory(DjangoModelFactory):
    class Meta:
        model = AliasGroup
