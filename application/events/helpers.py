import datetime
import calendar
from events.models import Event

rep_dict = {'D': 'Daily', 'W': 'Weekly', 'M': 'Monthly'}


def format_schedule(date, time):
    return datetime.datetime.combine(date, time).strftime('%Y-%m-%dT%H:%M:%S')


def get_repeated_events(events, start_date_range, end_date_range):
    items = []
    for event in events:
        start_date_generator = repeating_date_generator(event.start_date, event.repetition)
        end_date_generator = repeating_date_generator(event.end_date, event.repetition)
        start_date = event.start_date
        end_date = event.end_date
        event_ends = end_date_range if event.ends is None else min(event.ends, end_date_range)
        while event_ends > start_date:
            if start_date_range <= start_date <= end_date_range:
                rep_event = Event(
                            title=event.title, start_date=start_date, end_date=end_date,
                            start_time=event.start_time, end_time=event.end_time, location=event.location,
                            description=event.description, is_repeat=event.is_repeat, repetition=event.repetition,
                            ends=event.ends, id=event.id)
                items.append(rep_event)
            start_date = start_date_generator.next()
            end_date = end_date_generator.next()
    return items


def repeating_date_generator(date, repeat):
    temp_date = date
    while True:
        if repeat == 'D':
            temp_date += datetime.timedelta(days=1)
            yield temp_date
        elif repeat == 'W':
            temp_date += datetime.timedelta(days=7)
            yield temp_date
        elif repeat == 'M':
            year = int(temp_date.year + temp_date.month / 12)
            month = temp_date.month % 12 + 1
            day = min(date.day, calendar.monthrange(year, month)[1])
            temp_date = datetime.date(year, month, day)
            yield temp_date
        else:
            raise StopIteration


def dashboard_event_list(qs_list):
    week_day = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
    this_day = datetime.date.today()
    days_list = [this_day + datetime.timedelta(i) for i in range(7)]
    today = datetime.date.today().weekday()
    week_list = [(today+i) % 7 for i in range(7)]
    ls = [[{'weekday': '{} {} - {}'.format(week_day[item], days_list[i].month, days_list[i].day)}] for i, item in enumerate(week_list)]

    for item in qs_list:
        ends = item.ends.strftime('%Y-%m-%d') if item.ends else ''
        temp = {
            'id': item.id,
            'location': item.location,
            'description': item.description,
            'is_repeat': item.is_repeat,
            'repetition': rep_dict.get(item.repetition, ''),
            'ends': ends,
            'start_date': item.start_date.strftime('%Y-%m-%d'),
            'end_date': item.end_date.strftime('%Y-%m-%d'),
            'start_time': str(item.start_time),
            'end_time': str(item.end_time),
            'weekday': week_day[item.start_date.weekday()],
            'week_count': item.start_date.weekday(),
            'start': format_schedule(item.start_date, item.start_time),
            'end': format_schedule(item.end_date, item.end_time),
            'title': item.title
        }
        ind = week_list.index(temp['week_count'])
        ls[ind].append(temp)
    return ls


def event_list(qs_list):
    ls = []
    for item in qs_list:
        ends = item.ends.strftime('%Y-%m-%d') if item.ends else ''
        temp = {
            'id': item.id,
            'location': item.location,
            'description': item.description,
            'is_repeat': item.is_repeat,
            'repetition': rep_dict.get(item.repetition, ''),
            'ends': ends,
            'start_date': item.start_date.strftime('%Y-%m-%d'),
            'end_date': item.end_date.strftime('%Y-%m-%d'),
            'start_time': str(item.start_time),
            'end_time': str(item.end_time),
            'start': format_schedule(item.start_date, item.start_time),
            'end': format_schedule(item.end_date, item.end_time),
            'title': item.title
        }
        ls.append(temp)
    return ls
