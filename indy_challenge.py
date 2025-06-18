#!/usr/bin/python3

# --- Imports standard ---
import time
import threading
import statistics
import logging
from datetime import datetime

# --- Imports tiers ---
import RPi.GPIO as GPIO
from hx711 import HX711
from RPLCD.i2c import CharLCD

# --- Configuration générale ---
LOG_FILE = "/home/pi/indy.log"
NUM_READINGS = 5
CALIBRATION_FACTOR = 747.74
WEIGHT_CHANGE_THRESHOLD = 10  # en grammes
REPLACEMENT_TIME_LIMIT = 1    # en secondes

# --- GPIO ---
DATA_PIN = 5
CLOCK_PIN = 6
BUTTON_PIN = 20  # Bouton "Rejouer"


# --- Config log ---
LOG_LEVEL = logging.WARNING

logging.basicConfig(
    filename=LOG_FILE,
    level=LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- Init écran LCD ---
def init_display():
    lcd = CharLCD('PCF8574', 0x3f)
    lcd.clear()
    return lcd

def display_lines(lcd, lines, size=None):
    lcd.clear()
    for i, line in enumerate(lines[:2]):
        lcd.cursor_pos = (i, 0)
        lcd.write_string(line.ljust(16)[:16])

# --- Init HX711 ---
def init_hx711():
    hx = HX711(dout_pin=DATA_PIN, pd_sck_pin=CLOCK_PIN, gain=128, channel='A')
    if hx.reset():
        logging.warning("HX711 prêt")
    else:
        logging.error("Erreur HX711")
    return hx

# --- Lecture du poids ---
def get_weight(hx):
    data = hx.get_raw_data(NUM_READINGS)

    if data and len(data) == NUM_READINGS:
        logging.info(f"----")
        logging.info(f"Lectures HX711: {data}")
        prefiltered = [x for x in data if (x < 2000 * CALIBRATION_FACTOR) and (x > 100 * CALIBRATION_FACTOR)]
        logging.info(f"filtre brut    :   {prefiltered}")

        try:
            mean = statistics.mean(prefiltered)     # Moyenne
            stddev = statistics.pstdev(prefiltered) # Ecart type
            median = statistics.median(prefiltered) # Mediane
            mad = statistics.median([abs(x - median) for x in prefiltered])
        except statistics.StatisticsError:
            logging.warning("Erreur statistique.")
            return None

        logging.info(f"Moyenne: {mean}")
        logging.info(f"Médiane: {median}")
        logging.info(f"MAD: {mad}")
        logging.info(f"Écart-type (population): {stddev}")

        threshold = 3 * mad if mad > 0 else 1000  # fallback si mad=0
        filtered = [x for x in prefiltered if abs(x - median) <= threshold]
        # threshold = 2 * stddev
        # filtered = [x for x in prefiltered if abs(x - mean) <= threshold]
        logging.info(f"filtre mad : {filtered}")
        logging.info(f"Valeurs filtrées ({len(filtered)} sur {len(data)}): {filtered}")

        if len(filtered) < len(data) // 2:
            logging.warning("Trop peu de valeurs fiables, mesure rejetée.")
            return None

        clean_mean = statistics.mean(filtered)
        weight = round(clean_mean / CALIBRATION_FACTOR)
        logging.info(f"Poids estimé: {weight:.2f} g")
        return weight
    else:
        logging.warning("Erreur : Pas assez de données valides.")
        return None

# --- Init bouton GPIO ---
def init_buttons():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --- Attente bouton ---
def wait_for_button_press():
    logging.warning("En attente du bouton pour rejouer...")
    while GPIO.input(BUTTON_PIN) == 0:
        time.sleep(0.1)
    while GPIO.input(BUTTON_PIN) == 1:
        time.sleep(0.1)

# --- Animations ---
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

# --- Partie principale ---
def run_game(disp, hx):
    stop_event = threading.Event()
    anim_thread = threading.Thread(target=animation_pesee, args=(disp, stop_event))
    anim_thread.start()

    logging.info("Indy Challenge! Pesee de l'idole...")
    tare_weight = get_weight(hx)
    time.sleep(1)
    stop_event.set()
    anim_thread.join()

    print(f"Poids de référence : {tare_weight} g")

    display_lines(disp, ["Allez y ...", "doucement..."])
    logging.info("Attente du retrait de la statue...")

    while True:
        current = get_weight(hx)
        if current is not None:
            variation = abs(current - tare_weight)
            if variation >= WEIGHT_CHANGE_THRESHOLD:
                logging.info("Changement détecté : déclenchement du chrono.")
                break
        time.sleep(0.1)

    for _ in range(REPLACEMENT_TIME_LIMIT, 0, -1):
        display_lines(disp, ["Attention !!", "..."])
        time.sleep(1)

    final_weight = get_weight(hx)

    if final_weight is None:
        display_lines(disp, ["Erreur mesure", "Rejouer ?"])
        return

    diff = final_weight - tare_weight
    abs_diff = abs(diff)
    print(f"Écart final: {diff:+} g")

    if abs_diff <= 30:
        display_lines(disp, [f"Ecart: {diff:+} g", "Bravo !"])
    elif abs_diff <= 50:
        display_lines(disp, [f"Ecart: {diff:+} g", "C'est limite !"])
    else:
        display_lines(disp, ["Fuis! Le temple", "  s'ecroule!"])
        time.sleep(2)
        display_lines(disp, [f"Ecart: {diff:+} g", "Rejouer ?"])

# --- Main loop ---
def main():
    disp = init_display()
    hx = init_hx711()
    init_buttons()

    while True:
        display_lines(disp, ["Indy Challenge !", "          by G2S"])
        wait_for_button_press()
        run_game(disp, hx)
        wait_for_button_press()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.warning("Arrêt !")
    finally:
        GPIO.cleanup()
