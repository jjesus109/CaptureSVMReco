"""
Metodos para redimensisonar los rostros capturados y enfocarlos en el area de
interes que es el rostros eliminando el posible ruido de los mismos
"""

import cv2
import os
import numpy as np


face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
def detect(gray):
    crop_img=np.array([0,0,0])
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    for (x, y, w, h) in faces:
#        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        medidasX1 = int(x*1.4)
        medidasX2 = int(x+(w*0.9))
        medidasY2 = int(y*1.25)
        medidasY1 = int(y+(h*0.98))
#        
#        cv2.rectangle(frame, (medidasX1, medidasY1), (medidasX2, medidasY2), (255, 0, 0), 2)
        crop_img = gray[medidasY2:medidasY1, medidasX1:medidasX2]
        
        tamanioCrop = np.shape(crop_img)
        if tamanioCrop == ():
            crop_img = np.array([[[0],[0],[0]],[[0],[0],[0]],[[0],[0],[0]]])
    return gray, crop_img
#
def filtrar(carpeta):
    resizeW = 96
    resizeH = 130

    folders = os.listdir(carpeta)
    n = 0
    for im in folders:
#        label =int(im[0])
        Rimagen = carpeta+"/"+im
#        print(Rimagen)
        imagen=cv2.imread(Rimagen)
        gris = cv2.cvtColor(imagen,cv2.COLOR_BGR2GRAY)
    #    gris = cv2.cvtColor(image,cv2.)
        gris,crop_img = detect(gris)
        # no reconcoe algun rostro
        if n<10:
            os.remove(Rimagen)
        n += 1
        if crop_img.all()==0:
            #borrar la imagen
            os.remove(Rimagen)
        else:
             tamanioCara = np.shape(crop_img)
             if tamanioCara[0] >int(resizeW*0.7):
    #        crop_img = cv2.resize(crop_img,(resizeW,resizeH))
                 crop_img = cv2.resize(crop_img,(resizeW,resizeH))
                 cv2.imwrite(Rimagen, crop_img)
    #        time.sleep(0.1)
#    print()
            #obtenerPuroRostro
    
