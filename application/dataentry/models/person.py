from django.db import models

from addresses import Address1, Address2
from alias_group import AliasGroup

class PersonFormData:
    photo = ''

class Person(models.Model):
    GENDER_CHOICES = [('M', 'm'), ('F', 'f')]

    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=4, choices=GENDER_CHOICES, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    address1 = models.ForeignKey(Address1, null=True, blank=True)
    address2 = models.ForeignKey(Address2, null=True, blank=True)
    phone_contact = models.CharField(max_length=255, blank=True)
    alias_group = models.ForeignKey(AliasGroup, null=True)
    aliases = None

    def get_aliases(self):
        if self.aliases is not None:
            return self.aliases

        if self.alias_group is None:
            self.aliases = ''
        else:
            alias_persons = Person.objects.filter(alias_group = self.alias_group).order_by('full_name')
            sep = ''
            self.aliases = ''
            for alias_person in alias_persons:
                if self.aliases.find(alias_person.full_name) == -1:
                    self.aliases = self.aliases + sep + alias_person.full_name
                    sep = ','

        return self.aliases

    def get_form_type(self):
        if not hasattr(self, 'forms'):
            self.get_form_data()

        if len(self.forms) > 0:
            return self.forms[0].type
        else:
            return ''

    def get_form_number(self):
        if not hasattr(self,'forms'):
            self.get_form_data()

        if len(self.forms) > 0:
            return self.forms[0].number
        else:
            return ''

    def get_form_date(self):
        if not hasattr(self,'forms'):
            self.get_form_data()

        if len(self.forms) > 0:
            return self.forms[0].date
        else:
            return ''

    def get_form_photo(self):
        if not hasattr(self, 'forms'):
            self.get_form_data()

        if len(self.forms) > 0:
            return self.photo
        else:
            return ''

    def get_form_kind(self):
        if not hasattr(self, 'forms'):
            self.get_form_data()

        if len(self.forms) > 0:
            return self.forms[0].kind
        else:
            return ''

    def get_form_data(self):
        import interceptee
        import victim_interview
        import  person_box

        self.forms = []
        self.photo = ''

        vifs = victim_interview.VictimInterview.objects.filter(victim = self)
        if len(vifs) > 0:
            for vif in vifs:
                form = PersonFormData()
                form.type = 'VIF'
                form.number = vif.vif_number
                form.date = vif.date
                form.photo = ''
                form.kind = 'Victim'
                self.forms.append(form)

        person_boxes = person_box.VictimInterviewPersonBox.objects.filter(person = self)
        if len(person_boxes) > 0:
            for person_box in person_boxes:
                form = PersonFormData()
                form.type = 'VIF'
                form.number = person_box.victim_interview.vif_number
                form.date = person_box.victim_interview.date
                form.photo = ''
                form.kind = 'Trafficker'
                for field in person_box._meta.fields:
                    if field.name.startswith('who_is_this_role'):
                        value = getattr(person_boxes[0], field.name)
                        if value:
                            if isinstance(field, models.BooleanField) or isinstance(field, models.NullBooleanField):
                                form.kind = field.verbose_name
                                break
                self.forms.append(form)

        interceptees = interceptee.Interceptee.objects.filter(person = self)
        if len(interceptees) > 0:
            for interceptee in interceptees:
                form = PersonFormData()
                form.type = 'IRF'
                form.number = interceptee.interception_record.irf_number
                form.date = interceptee.interception_record.date_time_of_interception.date()
                form.photo = interceptee.photo_thumbnail
                form.kind = interceptees[0].kind
                if form.kind == 't':
                    form.kind = 'Trafficker'
                elif form.kind == 'v':
                    form.kind = 'Victim'
                self.forms.append(form)

                if self.photo == '' and form.photo is not None:
                    self.photo = form.photo

        return self.forms
