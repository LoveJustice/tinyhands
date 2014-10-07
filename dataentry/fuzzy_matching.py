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
    matches = process.extractBests(locationName, districtNames, score_cutoff=70, limit=1)
    if(len(matches) > 0):
        return District.objects.get(name=matches[0][0])
    else:
        return None

def match_vdc(vdc_name):
    vdcNames = [vdc.name for vdc in VDC.objects.all()]
    matches = process.extractBests(vdc_name, vdcNames, score_cutoff=70, limit=1)
    if(len(matches) > 0):
        return VDC.objects.get(name=matches[0][0])
    else:
        return None

def match_vdc_district(vdc_name, district_name):
    locations = [vdc.name+", "+vdc.district.name for vdc in VDC.objects.all()]
    name = vdc_name + ", " + district_name
    matches = process.extractBests(name, locations, score_cutoff=70, limit=1)
    if(len(matches) > 0 ):
        names = matches[0][0].split(", ")
        vdc = VDC.objects.get(name=names[0])
        district = vdc.district
        return (vdc, district)
    else:
        return None
