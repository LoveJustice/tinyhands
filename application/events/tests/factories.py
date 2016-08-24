import datetime
import factory
from factory.django import DjangoModelFactory

from events.models import Event

class EventFactory(DjangoModelFactory):
    class Meta:
        model = Event
        django_get_or_create = ('title',)

    title = factory.Sequence(lambda n: 'Event {0}'.format(n))
    location = factory.Sequence(lambda n: 'Location {0}'.format(n))
    start_date = datetime.date.today()
    start_time = datetime.datetime.now().time()
    end_date = datetime.date.today()
    end_time = (datetime.datetime.now() + datetime.timedelta(days=1)).time()
    description = factory.Sequence(lambda n: 'This is Event {0}'.format(n))
    is_repeat = True
    repetition = 'D'
    ends = datetime.date.today() + datetime.timedelta(days=3)
    created_on = datetime.datetime.now() - datetime.timedelta(days=3)
    modified_on = datetime.datetime.now() - datetime.timedelta(days=2)
