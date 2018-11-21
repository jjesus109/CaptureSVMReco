# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 20:25:32 2018

@author: shuuz
"""
import cv2
import os
import time
import face_recognition

def encode(NombreCarpetaPrueba):
    images_encondes = []
    folders = os.listdir(NombreCarpetaPrueba)
#    indiceImagen = 1
    imagenes = ["1_27.","2_27.","3_27."]
    folders.sort()
    for im in folders:
#        print(label)
        label =im[0:5]
#        print(im)
        Rimagen = NombreCarpetaPrueba+"/"+im
#        if indiceImagen==numeroMuestrasRostros:
#            indiceImagen = 0
        
        if label in imagenes :
#            print(Rimagen)
#            print(type(Rimagen))
            image = face_recognition.load_image_file(Rimagen)
            image_face_encoding = face_recognition.face_encodings(image)[0]
            images_encondes.append(image_face_encoding)
        

        
    return images_encondes

def recog( images_encondes, target_names,db,ledes,pca, clf,video_capture ):
    ledes.on()
    if video_capture == 1.0:
        video_capture = cv2.VideoCapture(0) 
        print("Valor video Capture")
        print(video_capture)
        print("Simon")
    elif video_capture.isOpened() == False:
        video_capture.release()
        time.sleep(0.5)
        video_capture = cv2.VideoCapture(0) 
    
#    images_encondes = []
#    folders = os.listdir(NombreCarpetaPrueba)
##    indiceImagen = 1
#    imagenes = ["1_57.","2_57.","3_57."]
#    print("numero de muestras")
#    print(numeroMuestrasRostros)
#    for im in folders:
##        print(label)
#        label =im[0:5]
#        print(im)
#        Rimagen = NombreCarpetaPrueba+"/"+im
##        if indiceImagen==numeroMuestrasRostros:
##            indiceImagen = 0
#        if label in imagenes :
#            print(Rimagen)
#            print(type(Rimagen))
#            image = face_recognition.load_image_file(Rimagen)
#            image_face_encoding = face_recognition.face_encodings(image)[0]
#            images_encondes.append(image_face_encoding)
#        indiceImagen += 1
#
#        
        
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
                        print("Nombre: "+ nombre)
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
                db.child("Facial").update({"RostroValidado":True})
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
                time.sleep(3)
                print("reconocio a :")
                print(nombre)
                break
            elif nombre in target_names:
                db.child("Facial").update({"RostroValidado":True})
                db.child("Facial").update({"NombreRostroReconocido":nombre})
                ledes.off()
                time.sleep(0.4)
                ledes.on()
                time.sleep(0.4)
                ledes.off()
                time.sleep(3)
                print("reconocio a :")
                print(nombre)
                
                break
        
        # Release handle to the webcam
        video_capture.release()
        cv2.destroyAllWindows()
    return video_capture, nombre
