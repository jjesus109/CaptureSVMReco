"""
Script principal donde se ejecuta la extraccion de rostros y 
posteriormetne el entrenamiento

"""
print(__doc__)
import pyrebase
import time
import pathlib
import capturaRostrosQueues as cr
import svm_pca_final as svm
import cv2
#import

# conexion a firebase
def conectarFirebase():
    conexionExitosa=True
    firebase = 0
    db = 0
    valores = 0
    entrenamiento = "False"
    config = {
          "apiKey": "4yqY4AS24CGMfIFrNnaDVZYU4ITPl9XmE7mXmsCc",
          "authDomain": "casa-34c19.firebaseapp.com",
          "databaseURL": "https://casa-34c19.firebaseio.com",
          "storageBucket": "casa-34c19.appspot.com",
    #          "serviceAccount":  "base-rostros-firebase-adminsdk-2w8tl-1940b517ba.json"
          }
    try:
        firebase = pyrebase.initialize_app(config)
        db = firebase.database()
        # Para validara que si  se conecto se obtiene los datos de la los usuarios
        valores = db.child("Users").get()    
        entrenamiento = db.child("Facial/EntrenamientoHecho").get()    
    except:
        return False, firebase, db, valores,entrenamiento
    return conexionExitosa, firebase, db, valores, entrenamiento.val()

def obtenerRostros():
#    NombreCarpetaPrueba = "D:/Documentos HDD/10mo/TT1/Pruebas mulicategorico/Proyecto del " + time.strftime("%Y_%B_%d") + "_" + time.strftime('%H_%M_%S')
    NombreCarpetaPrueba = "/home/pi/Desktop/P2/Prue/" + time.strftime("%Y_%B_%d") + "_" + time.strftime('%H_%M_%S')+"/"
    pathlib.Path(NombreCarpetaPrueba).mkdir(parents=True, exist_ok=True)
    nombreUsuarios = []
    # Variable para saber si hubo pedos cuando capturo los rostros
    errorCaptura = True
    conexionExitosa,firebase,db, valores,_ = conectarFirebase()
    if conexionExitosa ==False:
        print("Favor de conectar a internet")
    else:
        # validacion para saber en que momento inicia la catura de los usuarios 
        # que tendran el acceso por reconocimiento 
        try:
            comenzarCaptura = db.child("Facial/Activacion").get()
            print("comenzarcaptura")
            print(comenzarCaptura.val())
        except:
            print("Favor de conectar a internet")
        if comenzarCaptura.val()  == "True":
            
            usuarios = list(valores.val())
            
            indexReconocimiento = []
            for i in range(len(usuarios)):
                # extraccion de variable para identificara  usuarios para reconocer
                respuesta = db.child("Users/"+str(usuarios[i])+"/reconocimiento").get() 
                # identifacion de nombre de usuarios para obtener su nombre
                Nusuarios = db.child("Users/"+str(usuarios[i])+"/name").get() 
                if respuesta.val() == "True":
                    indexReconocimiento.append(i)
                    nombreUsuarios.append(Nusuarios.val())
                print("Nombres usuarios")
                print(nombreUsuarios)
#            numeroUsuariosDeteccion = len(usuarios)
#            for j in range(len(nombreUsuarios)):
            print("Estes es el numero de usuarios:")
            print(len(nombreUsuarios))
            p, inputQueue, outputQueue = 0 ,0 ,0
            llamada=False
#            for i in range(len(nombreUsuarios)):
            NombresEtiquetas={}
            numeroUsuarios=1
            while numeroUsuarios<4:
                deteccionActivada = db.child("Facial/Activacion2").get()
                if deteccionActivada.val()=="True":
                    deteccionActivadaUsuario = db.child("Facial/UsuarioActivado").get()
                    deteccionActivadaUsuario = deteccionActivadaUsuario.val()
                    deteccion_correcta,p, inputQueue, outputQueue, videoCapture= cr.capturaCamara(NombreCarpetaPrueba,i,llamada,p, inputQueue, outputQueue)
                    numeroUsuarios+=1
                    db.child("Facial").update({"Activacion2":"False"})
                    NombresEtiquetas.update({str(numeroUsuarios):deteccionActivadaUsuario})
                    
                llamada=True
            if deteccion_correcta == False:
                print("Error al capturar los rostros")
                errorCaptura = True
                videoCapture.release()
            else:
                errorCaptura = False
                videoCapture.release()
        else:
            print("Aun no se inicia la captura de rostros")
            errorCaptura = True
            
    return errorCaptura,NombreCarpetaPrueba, nombreUsuarios, NombresEtiquetas


while True:
#def main():
    NombresEtiquetas = 0
    conexionExitosa,firebase,db, valores,entrenamiento = conectarFirebase()
    if entrenamiento=="False":
        try:
            errorObtencion = True
            errorObtencion, NombreCarpetaPrueba, nombreUsuarios, NombresEtiquetas = obtenerRostros()
        except:
            print("Fallo en metodo de obtencion de rostros")
        if errorObtencion ==False:
            try:
                svm.SVM(NombreCarpetaPrueba,nombreUsuarios)
                print("Termino modelo")
                print("Coninua con identifcacion de rostros")
                db.child("Facial").update({"EntrenamientoHecho":"True"})  
                break
    
            except:
                print("Fallo modelo")
                print("reintentando")
    else:
        break
"""
Metodos para reconocimiento
"""

# Importing the libraries
#import cv2
import numpy as np   
from multiprocessing import Process
from multiprocessing import Queue
#import time

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


def reconocimiento(db,llamada,indexCamara, p, inputQueue, outputQueue):
    print("Estos son los target names")
    print(target_names)
    
    video_capture = cv2.VideoCapture(indexCamara)
    nombre="sin reconocer"
    resizeW = 96
    resizeH = 130
    listaImagenes = []
    numeroappend=0
    if llamada == False:
        inputQueue = Queue(maxsize=1)
        outputQueue = Queue(maxsize=1)
        p = Process(target=detect, args=(inputQueue, outputQueue,))
        p.daemon = True
        p.start()
        print("Esta vivo el proceso??")
        print(p.is_alive())
    vectorDim = [0,0,0,0]
    print("[INFO] starting process...")
    
    
#    print( p.exitcode == -signal.SIGTERM)
    conexionCamara = True
    conexionCamara = video_capture.isOpened()
    video_capture.set(3 ,312)
    video_capture.set(4, 512)
    print("Se comunico con camara:" +str(video_capture.isOpened()))
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
                        nombre = NombresEtiquetas.get(str(target_probable),"Desconocido")
                        listaImagenes = []
                        print("ya reconocio a:")
                        print(nombre)
                        cv2.putText(frame, nombre, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                        db.child("Facial").update({"RostroValidado":"True"})
                        db.child("Facial").update({"NombreRostro":nombre})
                        break
                    else:
                        print("aun no")
#                        print("Width :"+str(video_capture.get(3)))
#                        print("Height :"+str(video_capture.get(4)))

                        db.child("Facial").update({"RostroValidado":"False"})
                    
        
            cv2.putText(frame, nombre, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            numeroappend += 1
            cv2.imshow('Video', frame)
        ##    cv2.imshow('Video correccion', Clahe_Gamma)
        
#            if cv2.waitKey(1) & 0xFF == ord('q'):
#               break
       
#    p.join()    
    print("Salio del while")
    video_capture.release()
    cv2.destroyAllWindows()
    return conexionCamara, p, inputQueue, outputQueue,video_capture 

    

print("Inicia reconocimiento de rostros")
conexionExitosa,firebase,db, valores, entrenamiento = conectarFirebase()
import recog_queues as rL
from gpiozero import MotionSensor
pir = MotionSensor(4) # Numero de pin de raspberry
#import pickle
#data = open(NombreCarpetaPrueba+"/archivo_modelo_LBP.pickle",'wb')
#ya llamo a process
llamada = False
p, inputQueue, outputQueue = 0 ,0 ,0
indexCamara=1
while True:
#    pir.when_motion = rL.reconocimiento(db)
#    print("En el While de recog")
#    sensor = db.child("Facial/Activacion").get()
#    """Leer datos del senosor de presencia"""
    
    """cuando detecte presencia"""
#    print("Vallor de sensor"+str(sensor.val()))
    if pir.motion_detected:
#    if sensor.val()=="True":
        print("Index actual = " + str(indexCamara))
        conexionCamara, p, inputQueue, outputQueue, vd = rL.reconocimiento(db,llamada,indexCamara,p, inputQueue, outputQueue)
        vd.release()
        if conexionCamara== False:
            indexCamara += 1
            
            if indexCamara>=3:
                indexCamara=0
        llamada= True
        print("Sale del reconocimiento")
    time.sleep(0.5)
    print("Ya espero")
 

    
##    if cv2.waitKey(1) & 0xFF == ord('q'):
#    break
        
        
        