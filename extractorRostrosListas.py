
# Importing the libraries
import cv2
# documentacion de mtodos de camara
# https://docs.opencv.org/3.0-beta/modules/videoio/doc/reading_and_writing_video.html?highlight=videocapture#videocapture-isopened

import numpy as np
import time
import pathlib

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
smile_cascade = cv2.CascadeClassifier('haarcascade_smile.xml')



#NombreCarpetaPrueba = "D:/Documentos HDD/10mo/TT1/Pruebas mulicategorico/Proyecto del " + time.strftime("%Y_%B_%d") + "_" + time.strftime('%H_%M_%S')
#NombreCarpetaTraining =NombreCarpetaPrueba + "/training_set"
#NombreCarpetaTest =NombreCarpetaPrueba + "/test_set"
#pathlib.Path(NombreCarpetaPrueba).mkdir(parents=True, exist_ok=True)
#pathlib.Path(NombreCarpetaTraining).mkdir(parents=True, exist_ok=True)
#pathlib.Path(NombreCarpetaTest).mkdir(parents=True, exist_ok=True)
#for i in range(numeroClases):
#    NombreCarpetaUsuario=NombreCarpetaTest + "/Usuario"+str(i+1)
#    pathlib.Path(NombreCarpetaUsuario).mkdir(parents=True, exist_ok=True)
#    NombreCarpetaUsuario=NombreCarpetaTraining + "/Usuario"+str(i+1)
#    pathlib.Path(NombreCarpetaUsuario).mkdir(parents=True, exist_ok=True)



nUsuarios=1
numeroImagen = 1
numeroUsuario = 1
tamanioCara =  (0,0,0)
dataRostros=[]
labelRostros=[]
valorGamma=1.3
valorGammaAlto=False
EncontroUsuario=False
resizeW = 96
resizeH = 130

# Defining a function that will do the detections
def detect(gray, frame):
    crop_img=np.array([0,0,0])
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        medidasX1 = int(x*1.15)
        medidasX2 = int(x+(w*0.82))
        medidasY2 = int(y*1.2)
        medidasY1 = int(y+(h*0.95))
        
#        cv2.rectangle(frame, (medidasX1, medidasY1), (medidasX2, medidasY2), (255, 0, 0), 2)
        crop_img = gray[medidasY2:medidasY1, medidasX1:medidasX2]
        
        tamanioCrop = np.shape(crop_img)
        if tamanioCrop == ():
            crop_img = np.array([[[0],[0],[0]],[[0],[0],[0]],[[0],[0],[0]]])
    return gray, crop_img,frame

def ajusteGamma(imagen,gamma=1.0):
    invGamma =  1.0 / gamma
    table = np.array([((i/255.0)**invGamma)*255
        for i in np.arange(0,256)]).astype("uint8")
    return cv2.LUT(imagen,table)


#video_capture = cv2.VideoCapture(0)
## Ajuste de ancho de espacio de visualizacion de camara
##video_capture.set(3,800)
## Ajuste de alto de espacion de visualizacion de camara
##video_capture.set(4,600)
##Ajustar frames por segundo
#video_capture.set(5,20)
#if video_capture.isOpened():
#    print("Inicializacion de camara exitosa")
#    print("Comienza captura de video")
#    while True:
#            
#        _, frame = video_capture.read()
#        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#    
#        
#        CorreccionGamma = ajusteGamma(gray,1.8)
#        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
#        Clahe_Gamma = clahe.apply(CorreccionGamma)
#        
#        gris,crop_img, frame = detect(Clahe_Gamma, frame)
#        # Para evitar que devuelve basura en este caso un entero cuando 
#        # no reconcoe algun rostro
##        if crop_img.all()==0:
##            tamanioCara = (0,0,0)
##        else:
##            tamanioCara = np.shape(crop_img)
##        cv2.imshow('Video original Gris', gray)
##        cv2.imshow('Video', frame)
#        cv2.imshow('Video corregido', Clahe_Gamma)
#        
#        """AJUSTARLO RESPECTO A LA DISTANCIA MINIMA QUE SE DEBA POSICIONAR UNA 
#        PERSONA FRENTE A LA CAMAR"""
##            
##        if tamanioCara[0] >int(resizeW*0.7):
##            # ajust de tamaño de rostros
##            crop_img = cv2.resize(crop_img,(resizeW,resizeH))
###            cv2.imwrite(NombreCarpetaPrueba+"/"+str(numeroUsuario)+"_"+str(numeroImagen)+".png", crop_img)
###            numeroImagen += 1
##            
##        if numeroImagen >=80:
##            if numeroUsuario >= nUsuarios:
##                break
##            else:            
##                print("********Termino de adquisisción de usuario"+str(numeroUsuario))
##                time.sleep(6)
##                print("********Empieza usuario "+str(numeroUsuario))
##                numeroUsuario+=1
##                numeroImagen=1
##    
##        
#        if cv2.waitKey(1) & 0xFF == ord('q'):
#            break
##        print("numeroImagen")
##        print(numeroImagen)
#        
#    #    print(tamanioCara[0])
#    
##        print(video_capture.get(5))
#else:
#    print("No se pudo conectar con la camara")
#    
#   
#print("---------------Termino de adquisisción de rostros----------------")

"""Verificacion de imagenes extraidas, se comparara """        


"""PRueba con raspberry camera"""


# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera

import cv2
 
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 15
rawCapture = PiRGBArray(camera, size=(640, 480))
 
# allow the camera to warmup
time.sleep(0.1)
 
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
    image = frame.array
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    
    CorreccionGamma = ajusteGamma(gray,1.8)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    Clahe_Gamma = clahe.apply(CorreccionGamma)
    
    gris,crop_img, frame = detect(Clahe_Gamma, image)
    # Para evitar que devuelve basura en este caso un entero cuando 
    # no reconcoe algun rostro
#        if crop_img.all()==0:
#            tamanioCara = (0,0,0)
#        else:
#            tamanioCara = np.shape(crop_img)
#        cv2.imshow('Video original Gris', gray)
#        cv2.imshow('Video', frame)
    cv2.imshow('Video corregido', frame)
 
	# show the frame
#	cv2.imshow("Frame", image)

	# clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
#video_capture.release()
#cv2.destroyAllWindows()