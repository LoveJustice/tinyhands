from fuzzywuzzy import process, fuzz
from dataentry.models import District, VDC

def match_location(district_name=None, vdc_name=None):
    '''
    Currently we only send one or the other, so that's all this function
    handles. For more flexible (and unDRY) code (which should DRYed before use),
    look at commit 656d770fbaf28c82fca7fed11e7c1679982de3a5.
    '''

    # Determine the appropriate model
    model = District
    locationName = district_name
    if vdc_name != None:
        model = VDC
        locationName = vdc_name

    # Get all relevant data.
    regionNames = {region.id: region.name for region in model.objects.all()}

    # matches is in the form of [(u'match', score, id), ...]
    matches = process.extractBests(locationName, regionNames, limit=7)

    # Return the correct objects.
    objects = None
    if(len(matches) > 0):
        objects = [model.objects.get(id=id) for name, score, id in matches]
    return objects
