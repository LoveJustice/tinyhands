from django.core.serializers import json
from collections import OrderedDict
from django.utils.encoding import force_text, is_protected_type

"""
    Override python serializer methods modify the values produced when indicated in the adjustments
    - update get_dump_object to  remove id (pk) values
    - update handle_fk field to replase foreign key id values
    - update handle_m2m_field to replace all of the foreign key id values with tag values for many to many relationship
"""
class Serializer(json.Serializer):
    def __init__(self):
        self.adjustments = {}

    def get_dump_object(self, obj):
        data = OrderedDict([('model', force_text(obj._meta))])
        if not self.use_natural_primary_keys or not hasattr(obj, 'natural_key'):
            if obj.__class__ in self.adjustments and not self.adjustments[obj.__class__]['dropId']:  
                data["pk"] = force_text(obj._get_pk_val(), strings_only=True)
        data['fields'] = self._current
        return data
    
    def handle_fk_field(self, obj, field):
        if obj.__class__ in self.adjustments and 'fk' in self.adjustments[obj.__class__] and field.attname in self.adjustments[obj.__class__]['fk']:
            value = getattr(obj, field.get_attname())
            if value is not None:
                cls = self.adjustments[obj.__class__]['fk'][field.attname]
                foreign_object = cls.objects.get(id=value)
                self._current[field.name] = foreign_object.form_tag
            else:
                self._current[field.name] = value
        else:
            return super(Serializer, self).handle_fk_field(obj, field)
    
    def handle_m2m_field(self, obj, field):
        if obj.__class__ in self.adjustments and 'clear-m2m' in self.adjustments[obj.__class__] and self.adjustments[obj.__class__]['clear-m2m'] == field.attname:
            self._current[field.name] = []
        elif obj.__class__ in self.adjustments and 'm2m' in self.adjustments[obj.__class__] and field.attname in self.adjustments[obj.__class__]['m2m']:
            cls = self.adjustments[obj.__class__]['m2m'][field.attname]
            lst = []
            for related in getattr(obj, field.name).iterator():
                value = related._get_pk_val()
                foreign_object = cls.objects.get(id=value)
                lst.append(foreign_object.form_tag)
            self._current[field.name] = lst
        else:
            return super(Serializer, self).handle_m2m_field(obj, field)