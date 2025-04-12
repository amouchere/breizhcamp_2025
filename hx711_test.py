#!/usr/bin/python3
from hx711 import HX711  # Importation de la classe HX711
import RPi.GPIO as GPIO  # Importation de GPIO
import time
from datetime import datetime

try:
    DataPin = 5
    ClockPin = 6
    NumReadings = 2  # Nombre de lectures à effectuer pour calculer la moyenne
    
    # Ajuste le facteur de calibration (calculé précédemment)
    calibration_factor = 747.74
    
    print("Lecture du HX711")
    
    hx = HX711(dout_pin=DataPin, pd_sck_pin=ClockPin, gain=128, channel='A')
    
    print("Réinitialisation")
    result = hx.reset()
    if result:
        print('Prêt à l\'emploi')
    else:
        print('Pas prêt')

    # Tare
    print("Effectuer la tare ...")
    tare_data = hx.get_raw_data(NumReadings)  # Lire les données à vide
    tare_average = sum(tare_data) / len(tare_data)  # Calculer la moyenne des données à vide
    print(f"Valeur à vide : {tare_average}")
    
    # Calculer le poids
    weight = tare_average / calibration_factor
    print(f"Poids estimé: {weight:.2f} g")
    time.sleep(3)

    while True:
       while True:
        # Lire les données plusieurs fois et renvoyer la valeur moyenne
        data = hx.get_raw_data(NumReadings)
        
        if data != False:  # Vérifie si tu as reçu des données valides
            print(f'Données brutes : {data}')
            
            # Filtrage des données aberrantes
            min_value = tare_average - 600000  # Valeur minimale raisonnable
            max_value = tare_average + 600000  # Valeur maximale raisonnable
            valid_data = [x for x in data if min_value < x < max_value]
            print(f'Données brutes valides : {valid_data}')
            if valid_data:
                # Calculer la moyenne des valeurs valides
                average_raw_value = sum(valid_data) / len(valid_data)
                print(f'Moyenne des données valides : {average_raw_value}')
                
                # Soustraire la valeur à vide pour la tare
                net_weight_raw_value = average_raw_value - tare_average
                print(f'Valeur nette après tare : {net_weight_raw_value}')

                # Calculer le poids
                weight = net_weight_raw_value / calibration_factor
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"---> [{current_time}] Poids estimé: {weight:.2f} g")
            else:
                print("Toutes les données sont invalides")
        else:
            print("Erreur de lecture des données")

        time.sleep(0.1)
except (KeyboardInterrupt, SystemExit):
    print('Au revoir :)')

finally:
    GPIO.cleanup()
