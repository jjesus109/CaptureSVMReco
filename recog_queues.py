# Importing the libraries
import cv2
import numpy as np   
from multiprocessing import Process
from multiprocessing import Queue
import time

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
import pickle

tomaDatos = open("/home/pi/Desktop/P2/archivo_modelo_LBP.pickle", "rb")
datos = pickle.load(tomaDatos)
clf = datos["modelo"]
pca = datos["pca"]
target_names =datos["target_names"]


#from skimage.feature import local_binary_pattern
#radius = 4
#n_points = 9


def detect(inputQueue, outputQueue):
    while True:
        if not inputQueue.empty():
            gray = inputQueue.get()
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
#            print("Aqui en faces")
            for (x, y, w, h) in faces:
                
                medidasX1 = int(x*1.135)
                medidasX2 = int(x+(w*0.82))
                medidasY2 = int(y*1.2)
                medidasY1 = int(y+(h*0.95))
                vectorDim = [medidasX1,medidasY1,medidasX2,medidasY2] 
#                cv2.rectangle(frame, (medidasX1, medidasY1), (medidasX2, medidasY2), (255, 0, 0), 2)
                outputQueue.put(vectorDim)
                


def ajusteGamma(imagen,gamma=1.0):
    invGamma =  1.0 / gamma
    table = np.array([((i/255.0)**invGamma)*255
        for i in np.arange(0,256)]).astype("uint8")
    return cv2.LUT(imagen,table)
valorGamma=1.2
valorGammaAlto=False
EncontroUsuario=False


def obtenerModa(matriz,matrizlista):
    listavalores=[]
    probaminima = 0.98
    repeticiones = {}
    probas = {}
#    numeroRepeticiones
    for i in range(len(matriz)):
        valor = matriz[i].max()
        categoria = matrizlista[i].index(valor)
        # Evalua que el valor este por encima de la probabilidad minima
        if valor>probaminima:
            listavalores.append(categoria)
        # Si no es asi, pone un cero
        else:
            listavalores.append(-1)
            categoria = -1
        if categoria in listavalores:
            try:
                repeticiones[categoria] += 1
                probas[categoria] += valor
            except:
                repeticiones[categoria] = 1
                probas[categoria] = valor
        else:
            repeticiones[categoria] = 1
            probas[categoria] = valor
    
    return repeticiones, probas
    

def mayorFrecuencia(dk2):
     
     valores=list(dk2.values())
     llaves=list(dk2.keys())
     if llaves[valores.index(max(valores))]==-1:
         print(0)
         target = -1
     else:
         target = llaves[valores.index(max(valores))]
        
     return target, max(valores)


def reconocimiento(db):
    print("Estos son los target names")
    print(target_names)

    video_capture = cv2.VideoCapture(0)
    nombre="sin reconocer"
    resizeW = 96
    resizeH = 130
    listaImagenes = []
    numeroappend=0
    inputQueue = Queue(maxsize=2)
    outputQueue = Queue(maxsize=2)
    vectorDim = [0,0,0,0]
    print("[INFO] starting process...")
    p = Process(target=detect, args=(inputQueue, outputQueue,))
    p.daemon = True
    p.start()
    if video_capture.isOpened():
        while True:
            _, frame = video_capture.read()
        
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
                tamanioCara = np.shape(crop_img)
                if tamanioCara[0] >int(resizeW*0.7):
                    crop_img = cv2.resize(crop_img,(resizeW,resizeH))
                    imagenFlatten = crop_img.ravel()
                    imagenLista = imagenFlatten.tolist()
                    listaImagenes.append(imagenLista)
                    if len(listaImagenes)==10:
                        matrizImagenes= np.asarray(listaImagenes)
                        prueba_pca = pca.transform(matrizImagenes)
                        probabilidades = clf.predict_proba(prueba_pca)
        #                matriz = probabilidades
        #                matrizlista = probabilidades.tolist()
                        
                        repeticiones,probas = obtenerModa(probabilidades,probabilidades.tolist())
                        print("reps")
                        print(repeticiones)
                        print("proba")
                        print(probas)
                        # calcula la categoria mas repetida
                        target_probable, frecuencia = mayorFrecuencia(repeticiones)
                        print("target")
                        print(target_probable)
                        print("frw")
                        print(frecuencia)
                        if target_probable == -1:
                                nombre= "Desconocido"    
                        else:
                            probabilidadSumada = probas[target_probable]
                            probabilidadFinal = probabilidadSumada/frecuencia
                            nombreUsuario = target_names[target_probable]
                            nombre = nombreUsuario+":"+str(probabilidadFinal*100    )
                       
                        listaImagenes = []
                        print("ya reconocio a:")
                        print(nombre)
                        cv2.putText(frame, nombre, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                        db.child("Facial/RostroValidado").push("True")
                        db.child("Facial/NombreRostro").push(nombre)
                        break
                    else:
                        print("aun no")
                        db.child("Facial/RostroValidado").push("False")
                    
        
            cv2.putText(frame, nombre, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            numeroappend += 1
            cv2.imshow('Video', frame)
        ##    cv2.imshow('Video correccion', Clahe_Gamma)
        
            if cv2.waitKey(1) & 0xFF == ord('q'):
               break
    
    video_capture.release()
    cv2.destroyAllWindows()
    p.terminate()
    time.sleep(0.1)
    inputQueue.close()
    outputQueue.close()
#exit()
#quit()