from django import forms
from dataentry.models import InterceptionRecord, Interceptee
from django.forms.models import inlineformset_factory


class InterceptionRecordForm(forms.ModelForm):

    who_in_group = forms.ChoiceField(
        choices=InterceptionRecord.WHO_IN_GROUP_CHOICES,
        widget=forms.RadioSelect(),
        required=False
    )
    where_going = forms.ChoiceField(
        choices=InterceptionRecord.WHERE_GOING_CHOICES,
        widget=forms.RadioSelect(),
        required=False
    )

    class Meta:
        model = InterceptionRecord

    def __init__(self, *args, **kwargs):

        kwargs.setdefault('label_suffix', '')
        super(InterceptionRecordForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.iteritems():

            if type(field) == forms.fields.BooleanField:
                model_field = InterceptionRecord._meta.get_field_by_name(field_name)[0]
                if hasattr(model_field, 'weight'):
                    field.weight = model_field.weight


IntercepteeFormSet = inlineformset_factory(InterceptionRecord, Interceptee, extra=12)
