from fuzzywuzzy import process
from itertools import chain

from dataentry.models import Address1, Address2, SiteSettings, Person, Interceptee, VictimInterview, Form, FormCategory


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

    site_settings = SiteSettings.objects.all()[0]

    if filter_by_address1:
        fuzzy_cutoff = site_settings.get_setting_value_by_name('address2_cutoff')
        fuzzy_limit = site_settings.get_setting_value_by_name('address2_limit')
        region_names = {region.id: region.name
                        for region in model.objects.filter(address1__name__contains=address1_name).select_related('address1', 'canonical_name__address1')
                        }
    else:
        fuzzy_limit = site_settings.get_setting_value_by_name('address1_limit')
        fuzzy_cutoff = site_settings.get_setting_value_by_name('address1_cutoff')
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

def match_person(person_name, filter):
    fuzzy_limit = 11
    fuzzy_score_cutoff=80
    if filter != None and filter == 'PVOT':
        victims = pvot_ids()
        choices = {choice.id: choice.full_name for choice in Person.objects.filter(id__in = victims)}
    elif filter != None and filter == 'Suspect':
        suspects = suspect_ids()
        choices = {choice.id: choice.full_name for choice in Person.objects.filter(id__in = suspects)}
    else:
        choices = {choice.id: choice.full_name for choice in Person.objects.all()}
    try:
         site_settings = SiteSettings.objects.all()[0]
         fuzzy_score_cutoff = site_settings.get_setting_value_by_name('idmanagement_name_cutoff')
         fuzzy_limit = site_settings.get_setting_value_by_name('idmanagement_name_limit')
    except BaseException:
        # use default hard coded values
        pass

    results = []
    matches = process.extractBests(person_name, choices, score_cutoff=fuzzy_score_cutoff, limit=fuzzy_limit)

    for match in matches:
        results.append(Person.objects.get(id=match[2]))

    return results

def pvot_ids():
    irf_victim_ids = Interceptee.objects.filter(kind = 'v').values_list('person', flat=True)
    vif_victim_ids = VictimInterview.objects.all().values_list('victim', flat=True)
    victim_ids = list(chain(irf_victim_ids, vif_victim_ids))
    
    form_categories = FormCategory.objects.filter(form__form_type__name='IRF', name='Interceptees')
    for form_category in form_categories:
        mod = __import__(form_category.storage.module_name, fromlist=[form_category.storage.form_model_name])
        interceptee_class = getattr(mod, form_category.storage.form_model_name, None)           
        irf_victim_ids = interceptee_class.objects.filter(kind = 'v').values_list('person', flat=True)
        victim_ids = victim_ids + list(irf_victim_ids)
    
    cif_forms = Form.objects.filter(form_type__name='CIF')
    for cif_form in cif_forms:
        mod = __import__(cif_form.storage.module_name, fromlist=[cif_form.storage.form_model_name])
        cif_class = getattr(mod, cif_form.storage.form_model_name, None)
        cif_victim_ids = cif_class.objects.all().values_list('main_pv', flat=True)
        victim_ids = victim_ids + list(cif_victim_ids)
    
    potential_victims = FormCategory.objects.filter(form__form_type__name='CIF', name='OtherPotentialVictims')
    for potential_victim in potential_victims:
        mod = __import__(potential_victim.storage.module_name, fromlist=[potential_victim.storage.form_model_name])
        potential_victim_class = getattr(mod, potential_victim.storage.form_model_name, None)           
        potential_victim_ids = potential_victim_class.objects.all().values_list('person', flat=True)
        victim_ids = victim_ids + list(potential_victim_ids)
    
    vdf_forms = Form.objects.filter(form_type__name='VDF')
    for vdf_form in vdf_forms:
        mod = __import__(vdf_form.storage.module_name, fromlist=[vdf_form.storage.form_model_name])
        vdf_class = getattr(mod, vdf_form.storage.form_model_name, None)
        vdf_victim_ids = vdf_class.objects.all().values_list('victim', flat=True)
        victim_ids = victim_ids + list(vdf_victim_ids)
    
    return victim_ids

def suspect_ids():
    irf_suspect_ids = Interceptee.objects.filter(kind = 't').values_list('person', flat=True)
    suspect_ids = list(irf_suspect_ids)

    form_categories = FormCategory.objects.filter(form__form_type__name='IRF', name='Interceptees')
    for form_category in form_categories:
        mod = __import__(form_category.storage.module_name, fromlist=[form_category.storage.form_model_name])
        interceptee_class = getattr(mod, form_category.storage.form_model_name, None)           
        irf_suspect_ids = interceptee_class.objects.filter(kind = 't').values_list('person', flat=True)
        suspect_ids = suspect_ids + list(irf_suspect_ids)
    
    person_boxes = FormCategory.objects.filter(form__form_type__name='CIF', name='PersonBoxes')
    for person_box in person_boxes:
        mod = __import__(person_box.storage.module_name, fromlist=[person_box.storage.form_model_name])
        person_box_class = getattr(mod, person_box.storage.form_model_name, None)           
        person_box_suspect_ids = person_box_class.objects.all().values_list('person', flat=True)
        suspect_ids = suspect_ids + list(person_box_suspect_ids)
        
    return suspect_ids
    
