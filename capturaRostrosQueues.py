
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
            bgr = inputQueue.get()
            gray = gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY) 
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                medidasX1 = int(x*1.15)                
                medidasX2 = int(x+(w*0.88))
                medidasY2 = int(y*1.24)
                medidasY1 = int(y+(h*0.96))
#        cv2.rectangle(frame, (medidasX1, medidasY1), (medidasX2, medidasY2), (255, 0, 0), 2)
                
                vectorDim = [medidasX1,medidasY1,medidasX2,medidasY2] 
#                vectorDim = [x,y+h,x+w,y] 
#                vectorDim = [medidasX1,medidasY1,medidasX2,medidasY2] 
                outputQueue.put(vectorDim)

# Funcion de ajuste Gamma
def ajusteGamma(imagen,gamma):
    invGamma =  1.0 / gamma
    table = np.array([((i/255.0)**invGamma)*255

        for i in np.arange(0,256)]).astype("uint8")
    return cv2.LUT(imagen,table)



# se pasa el label del usuario desde el script principal
def capturaCamara(NombreCarpetaPrueba,numeroUsuarios, llamada,p, inputQueue, outputQueue , video_capture, ledes):

    


##    else:
#        video_capture.open(indexCamara)
    # Configuración de queues        
    
    resizeW = 180
    resizeH = 180
    vectorDim = [0,0,0,0]
    tamanioCara =  (0,0,0)
    numeroMuestrasRostros = 70
    numeroImagen = 1
    numeroUsuarioActual = numeroUsuarios         
    print("valor llamada : "+ str(llamada))
    if llamada == False:
        inputQueue = Queue(maxsize=1)
        outputQueue = Queue(maxsize=1)
        p = Process(target=_detect_, args=(inputQueue, outputQueue,))
        p.daemon = True
        p.start()
        print("Esta vivo el proceso??")
        print(p.is_alive())
    
#    video_capture.set(3 ,312)
#    video_capture.set(4, 512)
    conexionCamara = True
    if video_capture == 1.0:
        video_capture = cv2.VideoCapture(0) 
        print("Valor video Capture")
        print(video_capture)
        print("Simon")
    elif video_capture.isOpened() == False:
        video_capture.release()
        time.sleep(1)
        video_capture = cv2.VideoCapture(0) 

    conexionCamara = video_capture.isOpened()
    if video_capture.isOpened():
        ledes.on()
#        ledes.value = 0.7
        print("Inicializacion de camara exitosa")
        print("Comienza captura de video")
        while True:
            _, frame = video_capture.read()
#            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#            CorreccionGamma = ajusteGamma(gray,1.8)
#            clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
#            Clahe_Gamma = clahe.apply(CorreccionGamma)
#            

            CGamma = ajusteGamma(frame,1.2)
            clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
            lab = cv2.cvtColor(CGamma, cv2.COLOR_BGR2LAB)
            lab_planes = cv2.split(lab)
            lab_planes[0] = clahe.apply (lab_planes[0])
            lab = cv2.merge(lab_planes)
            bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
#            Clahe_Gamma = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
#                cv2.imshow("CAPTURA",Clahe_Gamma)
            if inputQueue.empty():
                inputQueue.put(bgr)
            if not outputQueue.empty():
                vectorDim = outputQueue.get()
            if vectorDim !=[0,0,0,0]:
                medidasX1,medidasY1,medidasX2,medidasY2 = vectorDim
                cv2.rectangle(frame, (medidasX1, medidasY1), (medidasX2, medidasY2), (255, 0, 0), 2)
                crop_img = bgr[medidasY2:medidasY1, medidasX1:medidasX2]
    #                crop_img = cv2.resize(crop_img,(resizeW,resizeH))
                # Para evitar que devuelve basura en este caso un entero cuando 
                # no reconcoe algun rostro


                tamanioCara = np.shape(crop_img)
#                print("se hace el crop")
                
                """AJUSTARLO RESPECTO A LA DISTANCIA MINIMA QUE SE DEBA POSICIONAR UNA 
                PERSONA FRENTE A LA CAMAR"""
                
                if tamanioCara[0] >int(resizeW*0.78):
                    # ajust de tamaño de rostros
#                    crop_img = cv2.resize(crop_img,(0,0),fx=0.7, fy=0.7)
                    crop_img = cv2.resize(crop_img,(resizeW,resizeH))
#                     cv2.imwrite(Rimagen, crop_img)
                    cv2.imwrite(NombreCarpetaPrueba+"/"+str(numeroUsuarioActual)+"_"+str(numeroImagen)+".png", crop_img)
                    time.sleep(0.1)
                    numeroImagen += 1
            
            
            # Solo se deje un usuario por que se realizará por usuario    
    #            print("numeroImagen")
            print(numeroImagen)
            cv2.imshow('Video', bgr)
            if cv2.waitKey(1) & 0xFF == ord('q'):
               break
            if numeroImagen >numeroMuestrasRostros:
                ledes.off()
#                ledes.value = 0.0
                print("********Termino de adquisisción de usuario"+str(numeroUsuarioActual))
                break
    else:
        print("no se conecto con la camara")
    #time.sleep(1)   

    video_capture.release()
    cv2.destroyAllWindows()
        
    return conexionCamara,p, inputQueue, outputQueue,video_capture,numeroMuestrasRostros-10
