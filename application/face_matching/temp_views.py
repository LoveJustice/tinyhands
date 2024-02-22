# from django.shortcuts import render

# from . import helper, helper_take_photo, helper_upload_photo, helper_compare_photos
# from .forms import UploadPhotoForm, ParamsForm


# def home(request):
#     context = {}
#     return render(request, 'home.html', context=context)


# def compare_photos(request):
#     context = {}
    
#     # Render two forms based on user selection
#     print(request.GET)
#     if 'photo_1' in request.GET and 'photo_2' in request.GET:
#             print('yes')
#             request, context = helper_compare_photos.handle_compare_options_form_submission(request)
#         # return render(request, 'compare_photos.html', context=context)

#     context['nav'] = 'compare'
#     return render(request, 'compare_photos.html', context=context)


# # Renders page for selecting a photo for analysis based on filters
# def select_from_records(request):
#     context = {}

#     # If params_form has been submitted, handle form submission
#     if 'submit-params' in request.GET:
#         request, context = helper.handle_params_form_submission(request)
#         return render(request, 'select_from_records.html', context=context)

#     # If IRF has been selected and submitted from dropdown
#     if 'submit-irf' in request.GET:
#         request, context = helper.handle_irf_form_submission(request)
#         return render(request, 'select_from_records.html', context=context)

#     # If person_id has been selected and submitted from dropdown
#     if 'submit-person' in request.GET:
#         request, context = helper.handle_person_form_submission(request)
#         return render(request, 'select_from_records.html', context=context)

#     # Display empty form
#     form = ParamsForm()
#     context['nav'] = 'select'
#     return render(request, 'select_from_records.html', {'params_form': form})


# Renders page for uploading a photo for analysis
def upload_photo(request):
    context = {}

    # If file and parameters have been submitted, handle form submission
    if 'submit-upload-photo' in request.POST:
        request, context = helper_upload_photo.handle_upload_photo_form_submission(
            request)
        return render(request, 'upload_photo.html', context=context)

    # Display empty form
    context['upload_photo_form'] = UploadPhotoForm()
    context['nav'] = 'upload'
    return render(request, 'upload_photo.html', context=context)


# # Renders page for taking a photo and uploading it for analysis
# def take_photo(request):
#     context = {}
#     context['nav'] = 'take'

#     (
#         given_encoding,
#         selected_person,
#         selected_person_image,
#         selected_person_np,
#     ) = helper_take_photo.handle_take_picture_choice()

#     # Populate context with data for output
#     # TODO: Replace with actual output
#     print("selected_person: ", selected_person)
#     context['selected_person'] = selected_person

#     return render(request, 'take_photo.html', context=context)
