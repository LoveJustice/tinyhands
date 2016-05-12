import datetime
from events.models import Event

rep_dict = {'D': 'Daily', 'W': 'Weekly', 'M': 'Monthly'}


def list_weekday(day):
    return [(day+i) % 7 for i in range(7)]


def format_schedule(date, time):
    return datetime.datetime.combine(date, time).strftime('%Y-%m-%dT%H:%M:%S')


def get_repeated(qs, start, end):
    items = []
    for item in qs:
        if item.start_date:
            start = datetime.date(start.year, start.month, start.day)
            end = datetime.date(end.year, end.month, end.day)
            check_start = item.start_date
            check_end = item.end_date
            ends = item.ends if item.ends else end
            repetition = item.repetition
            if not repetition:
                continue
            while end > check_start and ends > check_start:
                if start <= check_start:
                    temp_event = Event(
                        title=item.title, start_date=check_start, end_date=check_end,
                        start_time=item.start_time, end_time=item.end_time, location=item.location,
                        description=item.description, is_repeat=item.is_repeat, repetition=item.repetition,
                        ends=item.ends)
                    items.append(temp_event)
                check_start = add_repeat(check_start, repetition)
                check_end = add_repeat(check_end, repetition)
    return items


def add_repeat(date, repeat):
    if repeat == 'D':
        date += datetime.timedelta(days=1)
        return date
    if repeat == 'W':
        date += datetime.timedelta(days=7)
        return date
    if repeat == 'M':
        month = date.month + 1
        if month > 12:
            month = 1
            year = date.year + 1
        else:
            year = date.year
        try:
            date = datetime.date(year, month, date.day)
        except ValueError:
            temp_date = datetime.date(year, month, 1) - datetime.timedelta(1)
            date = datetime.date(year, month, temp_date.day)
        return date
    else:
        return date


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
