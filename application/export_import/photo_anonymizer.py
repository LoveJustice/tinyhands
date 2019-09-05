import numpy as np
import cv2
import os

from django.dispatch import receiver
from django.conf import settings

from dataentry.models import ExportImportCard, ExportImport
from dataentry.dataentry_signals import background_form_done


@receiver(background_form_done)
def anonymize_photo_receiver(sender, form_data, **kwargs):
    # IRF model object is form_data.form_object.
    if form_data.form.form_type.name == 'IRF':
        card_dict = form_data.card_dict
        ei = ExportImport.objects.get(form=form_data.form)
        ei_cards = ExportImportCard.objects.filter(export_import=ei)
        for card_list in card_dict:

            # Find card list that has the photo attribute (is Interceptee model)
            if len(card_dict[card_list]) > 0 and hasattr(card_dict[card_list][0].form_object, 'photo'):
                for card in card_dict[card_list]:
                    card_object = card.form_object
                    ## If interceptee is a victim and picture is not null and is not present in public folder
                    if card_object.kind == 'v' and  card_object.photo != '' and not os.path.exists(settings.PUBLIC_ROOT + '/interceptee_photos/'+ card_object.photo.path.split("/")[-1]):
                        anonymize_file_name = anonymize_photo(card_object.photo.path)
                        # Set anonymize_photo field to empty string if no faces were found, otherwise the file name including interceptee_photos
                        card_object.anonymized_photo = anonymize_file_name
                        card_object.save()


def anonymize_photo(image_path):
    image_name = image_path.split("/")[-1]
    image = cv2.imread(image_path)
    if image != None:
        result_image = image.copy()

        # Specify the trained cascade classifier
        face_cascade_path = "/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml"

        # Create a cascade classifier and load face cascade
        face_cascade = cv2.CascadeClassifier()
        face_cascade.load(face_cascade_path)

        #Preprocess the image
        grayimg = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        grayimg = cv2.equalizeHist(grayimg)

        #Run the classifiers
        faces = face_cascade.detectMultiScale(grayimg, 1.05, 2, 0|cv2.CASCADE_SCALE_IMAGE, (15, 15))
        write_path = settings.PUBLIC_ROOT+'/interceptee_photos/'+image_name
        
        if len(faces) != 0:
            for f in faces:
                # Get the origin co-ordinates and the length and width of face
                x, y, w, h = [ v for v in f ]
                sub_face = image[y:y+h, x:x+w]
                
                # Scale blur effect based on size of face
                blur_effect = h//8
                if blur_effect % 2 == 0:
                    blur_effect += 1
                
                # Apply Gaussian blur to face and merge that face with final image
                blurred_face = cv2.GaussianBlur(sub_face,(blur_effect, blur_effect), 30)
                result_image[y:y+h, x:x+w] = blurred_face
        
            cv2.imwrite(write_path, result_image)
            return 'interceptee_photos/' + image_name
        return ''