# Projet Capteur de Force avec HX711 pour BreizhCamp

Ce projet utilise un capteur de force connecté à un module HX711 pour mesurer des poids via un Raspberry Pi. Il est conçu pour être présenté lors de la conférence **BreizhCamp** afin de démontrer des applications de capteurs dans des projets IoT.

## Matériel nécessaire

- Raspberry Pi
- Module HX711
- Cellule de charge (balance)
- Câbles de connexion

## Installation du projet sur Raspberry Pi

### 1. Préparer l'environnement

#### Créer un environnement virtuel (recommandé) :

Si tu souhaites utiliser un environnement isolé pour tes dépendances Python, voici les étapes à suivre :

```bash
# Installer les outils nécessaires (si pas déjà fait)
sudo apt-get update
sudo apt-get install python3-pip python3-venv

# Créer un dossier pour ton projet
mkdir ~/mon_projet_hx711
cd ~/mon_projet_hx711

# Créer un environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate