# -*- coding: utf-8 -*-
"""
Created on Sat Nov 10 19:32:34 2018

@author: shuuz
"""

"""
Script principal donde se ejecuta la extraccion de rostros y 
posteriormetne el entrenamiento

"""
print(__doc__)
import pyrebase
import time

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

from gpiozero import MotionSensor, LED
ledes = LED(17)
pir = MotionSensor(4) # Numero de pin de raspberry

conexionExitosa, firebase, db, valores, entrenamiento = conectarFirebase()
if conexionExitosa:
    while True:
        deteccionPasillo = db.child("Habitaciones/Pasillo2/Presencia").get()
        deteccionPasillo = deteccionPasillo.val()
        puertaAbierta = db.child("Habitaciones/Entrada/Puerta").get()
        puertaAbierta = puertaAbierta.val()
        if puertaAbierta == "Encender":
            if pir.motion_detected == False and deteccionPasillo== False :
                db.child("Habitaciones/Entrada").update({"Puerta":"Apagar"})
                time.sleep(10)        
            
            
        
        

 

        
        