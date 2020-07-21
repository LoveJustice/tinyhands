from datetime import date
from collections import namedtuple
from django.db import models
from django.db import transaction
from django.contrib.postgres.fields import JSONField


from .addresses import Address1, Address2
from .alias_group import AliasGroup
from .master_person import MasterPerson, AddressType, PhoneType, SocialMediaType
from .form import Form, FormCategory
from accounts.models import Account

class PersonFormData:
    photo = ''

class Person(models.Model):
    GENDER_CHOICES = [('M', 'm'), ('F', 'f')]
    
    master_person = models.ForeignKey(MasterPerson)
    master_set_by = models.ForeignKey(Account, related_name='%(class)s_entered_by', null=True, on_delete=models.SET_NULL)
    master_set_date = models.DateField(auto_now_add=True)
    master_set_notes = models.TextField('Match Notes', blank=True)
    
    full_name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=4, choices=GENDER_CHOICES, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    address1 = models.ForeignKey(Address1, null=True, blank=True)
    address2 = models.ForeignKey(Address2, null=True, blank=True)
    address = JSONField(null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    address_notes = models.TextField('Address Notes', blank=True)
    address_verified = models.BooleanField('Address Verified', default=False)
    address_type = models.ForeignKey(AddressType, null=True)
    phone_contact = models.CharField(max_length=255, blank=True)
    phone_verified = models.BooleanField('Phone Verified', default=False)
    phone_type = models.ForeignKey(PhoneType, null=True)
    alias_group = models.ForeignKey(AliasGroup, null=True)
    birthdate = models.DateField(null=True)
    estimated_birthdate= models.DateField(null=True)
    nationality = models.CharField(max_length=127, blank=True, default='')
    aliases = None
    
    photo = models.ImageField(upload_to='interceptee_photos', default='', blank=True)
    anonymized_photo = models.CharField(max_length=126, null=True)
    
    case_filed_against = models.CharField(max_length=126, null=True)
    arrested = models.CharField(max_length=126, null=True)
    social_media = models.CharField(max_length=1024, null=True)
    social_media_verified = models.BooleanField('Social Media Verified', default=False)
    social_media_type = models.ForeignKey(SocialMediaType, null=True)
    role = models.CharField(max_length=126, null=True)
    appearance = models.CharField(max_length=126, null=True)
    occupation = models.CharField(max_length=126, null=True)
    interviewer_believes = models.CharField(max_length=126, null=True)
    pv_believes = models.CharField(max_length=126, null=True)
    
    education = models.CharField('Occupation', max_length=126, null=True)
    guardian_name = models.CharField('Guardian Name', max_length=126, null=True)
    guardian_phone = models.CharField('Guardian Phone', max_length=126, null=True)
    guardian_relationship = models.CharField('Guardian Relationship', max_length=1024, null=True)

    def get_aliases(self):
        if self.aliases is not None:
            return self.aliases

        if self.master_person is None:
            self.aliases = ''
        else:
            alias_persons = Person.objects.filter(master_person = self.master_person).order_by('full_name')
            sep = ''
            self.aliases = ''
            for alias_person in alias_persons:
                if self.aliases.find(alias_person.full_name) == -1:
                    self.aliases = self.aliases + sep + alias_person.full_name
                    sep = ','

        return self.aliases
    
    def get_master_person_id(self):
        if self.master_person is None:
            return None
        else:
            return self.master_person.id
    
    def get_form_element(self, element_name):
        if not hasattr(self, 'forms'):
            self.forms = PersonFormCache.get_form_data(self)
        
        if len(self.forms) > 0 and element_name in self.forms[0].form_detail:
            return self.forms[0].form_detail[element_name]
        else:
            return '' 

    def get_form_type(self):
        return self.get_form_element('type')
    
    def get_form_name(self):
        return self.get_form_element('form_name')

    def get_form_number(self):
        return self.get_form_element('number')

    def get_form_date(self):
        return self.get_form_element('date')

    def get_form_photo(self):
        return self.get_form_element('photo')

    def get_form_kind(self):
        return self.get_form_element('kind')
    
    def get_station_id(self):
        return self.get_form_element('station_id')
    
    def get_country_id(self):
        return self.get_form_element('country_id')
    
    def get_form_id(self):
        return self.get_form_element('form_id')
    
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
        
        val = val + ', master_person id='
        if self.master_person is not None:
            val = val + str(self.master_person.id)
        else:
            val = val + 'None'
        
        val = val + ')'
        return val
        

class PersonFormCache(models.Model):
    person = models.ForeignKey(Person)
    form_detail = JSONField(null=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    
    @staticmethod
    def get_form_data(person):
        person_forms = list(PersonFormCache.objects.filter(person=person))
        
        if len(person_forms) == 0:
            person_forms = PersonFormCache.load_cache(person)
        
        return person_forms
    
    def get_detail_as_object(self):
        if 'form_id' in self.form_detail:
            value = namedtuple("FormDetail", self.form_detail.keys())(*self.form_detail.values())
        else:
            value = None
        
        return value
    
    @staticmethod
    def load_cache(person):
        forms = []
        person_forms = []
        
        with transaction.atomic():
            old_forms = PersonFormCache.objects.filter(person=person)
            for old_form in old_forms:
                old_form.delete()
            
            vdf_forms = Form.objects.filter(form_type__name='VDF')
            for vdf_form in vdf_forms:
                vdf_class = vdf_form.storage.get_form_storage_class()
                vdfs = vdf_class.objects.filter(victim=person, station__in = vdf_form.stations.all())
                for vdf in vdfs:
                    form_entry = {}
                    form_entry['form_id'] = vdf.id
                    form_entry['type'] = 'VDF'
                    form_entry['form_name'] = vdf_form.form_name
                    form_entry['number'] = vdf.vdf_number
                    form_entry['date'] = str(vdf.interview_date)
                    form_entry['photo'] = ''
                    form_entry['kind'] = 'PVOT'
                    form_entry['station_id'] = vdf.station.id
                    form_entry['country_id'] = vdf.station.operating_country.id
                    forms.append(form_entry)
            
            cif_forms = Form.objects.filter(form_type__name='CIF')
            for cif_form in cif_forms:
                cif_class = cif_form.storage.get_form_storage_class()
                cifs = cif_class.objects.filter(main_pv=person, station__in=cif_form.stations.all())
                for cif in cifs:
                    form_entry = {}
                    form_entry['form_id'] = cif.id
                    form_entry['type'] = 'CIF'
                    form_entry['form_name'] = cif_form.form_name
                    form_entry['number'] = cif.cif_number
                    form_entry['date'] = str(cif.incident_date)
                    form_entry['photo'] = ''
                    form_entry['kind'] = 'PVOT'
                    form_entry['station_id'] = cif.station.id
                    form_entry['country_id'] = cif.station.operating_country.id
                    forms.append(form_entry)
                
                form_categories = FormCategory.objects.filter(form=cif_form, name='OtherPotentialVictims')
                if len(form_categories) == 1:
                    other_victims_class = form_categories[0].storage.get_form_storage_class()
                    other_victims = other_victims_class.objects.filter(person=person, cif__station__in=cif_form.stations.all())
                    for other_victim in other_victims:
                        form_entry = {}
                        form_entry['form_id'] = other_victim.cif.id
                        form_entry['type'] = 'CIF'
                        form_entry['form_name'] = cif_form.form_name
                        form_entry['number'] = other_victim.cif.cif_number
                        form_entry['date'] = str(other_victim.cif.incident_date)
                        form_entry['photo'] = ''
                        form_entry['kind'] = 'PVOT'
                        form_entry['station_id'] = other_victim.cif.station.id
                        form_entry['country_id'] = other_victim.cif.station.operating_country.id
                        forms.append(form_entry)
                
                form_categories = FormCategory.objects.filter(form=cif_form, name='PersonBoxes')
                if len(form_categories) == 1:
                    person_box_class = form_categories[0].storage.get_form_storage_class()
                    person_boxes = person_box_class.objects.filter(person=person, cif__station__in=cif_form.stations.all())
                    for person_box in person_boxes:
                        form_entry = {}
                        form_entry['form_id'] = person_box.cif.id
                        form_entry['type'] = 'CIF'
                        form_entry['form_name'] = cif_form.form_name
                        form_entry['number'] = person_box.cif.cif_number
                        form_entry['date'] = str(person_box.cif.incident_date)
                        form_entry['photo'] = ''
                        form_entry['kind'] = 'Suspect'
                        for field in person_box._meta.fields:
                            if field.name.startswith('role_'):
                                value = getattr(person_box, field.name)
                                if value:
                                    if isinstance(field, models.BooleanField) or isinstance(field, models.NullBooleanField):
                                        form_entry['kind'] = field.verbose_name
                                        break
                        form_entry['station_id'] = person_box.cif.station.id
                        form_entry['country_id'] = person_box.cif.station.operating_country.id
                        forms.append(form_entry)
                        
            irf_forms = Form.objects.filter(form_type__name='IRF')
            for irf_form in irf_forms:
                form_categories = FormCategory.objects.filter(form=irf_form, name='Interceptees')
                if len(form_categories) == 1:
                    interceptee_class = form_categories[0].storage.get_form_storage_class()
                    interceptees = interceptee_class.objects.filter(person=person, interception_record__station__in=irf_form.stations.all())
                    for interceptee in interceptees:
                        form_entry = {}
                        form_entry['form_id'] = interceptee.interception_record.id
                        form_entry['type'] = 'IRF'
                        form_entry['form_name'] = irf_form.form_name
                        form_entry['number'] = interceptee.interception_record.irf_number
                        form_entry['date'] = str(interceptee.interception_record.date_time_of_interception.date())
                        if interceptee.person.photo is not None and interceptee.person.photo != '':
                            form_entry['photo'] = interceptee.person.photo.url
                        if interceptee.person.role == 'PVOT':
                            form_entry['kind'] = 'PVOT'
                        else:
                            form_entry['kind'] = 'Suspect'
                        form_entry['station_id'] = interceptee.interception_record.station.id
                        form_entry['country_id'] = interceptee.interception_record.station.operating_country.id
                        forms.append(form_entry)
            
            if len(forms) > 0:
                for form in forms:
                    cache_entry = PersonFormCache()
                    cache_entry.person = person
                    cache_entry.form_detail = form
                    cache_entry.save()
                    person_forms.append(cache_entry)
            else:
                cache_entry = PersonFormCache()
                cache_entry.person = person
                cache_entry.form_detail = {}
                cache_entry.save()
                person_forms.append(cache_entry)
            

        return person_forms
        
        
    
