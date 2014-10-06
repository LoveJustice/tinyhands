from fuzzywuzzy import process
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
    return District.objects.get(name=matches[0][0])

def match_vdc(vdcName):
    vdcNames = [vdc.name for vdc in VDC.objects.all()]
    vdcCanonicalNames = [vdc.cannonical_name for vdc in VDC.objects.all() if vdc.cannonical_name is not None]
    vdcNames.extend(vdcCanonicalNames)
    matches = process.extractBests(vdcName, vdcNames, score_cutoff=70, limit=1)
    return VDC.objects.get(name=matches[0][0])

def match_vdc_district(vdc_name, district_name):
    #code to match vdc and district
    return None
