# test_oled.py

import board
import busio
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont

# Initialisation I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Taille écran
WIDTH = 128
HEIGHT = 64

# Initialisation OLED
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Efface l'écran
oled.fill(0)
oled.show()

# Crée une image noir et blanc
image = Image.new("1", (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)

# Dessine du texte
font = ImageFont.load_default()
draw.text((10, 20), "Hello BreizhCamp!", font=font, fill=255)

# Affiche l'image
oled.image(image)
oled.show()
