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
          "apiKey": "4yqY4AS24CGMfIFrNnaDVZYU4ITPl9XmE7mXmsCc",
          "authDomain": "casa-34c19.firebaseapp.com",
          "databaseURL": "https://casa-34c19.firebaseio.com",
          "storageBucket": "casa-34c19.appspot.com",
#          "apiKey": "tASIqdHPCcl9RrZ139kwoAMWjS68WMaQ62z9Hosr",
#          "authDomain": "casa-90566.firebaseapp.com",
#          "databaseURL": "https://casa-90566.firebaseio.com",
#          "storageBucket": "casa-90566.appspot.com",    
    #          "serviceAccount":  "base-rostros-firebase-adminsdk-2w8tl-1940b517ba.json"
          }
    try:
        firebase = pyrebase.initialize_app(config)
        db = firebase.database()
        # Para validara que si  se conecto se obtiene los datos de la los usuarios
        valores = db.child("Users").get()
        entrenamiento = db.child("Facial/Configurado").get()
        return conexionExitosa, firebase, db, valores, entrenamiento.val()    
    except:
        return False, firebase, db, valores,entrenamiento
    



def obtenerRostros(indexCamara, targetnames, numeroUsuarios,NombresEtiquetas):
    detener = False
    deteccion_correcta=False
    video_capture = 1.0
    # Variable para saber si hubo pedos cuando capturo los rostros
    errorCaptura = True
    conexionExitosa,firebase,db, valores,_ = conectarFirebase()
    if conexionExitosa ==False:
        print("Favor de conectar a internet")
    else:
                 
        p, inputQueue, outputQueue = 0 ,0 ,0            
        numeroUsuariosAEntrenar = db.child("Facial/NumeroUsuarios").get()
        numeroUsuariosAEntrenar = int(numeroUsuariosAEntrenar.val())
        llamada=False
        


        while numeroUsuarios<numeroUsuariosAEntrenar+1:
            deteccionActivada = db.child("Facial/Captura").get()
            print("Esperando usuario para ser capturado...")
            detener= db.child("Facial/Detener").get()
            if detener.val() == True:
                break
            if deteccionActivada.val()==True:
                deteccionActivadaUsuario = db.child("Facial/UsuarioActivado").get()
                deteccionActivadaUsuario = deteccionActivadaUsuario.val()
                print("La captura de rostros del usuario "+deteccionActivadaUsuario)
                for i in range(3):
                    print("Inicia en " +str(3-i))
                    time.sleep(1)
                print("enciendo los #ledes")
                print("conectando con la camara...")        
                
                deteccion_correcta, p, inputQueue, outputQueue, video_capture,numeroMuestrasRostros= cr.capturaCamara(NombreCarpetaPrueba,numeroUsuarios,llamada,p, inputQueue, outputQueue,video_capture, ledes)
                
                if deteccion_correcta==True:

                    targetnames.append(deteccionActivadaUsuario)
                    numeroUsuarios+=1
                    db.child("Facial").update({"Captura":False})
                    #print("Usuario capturado: "+deteccionActivadaUsuario)
                    #print(NombresEtiquetas)
                    nombreUsuario= {deteccionActivadaUsuario: True}
                    db.child("Facial/UsuariosActivados").update(nombreUsuario)
                
                llamada=True
            
        #keys = list(NombresEtiquetas.keys())
        #keys.sort()
        #for i in keys:

            #targetnames.append(NombresEtiquetas[i])
        print("Estos son los los target names")
        print(targetnames)
        if deteccion_correcta == False:
            print("Error al capturar los rostros")
            errorCaptura = True
#                videoCapture.release()

        else:
            errorCaptura = False
#                videoCapture.release()
            print("Termino captura de rostros exitosamente")
    
            
            
    return errorCaptura,NombreCarpetaPrueba, targetnames, NombresEtiquetas,video_capture, indexCamara,numeroMuestrasRostros

numeroMuestrasRostros=61
import validarRostro as vR
indexCamara = 0
video_capture = 1.0

import recog as rg
from gpiozero import MotionSensor   
import pickle 
pir = MotionSensor(4) # Numero de pin de raspberry


llamada = False
p, inputQueue, outputQueue = 0 ,0 ,0
estadoActualPasillo = False
estadoActualPuerta = False

nombre = "Sin reconocer"
conexionExitosa,firebase,db, valores,_ = conectarFirebase()
extraccion = False
while True:
    
    numeroMuestrasRostros = 60
    configurado = db.child("Facial/Configurado").get()
    configurado = configurado.val()

    if configurado==True:

        numeroUsuarios = db.child("Facial/NumeroUsuarios").get()
        numeroUsuarios = numeroUsuarios.val()
        detener= db.child("Facial/Detener").get()
        if detener.val() == True:
            break
        if extraccion == False:
            try:
                print("Esta configurado")
                
                tomaDatos = open("archivo_modelo_LBP.pickle", "rb")
                datos = pickle.load(tomaDatos)
                clf = datos["modelo"]
                pca = datos["pca"]
                target_names =datos["target_names"]
                NombreCarpetaPrueba = datos["NombreCarpetaPrueba"]
    
                im_en = rg.encode(NombreCarpetaPrueba, numeroUsuarios)
                extraccion = True
                print("Extracciòn de modelo realizado correctamente")
                db.child("Facial/Error").update("NoErrorExtract")
            except:
                print("Fallo en la extracción del modelo")
                db.child("Facial/Error").update("Extract")
        
        

        #Validacion para entrenar mas usuarios
        if len(target_names)<numeroUsuarios:
            print("se va a añadir un nuevo usuario")
            NombresEtiquetas={}
            for i in range(len(target_names)):
                NombresEtiquetas[i+1] = target_names[i]
            #Obtencion de rostros fatantes
            try:
                errorObtencion, NombreCarpetaPrueba, nombreUsuarios, NombresEtiquetas, video_capture, indexCamara,numeroMuestrasRostros= obtenerRostros(indexCamara, list(target_names),len(target_names)+1,NombresEtiquetas)
            # Envio de mensaje de error <-------------------
                db.child("Facial/Error").update("NoErrorCaptura")
            except:
                
                print("Fallo en metodo de obtencion de rostros")
                # Envio de mensaje de error <-------------------
                db.child("Facial/Error").update("Captura")
            detener= db.child("Facial/Detener").get()
            if detener.val() == True:
                break
                
            # Entrenamiento de rostros
            vR.filtrar(NombreCarpetaPrueba,numeroUsuarios)
#            NombreCarpetaPrueba = "/home/pi/Desktop/P2/CaptureSVMReco/"
            detener= db.child("Facial/Detener").get()
            if detener.val() == True:
                break
            svm.SVM(NombreCarpetaPrueba,nombreUsuarios,numeroMuestrasRostros)
            detener= db.child("Facial/Detener").get()
            if detener.val() == True:
                break
            print("Extraccion de modelo con nuevos usuarios")
            tomaDatos = open("archivo_modelo_LBP.pickle", "rb")
            datos = pickle.load(tomaDatos)
            clf = datos["modelo"]
            pca = datos["pca"]
            target_names = datos["target_names"]
            NombreCarpetaPrueba = datos["NombreCarpetaPrueba"]

            im_en = rg.encode(NombreCarpetaPrueba,numeroUsuarios)
        
        print("Clasificación de rostros")
        # Obtener Discriminantes
        usuariosActivados = db.child("Facial/UsuariosActivados").get()
        usuariosActivados = usuariosActivados.val()
        usuariosActivados = list(usuariosActivados)
        discriminantes=[]
        target_names = list(target_names)
        # Comparacion de metodos
        for i in target_names:
            if i not in usuariosActivados:
                discriminantes.append(i)
        if pir.motion_detected == True and (nombre =="Desconocido" or nombre == "Sin reconocer"):
            detener= db.child("Facial/Detener").get()
            if detener.val() == True:
                break
    #        ledes.on()
    #        conexionCamara, p, inputQueue, outputQueue, video_capture,nombre = rL.reconocimiento(db,llamada,indexCamara,p, inputQueue, outputQueue,video_capture, ledes, clf, pca, target_names)

            video_capture,nombre = rg.recog(im_en, target_names, db, ledes,pca,clf,video_capture)
    #        vd.release()
    #        ledes.off()
            if nombre=="Desconocido":
                time.sleep(4)
            elif nombre == "Sin reconocer":
                time.sleep(4)
            elif nombre!="Desconocido":
                db.child("Habitaciones/Entrada").update({"Puerta":"Abrir"})
                time.sleep(15)
    #            t0 = 0.0
    #            if t0 == 0.0:
    #                t0 = time.time()
                
            llamada= True
            print("valor llamada: "+ str(llamada))
            print("Sale del reconocimiento")
        elif nombre != "Sin reconocer" and nombre != "Desconocido":
    
            print("estado actual PIR")
            print(pir.motion_detected)
                
            if pir.motion_detected == False:
                time.sleep(5)
                print("Puerta cerrada")
                db.child("Habitaciones/Entrada").update({"Puerta":"Cerrar"})
                nombre = "Sin reconocer"   
        time.sleep(1)
    
    
    else:
        NombreCarpetaPrueba = "/home/pi/Desktop/P2/Imagenes/Proyecto del " + time.strftime("%Y_%B_%d") + "_" + time.strftime('%H_%M_%S')
        #NombreCarpetaPrueba = "/home/pi/Desktop/P2/Prue/2018_October_11_16_49_11/"
        pathlib.Path(NombreCarpetaPrueba).mkdir(parents=True, exist_ok=True)
        try:
            errorObtencion = True
            targetnames = []
            NombresEtiquetas={}
            numeroUsuario=1
            errorObtencion, NombreCarpetaPrueba, nombreUsuarios, NombresEtiquetas, video_capture, indexCamara,numeroMuestrasRostros= obtenerRostros(indexCamara, targetnames, numeroUsuario, NombresEtiquetas)
            # Envio de mensaje de error <-------------------
            db.child("Facial/Error").update("NoErrorCaptura")
        except:
            
            print("Fallo en metodo de obtencion de rostros")
            # Envio de mensaje de error <-------------------
            db.child("Facial/Error").update("Captura")
        if errorObtencion ==False:
#            try:
            print("ruta carpeta imagenes: "+NombreCarpetaPrueba)
            vR.filtrar(NombreCarpetaPrueba,len(nombreUsuarios))
#            NombreCarpetaPrueba = "/home/pi/Desktop/P2/CaptureSVMReco/"
            try:
                svm.SVM(NombreCarpetaPrueba,nombreUsuarios,numeroMuestrasRostros)
                # Envio de mensaje de error <-------------------
                print("Entrenamiento realizado correctamente")
                db.child("Facial/Error").update("NoErrorTrain")
            except:
                # Envio de mensaje de error <-------------------
                print("Fallo entrenamiento")
                db.child("Facial/Error").update("Train")
            print("Termino modelo")
            print("Coninua con identifcacion de rostros")
            db.child("Facial").update({"Configurado":True})
            
        
    



