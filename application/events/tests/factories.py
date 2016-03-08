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
    end_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).time()
    description = factory.Sequence(lambda n: 'This is Event {0}'.format(n))
    is_repeat = False
    repetition = ''
    ends = None
    created_on = None
    modified_on = None