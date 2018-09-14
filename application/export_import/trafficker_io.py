import os
from django.conf import settings

from .field_types import Address1CsvField
from .field_types import Address2CsvField
from .field_types import CopyCsvField

interceptee_data = [
    {
        'field':CopyCsvField('id', 'id', False),
    },
    {
        'field':CopyCsvField('photo', 'Photo', False), 
        'prefix':'https://' + os.environ.get('SITE_HOSTNAME') + settings.MEDIA_URL
    }
]

person_data = [
    {
        'field':CopyCsvField('full_name', 'Full Name', False),
    },
    {
        'field':CopyCsvField('age', 'Age', False),
    },
    {
        'field':CopyCsvField('gender', 'Gender', False),
    },
    {
        'field':CopyCsvField('phone_contact', 'Phone', False),
    },
    {
        'field':Address1CsvField('address1', 'Address 1'),
    },
    {
        'field':Address2CsvField('address2', 'Address 2', 'address1'),
    }
]

def get_trafficker_export_rows(interceptees):
    rows = []
    headers = []
    for field in interceptee_data:
        headers.append(field['field'].title)
    for field in person_data:
        headers.append(field['field'].title)    
    rows.append(headers)

    for interceptee in interceptees:
        row = []
        for field in interceptee_data:
            val = field['field'].exportField(interceptee)
            if 'prefix' in field:
                val = field['prefix'] + str(val)
            row.append(val)
        
        for field in person_data:
            val = field['field'].exportField(interceptee.person)
            if 'prefix' in field:
                val = field['prefix'] + str(val)
            row.append(val)
            
        rows.append(row)
        
    return rows