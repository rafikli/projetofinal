import RPi.GPIO as GPIO
from datetime import datetime
import time
from picamera import PiCamera
import datetime

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(17, GPIO.OUT)


camera = PiCamera()
with open("historico.json","r") as arquivo:
	historico = arquivo.read
while True:
	if GPIO.input(17) == GPIO.HIGH:
		i=GPIO.input(13)
		if i == GPIO.LOW:                 
			print("Sem intrusos")
			time.sleep(0.5)
		elif i == GPIO.HIGH:               
			data = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
			with open("historico.json","w") as arquivo:
				arquivo.write("{}.jpg".format(data))
			camera.start_preview()
			time.sleep(2)
			camera.capture("/home/pi/projetofinal/static/intrusos/{}.jpg".format(data))
			print("Intruso detectado.Foto tirada {}".format(data))
			camera.stop_preview()
			time.sleep(0.5)
