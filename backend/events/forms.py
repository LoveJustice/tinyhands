from django import forms
from events.models import Event


class EventForm(forms.ModelForm):
    REPEAT_CHOICES = (
        ('D', 'Daily'),
        ('W', 'Weekly'),
        ('M', 'Monthly'),
    )

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'is_repeat':
                continue
            self.fields[field].widget.attrs['class'] = 'form-control'

        for field in self.fields.values():
            field.error_messages = {'required':'"{fieldname}"  field is required'.format(
                fieldname=field.label)}

        self.fields['start_date'].widget.attrs['placeholder'] = 'Start date'
        self.fields['start_time'].widget.attrs['placeholder'] = 'Start time'

        self.fields['end_date'].widget.attrs['placeholder'] = 'End date'
        self.fields['end_time'].widget.attrs['placeholder'] = 'End time'

        self.fields['repetition'].choices = self.REPEAT_CHOICES

    class Meta:
        model = Event
        fields = ('title', 'location', 'start_date', 'start_time', 'end_date', 'end_time', 'description', 'is_repeat', 'repetition', 'ends')

    def clean(self):
        data = self.cleaned_data
        is_repeat = data.get('is_repeat', '')
        repetition = data.get('repetition', '')
        if is_repeat and not repetition:
            raise forms.ValidationError('Repetition is required if event is repeated.')

        start_date = data.get('start_date', '')
        end_date = data.get('end_date', '')
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')

        ends = data.get('ends', '')

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError('Start date is not allowed to be greater than end date.')
            if start_date == end_date:
                if start_time >= end_time:
                    raise forms.ValidationError('Start time must less than end time for same day.')

        if ends and ends <= start_date:
            raise forms.ValidationError('Events repetition ends must be greater than first event end date.')

        return data