# -*- coding: utf-8 -*-
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
from gpiozero import LED
ledes = LED(17)
# Activacion variable para saber cuando esta activado el sensor
#NombreCarpetaPrueba = "D:/Documentos HDD/10mo/TT1/Pruebas mulicategorico/Proyecto del " + time.strftime("%Y_%B_%d") + "_" + time.strftime('%H_%M_%S')


# conexion a firebase
def conectarFirebase():
    conexionExitosa=True
    firebase = 0
    db = 0
    valores = 0
    entrenamiento = "False"
    config = {
#          "apiKey": "4yqY4AS24CGMfIFrNnaDVZYU4ITPl9XmE7mXmsCc",
#          "authDomain": "casa-34c19.firebaseapp.com",
#          "databaseURL": "https://casa-34c19.firebaseio.com",
#          "storageBucket": "casa-34c19.appspot.com",
          "apiKey": "tASIqdHPCcl9RrZ139kwoAMWjS68WMaQ62z9Hosr",
          "authDomain": "casa-90566.firebaseapp.com",
          "databaseURL": "https://casa-90566.firebaseio.com",
          "storageBucket": "casa-90566.appspot.com",    
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



def obtenerRostros(indexCamara):
    NombresEtiquetas={}
    targetnames = []
    # Variable para saber si hubo pedos cuando capturo los rostros
    errorCaptura = True
    conexionExitosa,firebase,db, valores,_ = conectarFirebase()
    if conexionExitosa ==False:
        print("Favor de conectar a internet")
    else:
        # validacion para saber en que momento inicia la catura de los usuarios 
        # que tendran el acceso por reconocimiento 
        try:
            comenzarCaptura = db.child("Facial/IniciarCaptura").get()
            print("comenzarcaptura")
            print(comenzarCaptura.val())
            

        except:
            print("Favor de conectar a internet")
        if comenzarCaptura.val()  == "True":
            
            p, inputQueue, outputQueue = 0 ,0 ,0            
#            for i in range(len(nombreUsuarios)):
            
            numeroUsuarios=1
            numeroUsuariosAEntrenar = db.child("Facial/NumeroUsuarios").get()
            numeroUsuariosAEntrenar = int(numeroUsuariosAEntrenar.val())
            llamada=False
            

            video_capture = 1.0
            while numeroUsuarios<numeroUsuariosAEntrenar+1:
                deteccionActivada = db.child("Facial/Activacion").get()
                if deteccionActivada.val()=="True":
                    deteccionActivadaUsuario = db.child("Facial/UsuarioActivado").get()
                    deteccionActivadaUsuario = deteccionActivadaUsuario.val()
                    print("La captura de rostros del usuario "+deteccionActivadaUsuario)
                    for i in range(3):
                        print("Inicia en " +str(3-i))
                        time.sleep(1)
                    print("enciendo los ledes")
                    print("conectando con la camara...")        
                    
                    deteccion_correcta, p, inputQueue, outputQueue, video_capture= cr.capturaCamara(NombreCarpetaPrueba,numeroUsuarios,llamada,p, inputQueue, outputQueue,video_capture, ledes)
                    
                    if deteccion_correcta==True:
                        
                        NombresEtiquetas[numeroUsuarios] = deteccionActivadaUsuario
                        numeroUsuarios+=1
                        db.child("Facial").update({"Activacion":"False"})
                        print("Usuario capturado: "+deteccionActivadaUsuario)
                        print(NombresEtiquetas)
                    llamada=True
            
            keys = list(NombresEtiquetas.keys())
            keys.sort()
            
            for i in keys:
                
                targetnames.append(NombresEtiquetas[i])
            print("Estos son los los target names")
            print(targetnames)
            if deteccion_correcta == False:
                print("Error al capturar los rostros")
                errorCaptura = True
#                videoCapture.release()

            else:
                errorCaptura = False
#                videoCapture.release()
                print("Termino captura de rostros exitosament")
        else:
            print("Aun no se inicia la captura de rostros")
            errorCaptura = True
            
            
    return errorCaptura,NombreCarpetaPrueba, targetnames, NombresEtiquetas,video_capture, indexCamara


import validarRostro as vR
indexCamara = 0
video_capture = 1.0
while True:
    NombresEtiquetas = 0
    conexionExitosa,firebase,db, valores,entrenamiento = conectarFirebase()
    if entrenamiento=="False":
        NombreCarpetaPrueba = "/home/pi/Desktop/P2/Imagenes/Proyecto del " + time.strftime("%Y_%B_%d") + "_" + time.strftime('%H_%M_%S')
        #NombreCarpetaPrueba = "/home/pi/Desktop/P2/Prue/2018_October_11_16_49_11/"
        pathlib.Path(NombreCarpetaPrueba).mkdir(parents=True, exist_ok=True)
#        try:
        errorObtencion = True
        errorObtencion, NombreCarpetaPrueba, nombreUsuarios, NombresEtiquetas, video_capture, indexCamara= obtenerRostros(indexCamara)
#        except:
#            print("Fallo en metodo de obtencion de rostros")
            
        if errorObtencion ==False:
#            try:
            print("ruta carpeta imagenes: "+NombreCarpetaPrueba)
            vR.filtrar(NombreCarpetaPrueba)
#            NombreCarpetaPrueba = "/home/pi/Desktop/P2/CaptureSVMReco/"
            svm.SVM(NombreCarpetaPrueba,nombreUsuarios)
            print("Termino modelo")
            print("Coninua con identifcacion de rostros")
            db.child("Facial").update({"EntrenamientoHecho":"True"})  
            break

    else:
        break
    

print("Inicia clasificación de rostros")
print("conectandose a Firebase")
conexionExitosa,firebase,db, valores, entrenamiento = conectarFirebase()


import recog_queues as rL
from gpiozero import MotionSensor
import pickle 
pir = MotionSensor(4) # Numero de pin de raspberry
tomaDatos = open("archivo_modelo_LBP.pickle", "rb")
datos = pickle.load(tomaDatos)
clf = datos["modelo"]
pca = datos["pca"]
target_names =datos["target_names"]
print(target_names)
#ya llamo a process
llamada = False
p, inputQueue, outputQueue = 0 ,0 ,0

while True:
    print("Index actual = " + str(indexCamara))
#    """Leer datos del senosor de presencia"""
    if pir.motion_detected:
    
        print("Index actual = " + str(indexCamara))
#        ledes.on()
        conexionCamara, p, inputQueue, outputQueue, video_capture,nombre = rL.reconocimiento(db,llamada,indexCamara,p, inputQueue, outputQueue,video_capture, ledes, clf, pca, target_names)
#        vd.release()
#        ledes.off()
        if nombre=="Desconocido":
            time.sleep(4)
        elif nombre!="Desconocido":
            time.sleep(2)    

        llamada= True
        print("valor llamada: "+ str(llamada))
        print("Sale del reconocimiento")
        
        
    time.sleep(1)
    
    print("Ya espero")
 

        
        