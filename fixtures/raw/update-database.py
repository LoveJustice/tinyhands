#!/usr/bin/env python

import json
import os
import sys
sys.path[0] = os.getcwd()

import django
django.setup()                  # Standalone Python script does this itself.

from dataentry.models import (District, VDC, Interceptee,
                              VictimInterview, VictimInterviewLocationBox, VictimInterviewPersonBox)


def process_canonical_names():
    print "\nProcessing canonical names"
    district_count = vdc_count = 0
    with open('fixtures/raw/canonical-names.json', 'r') as json_file:
        canonical_names = json.load(json_file)
        print len(canonical_names), "canonical names"
        for canonical in canonical_names:
            district, created = District.objects.get_or_create(name=canonical['can1'])
            if created:
                district_count += 1
            VDC.objects.create(name=canonical['can2'],
                               latitude=canonical['lat'],
                               longitude=canonical['long'],
                               district=district,
                               cannonical_name=None,
                               verified=True)
            vdc_count += 1
    print "Created {} districts, {} VDCs".format(district_count, vdc_count)


def look_up_vdc(district_name, vdc_name):
    try:
        can_district = District.objects.get(name=district_name)
    except District.DoesNotExist:
        return None

    can_vdc_set = VDC.objects.filter(name=vdc_name, district=can_district)
    address_count = len(can_vdc_set)
    if address_count == 0:
        return None
    elif address_count == 1:
        return can_vdc_set[0]
    else:
        raise RuntimeError("More than one matching address: {}".format(can_vdc_set))


def process_name_variations():
    print "\nProcessing name variations"
    district_count = vdc_count = 0
    with open('fixtures/raw/name-variations.json', 'r') as json_file:
        name_variations = json.load(json_file)
        print len(name_variations), "name variations"
        for variation in name_variations:
            existing_vdc = look_up_vdc(variation['adr1'], variation['adr2'])
            if existing_vdc is not None and existing_vdc.is_canonical:
                # Already have this one and it's canonical.
                continue

            # Look up canonical VDC.
            can_vdc = look_up_vdc(variation['can1'], variation['can2'])

            # Add name variation.
            district, created = District.objects.get_or_create(name=variation['adr1'])
            if created:
                district_count += 1
            VDC.objects.create(name=variation['adr2'],
                               latitude=variation['lat'],
                               longitude=variation['long'],
                               district=district,
                               cannonical_name=can_vdc,
                               verified=True)
            vdc_count += 1
    print "Created {} districts, {} VDCs".format(district_count, vdc_count)


class AddressMapping(object):
    def __init__(self, form_data, model_class, district_attr_name, vdc_attr_name):
        self.form_data = form_data
        self.model_class = model_class
        self.district_attr_name = district_attr_name
        self.vdc_attr_name = vdc_attr_name

        self.mapping = []
        self.model_name = self.model_class.__name__

        self.create_mapping()

    def create_mapping(self):
        print "\n Mapping {} objects ({}, {})".format(self.model_name,
                                             self.district_attr_name,
                                             self.vdc_attr_name)
        for object in self.model_class.objects.all():
            try:
                vdc = getattr(object, self.vdc_attr_name)
                if vdc is None:
                    print "No {} for {} {}".format(self.vdc_attr_name, self.model_name, object)
                    continue
            except:
                print "! Invalid {} for {} {}".format(self.vdc_attr_name, self.model_name, object)
                continue

            try:
                district = getattr(object, self.district_attr_name)
                if district is None:
                    print "No {} for {} {}".format(self.district_attr_name, self.model_name, object)
                    continue
            except:
                print "! Invalid {} for {} {}".format(self.district_attr_name, self.model_name, object)
                continue

            vdc_name = getattr(object, self.vdc_attr_name).name
            district_name = getattr(object, self.district_attr_name).name
            found = False

            for datum in self.form_data:
                if datum['cur1'] == district_name and datum['cur2'] == vdc_name:
                    self.mapping.append({'id': object.id,
                                         'adr1': datum['adr1'],
                                         'adr2': datum['adr2']})
                    found = True
                    break
            if not found:
                print "! No location {} {} -- {} {}, {} {}".format(self.model_name, object,
                                                                   self.district_attr_name, district_name,
                                                                   self.vdc_attr_name, vdc_name)
        print "{} {} mappings".format(len(self.mapping), self.model_name)

    def apply_mapping(self):
        print "\nUpdating {} objects".format(self.model_name)
        object_count = 0
        for entry in self.mapping:
            object = self.model_class.objects.get(pk=entry['id'])
            vdc = look_up_vdc(entry['adr1'], entry['adr2'])
            district = vdc.district
            setattr(object, self.district_attr_name, district)
            setattr(object, self.vdc_attr_name, vdc)
            object.save()
            object_count += 1
        print "Updated {} {} objects".format(object_count, self.model_name)


def map_addresses():
    form_data = None
    with open('fixtures/raw/from-vifs-and-irfs.json', 'r') as json_file:
        form_data = json.load(json_file)

    # Create mappings to corrected addresses for each element.
    interceptee_mapping = AddressMapping(form_data, Interceptee,
                                         'district', 'vdc')
    vif_victim_mapping = AddressMapping(form_data, VictimInterview,
                                        'victim_address_district', 'victim_address_vdc')
    vif_guardian_mapping = AddressMapping(form_data, VictimInterview,
                                          'victim_guardian_address_district', 'victim_guardian_address_vdc')
    pb_mapping = AddressMapping(form_data, VictimInterviewPersonBox,
                                'address_district', 'address_vdc')
    lb_mapping = AddressMapping(form_data, VictimInterviewLocationBox,
                                'district', 'vdc')

    # Purge existing districts and VDCs. Can't do this easily through Django
    # due to foreign key constratins (that we are intentionally ignoring).
    from subprocess import call
    for table in ('vdc', 'district'):
        call(['sqlite3', 'db.sqlite3', 'delete from dataentry_{}'.format(table)])

    process_canonical_names()
    process_name_variations()

    # Apply the mappings using the new address data.
    interceptee_mapping.apply_mapping()
    vif_victim_mapping.apply_mapping()
    vif_guardian_mapping.apply_mapping()
    pb_mapping.apply_mapping()
    lb_mapping.apply_mapping()


map_addresses()
