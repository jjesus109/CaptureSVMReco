#!/bin/bash
source /home/pi/.virtualenvs/cv/bin/activate
cd /home/pi/Desktop/P2/CaptureSVMReco
git pull origin master --allow-unrelated-histories
#modificacion en mi compu
python ScriptPrincipal.py

#python reconocimientoSVM_Live_10tomas.py



