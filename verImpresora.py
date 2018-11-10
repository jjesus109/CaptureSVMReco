# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 19:27:45 2018

@author: shuuz
"""
import cv2
import numpy as np
def ajusteGamma(imagen,gamma=1.0):
    invGamma =  1.0 / gamma
    table = np.array([((i/255.0)**invGamma)*255
        for i in np.arange(0,256)]).astype("uint8")
    return cv2.LUT(imagen,table)

valorGamma=1.2
valorGammaAlto=False
EncontroUsuario=False

video_capture = cv2.VideoCapture(2)
if video_capture.isOpened():
#    print("Inicializacion de camara exitosa")
#    print("Comienza captura de video")
    while True:
            
        _, frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        CorreccionGamma = ajusteGamma(gray,1.8)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        Clahe_Gamma = clahe.apply(CorreccionGamma)
#        rows,cols = frame.shape
#        M = cv2.getRotationMatrix2D((cols/2,rows/2),180,1)
#        dst = cv2.warpAffine(frame,M,(cols,rows))
#        cv2.imshow('Video impresora',frame)
        cv2.imshow('Video Clahe',Clahe_Gamma)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
video_capture.release()
cv2.destroyAllWindows()

