# Projet Capteur de Force avec HX711 pour BreizhCamp

Ce projet utilise un capteur de force connecté à un module HX711 pour mesurer des poids via un Raspberry Pi. Il est conçu pour être présenté lors de la conférence **BreizhCamp** afin de démontrer des applications de capteurs dans des projets IoT.

## Matériel nécessaire

- Raspberry Pi
- Module HX711
- Cellule de charge (balance)
- Câbles de connexion

## Installation du projet sur Raspberry Pi

### 1. Préparer l'environnement

Si tu souhaites utiliser un environnement isolé pour tes dépendances Python, voici les étapes à suivre :

```bash
# Activation I2C : Interface Options → I2C → Enable.
sudo raspi-config

git clone git@github.com:amouchere/breizhcamp_2025.git

# Installer les outils nécessaires (si pas déjà fait)
sudo apt-get update
sudo apt-get install python3-pip python3-venv

# Pour utiliser l'écran OLED
sudo apt-get install -y libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7 libwebp-dev tk-dev python3-dev libtiff-dev

# Créer un environnement virtuel
cd ~/breizhcamp_2025
python3 -m venv venv

# Activer l'environnement virtuel
cd ~/breizhcamp_2025
source venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt
```

### 2. Lancement du projet

```bash
# Activer l'environnement virtuel
cd ~/breizhcamp_2025
source venv/bin/activate

# Launch
python3 indy_challenge.py


```