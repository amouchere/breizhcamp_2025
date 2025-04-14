#!/usr/bin/python3
from hx711 import HX711
import RPi.GPIO as GPIO
import time
from datetime import datetime

# Pour l'écran OLED
import board
import busio
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont

try:
    # --- Config capteur HX711 ---
    DataPin = 5
    ClockPin = 6
    NumReadings = 2
    calibration_factor = 747.74
    
    print("Lecture du HX711")
    hx = HX711(dout_pin=DataPin, pd_sck_pin=ClockPin, gain=128, channel='A')
    
    print("Réinitialisation")
    result = hx.reset()
    if not result:
        print("Erreur de réinitialisation HX711")
        exit()

    print("Effectuer la tare ...")
    tare_data = hx.get_raw_data(NumReadings)
    tare_average = sum(tare_data) / len(tare_data)
    print(f"Valeur à vide : {tare_average}")

    # --- Config écran OLED ---
    WIDTH = 128
    HEIGHT = 64
    i2c = busio.I2C(board.SCL, board.SDA)
    oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
    oled.fill(0)
    oled.show()

    font = ImageFont.load_default()

    print("Lancement de la boucle de mesure...")
    time.sleep(1)

    while True:
        data = hx.get_raw_data(NumReadings)

        if data:
            min_value = tare_average - 600000
            max_value = tare_average + 600000
            valid_data = [x for x in data if min_value < x < max_value]

            if valid_data:
                average_raw_value = sum(valid_data) / len(valid_data)
                net_weight_raw_value = average_raw_value - tare_average
                weight = net_weight_raw_value / calibration_factor

                # Affichage console
                current_time = datetime.now().strftime('%H:%M:%S')
                print(f"[{current_time}] Poids: {weight:.2f} g")

                # Affichage OLED
                image = Image.new("1", (WIDTH, HEIGHT))
                draw = ImageDraw.Draw(image)

                draw.text((5, 20), "Poids:", font=font, fill=255)
                draw.text((5, 35), f"{weight:.2f} g", font=font, fill=255)

                oled.image(image)
                oled.show()
            else:
                print("Toutes les données sont invalides")
        else:
            print("Erreur de lecture")

        time.sleep(0.2)

except (KeyboardInterrupt, SystemExit):
    print('Au revoir :)')

finally:
    GPIO.cleanup()
