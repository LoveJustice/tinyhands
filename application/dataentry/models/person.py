from datetime import date
from django.db import models

from .addresses import Address1, Address2
from .alias_group import AliasGroup

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
    birthdate = models.DateField(null=True)
    estimated_birthdate= models.DateField(null=True)
    nationality = models.CharField(max_length=127, blank=True, default='')
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
    
    def get_form_name(self):
        if not hasattr(self, 'forms'):
            self.get_form_data()

        if len(self.forms) > 0:
            return self.forms[0].form_name
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
    
    def get_station_id(self):
        if not hasattr(self, 'forms'):
            self.get_form_data()

        if len(self.forms) > 0:
            return self.forms[0].station_id
        else:
            return ''
    
    def get_country_id(self):
        if not hasattr(self, 'forms'):
            self.get_form_data()

        if len(self.forms) > 0:
            return self.forms[0].country_id
        else:
            return ''
    
    def get_form_id(self):
        if not hasattr(self, 'forms'):
            self.get_form_data()

        if len(self.forms) > 0:
            return self.forms[0].form_id
        else:
            return ''

    def get_form_data(self):
        from . import interceptee
        from . import victim_interview
        from . import person_box
        from . import Form, FormCategory

        self.forms = []
        self.photo = ''
        
        if self.id == 3279:
            print('in get_form_data')
        
        vdf_forms = Form.objects.filter(form_type__name='VDF')
        for vdf_form in vdf_forms:
            vdf_class = vdf_form.storage.get_form_storage_class()
            vdfs = vdf_class.objects.filter(victim=self)
            for vdf in vdfs:
                form_entry = PersonFormData()
                form_entry.form_id = vdf.id
                form_entry.type = 'VDF'
                form_entry.form_name = vdf_form.form_name
                form_entry.number = vdf.vdf_number
                form_entry.date = vdf.interview_date
                form_entry.photo = ''
                form_entry.kind = 'PVOT'
                form_entry.station_id = vdf.station.id
                form_entry.country_id = vdf.station.operating_country.id
                self.forms.append(form_entry)
        
        cif_forms = Form.objects.filter(form_type__name='CIF')
        for cif_form in cif_forms:
            cif_class = cif_form.storage.get_form_storage_class()
            cifs = cif_class.objects.filter(main_pv=self)
            for cif in cifs:
                form_entry = PersonFormData()
                form_entry.form_id = cif.id
                form_entry.type = 'CIF'
                form_entry.form_name = cif_form.form_name
                form_entry.number = cif.cif_number
                form_entry.date = cif.incident_date
                form_entry.photo = ''
                form_entry.kind = 'PVOT'
                form_entry.station_id = cif.station.id
                form_entry.country_id = cif.station.operating_country.id
                self.forms.append(form_entry)
            
            form_categories = FormCategory.objects.filter(form=cif_form, name='OtherPotentialVictims')
            if len(form_categories) == 1:
                other_victims_class = form_categories[0].storage.get_form_storage_class()
                other_victims = other_victims_class.objects.filter(person=self)
                for other_victim in other_victims:
                    form_entry = PersonFormData()
                    form_entry.form_id = other_victim.cif.id
                    form_entry.type = 'CIF'
                    form_entry.form_name = cif_form.form_name
                    form_entry.number = other_victim.cif.cif_number
                    form_entry.date = other_victim.cif.incident_date
                    form_entry.photo = ''
                    form_entry.kind = 'PVOT'
                    form_entry.station_id = other_victim.cif.station.id
                    form_entry.country_id = other_victim.cif.station.operating_country.id
                    self.forms.append(form_entry)
            
            form_categories = FormCategory.objects.filter(form=cif_form, name='PersonBoxes')
            if len(form_categories) == 1:
                person_box_class = form_categories[0].storage.get_form_storage_class()
                person_boxes = person_box_class.objects.filter(person=self)
                if self.id == 3279:
                    print('person_boxes', len(person_boxes))
                for person_box in person_boxes:
                    form_entry = PersonFormData()
                    form_entry.form_id = person_box.cif.id
                    form_entry.type = 'CIF'
                    form_entry.form_name = cif_form.form_name
                    form_entry.number = person_box.cif.cif_number
                    form_entry.date = person_box.cif.incident_date
                    form_entry.photo = ''
                    form_entry.kind = 'Suspect'
                    for field in person_box._meta.fields:
                        if field.name.startswith('role_'):
                            value = getattr(person_box, field.name)
                            if value:
                                if isinstance(field, models.BooleanField) or isinstance(field, models.NullBooleanField):
                                    form_entry.kind = field.verbose_name
                                    break
                    form_entry.station_id = person_box.cif.station.id
                    form_entry.country_id = person_box.cif.station.operating_country.id
                    self.forms.append(form_entry)
                    
        irf_forms = Form.objects.filter(form_type__name='IRF')
        for irf_form in irf_forms:
            form_categories = FormCategory.objects.filter(form=irf_form, name='Interceptees')
            if len(form_categories) == 1:
                interceptee_class = form_categories[0].storage.get_form_storage_class()
                interceptees = interceptee_class.objects.filter(person=self)
                for interceptee in interceptees:
                    form_entry = PersonFormData()
                    form_entry.form_id = interceptee.interception_record.id
                    form_entry.type = 'IRF'
                    form_entry.form_name = irf_form.form_name
                    form_entry.number = interceptee.interception_record.irf_number
                    form_entry.date = interceptee.interception_record.date_time_of_interception.date()
                    form_entry.photo = ''
                    if interceptee.kind == 'v':
                        form_entry.kind = 'PVOT'
                    else:
                        form_entry.kind = 'Suspect'
                    form_entry.station_id = interceptee.interception_record.station.id
                    form_entry.country_id = interceptee.interception_record.station.operating_country.id
                    self.forms.append(form_entry)

        return self.forms
    
    def set_estimated_birthdate(self, base_date):
        if self.birthdate is not None:
            self.estimated_birthdate = self.birthdate
        elif self.age is not None:
            birth_year = base_date.year - self.age
            if base_date.month < 7:
                birth_year = birth_year - 1
            self.estimated_birthdate = date(birth_year,7,1)
        else:
            self.estimated_birthdate = None
    
    def estimate_current_age(self, base_date):
        if self.estimated_birthdate is not None:
            delta = base_date - self.estimated_birthdate
            return delta.days // 365
        else:
            return None
        
    def __str__(self):
        val = 'Person(id='+ str(self.id) + ',  full_name=' + self.full_name + ', address1 '
        if self.address1 is not None:
            val = val + 'id=' + str(self.address1.id)
        else:
            val = val + 'None'
        
        val = val + ', address2 '
        
        if self.address2 is not None:
            val = val + 'id=' + str(self.address2.id)
        else:
            val = val + 'None'
        
        val = val + ', alias_group id='
        if self.alias_group is not None:
            val = val + str(self.alias_group.id)
        else:
            val = val + 'None'
        
        val = val + ')'
        return val
        
            
