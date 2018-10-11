
# Importing the libraries
import cv2
# https://docs.opencv.org/3.0-beta/modules/videoio/doc/reading_and_writing_video.html?highlight=videocapture#videocapture-isopened
import numpy as np
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
#smile_cascade = cv2.CascadeClassifier('haarcascade_smile.xml')
# Defining a function that will do the detections
def detect(gray, frame):
    crop_img=np.array([0,0,0])
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        medidasX1 = int(x*1.135)
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



# se pasa el label del usuario desde el script principal
def capturaCamara(numeroUsuario,NombreCarpetaPrueba):
    tamanioCara =  (0,0,0)
    resizeW = 96
    resizeH = 130
    video_capture = cv2.VideoCapture(0)
    # Ajuste de ancho de espacio de visualizacion de camara
#    video_capture.set(3,800)
    # Ajuste de alto de espacion de visualizacion de camara
#    video_capture.set(4,600)
    #Ajustar frames por segundo
    #video_capture.set(5,40)
    numeroImagen = 1
    if video_capture.isOpened():
        print("Inicializacion de camara exitosa")
        print("Comienza captura de video")
        while True:
                
            _, frame = video_capture.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
            
            CorreccionGamma = ajusteGamma(gray,1.8)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            Clahe_Gamma = clahe.apply(CorreccionGamma)
            
            gris,crop_img, frame = detect(Clahe_Gamma, frame)
            # Para evitar que devuelve basura en este caso un entero cuando 
            # no reconcoe algun rostro
            if crop_img.all()==0:
                tamanioCara = (0,0,0)
            else:
                tamanioCara = np.shape(crop_img)
            cv2.imshow('Video original Gris', gray)
#            cv2.imshow('Video', frame)
##             cv2.imshow('Video corregido', Clahe_Gamma)
            
            """AJUSTARLO RESPECTO A LA DISTANCIA MINIMA QUE SE DEBA POSICIONAR UNA 
            PERSONA FRENTE A LA CAMAR"""
                
            if tamanioCara[0] >int(resizeW*0.7):
                # ajust de tamaño de rostros
                crop_img = cv2.resize(crop_img,(resizeW,resizeH))
                cv2.imwrite(NombreCarpetaPrueba+"/"+str(numeroUsuario)+"_"+str(numeroImagen)+".png", crop_img)
                numeroImagen += 1
            # Solo se deje un usuario por que se realizará por usuario    
            if numeroImagen >=80:
                print("********Termino de adquisisción de usuario"+str(numeroUsuario))
                break
            
            print("numeroImagen")
            print(numeroImagen)
        # Conexion extiosa con Camara
        conexionCamara = True 
    
    else:
        print("No se pudo conectar con la camara")
        # NO se pudo conectar con camara
        conexionCamara = False
    video_capture.release()
    cv2.destroyAllWindows()
    return conexionCamara,video_capture
