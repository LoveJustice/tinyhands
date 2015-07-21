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
                logging.warning("Key %s=%s has %d values", key_name, key_val, len(cur_value))
                self._set(cur_value, key_name, key_val)
            else:
                self._set(new_value, key_name, key_val)

    def fetch(self, **kwargs):
        """Fetch a value by a single key."""
        key_name, key_val = one_key_val(**kwargs)
        self._validate_key_name(key_name)
        result = self._get(key_name, key_val)
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

def prepare_value(val):
    if val is None:
        return "NULL"
    elif type(val) in [ str, unicode ]:
        return "'{}'".format(val)
    else:
        return str(val)

def make_update_statement(table_name, pk, **kwargs):
    set_clause = [ ]
    for key, val in kwargs.iteritems():
        set_clause.append("{}={}".format(key, val))
    print "UPDATE {} SET {} WHERE id={};".format(table_name,
                                                 ', '.join(set_clause),
                                                 prepare_value(pk))

def make_insert_statement(table_name, field_dict):
    column_names = [ ]
    values = [ ]
    for key, val in field_dict.iteritems():
        column_names.append(key)
        values.append(prepare_value(val))
    print "INSERT INTO {}({}) VALUES({});".format(table_name, ', '.join(column_names), ', '.join(values))

def make_delete_statement(table_name):
    print "DELETE from {};".format(table_name)

def next_pk(map):
    return max(map.iterkeys('pk')) + 1

def store_district(map, pk, name):
    if not name:
        raise RuntimeError("Empty district name")
    if pk is None:
        pk = next_pk(map)
    value = { 'id': pk,
              'name': name }
    map.store(value, pk=pk, name=name)
    make_insert_statement('dataentry_district', value)
    return value

def store_vdc(map, pk, name, cannonical_name,
              district, latitude, longitude, verified):
    if not name:
        raise RuntimeError("Empty VDC name")
    if pk is None:
        pk = next_pk(map)
    value = { 'id': pk,
              'name': name,
              'cannonical_name_id': cannonical_name,
              'district_id': district,
              'latitude': latitude,
              'longitude': longitude,
              'verified': verified }
    map.store(value, pk=pk, name=name)
    make_insert_statement('dataentry_vdc', value)
    return value
    
def load_district_data(file_name):
    district_map = MultiMap('pk', 'name')
    store_district(district_map, 0, 'Unknown')
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
                      fields['latitude'], fields['longitude'], 1)

    for pk, data in vdc_map.iteritems('pk'):
        cannonical_name = data['cannonical_name_id']
        if cannonical_name is not None:
            if not vdc_map.contains(pk=cannonical_name):
                raise RuntimeError(
                    "VDC {} has bogus cannonical_name {}".format(pk, cannonical_name))
    return vdc_map

def resolve_vdc_list(district, vdc_list, vdc_name):
    # There's more than one VDC; figure out which one we want to use.
    if district is None:
        # No way to resolve -- pick the first.
        return vdc_list[0]
    else:
        # See if one of the VDCs listed refers to the district.
        for vdc in vdc_list:
            if vdc['district_id'] == district['id']:
                return vdc
        # Cook up a new VDC pointing to the district
        return store_vdc(vdc_map, None, vdc_name, None,
                         district['id'], 0.0, 0.0, 0)

def get_row_value(row, field_name):
    if field_name in row.keys():
        value = row[field_name]
        if type(value) in [ str, unicode ]:
            value = value.strip()
        return value
    else:
        return ''

def resolve_district_and_vdc(row, table_pk, district_field_name, vdc_field_name):
    district = None
    vdc = None

    district_name = get_row_value(row, district_field_name)
    if district_name:
        district = district_map.fetch(name=district_name)
        if not district:
            district = store_district(district_map, None, district_name)
            logging.debug("Added district '%s' as pk %s",
                          district_name, district['id'])

    vdc_name = get_row_value(row, vdc_field_name)
    if vdc_name:
        vdc = vdc_map.fetch(name=vdc_name)
        if not vdc:
            if district is not None:
                district_pk = district['id']
            else:
                district_pk = 0  # "Unknown" district
            vdc = store_vdc(vdc_map, None, vdc_name, None,
                            district_pk, 0.0, 0.0, 0)
            logging.debug("Added vdc '%s' (dist %s) as pk %s",
                          vdc_name, str(district_pk), next_pk)
        if type(vdc) is list:
            vdc = resolve_vdc_list(district, vdc, vdc_name)
                
    return district, vdc

district_file_name = "../dataentry/fixtures/district.json"
vdc_file_name = "../dataentry/fixtures/vdc.json"

old_query_file_name = "queries-old-model.sql"
new_query_file_name = "queries-new-model.sql"

old_db_file_name = "prod-old/db-2015-07-19-17-01.sqlite3"
new_db_file_name = "prod-new/db-2015-07-19-17-01.sqlite3"

make_delete_statement('dataentry_district')
make_delete_statement('dataentry_vdc')

district_map = load_district_data(district_file_name)
logging.info("Read %d district entries from %s", district_map.size(), district_file_name)
vdc_map = load_vdc_data(vdc_file_name, district_map)
logging.info("Read %d VDC entries from %s", vdc_map.size(), vdc_file_name)

old_queries = load_queries(old_query_file_name)
logging.info("Loaded queries from %s", old_query_file_name)
new_queries = load_queries(new_query_file_name)
logging.info("Loaded queries from %s", new_query_file_name)

def update_table(db_file, query,
                 table_name, table_pk,
                 district_field_name, vdc_field_name,
                 skip_pks=set()):
    update_count = skip_count = nop_count = 0
    for row in run_query(db_file, query):
        if row[table_pk] in skip_pks:
            skip_count += 1
            continue
        district, vdc = resolve_district_and_vdc(row, table_pk,
                                                 district_field_name,
                                                 vdc_field_name)
        kwargs = { }
        if district:
            kwargs[district_field_name + "_id"] = district['id']
        if vdc:
            kwargs[vdc_field_name + "_id"] = vdc['id']
        if len(kwargs) > 0:
            update_count += 1
            make_update_statement(table_name, row[table_pk], **kwargs)
        else:
            nop_count += 1
    logging.info("Table %s: updated %s, skipped %d, nop %d",
                 table_name, update_count, skip_count, nop_count)

update_table(old_db_file_name, old_queries['interceptee'],
             'dataentry_interceptee', 'id',
             'district',
             'vdc')
update_table(old_db_file_name, old_queries['victim-address'],
             'dataentry_victiminterview', 'vif_number',
             'victim_address_district',
             'victim_address_vdc')
update_table(old_db_file_name, old_queries['victim-guardian-address'],
             'dataentry_victiminterview', 'vif_number',
             'victim_guardian_address_district',
             'victim_guardian_address_vdc')
update_table(old_db_file_name, old_queries['person-box'],
             'dataentry_victiminterviewpersonbox', 'id',
             'address_district',
             'address_vdc')
update_table(old_db_file_name, old_queries['location-box'],
             'dataentry_victiminterviewlocationbox', 'id',
             'district',
             'vdc')

def update_partial_table(old_db_file, id_query,
                         new_db_file, query,
                         table_name, table_pk,
                         district_field_name, vdc_field_name):
    skip_pks = [ row['id'] for row in run_query(old_db_file, id_query) ]
    logging.info("Partial table %s: skip %d", table_name, len(skip_pks))
    update_table(new_db_file, query,
                 table_name, table_pk,
                 district_field_name, vdc_field_name,
                 set(skip_pks))
    
update_partial_table(old_db_file_name, old_queries['interceptee-ids'],
                     new_db_file_name, new_queries['interceptee'],
                     'dataentry_interceptee', 'id',
                     'district',
                     'vdc')
update_partial_table(old_db_file_name, old_queries['victim-interview-ids'],
                     new_db_file_name, new_queries['victim-address'],
                     'dataentry_victiminterview', 'vif_number',
                     'victim_address_district',
                     'victim_address_vdc')
update_partial_table(old_db_file_name, old_queries['victim-interview-ids'],
                     new_db_file_name, new_queries['victim-guardian-address'],
                     'dataentry_victiminterview', 'vif_number',
                     'victim_guardian_address_district',
                     'victim_guardian_address_vdc')
update_partial_table(old_db_file_name, old_queries['person-box-ids'],
                     new_db_file_name, new_queries['person-box'],
                     'dataentry_victiminterviewpersonbox', 'id',
                     'address_district',
                     'address_vdc')
