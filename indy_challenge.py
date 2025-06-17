#!/usr/bin/python3
from hx711 import HX711
import RPi.GPIO as GPIO
import time
import threading
from datetime import datetime
import statistics
import logging
from RPLCD.i2c import CharLCD

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
NumReadings = 20
calibration_factor = 747.74

# Init écran LCD 16x2 via I2C
def init_display():
    lcd = CharLCD('PCF8574', 0x3f)
    lcd.clear()
    return lcd

def display_lines(lcd, lines, size=None):  # 'size' est ignoré ici
    lcd.clear()
    for i, line in enumerate(lines[:2]):  # LCD 2 lignes
        lcd.cursor_pos = (i, 0)
        lcd.write_string(line.ljust(16)[:16])

# Init HX711
def init_hx711():
    hx = HX711(dout_pin=DataPin, pd_sck_pin=ClockPin, gain=128, channel='A')
    if hx.reset():
        logging.info("HX711 prêt")
    else:
        logging.error("Erreur HX711")
    return hx

# Mesure poids actuel
def get_weight(hx):
    data = hx.get_raw_data(NumReadings)

    if data and len(data) == NumReadings:
        print(f"Lectures HX711: {data}")

        prefiltered = [x for x in data if (x < 2000*calibration_factor) and (x > calibration_factor)]
        print(f"prefiltered : {prefiltered}")

        try:
            mean = statistics.mean(prefiltered)      # Calcul de la moyenne de l'échantillon
            stddev = statistics.pstdev(prefiltered)  # Calcul de l'écart type de l'échantillon
        except statistics.StatisticsError:
            logging.info("Erreur statistique.")
            return None

        print(f"Moyenne: {mean}")
        print(f"Écart-type (population): {stddev}")

        threshold = 2 * stddev  # on garde les valeurs dans ±2σ

        filtered = [x for x in prefiltered if abs(x - mean) <= threshold]

        print(f"Valeurs filtrées ({len(filtered)} sur {len(data)}): {filtered}")

        if len(filtered) < len(data) // 2:
            logging.info("Trop peu de valeurs fiables, mesure rejetée.")
            return None

        clean_mean = statistics.mean(filtered)
        weight = round(clean_mean / calibration_factor)
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

def animation_pesee(disp, stop_event):
    dots = 0
    while not stop_event.is_set():
        display_lines(disp, ["Pesee de l'idole", "." * (dots % 10)])
        dots += 1
        time.sleep(0.2)

def animation_indy_challenge(disp, stop_event):
    visible = True
    while not stop_event.is_set():
        if visible:
            display_lines(disp, ["Indy Challenge !", "> par G2S"])
        else:
            display_lines(disp, ["Indy Challenge !", "  par G2S"])
        visible = not visible
        time.sleep(0.5)


# Lancer une partie
def run_game(disp, hx):
    stop_event = threading.Event()
    anim_thread = threading.Thread(target=animation_pesee, args=(disp, stop_event))
    anim_thread.start()

    logging.info("Indy Challenge! Pesee de l'idole...")
    tare_weight = get_weight(hx)

    stop_event.set()  # on arrête l’animation
    anim_thread.join()
    
    if tare_weight is None:
        display_lines(disp, ["Erreur tare", "Rejoue!"])
        logging.error("Tare échouée.")
        return
    print(f"Poids de référence : {tare_weight:.2f} g")

    while True:
        weight = get_weight(hx)
        if weight is not None:
            diff = weight - tare_weight
            abs_diff = abs(diff)

            print(f"Écart: {diff:+} g")

            if abs_diff <= 30:
                display_lines(disp, [
                    f"Ecart: {diff:+} g",
                    "C'est bon !"
                ], 14)
            elif abs_diff <= 50:
                display_lines(disp, [
                    f"Ecart: {diff:+} g",
                    "C'est limite !"
                ], 14)
            else:
                display_lines(disp, [
                    "Fuis! Le temple",
                    "  s'ecroule!"]
                , 14)
                time.sleep(2)
                final_weight = get_weight(hx)
                diff = final_weight - tare_weight
                display_lines(disp, [
                    "Ecart: "+ f"{diff:+} g", "Rejouer ?"
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
        display_lines(disp, ["Indy Challenge !", "         par G2S"], 18)
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
