#!/usr/bin/python3
from hx711 import HX711
import RPi.GPIO as GPIO
import time
from datetime import datetime
import board
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# === CONFIGURATION ===
DataPin = 5
ClockPin = 6
NumReadings = 2
calibration_factor = 747.74  # Ajuster en fonction du capteur

# === INITIALISATION OLED ===
def init_display():
    i2c = busio.I2C(board.SCL, board.SDA)
    disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
    disp.fill(0)
    disp.show()
    return disp

# === AFFICHAGE MULTILIGNE ===
def display_multiline_text(disp, lines):
    image = Image.new('1', (disp.width, disp.height))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    y = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_height = bbox[3] - bbox[1]
        draw.text((0, y), line, font=font, fill=255)
        y += line_height + 2

    disp.image(image)
    disp.show()

# === INITIALISATION CAPTEUR HX711 ===
def init_hx711():
    hx = HX711(dout_pin=DataPin, pd_sck_pin=ClockPin, gain=128, channel='A')
    result = hx.reset()
    if not result:
        raise RuntimeError("Erreur d'initialisation HX711")
    return hx

# === MESURE DE RÉFÉRENCE ===
def measure_reference_weight(hx):
    print("Mesure de l'objet de référence...")
    tare_data = hx.get_raw_data(NumReadings)
    tare_avg_raw = sum(tare_data) / len(tare_data)
    tare_weight = tare_avg_raw / calibration_factor
    print(f"Poids de référence : {tare_weight:.2f} g")
    return tare_weight

# === MESURE DU POIDS ACTUEL ===
def get_weight(hx, reference_raw_value):
    data = hx.get_raw_data(NumReadings)
    if data:
        min_val = reference_raw_value - 600000
        max_val = reference_raw_value + 600000
        valid_data = [x for x in data if min_val < x < max_val]

        if valid_data:
            avg_raw = sum(valid_data) / len(valid_data)
            return avg_raw / calibration_factor
    return None

# === FONCTION PRINCIPALE DU JEU ===
def main():
    disp = init_display()
    hx = init_hx711()

    display_multiline_text(disp, ["Indy Challenge !", "C'est à vous !"])
    time.sleep(2)

    reference_weight = measure_reference_weight(hx)
    reference_raw_value = reference_weight * calibration_factor

    display_multiline_text(disp, ["Placez votre sac", "de sable..."])
    time.sleep(1)

    while True:
        weight = get_weight(hx, reference_raw_value)

        if weight is not None:
            difference = weight - reference_weight
            difference_abs = abs(weight - reference_weight)
            print(f"Écart mesuré : {difference:.2f} g")

            if difference_abs <= 20:
                comment = "🟢 Parfait !"
                display_multiline_text(disp, [
                    f"Écart: {difference:.2f} g",
                    comment
                ])
                print(f"{comment}")
                time.sleep(2)  # On continue à jouer
            else:
                if difference_abs <= 50:
                    comment = "🟡 Pas mal... mais risqué !"
                elif difference_abs <= 75:
                    comment = "🔴 Trop risqué, piège activé !"
                else:
                    comment = "💀 Temple effondré !"

                display_multiline_text(disp, [
                    f"Écart: {difference:.2f} g",
                    comment
                ])
                print(f"{comment}")
                break  # On sort du jeu si l’écart est trop grand
        else:
            display_multiline_text(disp, ["Erreur capteur...", "Réessayez..."])
            time.sleep(1)


# === LANCEMENT ===
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Jeu interrompu par l'utilisateur.")
    finally:
        GPIO.cleanup()
