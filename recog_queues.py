# Importing the libraries
import cv2
import numpy as np   
from multiprocessing import Process
from multiprocessing import Queue
import time

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
import pickle




#from skimage.feature import local_binary_pattern
#radius = 4
#n_points = 9


def detect(inputQueue, outputQueue):
#    crop_img=np.array([0,0,0])
    while True:
        if not inputQueue.empty():
            gray = inputQueue.get()
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
#            print("Aqui en faces")
            for (x, y, w, h) in faces:
                medidasX1 = int(x*1.15)                
                medidasX2 = int(x+(w*0.88))
                medidasY2 = int(y*1.24)
                medidasY1 = int(y+(h*0.96))
#        cv2.rectangle(frame, (medidasX1, medidasY1), (medidasX2, medidasY2), (255, 0, 0), 2)
                
                vectorDim = [medidasX1,medidasY1,medidasX2,medidasY2] 
#                vectorDim = [x,y+h,x+w,y] 
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
    probaminima = 0.8
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

def diferenciaProbas(probabilidades,probabilidadesLista):
    nCategorias = probabilidades.shape[1]-1
    for i in range(len(probabilidades)):
        arreglo = probabilidades[i]
        valorMax = arreglo.max()
        categoria = probabilidadesLista[i].index(valorMax)
        otroValorPosicion = abs(categoria- nCategorias)
        otroValor = arreglo[otroValorPosicion]
        diferenciaProbas = valorMax - otroValor
        if diferenciaProbas >=0.4:
            arreglo[valorMax] =  arreglo[valorMax]*2
        return probabilidades
            
            
#    maximaProba = matrizlista[i].index(valor)
    
    
     
radius = 4
n_points = 8
nro = 0
from skimage.feature import local_binary_pattern

def reconocimiento(db,llamada,indexCamara, p, inputQueue, outputQueue, video_capture, ledes, clf, pca, target_names):


#    video_capture = cv2.VideoCapture(indexCamara)
    nombre="sin reconocer"
    resizeW = 96
    resizeH = 96
    listaImagenes = []
    
    if llamada == False:
        inputQueue = Queue(maxsize=1)
        outputQueue = Queue(maxsize=1)
        p = Process(target=detect, args=(inputQueue, outputQueue,))
        p.daemon = True
        p.start()
        print("Esta vivo el proceso??")
        print(p.is_alive())
    vectorDim = [0,0,0,0]

    
    
#    print( p.exitcode == -signal.SIGTERM)
    conexionCamara = True
    if video_capture == 1.0:
        video_capture = cv2.VideoCapture(0) 
        print("Valor video Capture")
        print(video_capture)
        print("Simon")
    elif video_capture.isOpened() == False:
        video_capture.release()
        time.sleep(0.5)
        video_capture = cv2.VideoCapture(0) 
    conexionCamara = video_capture.isOpened()
#    video_capture.set(3 ,312)
#    video_capture.set(4, 512)
    print("los target names:")
    print(target_names)
    print("Se comunico con camara:")
    if video_capture.isOpened():
        print(str(video_capture.isOpened()))
        
        n=1
        ledes.on()
#        ledes.value= 0.7
        while True:
            _, frame = video_capture.read()
        
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            CorreccionGamma = ajusteGamma(gray,1.6)
            clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
            Clahe_Gamma = clahe.apply(CorreccionGamma)
            
            if inputQueue.empty():
                inputQueue.put(Clahe_Gamma)
            if not outputQueue.empty():
                vectorDim = outputQueue.get()
            if vectorDim !=[0,0,0,0]:
                medidasX1,medidasY1,medidasX2,medidasY2 = vectorDim
                cv2.rectangle(Clahe_Gamma, (medidasX1, medidasY1), (medidasX2, medidasY2), (255, 0, 0), 2)
                crop_img = Clahe_Gamma[medidasY2:medidasY1, medidasX1:medidasX2]
                tamanioCara = np.shape(crop_img)
                if tamanioCara[0] >int(resizeW*0.98):
                    
                    n += 1
                    crop_img = cv2.resize(crop_img,(resizeW,resizeH))
                    cv2.imwrite(str(n)+".jpg",crop_img)
                    time.sleep(0.1)
#                    crop_img = cv2.imread(str(n)+".jpg")
#                    crop_img = cv2.cvtColor(crop_img,cv2.COLOR_BGR2GRAY)
                    lbp = local_binary_pattern(crop_img, n_points, radius, 'default')
                    imagenFlatten = lbp.ravel()
                    imagenFlatten = crop_img.ravel()
                    imagenLista = imagenFlatten.tolist()
                    listaImagenes.append(imagenLista)
                    if len(listaImagenes)==20:
                        del listaImagenes[0:10]
                        n = 0
                        matrizImagenes= np.array(listaImagenes)
                        prueba_pca = pca.transform(matrizImagenes)
                        probabilidades = clf.predict_proba(prueba_pca)
        #                matriz = probabilidades
        #                matrizlista = probabilidades.tolist()
                        print("probas antes de yorch")
                        print(probabilidades)
                        probabilidades = diferenciaProbas(probabilidades,probabilidades.tolist())
                        print("probas despues de yorch")
                        print(probabilidades)
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
                            ledes.off()
                            time.sleep(0.4)
                            ledes.on()
                            time.sleep(0.4)
                            

                        else:
                            probabilidadSumada = probas[target_probable]
                            probabilidadFinal = probabilidadSumada/frecuencia
                            nombreUsuario = target_names[target_probable]
                            nombre = nombreUsuario+":"+str(probabilidadFinal*100)
                            ledes.off()
                            time.sleep(0.4)
                            ledes.on()
                            time.sleep(0.4)
                            ledes.off()
                            time.sleep(0.4)
                            ledes.on()
                            time.sleep(0.4)
                            

#                       
                        listaImagenes = []
                        print("ya reconocio a:")
                        print(nombre)
                        cv2.putText(frame, nombre, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                        db.child("Facial").update({"RostroValidado":True})
                        db.child("Facial").update({"NombreRostroReconocido":nombre})
                        
                        
                        break
                    else:

                        db.child("Facial").update({"RostroValidado":False})
            cv2.imshow('Video correccion', Clahe_Gamma)
        
            if cv2.waitKey(1) & 0xFF == ord('q'):
               break

    print("False")
#    p.join()    
    print("Salio del while")
#    video_capture.release()
    ledes.off()
    cv2.destroyAllWindows()
    return conexionCamara, p, inputQueue, outputQueue,video_capture,nombre 
