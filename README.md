![indy](./indiana-jones-raiders-of-the-lost-ark.gif)

<a href="https://gitmoji.dev">
  <img
    src="https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg?style=flat-square"
    alt="Gitmoji"
  />
</a>

# Breizhcamp 2025 : Indiana Jones Challenge !

Ce projet utilise un capteur de force connecté à un module HX711 pour mesurer des poids via un Raspberry Pi. Il est conçu pour être présenté lors de la conférence **BreizhCamp** afin de démontrer des applications de capteurs dans des projets IoT.

## Matériel nécessaire

- Raspberry Pi
- Module HX711
- Cellule de charge (balance)
- Câbles de connexion
- Ecran LCD
- Buzzer passif

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

### 3. Installation du service systemd

#### Indy challenge service

```bash
sudo cp ~/breizhcamp_2025/indy.service /etc/systemd/system/indy.service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable indy.service
sudo systemctl start indy.service
```

#### Indy buzzer theme service

```bash
sudo cp ~/breizhcamp_2025/indy_buzzer_theme.service /etc/systemd/system/indy_buzzer_theme.service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable indy_buzzer_theme.service
sudo systemctl start indy_buzzer_theme.service
```