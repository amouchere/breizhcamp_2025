import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    print("Appuie sur le bouton...")
    while True:
        if GPIO.input(20) == GPIO.LOW:
            print("Bouton pressé !")
            break
        time.sleep(0.1)
finally:
    GPIO.cleanup()
