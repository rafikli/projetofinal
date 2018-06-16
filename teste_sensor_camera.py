import RPi.GPIO as GPIO
from datetime import datetime
import time
from picamera import PiCamera
import datetime
import json
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import smtplib

msg = MIMEMultipart()

password = 'pihomedsoft'
msg['From'] = 'pihomedigital@gmail.com'
msg['To'] = 'pedroluiz51@gmail.com'
#msg['To'] = 'rafael.libertini@gmail.com'
msg['Subject'] = 'Intruso Detectado'

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(17, GPIO.OUT)


camera = PiCamera()
with open("historico.json","r") as arquivo:
	leitura = arquivo.read()
	if len(leitura) == 0:
		historico = {}
	else:
		historico = json.loads(leitura)
while True:
	if GPIO.input(17) == GPIO.LOW:
		i=GPIO.input(13)
		if i == GPIO.LOW:                 
			print("Sem intrusos")
			time.sleep(0.5)
		elif i == GPIO.HIGH:
			data = datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")
			geral_separado = data.split("-")
			dia = "{}/{}".format(geral_separado[2],geral_separado[1])
			data_str = str(data)
			data_jpg = data_str + ".jpg"
			if dia not in historico.keys():
				historico[dia] = []
			historico[dia].append(data_jpg)  
			with open("historico.json","w") as arquivo:
				arquivo.write(json.dumps(historico))
			camera.start_preview()
			time.sleep(2)
			camera.capture("/home/pi/projetofinal/static/intrusos/{}.jpg".format(data))
			print("Intruso detectado.Foto tirada {}".format(data))
			camera.stop_preview()
			
			foto = open("/home/pi/projetofinal/static/intrusos/{}.jpg".format(data) , 'rb')
			#msg.attach(MIMEText(''))
			msg.attach(MIMEImage(foto.read()))
			server = smtplib.SMTP('smtp.gmail.com: 587')
			server.starttls()
			server.login(msg['From'], password)
			server.sendmail(msg['From'], msg['To'], msg.as_string())
			server.quit()
			
			time.sleep(0.5)
