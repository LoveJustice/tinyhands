#!/usr/bin/env python

import json

from util import load_queries, run_query

import logging
logging.basicConfig(level=logging.INFO)


def one_key_val(**kwargs):
    """Check that there is one kwarg and return it."""
    if len(kwargs) != 1:
        raise RuntimeError("Can only have one key, not {}".format(kwargs))
    return kwargs.items()[0]

class MultiMap(object):
    """Map (dictionary) with multiple keys.

    Implements multiple maps that all refer to the same collection of values. Allows
    values to be stored under multiple keys and be looked up by any one.

    """
    def __init__(self, *key_names):
        """Initialize to store keys under the list of key names."""
        self.key_names = key_names
        self.by = { k : { } for k in self.key_names }
        self.key_name_set = set(key_names)

    def _validate_key_name(self, key_name):
        """Check that 'key_name' is a valid key."""
        if key_name not in self.key_name_set:
            raise RuntimeError("Key {} not in {}".format(key_name, self.key_names))

    def _contains(self, key_name, key_val):
        return key_val in self.by[key_name]

    def _set(self, value, key_name, key_val):
        self.by[key_name][key_val] = value

    def _get(self, key_name, key_val):
        return self.by[key_name].get(key_val)

    def store(self, new_value, **kwargs):
        """Store a value indexed by all keys."""
        if set(kwargs.keys()) != self.key_name_set:
            raise RuntimeError(
                "Bogus keys {}; must have {}".format(kwargs, self.key_names))
        for key_name, key_val in kwargs.iteritems():
            if self._contains(key_name, key_val):
                cur_value = self._get(key_name, key_val)
                if type(cur_value) is list:
                    cur_value.append(new_value)
                else:
                    cur_value = [ cur_value, new_value ]
                logging.warning("Key %s=%s has %d values",
                                key_name, key_val, len(cur_value))
                self._set(cur_value, key_name, key_val)
            else:
                self._set(new_value, key_name, key_val)

    def fetch(self, **kwargs):
        """Fetch a value by a single key."""
        key_name, key_val = one_key_val(**kwargs)
        self._validate_key_name(key_name)
        result = self._get(key_name, key_val)
        if type(result) is list:
            raise RuntimeError("Fetched list value for %s=%s", key_name, key_val)
        return result

    def contains(self, **kwargs):
        """Return whether there is a value for a single given key."""
        key_name, key_val = one_key_val(**kwargs)
        self._validate_key_name(key_name)
        return self._contains(key_name, key_val)

    def iteritems(self, key_name):
        """Iterate over all the items under a single key."""
        self._validate_key_name(key_name)
        return self.by[key_name].iteritems()

    def iterkeys(self, key_name):
        """Iterate over all the keys under a single key name."""
        self._validate_key_name(key_name)
        return self.by[key_name].iterkeys()
    
    def size(self):
        """Return number of values stored."""
        return len(self.by[self.key_names[0]])


def store_district(map, pk, name):
    map.store({ 'pk': pk,
                'name': name },
              pk=pk, name=name)

def store_vdc(map, pk, name, cannonical_name, district, latitude, longitude):
    map.store({ 'pk': pk,
                'name': name,
                'cannonical_name': cannonical_name,
                'district': district,
                'latitude': latitude,
                'longitude': longitude },
              pk=pk, name=name)
    
def load_district_data(file_name):
    district_map = MultiMap('pk', 'name')
    with open(file_name, "r") as f:
        for elt in json.load(f):
            pk = elt['pk']
            name = elt['fields']['name']
            store_district(district_map, pk, name)
    return district_map

def load_vdc_data(file_name, district):
    vdc_map = MultiMap('pk', 'name')
    with open(file_name, "r") as f:
        for elt in json.load(f):
            pk = elt['pk']

            fields = elt['fields']
            name = fields['name']

            district_fk = fields['district']
            if not district_map.contains(pk=district_fk):
                raise RuntimeError(
                    "VDC {} has bogus district FK {}".format(pk, district_fk))

            store_vdc(vdc_map,
                      pk, name, 
                      fields['cannonical_name'],
                      district_fk,
                      fields['latitude'], fields['longitude'])

    for pk, data in vdc_map.iteritems('pk'):
        cannonical_name = data['cannonical_name']
        if cannonical_name is not None:
            if not vdc_map.contains(pk=cannonical_name):
                raise RuntimeError(
                    "VDC {} has bogus cannonical_name {}".format(pk, cannonical_name))
    return vdc_map

district_file_name = "../dataentry/fixtures/district.json"
vdc_file_name = "../dataentry/fixtures/vdc.json"
old_query_file_name = "queries-old-model.sql"
new_query_file_name = "queries-new-model.sql"
old_db_file_name = "prod-old/db-2015-07-19-17-01.sqlite3"

district_map = load_district_data(district_file_name)
logging.info("Read %d district entries from %s", district_map.size(), district_file_name)
vdc_map = load_vdc_data(vdc_file_name, district_map)
logging.info("Read %d VDC entries from %s", vdc_map.size(), vdc_file_name)

old_queries = load_queries(old_query_file_name)
logging.info("Loaded queries from %s", old_query_file_name)
new_queries = load_queries(new_query_file_name)
logging.info("Loaded queries from %s", new_query_file_name)

for row in run_query(old_db_file_name, old_queries['interceptee']):
    district_name = row['district'].strip()
    vdc_name = row['vdc'].strip()

    district_pk = None
    if district_name:
        district = district_map.fetch(name=district_name)
        if district:
            district_pk = district['pk']
        else:
            district_pk = max(district_map.iterkeys('pk')) + 1
            store_district(district_map, district_pk, district_name)
            logging.debug("Added district '%s' as pk %s", district_name, district_pk)

    if vdc_name:
        if not vdc_map.contains(name=vdc_name):
            next_pk = max(vdc_map.iterkeys('pk')) + 1
            store_vdc(vdc_map, next_pk, vdc_name, None, district_pk, 0.0, 0.0)
            logging.debug("Added vdc '%s' (dist %s) as pk %s",
                          vdc_name, str(district_pk), next_pk)

for pk, value in district_map.iteritems('pk'):
    print "INSERT INTO dataentry_district(id, name) VALUES({}, '{}')".format(value['pk'], value['name'])

for pk, value in vdc_map.iteritems('pk'):
    print "INSERT INTO dataentry_vdc(id, name, canonical_name, district, latitude, longitude) VALUES({}, '{}', {}, {}, {}, {})".format(value['pk'], value['name'], value['cannonical_name'], value['district'], value['latitude'], value['longitude'])
