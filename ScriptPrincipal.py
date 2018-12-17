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
import os
from gpiozero import LED
ledes = LED(17)
from gtts import gTTS
# Activacion variable para saber cuando esta activado el sensor

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
    



def obtenerRostros(indexCamara, targetnames, numeroUsuarios,NombresEtiquetas, NombreCarpetaPrueba ):
    nombresAñadir = []
    numeroMuestrasRostros = 70
    detener = False
    deteccion_correcta=False
    video_capture = 1.0
    # Variable para saber si hubo pedos cuando capturo los rostros
    errorCaptura = True
    conexionExitosa,firebase,db, valores,_ = conectarFirebase()
    if conexionExitosa ==False:
        print("Favor de conectar a internet")
    else:
                 

        
#        sale = False
        
        while True:
            print("Esperando a iniciar capturas")    
            mensajeError = db.child("Facial/Error").get()
            mensajeError = mensajeError.val()
            if mensajeError == "inicap":
                break
        p, inputQueue, outputQueue = 0 ,0 ,0            
        numeroUsuariosAEntrenar = db.child("Facial/NumeroUsuarios").get()
        numeroUsuariosAEntrenar = int(numeroUsuariosAEntrenar.val())
        llamada=False
        print("Ya comienza captura")
        print("Cuantas veces hara esto:")
        print(str(numeroUsuariosAEntrenar))
        while numeroUsuarios<numeroUsuariosAEntrenar:
            print(str(numeroUsuarios))
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
                    nombresAñadir.append(deteccionActivadaUsuario)
#                    nombreUsuario= {deteccionActivadaUsuario: True}
#                    db.child("Facial/UsuariosActivados").update(nombreUsuario)
                
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
    
            
            
    return errorCaptura,NombreCarpetaPrueba, targetnames, NombresEtiquetas,video_capture, indexCamara,numeroMuestrasRostros, nombresAñadir

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
"""Para reproducir  audio por bluetooth"""
from subprocess import call

def funcionPrincipal():
    video_capture = 1.0    
    movimientoPir = True
    primeraVez = True
    abriendo="nada"
    nombre = "Sin reconocer"
    extraccion = False
    indexCamara = 0
    db.child("Facial").update({"Error":"IniciaProg"})
    print("Inicia el proceso")
    while True:
        
        numeroMuestrasRostros = 60
        configurado = db.child("Facial/Configurado").get()
        configurado = configurado.val()
        print("valor configurado"+ str(configurado))
        if configurado==True:
    
            numeroUsuarios = db.child("Facial/NumeroUsuarios").get()
            numeroUsuarios = numeroUsuarios.val()
            detener= db.child("Facial/Detener").get()
            if detener.val() == True:
                break
            if extraccion == False:
#                try:
                    print("Esta configurado")
                    
                    tomaDatos = open("/home/pi/Desktop/P2/CaptureSVMReco/archivo_modelo_LBP.pickle", "rb")
                    datos = pickle.load(tomaDatos)
                    clf = datos["modelo"]
                    pca = datos["pca"]
                    target_names =datos["target_names"]
                    NombreCarpetaPrueba = datos["NombreCarpetaPrueba"]
                    tomaDatos.close()
                    im_en,errorExtraccionImagenes = rg.encode(NombreCarpetaPrueba, numeroUsuarios)
                    
                    if errorExtraccionImagenes:
                        print("Fallo Entrenamiento de modelo")
                        db.child("Facial").update({"Error":"Extract"})
#                        db.child("Facial").update({"Error":"Train"})
                        break
                    
                    extraccion = True
                    print("Extracción de modelo realizado correctamente")
                    
                    db.child("Facial").update({"Error":"NoErrorExtract"})
#                except:
#                    print("Fallo en la extracción del modelo")
                    
            """----------------!!!!!!!!!!!!!!!!!!!!!!!!!!!-----------------"""
            ### checar la reconexion a firebase
#            try:
#                db.child("Facial/UsuariosActivados").update(nombreUsuario)
#            except:
#                conexionExitosa, firebase, db, valores,entrenamiento = conectarFirebase()
                                            
    
            #Validacion para entrenar mas usuarios
            if len(target_names)<numeroUsuarios-1:
                print("se va a añadir un nuevo usuario")
                NombresEtiquetas={}
                for i in range(len(target_names)):
                    NombresEtiquetas[i+1] = target_names[i]
                #Obtencion de rostros fatantes
                try:
                    errorObtencion, NombreCarpetaPrueba, nombreUsuarios, NombresEtiquetas, video_capture, indexCamara,numeroMuestrasRostros, nombresAñadir= obtenerRostros(indexCamara, list(target_names),len(target_names)+1,NombresEtiquetas,NombreCarpetaPrueba)
                # Envio de mensaje de error <-------------------
                    if errorObtencion == True:
                        print("Se  reinicia el proceso")
                        break
                    
                    for i in nombresAñadir:
                        nombreUsuario= {i: True}
                        db.child("Facial/UsuariosActivados").update(nombreUsuario)    
                    
                    db.child("Facial").update({"Error":"NoErrorCaptura"})    
                    
                except:
                    
                    print("Fallo en metodo de obtencion de rostros")
                    # Envio de mensaje de error <-------------------
                    db.child("Facial").update({"Error":"Captura"})    
                    
                detener= db.child("Facial/Detener").get()
                if detener.val() == True:
                    break
                    
                # Entrenamiento de rostros
                vR.filtrar(NombreCarpetaPrueba,numeroUsuarios)
    #            NombreCarpetaPrueba = "/home/pi/Desktop/P2/CaptureSVMReco/"
                
    
                detener= db.child("Facial/Detener").get()
                if detener.val() == True:
                    break
                
                try:
                    svm.SVM(NombreCarpetaPrueba,nombreUsuarios,numeroMuestrasRostros)
                    # Envio de mensaje de error <-------------------
                    print("Entrenamiento realizado correctamente")
                    
                    db.child("Facial").update({"Error":"NoErrorTrain"})    
                except:
                    # Actualiza 
                    db.child("Facial").update({"ProcesoFinalizado":True})            
                    # Envio de mensaje de error <-------------------
                    print("Fallo entrenamiento")
                    db.child("Facial").update({"Error":"Train"})    
                print("Termino modelo")
                print("Coninua con identifcacion de rostros")
                db.child("Facial").update({"Configurado":True})
                db.child("Facial").update({"ProcesoFinalizado":True})  
                
                
                detener= db.child("Facial/Detener").get()
                if detener.val() == True:
                    break
                print("Extraccion de modelo con nuevos usuarios")
                tomaDatos = open("/home/pi/Desktop/P2/CaptureSVMReco/archivo_modelo_LBP.pickle", "rb")
                datos = pickle.load(tomaDatos)
                clf = datos["modelo"]
                pca = datos["pca"]
                target_names = datos["target_names"]
                NombreCarpetaPrueba = datos["NombreCarpetaPrueba"]
                tomaDatos.close()
    
                im_en,errorExtraccionImagenes = rg.encode(NombreCarpetaPrueba, numeroUsuarios)
                if errorExtraccionImagenes:
                    print("Fallo Entrenamiento de modelo")
                    db.child("Facial").update({"Error":"Extract"})
                    break
                
            print("Clasificación de rostros")
            
            # Obtener Discriminantes
            usuariosActivados = db.child("Facial/UsuariosActivados").get()
            usuariosActivados = usuariosActivados.val()
            usuariosActivados = list(usuariosActivados)
            discriminantes=[]
            target_names = list(target_names)
            # Comparacion de metodos
            print(usuariosActivados)
            for i in target_names:
                if i not in usuariosActivados:
                    discriminantes.append(i)
            if pir.motion_detected == True and (nombre =="Desconocido" or nombre == "Sin reconocer"):
                detener= db.child("Facial/Detener").get()
                if detener.val() == True:
                    break
        #        ledes.on()
        #        conexionCamara, p, inputQueue, outputQueue, video_capture,nombre = rL.reconocimiento(db,llamada,indexCamara,p, inputQueue, outputQueue,video_capture, ledes, clf, pca, target_names)
    
                video_capture,nombre = rg.recog(im_en, target_names, db, ledes,pca,clf,video_capture,discriminantes)
        #        vd.release()
        #        ledes.off()
                if nombre=="Desconocido":
                    #tts = gTTS(text="Detectado como Desconocido", lang='es')
                    #tts.save("/home/pi/Desktop/mal.mp3")
                    os.system("mpg321 mal.mp3")
                    #play = ["mplayer"]

                    time.sleep(4)
                elif nombre == "Sin reconocer":
                    time.sleep(4)
                elif nombre!="Desconocido":
                    tts = gTTS(text='Bienvenido' + nombre, lang='es')
                    tts.save("bien2.mp3")
                    cmd = ["mpg321", "-o", "alsa"]
                    audio = "bien2.mp3"
                    call(cmd+ [audio])

                    
                    db.child("Habitaciones/Entrada").update({"Puerta":"Abrir"})
                    while True:

                        print("Esta en el true")
                        abriendo = db.child("Habitaciones/Entrada/Puerta").get()            
                        abriendo = abriendo.val()
                        if abriendo == "Abierto":
                            break
                    print("Esta esperando los 10 segundos")
                    time.sleep(10)
                    
        #            t0 = 0.0
        #            if t0 == 0.0:
        #                t0 = time.time()
                    
                llamada= True
                print("valor llamada: "+ str(llamada))
                print("Sale del reconocimiento")
            
            elif nombre != "Sin reconocer" and nombre != "Desconocido":
                
                if primeraVez ==True:
                    t0= time.time()
                print("estado actual PIR")
                print(movimientoPir)
                if time.time()-t0 >= 5:
                    primeraVez=True
                    if pir.motion_detected == True:
                        movimientoPir = True
                        
                    else:
                        movimientoPir = False
                else:      
                    primeraVez=False
                if movimientoPir == False:
                    print("Puerta cerrada")
                    db.child("Habitaciones/Entrada").update({"Puerta":"Cerrar"})
                    
                    while True:
                        print("Esta en el true")
                        abriendo = db.child("Habitaciones/Entrada/Puerta").get()            
                        abriendo = abriendo.val()
                        if abriendo == "Cerrado":
                            break
                    nombre = "Sin reconocer"   
            

            time.sleep(1)

        
        else:
            os.remove("/home/pi/Desktop/P2/CaptureSVMReco/archivo_modelo_LBP.pickle")
            NombreCarpetaPrueba = "/home/pi/Desktop/P2/Imagenes/Proyecto del " + time.strftime("%Y_%B_%d") + "_" + time.strftime('%H_%M_%S')
            #NombreCarpetaPrueba = "/home/pi/Desktop/P2/Prue/2018_October_11_16_49_11/"
            pathlib.Path(NombreCarpetaPrueba).mkdir(parents=True, exist_ok=True)
            
            try:
                errorObtencion = True
                targetnames = []
                NombresEtiquetas={}
                numeroUsuario=1
                errorObtencion, NombreCarpetaPrueba, nombreUsuarios, NombresEtiquetas, video_capture, indexCamara,numeroMuestrasRostros, nombresAñadir= obtenerRostros(indexCamara, targetnames, numeroUsuario, NombresEtiquetas,NombreCarpetaPrueba)
                
                if errorObtencion == True:
                    print("Se  reinicia el proceso")
                    break
                for i in nombresAñadir:
                    nombreUsuario= {i: True}
                    db.child("Facial/UsuariosActivados").update(nombreUsuario)    
                # Envio de mensaje de error <-------------------
                db.child("Facial").update({"Error":"NoErrorCaptura"})    

                
            except:
                
                print("Fallo en metodo de obtencion de rostros")
                # Envio de mensaje de error <-------------------
                db.child("Facial").update({"Error":"Captura"})    
                
            if errorObtencion ==False:
    #            try:
                db.child("Facial").update({"ProcesoFinalizado":False})            
                print("ruta carpeta imagenes: "+NombreCarpetaPrueba)
                vR.filtrar(NombreCarpetaPrueba,len(nombreUsuarios))
    #            NombreCarpetaPrueba = "/home/pi/Desktop/P2/CaptureSVMReco/"
                try:
                    svm.SVM(NombreCarpetaPrueba,nombreUsuarios,numeroMuestrasRostros)
                    # Envio de mensaje de error <-------------------
                    print("Entrenamiento realizado correctamente")
                    
                    db.child("Facial").update({"Error":"NoErrorTrain"})    
                except:
                    # Actualiza 
                    db.child("Facial").update({"ProcesoFinalizado":True})            
                    # Envio de mensaje de error <-------------------
                    print("Fallo entrenamiento")
                    db.child("Facial").update({"Error":"Train"})    
                print("Termino modelo")
                print("Coninua con identifcacion de rostros")
                db.child("Facial").update({"Configurado":True})
                db.child("Facial").update({"ProcesoFinalizado":True})  
                
            
        

if __name__ == "__main__":
    
    while True:
        funcionPrincipal()
