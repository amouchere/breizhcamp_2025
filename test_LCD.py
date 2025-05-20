from RPLCD.i2c import CharLCD
from time import sleep

lcd = CharLCD('PCF8574', 0x3f)
lcd.write_string('Hello BreizhCamp!')
sleep(2)
lcd.clear()
lcd.write_string('Écran LCD OK 🎉')