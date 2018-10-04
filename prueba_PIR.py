from gpiozero import MotionSensor
pir = MotionSensor(4) # Numero de

while True:
#    pir.when_motion = rL.reconocimiento(db)

#    print("Vallor de sensor"+str(pir)
    if pir.motion_detected:
        print("En ell if del pir")