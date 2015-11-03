from fuzzywuzzy import process
from dataentry.models import District, VDC


def match_location(district_name=None, vdc_name=None):
    """
    Currently we only send one, the other, or both, so that's all this function
    handles. For more flexible (and unDRY) code (which should DRYed before use),
    look at commit 656d770fbaf28c82fca7fed11e7c1679982de3a5.
    """
    filter_by_district = False
    # Determine the appropriate model
    if vdc_name is not None and district_name is not None:
        model = VDC
        location_name = vdc_name
        filter_by_district = True
    elif vdc_name is not None:
        model = VDC
        location_name = vdc_name
    else:
        model = District
        location_name = district_name

    # TODO - Make sure to optimize this search; the select_related might be
    # necessary. Might also want to have cannonical_name__district in here.
    if filter_by_district:
        region_names = {region.id: region.name
                        for region in model.objects.filter(district__name__contains=district_name).select_related('district', 'cannonical_name__district')
                        }
    else:
        region_names = {region.id: region.name
                        for region in model.objects.all().select_related('district')
                        }

    # matches is in the form of [(u'match', score, id), ...]
    matches = process.extractBests(location_name, region_names, limit=7)

    # Return the correct objects.
    objects = None
    if len(matches) > 0:
        objects = [model.objects.get(pk=pk) for name, score, pk in matches]
    return objects


def match_vdc_district(vdc_name, district_name):
    locations = [vdc.name+", "+vdc.district.name for vdc in VDC.objects.all()]
    name = vdc_name + ", " + district_name
    matches = process.extractBests(name, locations, score_cutoff=70, limit=5)
    if len(matches) > 0:
        names = matches[0][0].split(", ")
        vdc = VDC.objects.get(name=names[0])
        district = vdc.district
        return vdc, district
    else:
        return None
