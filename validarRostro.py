import cv2
import os
import time
import numpy as np
#print("total time: ", time()-t0)


face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
def detect(gray, frame):
    crop_img=np.array([0,0,0])
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
#        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        medidasX1 = int(x*1.15)
        medidasX2 = int(x+(w*0.82))
        medidasY2 = int(y*1.2)
        medidasY1 = int(y+(h*0.95))
        
#        cv2.rectangle(frame, (medidasX1, medidasY1), (medidasX2, medidasY2), (255, 0, 0), 2)
        crop_img = gray[medidasY2:medidasY1, medidasX1:medidasX2]
        
        tamanioCrop = np.shape(crop_img)
        if tamanioCrop == ():
            crop_img = np.array([[[0],[0],[0]],[[0],[0],[0]],[[0],[0],[0]]])
    return gray, crop_img

datosAug =[]
labelsAug =[]
t0 = time()
carpeta = "D:/Documentos HDD/10mo/TT1/Pruebas mulicategorico/Proyecto del 2018_September_01_19_08_59/"
t0 = time()
folders = os.listdir(carpeta)
for im in folders:
    label =int(im[0])
    Rimagen = carpeta+im
    imagen=cv2.imread(Rimagen)
    gris = cv2.cvtColor(imagen,cv2.COLOR_BGR2GRAY)
#    gris = cv2.cvtColor(image,cv2.)
    gris,crop_img = detect(gris)
    # no reconcoe algun rostro
    if crop_img.all()==0:
        #borrar la imagen
    else:
        #dejarla