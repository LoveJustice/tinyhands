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
    
class NameFactory(DjangoModelFactory):
    class Meta:
        model = Name
    
    value = factory.Sequence(lambda n: 'John Doe {0}'.format(n))
    person = None
    
class AgeFactory(DjangoModelFactory):
    class Meta:
        model = Age
        django_get_or_create = ('value',)

    value = FuzzyInteger(20,40)

    @factory.post_generation
    def person(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.                                                               
            return

        if extracted:
            # A list of groups were passed in, use them                                               
            for group in extracted:
                self.person.add(group)

class PhoneFactory(DjangoModelFactory):
    class Meta:
        model = Phone

    value = str(FuzzyInteger(100000000000,999999999999).fuzz())
    person = None

class PersonFactory(DjangoModelFactory):
    class Meta:
        model = Person

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        name=kwargs.pop('name',None)
        age=kwargs.pop('age',None)
        phone=kwargs.pop('phone',None)
        instance = manager.create(*args, **kwargs)
        if name:
            name = NameFactory.create(value=name,person=instance)
        else:
            name = NameFactory.create(person=instance)
        if phone:
            phone = PhoneFactory.create(value=phone,person=instance)
        else:
            phone = PhoneFactory.create(person=instance)
        if age:
            age = AgeFactory.create(value=age, person=[instance])
        else:
            age = AgeFactory.create(person=[instance])
        instance.canonical_age = age
        instance.canonical_phone = phone
        instance.canonical_name = name
        return instance

class IntercepteeFactory(PersonFactory):
    class Meta:
        model = Interceptee
    
    photo = ''
    gender = 'Male'
    interception_record = factory.SubFactory(IrfFactory)
    kind = 'T'