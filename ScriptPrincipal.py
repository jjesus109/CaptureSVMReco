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
            
            deteccion_correcta, videoCapture= cr.capturaCamara(NombreCarpetaPrueba,len(nombreUsuarios))
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
            
    return errorCaptura,NombreCarpetaPrueba, nombreUsuarios


while True:
#def main():
    conexionExitosa,firebase,db, valores,entrenamiento = conectarFirebase()
    if entrenamiento=="False":
        try:
            errorObtencion = True
            errorObtencion, NombreCarpetaPrueba, nombreUsuarios = obtenerRostros()
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

print("Inicia reconocimiento de rostros")
conexionExitosa,firebase,db, valores, entrenamiento = conectarFirebase()
import recog_queues as rL
from gpiozero import MotionSensor
pir = MotionSensor(4) # Numero de pin de raspberry
#import pickle
#data = open(NombreCarpetaPrueba+"/archivo_modelo_LBP.pickle",'wb')
while True:
#    pir.when_motion = rL.reconocimiento(db)
#    print("En el While de recog")
#    sensor = db.child("Facial/Activacion").get()
#    """Leer datos del senosor de presencia"""
    """cuando detecte presencia"""
#    print("Vallor de sensor"+str(sensor.val()))
    if pir.motion_detected:
#    if sensor.val()=="True":
        rL.reconocimiento(db)
    time.sleep(0.5)
 

    
##    if cv2.waitKey(1) & 0xFF == ord('q'):
#    break
        
        
        