#!/usr/bin/python3
from hx711 import HX711
import RPi.GPIO as GPIO
import time
from datetime import datetime
import board
import busio
import statistics
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# GPIO
DataPin = 5
ClockPin = 6
ButtonPin = 20  # Bouton "Rejouer"
NumReadings = 5
calibration_factor = 747.74

# Init écran OLED
def init_display():
    i2c = busio.I2C(board.SCL, board.SDA)
    disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
    disp.fill(0)
    disp.show()
    return disp

# Affichage multi-ligne centré
def display_lines(disp, lines):
    disp.fill(0)
    image = Image.new('1', (disp.width, disp.height))
    draw = ImageDraw.Draw(image)
    
     # Charger une police TrueType qui supporte les accents
    font = ImageFont.truetype('/home/pi/breizhcamp_2025/dejavu-sans-bold.ttf', 14)


    total_height = sum([draw.textbbox((0, 0), line, font=font)[3] for line in lines]) + (len(lines) - 1) * 2
    y_offset = (disp.height - total_height) // 2

    y = y_offset
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        width = bbox[2] - bbox[0]
        x = (disp.width - width) // 2
        draw.text((x, y), line, font=font, fill=255)
        y += (bbox[3] - bbox[1]) + 2

    disp.image(image)
    disp.show()

# Init HX711
def init_hx711():
    hx = HX711(dout_pin=DataPin, pd_sck_pin=ClockPin, gain=128, channel='A')
    if hx.reset():
        print("HX711 prêt")
    else:
        print("Erreur HX711")
    return hx

# Mesure objet de référence
def measure_reference_weight(hx):
    print("Mesure de l'objet de référence...")
    tare_data = hx.get_raw_data(NumReadings)
    tare_average_raw = sum(tare_data) / len(tare_data)
    tare_weight = tare_average_raw / calibration_factor
    print(f"Poids de référence : {tare_weight:.2f} g")
    return tare_weight

# Mesure poids actuel
def get_weight(hx):
    data = hx.get_raw_data(NumReadings)

    if data and len(data) == NumReadings:
        print(f"Lectures HX711: {data}")

        try:
            stddev = statistics.stdev(data)
        except statistics.StatisticsError:
            stddev = 0  # Si on n'a qu'une seule valeur

        print(f"écart type: {stddev}")
        threshold = 100000  # Ajustable selon ton capteur

        if stddev < threshold:
            average = statistics.mean(data)
            return average / calibration_factor
        else:
            print(f"Écart-type trop élevé : {stddev:.2f}, rejet de la mesure.")
            return None
    else:
        print("Erreur : Pas assez de données valides.")
        return None
    
# Init bouton GPIO
def init_button():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Attente appui bouton
def wait_for_button_press():
    print("En attente du bouton pour rejouer...")
    while GPIO.input(ButtonPin) == 0:
        time.sleep(0.1)
    while GPIO.input(ButtonPin) == 1:  # anti-rebond
        time.sleep(0.1)

# Lancer une partie
def run_game(disp, hx):
    display_lines(disp, ["Indy Challenge!", "Place l'objet..."])
    print("Indy Challenge! Place l'objet...")
    time.sleep(2)
    tare_weight = measure_reference_weight(hx)

    while True:
        weight = get_weight(hx)
        if weight is not None:
            diff = weight - tare_weight
            abs_diff = abs(diff)

            print(f"Écart: {diff:+.2f} g")

            if abs_diff <= 20:
                display_lines(disp, [
                    f"Écart: {diff:+.2f} g"
                ])
            elif abs_diff <= 50:
                display_lines(disp, [
                    f"Écart: {diff:+.2f} g",
                    "Pas mal...",
                    "attention !"
                ])
                break
            elif abs_diff <= 75:
                display_lines(disp, [
                    f"Écart: {diff:+.2f} g",
                    "C'est perdu !"
                ])
                break
            else:
                display_lines(disp, [
                    f"Écart: {diff:+.2f} g",
                    "Fuis ! Le temple ",
                    "s'écroule !"
                ])
                break
        else:
            time.sleep(0.2)

# Programme principal
def main():
    disp = init_display()
    hx = init_hx711()
    init_button()

    while True:
        run_game(disp, hx)
        wait_for_button_press()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Arrêté par l'utilisateur")
    finally:
        GPIO.cleanup()
