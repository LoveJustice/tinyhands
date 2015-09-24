#!/usr/bin/env python

import csv
import json


class CSVtoJSON(object):
    def __init__(self, base_name):
        self.base_name = base_name
        self.all_data = []

    @property
    def input_name(self):
        return self.base_name + '.csv'

    @property
    def output_name(self):
        return self.base_name + '.json'

    def load(self):
        with open(self.input_name, 'rU') as csv_file:
            reader = csv.reader(csv_file)
            reader.next()               # Skip header row
            idx = 0
            for row in reader:
                entry = {'idx': idx}
                idx += 1
                for mapping in self.mappings:
                    value = row[mapping['col']].strip()
                    entry[mapping['name']] = mapping['type'](value)
                self.all_data.append(entry)

    def save(self):
        with open(self.output_name, 'w') as json_file:
            json.dump(self.all_data, json_file, sort_keys=True, indent=4)


class CanonicalNames(CSVtoJSON):
    def __init__(self, base_name):
        super(CanonicalNames, self).__init__(base_name)
        self.mappings = [{'name': 'can1', 'col': 0, 'type': str},
                         {'name': 'can2', 'col': 1, 'type': str},
                         {'name': 'lat', 'col': 3, 'type': float},
                         {'name': 'long', 'col': 4, 'type': float},
                         {'name': 'level', 'col': 5, 'type': str}]

    def validate(self):
        combo = {}
        for datum in self.all_data:
            can12 = ','.join([datum['can1'], datum['can2']])
            if can12 in combo:
                raise RuntimeError("{} appears more than once".format(can12))
        print "Canonical names valid"

    def find(self, can1, can2):
        for datum in self.all_data:
            if datum['can1'] == can1 and datum['can2'] == can2:
                return datum
        return None


class NameVariations(CSVtoJSON):
    def __init__(self, base_name):
        super(NameVariations, self).__init__(base_name)
        self.mappings = [{'name': 'adr1', 'col': 0, 'type': str},
                         {'name': 'adr2', 'col': 1, 'type': str},
                         {'name': 'lat', 'col': 3, 'type': float},
                         {'name': 'long', 'col': 4, 'type': float},
                         {'name': 'level', 'col': 5, 'type': str},
                         {'name': 'can1', 'col': 6, 'type': str},
                         {'name': 'can2', 'col': 7, 'type': str}]

    def validate(self, canonical_names):
        for datum in self.all_data:
            if canonical_names.find(datum['can1'], datum['can2']) is None:
                raise RuntimeError("{},{} not in canonical names".format(datum['can1'], datum['can2']))
        print "Name variations valid"

    def find(self, adr1, adr2):
        for datum in self.all_data:
            if datum['adr1'] == adr1 and datum['adr2'] == adr2:
                return datum
        return None


class FormData(CSVtoJSON):
    def __init__(self, base_name):
        super(FormData, self).__init__(base_name)
        self.mappings = [{'name': 'id', 'col': 0, 'type': str},
                         {'name': 'cur1', 'col': 1, 'type': str},
                         {'name': 'cur2', 'col': 2, 'type': str},
                         {'name': 'adr1', 'col': 3, 'type': str},
                         {'name': 'adr2', 'col': 4, 'type': str},
                         {'name': 'lat', 'col': 6, 'type': float},
                         {'name': 'long', 'col': 7, 'type': float},
                         {'name': 'level', 'col': 8, 'type': str},
                         {'name': 'can1', 'col': 9, 'type': str},
                         {'name': 'can2', 'col': 10, 'type': str}]

    def validate(self, canonical_names, name_variations):
        for datum in self.all_data:
            if (canonical_names.find(datum['adr1'], datum['adr2']) is None and
                name_variations.find(datum['adr1'], datum['adr2']) is None):
                print "{} ({}): {},{} in neither canonical nor variations".format(datum['id'], datum['idx'], datum['adr1'], datum['adr2'])


if __name__ == '__main__':
    canonical_names = CanonicalNames('canonical-names')
    canonical_names.load()
    canonical_names.validate()
    canonical_names.save()

    name_variations = NameVariations('name-variations')
    name_variations.load()
    name_variations.validate(canonical_names)
    name_variations.save()

    form_data = FormData('from-vifs-and-irfs')
    form_data.load()
    form_data.validate(canonical_names, name_variations)
    form_data.save()
