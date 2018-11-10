
# Importing the libraries
import cv2
# https://docs.opencv.org/3.0-beta/modules/videoio/doc/reading_and_writing_video.html?highlight=videocapture#videocapture-isopened
import numpy as np
from multiprocessing import Process
from multiprocessing import Queue
import time
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def _detect_(inputQueue, outputQueue):
    while True:
        if not inputQueue.empty():
            gray = inputQueue.get()
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                medidasX1 = int(x*1.135)
                medidasX2 = int(x+(w*0.82))
                medidasY2 = int(y*1.2)
                medidasY1 = int(y+(h*0.95))
                vectorDim = [x,y+h,x+w,y] 
                outputQueue.put(vectorDim)

# Funcion de ajuste Gamma
def ajusteGamma(imagen,gamma=1.0):
    invGamma =  1.0 / gamma
    table = np.array([((i/255.0)**invGamma)*255

        for i in np.arange(0,256)]).astype("uint8")
    return cv2.LUT(imagen,table)


from gpiozero import LED
ledes = LED(17)
# se pasa el label del usuario desde el script principal
def capturaCamara(NombreCarpetaPrueba,numeroUsuarios, llamada,p, inputQueue, outputQueue ):
    # Configuración de queues        
    vectorDim = [0,0,0,0]
    
    if llamada == False:
        inputQueue = Queue(maxsize=1)
        outputQueue = Queue(maxsize=1)
        p = Process(target=_detect_, args=(inputQueue, outputQueue,))
        p.daemon = True
        p.start()
        print("Esta vivo el proceso??")
        print(p.is_alive())
    print("se prenden los ledes")
    ledes.on()
    tamanioCara =  (0,0,0)
#    resizeW = 96
#    resizeH = 130
    numeroMuestrasRostros=160

    numeroImagen = 1
#    numeroUsuarioActual= 1
    numeroUsuarioActual = numeroUsuarios 
    print("La captura de rostros del usuario "+str(numeroUsuarioActual))
    for i in range(3):
        print("Inicia en " +str(3-i))
        time.sleep(1)
        
    video_capture = cv2.VideoCapture(0)
    # Ajuste de ancho de espacio de visualizacion de camara
    video_capture.set(3,640)
    # Ajuste de alto de espacion de visualizacion de camara
    video_capture.set(4,480)
    #Ajustar frames por segundo
    video_capture.set(5,10)
    if video_capture.isOpened():
        
        
        print("Inicializacion de camara exitosa")
        print("Comienza captura de video")
        
        
#        ledes.value = 0.6  
        while True:
                  
            _, frame = video_capture.read()
#
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            CorreccionGamma = ajusteGamma(gray,1.8)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            Clahe_Gamma = clahe.apply(CorreccionGamma)
            if inputQueue.empty():
                inputQueue.put(Clahe_Gamma)
            if not outputQueue.empty():
                vectorDim = outputQueue.get()
            if vectorDim !=[0,0,0,0]:
                medidasX1,medidasY1,medidasX2,medidasY2 = vectorDim
                cv2.rectangle(frame, (medidasX1, medidasY1), (medidasX2, medidasY2), (255, 0, 0), 2)
                crop_img = Clahe_Gamma[medidasY2:medidasY1, medidasX1:medidasX2]
#                crop_img = cv2.resize(crop_img,(resizeW,resizeH))
                # Para evitar que devuelve basura en este caso un entero cuando 
                # no reconcoe algun rostro
                if crop_img.all()==0:
                    tamanioCara = (0,0,0)
#                    print("tamaño de cara pequeño")
                else:
                    tamanioCara = np.shape(crop_img)
#                    print("se hace el crop")
                
                """AJUSTARLO RESPECTO A LA DISTANCIA MINIMA QUE SE DEBA POSICIONAR UNA 
                PERSONA FRENTE A LA CAMAR"""
                
                if tamanioCara[0] >int(resizeW*0.7):
                    # ajust de tamaño de rostros
                    crop_img = cv2.resize(crop_img,(0,0),fx=0.7, fy=0.7)
                    cv2.imwrite(NombreCarpetaPrueba+"/"+str(numeroUsuarioActual)+"_"+str(numeroImagen)+".png", crop_img)
                    time.sleep(0.1)
                    numeroImagen += 1
            
            
            # Solo se deje un usuario por que se realizará por usuario    
#            print("numeroImagen")
            print(numeroImagen)
            if numeroImagen >numeroMuestrasRostros:
                
                print("********Termino de adquisisción de usuario"+str(numeroUsuarioActual))
#                ledes.value = 0
                ledes.off()
                break
        # Conexion extiosa con Camara
        conexionCamara = True 
    
    else:
        print("No se pudo conectar con la camara")
        # NO se pudo conectar con camara
        conexionCamara = False
    #termino de proceso y de queue
    
#    video_capture.release()
    time.sleep(0.1)   
    return conexionCamara,p, inputQueue, outputQueue,video_capture 
