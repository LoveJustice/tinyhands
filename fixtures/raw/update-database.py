#!/usr/bin/env python

import json
import os
import sys
sys.path[0] = os.getcwd()

import django
django.setup()                  # Standalone Python script does this itself.

from dataentry.models import District, VDC


def process_canonical_names():
    print "Processing canonical names"
    district_count = vdc_count = 0
    with open('fixtures/raw/canonical-names.json', 'r') as json_file:
        canonical_names = json.load(json_file)
        print len(canonical_names), "canonical names"
        for canonical in canonical_names:
            district, created = District.objects.get_or_create(name=canonical['can2'])
            if created:
                district_count += 1
            VDC.objects.create(name=canonical['can1'],
                               latitude=canonical['lat'],
                               longitude=canonical['long'],
                               district=district,
                               cannonical_name=None,
                               verified=True)
            vdc_count += 1
    print "Created {} districts, {} VDCs".format(district_count, vdc_count)


def process_name_variations():
    print "Processing name variations"
    district_count = vdc_count = skip_count = 0
    with open('fixtures/raw/name-variations.json', 'r') as json_file:
        name_variations = json.load(json_file)
        print len(name_variations), "name variations"
        for variation in name_variations:
                # Canonical district and VDC must exist.
                can_district = District.objects.get(name=variation['can2'])
                can_vdc_set = VDC.objects.filter(name=variation['can1'], district=can_district)
                if len(can_vdc_set) == 1:
                    can_vdc = can_vdc_set[0]
                else:
                    raise RuntimeError("Bogus canonical VDC set: {}".format(can_vdc_set))

                district, created = District.objects.get_or_create(name=variation['adr2'])
                if created:
                    district_count += 1
                VDC.objects.create(name=variation['adr1'],
                                   latitude=variation['lat'],
                                   longitude=variation['long'],
                                   district=district,
                                   cannonical_name=can_vdc,
                                   verified=True)
                vdc_count += 1
    print "Created {} districts, {} VDCs; skipped {}".format(district_count, vdc_count, skip_count)


process_canonical_names()
process_name_variations()
