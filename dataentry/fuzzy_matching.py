from fuzzywuzzy import process, fuzz
from dataentry.models import District, VDC

def match_location(district_name=None,vdc_name=None):
    if district_name==None and vdc_name==None:
       return None
    elif vdc_name==None:
       return match_district(district_name)
    elif district_name==None:
       return match_vdc(vdc_name)
    else:
       return match_vdc_district(vdc_name, district_name)

def match_district(locationName):
    districtNames = [district.name for district in District.objects.all()]
    matches = process.extractBests(locationName, districtNames, score_cutoff=70, limit=5)
    if(len(matches) > 0):
        districts = []
        for match in matches:
            districts.append(District.objects.get(name=match[0]))
        return districts
    else:
        return None

def match_vdc(vdc_name):
    vdcNames = [vdc.name for vdc in VDC.objects.all()]
    matches = process.extractBests(vdc_name, vdcNames, score_cutoff=70, limit=5)
    if(len(matches) > 0):
        vdcs = []
        for match in matches:
            vdcs.append(VDC.objects.get(name=match[0]))
        return vdcs
    else:
        return None

def match_vdc_district(vdc_name, district_name):
    locations = [vdc.name+", "+vdc.district.name for vdc in VDC.objects.all()]
    name = vdc_name + ", " + district_name
    matches = process.extractBests(name, locations, score_cutoff=70, limit=5)
    if(len(matches) > 0 ):
        names = matches[0][0].split(", ")
        vdc = VDC.objects.get(name=names[0])
        district = vdc.district
        return (vdc, district)
    else:
        return None

def match_staff(station, enteredName):
    staffNames = [staff.name for staff in District.objects.all()]
    matches = process.extractBests(enteredName, staffNames, score_cutoff=70, limit=5)
    if(len(matches) > 0):
        names = []
        for match in matches:
            names.append(District.objects.get(name=match[0]))
        return names
    else:
        return None
