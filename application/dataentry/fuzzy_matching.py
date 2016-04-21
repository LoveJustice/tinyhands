from fuzzywuzzy import process
from dataentry.models import Address1, Address2, FuzzyMatching


def match_location(address1_name=None, address2_name=None):
    """
    Currently we only send one, the other, or both, so that's all this function
    handles. For more flexible (and unDRY) code (which should DRYed before use),
    look at commit 656d770fbaf28c82fca7fed11e7c1679982de3a5.
    """
    filter_by_address1 = False

    # Determine the appropriate model
    if address2_name is not None and address1_name is not None:
        model = Address2
        location_name = address2_name
        filter_by_address1 = True
    elif address2_name is not None:
        model = Address2
        location_name = address2_name
    else:
        model = Address1
        location_name = address1_name

    fuzzy_object = FuzzyMatching.objects.all()[0]

    if filter_by_address1:
        fuzzy_cutoff = fuzzy_object.address2_cutoff
        fuzzy_limit = fuzzy_object.address2_limit
        region_names = {region.id: region.name
                        for region in model.objects.filter(address1__name__contains=address1_name).select_related('address1', 'canonical_name__address1')
                        }
    else:
        fuzzy_limit = fuzzy_object.address1_limit
        fuzzy_cutoff = fuzzy_object.address1_cutoff
        region_names = {region.id: region.name
                        for region in model.objects.all()
                        }

    # matches is in the form of [(u'match', score, id), ...]
    matches = process.extractBests(location_name, region_names, score_cutoff=fuzzy_cutoff, limit=fuzzy_limit)

    objects = None
    if len(matches) > 0:
        objects = [model.objects.get(pk=pk) for name, score, pk in matches]
    return objects

# This function is not used anywhere else in code
def match_address2_address1(address2_name, address1_name):
    locations = [address2.name+", "+address2.address1.name for address2 in Address2.objects.all()]
    name = address2_name + ", " + address1_name
    matches = process.extractBests(name, locations, score_cutoff=70, limit=5)
    if len(matches) > 0:
        names = matches[0][0].split(", ")
        address2 = Address2.objects.get(name=names[0])
        address1 = address2.address1
        return address2, address1
    else:
        return None
