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
import logging

# Config log
logging.basicConfig(
    filename='/home/pi/indy.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# GPIO
DataPin = 5
ClockPin = 6
ButtonPin = 20  # Bouton "Rejouer"
NumReadings = 15
calibration_factor = 747.74

# Init écran OLED
def init_display():
    i2c = busio.I2C(board.SCL, board.SDA)
    disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
    disp.fill(0)
    disp.rotation = 2
    disp.show()
    return disp

# Affichage multi-ligne centré
def display_lines(disp, lines, size):
    disp.fill(0)
    image = Image.new('1', (disp.width, disp.height))
    draw = ImageDraw.Draw(image)
    
     # Charger une police TrueType qui supporte les accents
    font = ImageFont.truetype('/home/pi/breizhcamp_2025/dejavu-sans-bold.ttf', size)


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
        logging.info("HX711 prêt")
    else:
        logging.error("Erreur HX711")
    return hx

# Mesure objet de référence
def measure_reference_weight(hx):
    logging.info("Mesure de l'objet de référence...")
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
            mean = statistics.mean(data)      # Calcul de la moyenne de l'échantillon
            stddev = statistics.pstdev(data)  # Calcul de l'écart type de l'échantillon
        except statistics.StatisticsError:
            logging.info("Erreur statistique.")
            return None

        print(f"Moyenne: {mean}")
        print(f"Écart-type (population): {stddev}")

        threshold = 2 * stddev  # on garde les valeurs dans ±2σ
        filtered = [x for x in data if abs(x - mean) <= threshold]

        print(f"Valeurs filtrées ({len(filtered)} sur {len(data)}): {filtered}")

        if len(filtered) < len(data) // 2:
            logging.info("Trop peu de valeurs fiables, mesure rejetée.")
            return None

        clean_mean = statistics.mean(filtered)
        weight = clean_mean / calibration_factor
        print(f"Poids estimé: {weight:.2f} g")
        return weight
    else:
        logging.info("Erreur : Pas assez de données valides.")
        return None
    
# Init bouton GPIO
def init_buttons():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Attente appui bouton
def wait_for_button_press():
    logging.info("En attente du bouton pour rejouer...")
    while GPIO.input(ButtonPin) == 0:
        time.sleep(0.1)
    while GPIO.input(ButtonPin) == 1:  # anti-rebond
        time.sleep(0.1)

# Lancer une partie
def run_game(disp, hx):
    display_lines(disp, ["Pesée de", "l'idole..."], 14)
    logging.info("Indy Challenge! Pesée de l'idole...")
    time.sleep(2)
    tare_weight = measure_reference_weight(hx)

    while True:
        weight = get_weight(hx)
        if weight is not None:
            diff = weight - tare_weight
            abs_diff = abs(diff)

            print(f"Écart: {diff:+.2f} g")

            if abs_diff <= 30:
                display_lines(disp, [
                    f"Écart: {diff:+.2f} g",
                    "tout va bien"
                ], 14)
            elif abs_diff <= 50:
                display_lines(disp, [
                    f"Écart: {diff:+.2f} g",
                    "C'est juste !"
                ], 14)
            else:
                display_lines(disp, [
                    "Fuis ! !",
                    "Le temple",
                    "s'écroule !"]
                , 14)
                time.sleep(1)
                final_weight = get_weight(hx)
                diff = final_weight - tare_weight
                display_lines(disp, ["Ta place", "est dans", "un musée !"], 16)
                time.sleep(2)
                display_lines(disp, [
                    "Écart:", f"{diff:+.2f} g"
                ], 18)
                break
        else:
            time.sleep(0.2)

# Programme principal
def main():
    disp = init_display()
    hx = init_hx711()
    init_buttons()

    while True:
        display_lines(disp, ["Indy", "Challenge !"], 18)
        time.sleep(2)
        wait_for_button_press()
        run_game(disp, hx)
        wait_for_button_press()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Arrêt !")
    finally:
        GPIO.cleanup()
