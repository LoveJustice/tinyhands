from datetime import date
from collections import namedtuple
from django.db import models
from django.db import transaction
from django.db.models import JSONField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


from .addresses import Address1, Address2
from .alias_group import AliasGroup
from .master_person import MasterPerson, AddressType, PhoneType, SocialMediaType
from .form import Form, FormCategory
from accounts.models import Account

class PersonFormData:
    photo = ''

class Person(models.Model):
    GENDER_CHOICES = [('M', 'm'), ('F', 'f')]
    
    master_person = models.ForeignKey(MasterPerson, on_delete=models.CASCADE)
    master_set_by = models.ForeignKey(Account, related_name='%(class)s_entered_by', null=True, on_delete=models.SET_NULL)
    master_set_date = models.DateField(auto_now_add=True)
    master_set_notes = models.TextField('Match Notes', blank=True)
    
    full_name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=4, choices=GENDER_CHOICES, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    address1 = models.ForeignKey(Address1, null=True, blank=True, on_delete=models.SET_NULL)
    address2 = models.ForeignKey(Address2, null=True, blank=True, on_delete=models.SET_NULL)
    address = JSONField(null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    address_notes = models.TextField('Address Notes', blank=True)
    address_verified = models.BooleanField('Address Verified', default=False)
    address_type = models.ForeignKey(AddressType, null=True, on_delete=models.CASCADE)
    phone_contact = models.CharField(max_length=255, blank=True)
    phone_verified = models.BooleanField('Phone Verified', default=False)
    phone_type = models.ForeignKey(PhoneType, null=True, on_delete=models.CASCADE)
    alias_group = models.ForeignKey(AliasGroup, null=True, on_delete=models.CASCADE)
    birthdate = models.DateField(null=True)
    estimated_birthdate= models.DateField(null=True)
    nationality = models.CharField(max_length=127, blank=True, default='')
    aliases = None
    
    photo = models.ImageField(upload_to='interceptee_photos', default='', blank=True)
    anonymized_photo = models.CharField(max_length=126, null=True)
    
    case_filed_against = models.CharField(max_length=126, null=True)
    arrested = models.CharField(max_length=126, null=True)
    social_media = models.CharField(max_length=1024, null=True)
    social_media_platform = models.CharField(max_length=1024, null=True)
    social_media_verified = models.BooleanField('Social Media Verified', default=False)
    social_media_type = models.ForeignKey(SocialMediaType, null=True, on_delete=models.CASCADE)
    whatsApp = models.CharField(max_length=1024, null=True)
    role = models.CharField(max_length=126, null=True)
    appearance = models.CharField(max_length=126, null=True)
    occupation = models.CharField(max_length=126, null=True)
    interviewer_believes = models.CharField(max_length=126, null=True)
    pv_believes = models.CharField(max_length=126, null=True)
    
    education = models.CharField('Occupation', max_length=126, null=True)
    guardian_name = models.CharField('Guardian Name', max_length=126, null=True)
    guardian_phone = models.CharField('Guardian Phone', max_length=126, null=True)
    guardian_relationship = models.CharField('Guardian Relationship', max_length=1024, null=True)
    
    other_contact_name = models.CharField(max_length=126, null=True)
    other_contact_phone = models.CharField(max_length=126, null=True)
    
    last_modified_time = models.DateTimeField(auto_now=True)
    last_match_time = models.DateTimeField(null=True)

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
                if alias_person.full_name is not None and self.aliases.find(alias_person.full_name) == -1:
                    self.aliases = self.aliases + sep + alias_person.full_name
                    sep = ','

        return self.aliases
    
    def get_master_person_id(self):
        if self.master_person is None:
            return None
        else:
            return self.master_person.id
    
    
    def get_form(self):
        if not hasattr(self, 'forms'):
            self.forms = PersonForm.get_form_data(self)
        
        if len(self.forms) > 0:
            return self.forms[0]
        else:
            return None
    
    def get_form_type(self):
        form = self.get_form()
        if form is not None:
            return form.get_form_type()
        else:
            return ''
    
    def get_form_name(self):
        form = self.get_form()
        if form is not None:
            return form.get_form_name()
        else:
            return ''
    
    def get_form_number(self):
        form = self.get_form()
        if form is not None:
            return form.get_form_number()
        else:
            return ''
    
    def get_form_date(self):
        form = self.get_form()
        if form is not None:
            return form.get_form_date()
        else:
            return ''
    
    def get_form_id(self):
        form = self.get_form()
        if form is not None:
            return form.get_form_id()
        else:
            return ''
    
    def get_station_id(self):
        form = self.get_form()
        if form is not None:
            return form.get_station_id()
        else:
            return ''
    
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
        
class PersonForm(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True)
    content_object=GenericForeignKey('content_type', 'object_id')
    creation_time = models.DateTimeField(auto_now_add=True)
    
    def get_form_id(self):
        if self.content_object is None:
            return ''
        return self.content_object.id
     
    def get_form_type(self):
        if self.content_object is None:
            return ''
        form_type = self.content_object.get_form_type_name()
        if form_type == 'VDF':
            forms = self.content_object.station.form_set.filter(form_type__name='PVF')
            if len(forms) > 0:
                form_type = 'PVF'
        return form_type
    
    def get_form_name(self):
        if self.content_object is None:
            return ''
        form = Form.current_form(self.content_object.get_form_type_name(), self.content_object.station.id)
        if form is not None:
            return form.form_name
        else:
            return ''
    
    def get_form_number(self):
        if self.content_object is None:
            return ''
        return self.content_object.get_key()
    
    def get_form_date(self):
        if self.content_object is None:
            return ''
        return self.content_object.get_form_date()
    
    def get_station_id(self):
        if self.content_object is None:
            return ''
        return self.content_object.station.id
    
    def get_country(self):
        if self.content_object is None:
            return ''
        return self.content_object.station.operating_country
    
    def get_country_id(self):
        if self.content_object is None:
            return ''
        return self.content_object.station.operating_country.id
    
    def get_detail_as_object(self):
        if self.get_form_id() == '':
            return None
        
        form_dict = {
            'form_id': self.get_form_id(),
            'type': self.get_form_type(),
            'form_name': self.get_form_name(),
            'number': self.get_form_number(),
            'date': self.get_form_date(),
            'station_id': self.get_station_id(),
            'country_id': self.get_country_id()
            }
        return namedtuple("FormDetail", form_dict.keys())(*form_dict.values())

    @staticmethod
    def get_form_data(person):
        person_forms = list(PersonForm.objects.filter(person=person))
        
        if len(person_forms) == 0:
            person_forms = PersonForm.load_cache(person)
        
        return person_forms
    
    @staticmethod
    def load_cache(person):
        forms = []
        person_forms = []
        
        with transaction.atomic():
            old_forms = PersonForm.objects.filter(person=person)
            for old_form in old_forms:
                old_form.delete()
            
            vdf_forms = Form.objects.filter(form_type__name='VDF')
            for vdf_form in vdf_forms:
                vdf_class = vdf_form.storage.get_form_storage_class()
                vdfs = vdf_class.objects.filter(victim=person, station__in = vdf_form.stations.all())
                for vdf in vdfs:
                    form_entry = PersonForm()
                    form_entry.content_object = vdf
                    forms.append(form_entry)
            
            pvf_forms = Form.objects.filter(form_type__name='PVF')
            for pvf_form in pvf_forms:
                pvf_class = pvf_form.storage.get_form_storage_class()
                pvfs = pvf_class.objects.filter(victim=person, station__in = pvf_form.stations.all())
                for pvf in pvfs:
                    form_entry = PersonForm()
                    form_entry.content_object = pvf
                    forms.append(form_entry)
            
            cif_forms = Form.objects.filter(form_type__name='CIF')
            for cif_form in cif_forms:
                cif_class = cif_form.storage.get_form_storage_class()
                cifs = cif_class.objects.filter(main_pv=person, station__in=cif_form.stations.all())
                for cif in cifs:
                    form_entry = PersonForm()
                    form_entry.content_object = cif
                    forms.append(form_entry)
                
                form_categories = FormCategory.objects.filter(form=cif_form, name='OtherPotentialVictims')
                if len(form_categories) == 1:
                    other_victims_class = form_categories[0].storage.get_form_storage_class()
                    other_victims = other_victims_class.objects.filter(person=person, cif__station__in=cif_form.stations.all())
                    for other_victim in other_victims:
                        form_entry = PersonForm()
                        form_entry.content_object = other_victim.cif
                        forms.append(form_entry)
                
                form_categories = FormCategory.objects.filter(form=cif_form, name='PersonBoxes')
                if len(form_categories) == 1:
                    person_box_class = form_categories[0].storage.get_form_storage_class()
                    person_boxes = person_box_class.objects.filter(person=person, cif__station__in=cif_form.stations.all())
                    for person_box in person_boxes:
                        form_entry = PersonForm()
                        form_entry.content_object = person_box.cif
                        forms.append(form_entry)
            
            sf_forms = Form.objects.filter(form_type__name='SF')
            for sf_form in sf_forms:
                sf_class = sf_form.storage.get_form_storage_class()
                sfs = sf_class.objects.filter(merged_person=person, station__in=sf_form.stations.all())
                for sf in sfs:
                    form_entry = PersonForm()
                    form_entry.content_object = sf
                    forms.append(form_entry)

                form_categories = FormCategory.objects.filter(form=sf_form, name='Information')
                if len(form_categories) == 1:
                    suspect_info_class = form_categories[0].storage.get_form_storage_class()
                    suspect_infos = suspect_info_class.objects.filter(person=person, suspect__station__in=sf_form.stations.all())
                    for suspect_info in suspect_infos:
                        form_entry = PersonForm()
                        form_entry.content_object = suspect_info.suspect
                        forms.append(form_entry)
                        
            irf_forms = Form.objects.filter(form_type__name='IRF')
            for irf_form in irf_forms:
                form_categories = FormCategory.objects.filter(form=irf_form, name='People')
                if len(form_categories) == 1:
                    interceptee_class = form_categories[0].storage.get_form_storage_class()
                    interceptees = interceptee_class.objects.filter(person=person, interception_record__station__in=irf_form.stations.all())
                    for interceptee in interceptees:
                        form_entry = PersonForm()
                        form_entry.content_object = interceptee.interception_record
                        forms.append(form_entry)
            
            if len(forms) > 0:
                for form in forms:
                    form.person = person
                    form.save()
                    person_forms.append(form)
            else:
                form = PersonForm()
                form.person = person
                form.save()
                person_forms.append(form)

        return person_forms

        
        
    
