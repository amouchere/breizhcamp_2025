from gpiozero import PWMOutputDevice, Button
from time import sleep

# Dictionnaire notes -> fréquences (ton dictionnaire corrigé ici)
notes_freqs = {
    'B0': 31, 'C1': 33, 'CS1': 35, 'D1': 37, 'DS1': 39, 'E1': 41, 'F1': 44, 'FS1': 46,
    'G1': 49, 'GS1': 52, 'A1': 55, 'AS1': 58, 'B1': 62, 'C2': 65, 'CS2': 69, 'D2': 73,
    'DS2': 78, 'E2': 82, 'F2': 87, 'FS2': 93, 'G2': 98, 'GS2': 104, 'A2': 110, 'AS2': 117,
    'B2': 123, 'C3': 131, 'CS3': 139, 'D3': 147, 'DS3': 156, 'E3': 165, 'F3': 175, 'FS3': 185,
    'G3': 196, 'GS3': 208, 'A3': 220, 'AS3': 233, 'B3': 247, 'C4': 262, 'CS4': 277, 'D4': 294,
    'DS4': 311, 'E4': 330, 'F4': 349, 'FS4': 370, 'G4': 392, 'GS4': 415, 'A4': 440, 'AS4': 466,
    'B4': 494, 'C5': 523, 'CS5': 554, 'D5': 587, 'DS5': 622, 'E5': 659, 
    'F5': 698, 'FS5': 740, 'G5': 784, 'GS5': 831, 'A5': 880, 'AS5': 932, 'B5': 988, 'C6': 1047, 
    'CS6': 1109, 'D6': 1175, 'DS6': 1245, 'E6': 1319, 'F6': 1397, 'FS6': 1480, 'G6': 1568,
    'R': 0  # Silence
}

# Mélodie de Indiana Jones
melody = [
    # MI FA SOL DO 
    ("E4", 0.25), ("F4", 0.25), ("G4", 0.25), ("C5", 0.75),
    # RE MI FA 
    ("D4", 0.25), ("E4", 0.25), ("F4", 0.75),
    # SOL LA SI FA
    ("G4", 0.25), ("A4", 0.25), ("B4", 0.25), ("F5", 0.75),
    # LA SI DO RE MI 
    ("A4", 0.25), ("B4", 0.20), ("C5", 0.75), ("D5", 0.75), ("E5", 0.5),
    # MI FA SOL DO 
    ("E4", 0.25), ("F4", 0.25), ("G4", 0.25), ("C5", 1),
    # RE MI FA
    ("D5", 0.25), ("E5", 0.25), ("F5", 0.75),
    # SOL SOL MI RE SOL MI
    ("G4", 0.25),("G4", 0.25),("E5", 0.25),("D5", 0.25),("G4", 0.25),("E5", 0.25),
    # RE SOL MI RE SOL MI
    ("D5", 0.25),("G4", 0.25),("E5", 0.25), ("D5", 0.25),("G4", 0.25),("E5", 0.60),
    # RE
    # ("E5", 0.25),
    # MI FA SOL DO 
    #("E4", 0.25), ("F4", 0.25)
]

# Instancier le buzzer et le bouton
buzzer = PWMOutputDevice(18)
button = Button(16)

# Tempo
bpm = 80  # plus rapide que 120 pour le vrai feeling Indiana Jones
beat_duration = 60 / bpm

def play_melody():
    for note, duration in melody:
        freq = notes_freqs.get(note, 0)
        if freq == 0:
            buzzer.value = 0
        else:
            buzzer.frequency = freq
            buzzer.value = 0.5
        sleep(duration * beat_duration)
        buzzer.value = 0
        sleep(0.05)
        # petit blanc entre les notes

while True:
    button.wait_for_press()
    play_melody()