import requests
import json
import time
import traceback

from django.core.management.base import BaseCommand

from dataentry.models import Person, LocationBoxCommon


class Command(BaseCommand):
    location_addr_set = 0
    location_addr_failed = 0
    person_addr_set = 0
    person_addr_failed = 0
    fudge_adjustment = 0.15 # latitude/longitude fudge amount
    
    def match(self, candidates, addr, fudge):
        best = None
        for candidate in candidates:
            if addr.latitude ==0 and  addr.longitude == 0:
                    best = candidate
                    break
            if (candidate["extent"]["xmax"] + fudge >= addr.longitude and candidate["extent"]["xmin"] - fudge <= addr.longitude and
                candidate["extent"]["ymax"] + fudge >= addr.latitude and candidate["extent"]["ymin"] - fudge <= addr.latitude):
                best = candidate
                break
        
        return best
            
        
    def set_address (self, obj):
        addr_set = False
        address_notes = ''
        address1 = getattr(obj, 'address1', None)
        address2 = getattr(obj, 'address2', None)
        if address2 is None:
            if address1 is None or address1.name == 'Bad foreign Key Address1' or address1.name == 'Unknown':
                return addr_set
            addr = address1
            request_addr = address1.name
            address_notes += ' Address1:' + address1.name
            if address1.latitude != 0 or address1.longitude != 0:
                address_notes += '[' + str(address1.latitude) + ',' + str(address1.longitude) + ']'
        else:
            addr = address2
            if address2.name == 'Bad foreign Key Address2':
                return addr_set
            if address1 is None:
                address1 = address2.address1
            if address2.name == 'Unknown' or address2.name == '-':
                request_addr = address1.name
            else:
                request_addr = address1.name + ', ' + address2.name
            address_notes += ' Address1:' + address1.name
            if address1.latitude != 0 or address1.longitude != 0:
                address_notes += '[' + str(address1.latitude) + ',' + str(address1.longitude) + ']'
            address_notes += ', Address2:' + address2.name
            if address2.latitude != 0 or address2.longitude != 0:
                address_notes += '[' + str(address2.latitude) + ',' + str(address2.longitude) + ']'
                
        url = 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?f=json&singleLine='
        try:
            print(obj.id, url+request_addr)
            response = requests.get(url+request_addr)
            jdata = json.loads(response.content)
            candidates = jdata['candidates']
            best = self.match(candidates, addr, 0.0)
            if best is None:
                best = self.match(candidates, addr, Command.fudge_adjustment)
            
            if best is not None:
                obj.address = best
                obj.latitude = best['location']['y']
                obj.longitude = best['location']['x']
                obj.address_notes = 'converted-' + address_notes
            else:
                obj.address_notes = 'Failed to convert-' + address_notes
            
            obj.save()
            addr_set = True
        except:
             print ('Exception caught', traceback.format_exc())
             print ("request failed", response, 'id=', obj.id)
            
        return addr_set
    
    def process(self):
        print ('Begin processing of LocationBoxCommon')
        locations = LocationBoxCommon.objects.filter(address_notes='').exclude(address2=None).order_by('id')
        for location in locations:
            if self.set_address (location):
                Command.location_addr_set += 1
            else:
                Command.location_addr_failed += 1
        
        print ('LocationBoxCommon: #set=' + str(Command.location_addr_set) + ', #failed=' + str(Command.location_addr_failed))
        
        print ('Begin processing of Person ')
        Command.person_addr_set = 0
        Command.person_addr_failed = 0
        persons = Person.objects.filter(address_notes='').exclude(address1=None).order_by('id')
        for person in persons:
            if self.set_address (person):
                Command.person_addr_set += 1
            else:
                Command.person_addr_failed += 1
        
        print ('Person: #set=' + str(Command.person_addr_set) + ', #failed=' + str(Command.person_addr_failed))
        
    def handle(self, *args, **options):
        retry = True
        while retry:
            try:
                self.process()
                retry = False
            except:
                print ('Exception caught - retrying', traceback.format_exc())
                time.sleep(10)
            
            
           
                
