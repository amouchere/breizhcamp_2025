from gpiozero import PWMOutputDevice
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
    ("E4", 0.25), ("F4", 0.25), ("G4", 0.25), ("C5", 0.75),
    ("D4", 0.25), ("E4", 0.25), ("F4", 0.75),
    ("G4", 0.25), ("A4", 0.25), ("B4", 0.25), ("F5", 0.75),
    ("A4", 0.25), ("B4", 0.25), ("C4", 0.5), ("D4", 0.5), ("E5", 0.5),
    ("E4", 0.25), ("F4", 0.25), ("G4", 0.25), ("C5", 0.75)
]

# MI FA SOL DO 
# RE MI FA 
# SOL LA SI FA
# LA SI DO RE MI 
# MI FA SOL DO 
notes = [
    "E4", "G4", "E4", "E4", "G4", "E4", "E4", "G4", "B4", "A4",
    "G4", "E4", "D4", "E4", "R",  "E4", "G4", "E4", "E4", "G4",
    "E4", "E4", "G4", "B4", "A4", "G4", "B4", "A4", "G4", "E4",
    "D4", "E4"
]

durations = [
    0.25, 0.25, 0.5, 0.25, 0.25, 0.5, 0.25, 0.25, 0.25, 0.25,
    0.5, 0.25, 0.25, 0.5, 0.25, 0.25, 0.25, 0.5, 0.25, 0.25,
    0.5, 0.25, 0.25, 0.25, 0.25, 0.5, 0.25, 0.25, 0.25, 0.25,
    0.5, 0.5
]

# Instancier le buzzer sur GPIO 18
buzzer = PWMOutputDevice(18)

# Tempo
bpm = 80  # plus rapide que 120 pour le vrai feeling Indiana Jones
beat_duration = 60 / bpm

# Jouer la mélodie
for note, duration in melody:
    frequency = notes_freqs.get(note, 0)
    if frequency == 0:
        buzzer.value = 0
    else:
        buzzer.frequency = frequency
        buzzer.value = 0.5
    sleep(duration * beat_duration)
    buzzer.value = 0
    sleep(0.05)  # petit blanc entre les notes
