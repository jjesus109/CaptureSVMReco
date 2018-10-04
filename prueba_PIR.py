from gpiozero import MotionSensor
pir = MotionSensor(4) # Numero de

while True:
#    pir.when_motion = rL.reconocimiento(db)
    if pir.motion_detected:
        print("En ell if del pir")
