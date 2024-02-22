# from django.core.cache import cache

# from .forms import ParamsForm, IRFForm, PersonForm, FacematcherForm

# # Constants
# DEFAULT_IRF_PROMPT = "Select an IRF..."
# DEFAULT_PERSON_PROMPT = "Select a person..."


# # TODO: Remove abstraction for simplification or keep for consistency?
# # Returns form populated with previous selection and options
# def params_form(request):
#     return ParamsForm(request.session.get('submitted-params'))


# # Returns form populated with previous selection and options
# def irf_form(request, initial=False):
#     form = None
#     if initial:
#         form = IRFForm()
#     else:
#         form = IRFForm(request.session.get('submitted-irf'))
#     choices = [(irf, irf) for irf in request.session.get('irfs')]
#     choices.insert(0, ('', DEFAULT_IRF_PROMPT))
#     form.fields['irf'].choices = choices
#     return form


# # Returns form populated with previous selection and options
# def person_form(request, initial=False):
#     form = None
#     if initial:
#         form = PersonForm()
#     else:
#         form = PersonForm(request.session.get('submitted-person'))

#     irf = request.session.get('submitted-irf').get('irf')
#     matching_records = cache.get('matching_records')
#     results = matching_records[matching_records.irf_number == irf][[
#         'full_name', 'person_id']]
#     persons = [(results['person_id'][idx], ((str(results['person_id'][idx])) +
#                 " - " + results['full_name'][idx])) for idx in results.index]

#     choices = list([(person[0], person[1])
#                    for person in persons])
#     choices.insert(0, ('', DEFAULT_PERSON_PROMPT))
#     form.fields['person'].choices = choices
#     return form


# # Returns form populated with previous selection and options
# def facematcher_form(request, initial=False):
#     form = None
#     if initial:
#         form = FacematcherForm()
#     else:
#         form = FacematcherForm(request.session.get('submit-facematcher'))
#     return form
