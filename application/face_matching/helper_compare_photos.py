# from .forms import ParamsForm, UploadPhotoForm

# def handle_compare_options_form_submission(request):
#     context = {}
#     if ('upload' in request.GET.get('photo_1')):
#         context['photo_1_form'] = UploadPhotoForm()
#     else:
#         context['photo_1_form'] = ParamsForm()
#     if ('upload' in request.GET.get('photo_2')):
#         context['photo_2_form'] = UploadPhotoForm()
#     else:
#         context['photo_2_form'] = ParamsForm()

#     return request, context