# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 20:25:32 2018

@author: shuuz
"""

import face_recognition
import cv2
import os
import numpy as np
import time
# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)
def recog( NombreCarpetaPrueba,numeroMuestrasRostros, target_names,db,ledes,pca, clf,video_capture ):
    if video_capture == 1.0:
        video_capture = cv2.VideoCapture(0) 
        print("Valor video Capture")
        print(video_capture)
        print("Simon")
    elif video_capture.isOpened() == False:
        video_capture.release()
        time.sleep(0.5)
        video_capture = cv2.VideoCapture(0) 
    
    images_encondes = []
    folders = os.listdir(NombreCarpetaPrueba)
    indiceImagen = 0
    
    for im in folders:
#        label =int(im[0])
        Rimagen = NombreCarpetaPrueba+"/"+im
        if indiceImagen==numeroMuestrasRostros:
            indiceImagen = 0
        if indiceImagen== 47 :
            print(Rimagen)
            print(type(Rimagen))
            image = face_recognition.load_image_file(Rimagen)
            image_face_encoding = face_recognition.face_encodings(image)[0]
            images_encondes.append(image_face_encoding)
        indiceImagen += 1

        
        
#    for i in range(numeroUsuarios):
        
#        images.append(face_recognition.load_image_file(pathImage))
        # Load a sample picture and learn how to recognize it.
#    image = face_recognition.load_image_file("/home/pi/Desktop/P2/chu.png")
#    obama_face_encoding = face_recognition.face_encodings(obama_image)[0]
#    
#    # Load a second sample picture and learn how to recognize it.
#    biden_image = face_recognition.load_image_file("/home/pi/Desktop/P2/chong.png")
#    biden_face_encoding = face_recognition.face_encodings(biden_image)[0]
#    
    # Create arrays of known face encodings and their names
#    known_face_encodings = [
#        obama_face_encoding,
#        biden_face_encoding
#    ]
#    known_face_names = [
#        "chu",
#        "chong",
#    
#    ]
#    
    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    nombre = "Sin reconocer"
    print("los target names:")
    print(target_names)
    print("Se comunico con camara:")
    if video_capture.isOpened():
        while True:
            # Grab a single frame of video
            ret, frame = video_capture.read()
        
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]
        
            # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(images_encondes, face_encoding)
                    nombre = "Desconocido"
        
                    # If a match was found in known_face_encodings, just use the first one.
                    if True in matches:
                        first_match_index = matches.index(True)
                        nombre = target_names[first_match_index]
        
                    face_names.append(nombre)
        
            process_this_frame = not process_this_frame
        
        
            # Display the results
            for (top, right, bottom, left), nombre in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
        
                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        
                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (255, 255, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, nombre, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                db.child("Facial").update({"RostroValidado":"False"})
    
                
                
            # Display the resulting image
            cv2.imshow('Video', frame)
        
            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if nombre == "Desconocido":
                db.child("Facial").update({"RostroValidado":"True"})
                db.child("Facial").update({"NombreRostroReconocido":nombre})
                ledes.off()
                time.sleep(0.4)
                ledes.on()
                time.sleep(0.4)
                ledes.off()
                time.sleep(0.4)
                ledes.on()
                time.sleep(0.4)
                ledes.off()
            elif nombre in target_names:
                db.child("Facial").update({"RostroValidado":"True"})
                db.child("Facial").update({"NombreRostroReconocido":nombre})
                ledes.off()
                time.sleep(0.4)
                ledes.on()
                time.sleep(0.4)
                ledes.off()
        
        # Release handle to the webcam
        video_capture.release()
        cv2.destroyAllWindows()
    return video_capture, nombre
