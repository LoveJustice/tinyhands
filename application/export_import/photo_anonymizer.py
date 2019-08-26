#import numpy as np
import cv2

from dataentry.models import ExportImportCard, ExportImport

from django.dispatch import receiver

from django.conf import settings

from dataentry.dataentry_signals import form_done

@receiver(form_done)
def anonymize_photo_receiver(sender, form_data, **kwargs):
    # IRF model object is form_data.form_object.
    import pdb;
    if form_data.form.form_type.name == 'IRF':
        card_dict = form_data.card_dict
        ei = ExportImport.objects.get(form=form_data.form)
        ei_cards = ExportImportCard.objects.filter(export_import=ei)
        for card_list in card_dict:
            # If there are cards and it has the photo attribute (is Interceptee model)
            if len(card_dict[card_list]) > 0 and hasattr(card_dict[card_list][0].form_object, 'photo'):
                for card in card_dict[card_list]:
                    #card_data = card_dict[card_list][0]
                    #print(card_data)
                    ## IF not null pic and not present in other folder - run process
                    ## Save file in other folder with name in interceptee object
                    card_object = card.form_object
                    print("---")
                    print(card_object.photo.path)
                    print(card_object.photo.name.split('/',1)[-1])
                    print('saved')
                    path = settings.PUBLIC_ROOT + '/interceptee_photos/'
                    print(path)
                    #result_img = anonymize_photo(card_object.anonymize_photo)
                    print("Here")

def anonymize_photo(image_path):
    image = cv2.imread(image_path)
    result_image = image.copy()

    # Specify the trained cascade classifier
    #TODO find path
    face_cascade_name = "/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml"

    # Create a cascade classifier
    face_cascade = cv2.CascadeClassifier()

    # Load the specified classifier
    face_cascade.load(face_cascade_name)


    #face_cascade = cv2.CascadeClassifier('/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('/usr/local/share/OpenCV/haarcascades/haarcascade_eye.xml')

    #Preprocess the image
    grayimg = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    grayimg = cv2.equalizeHist(grayimg)

    #Run the classifiers
    faces = face_cascade.detectMultiScale(grayimg, 1.05, 2, 0|cv2.CASCADE_SCALE_IMAGE, (30, 30))

    print ("Faces detected")

    if len(faces) != 0:         # If there are faces in the images
        for f in faces:         # For each face in the image

            # Get the origin co-ordinates and the length and width till where the face extends
            x, y, w, h = [ v for v in f ]

            # get the rectangle img around all the faces
            #cv2.rectangle(image, (x,y), (x+w,y+h), (255,255,0), 5)
            roi_gray = grayimg[y:y+h, x:x+w]
            sub_face = image[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray, 1.5,2,0|cv2.CASCADE_SCALE_IMAGE, (30,30))
            for (ex,ey,ew,eh) in eyes:
                #cv2.rectangle(sub_face,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
            # apply a gaussian blur on this new recangle image
                eye = image[y+ey:y+ey+eh,x+ex:x+ex+ew]
                blurred_eye = cv2.GaussianBlur(eye,(23, 23), 30)
            # merge this blurry rectangle to our final image
                print(blurred_eye.shape)
                result_image[ey+y:ey+y+blurred_eye.shape[0], ex+x:ex+x+blurred_eye.shape[1]] = blurred_eye
            face_file_name = "./face_" + str(y) + ".jpg"
            #cv2.imwrite(face_file_name, sub_face)

    # cv2.imshow("Detected face", result_image)
    return result_image
    #cv2.imwrite("./result.png", result_image)