#!/usr/bin/python3
from hx711 import HX711
import RPi.GPIO as GPIO
import time

# Configuration des broches GPIO du HX711
DataPin = 5
ClockPin = 6
NumReadings = 15

def init_hx711():
    hx = HX711(dout_pin=DataPin, pd_sck_pin=ClockPin, gain=128, channel='A')
    if hx.reset():
        print("HX711 prêt")
    else:
        print("Erreur d'initialisation HX711")
    return hx

def get_average_raw(hx, readings=NumReadings):
    data = hx.get_raw_data(readings)
    if data and len(data) == readings:
        return sum(data) / len(data)
    else:
        raise Exception("Pas assez de données valides")

def main():
    print("Initialisation...")
    hx = init_hx711()
    time.sleep(1)

    input("Retire toute charge du capteur puis appuie sur Entrée pour tarer...")
    tare = get_average_raw(hx)
    print(f"Valeur brute à vide (tare) : {tare:.2f}")

    input("Place un poids connu sur le capteur, puis appuie sur Entrée...")
    loaded = get_average_raw(hx)
    print(f"Valeur brute avec poids : {loaded:.2f}")

    known_weight = float(input("Entre le poids connu en grammes : "))
    delta = loaded - tare
    if known_weight == 0:
        print("Erreur : le poids connu ne peut pas être zéro.")
        return

    calibration_factor = delta / known_weight
    print(f"\n✅ Facteur de calibration calculé : {calibration_factor:.2f}")
    print("Tu peux maintenant mettre à jour ton script principal avec ce facteur.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrompu par l'utilisateur.")
    finally:
        GPIO.cleanup()
