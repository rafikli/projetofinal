# Carrega as bibliotecas
import Adafruit_DHT
import RPi.GPIO as GPIO
import time
 
sensor = Adafruit_DHT.DHT22
 
GPIO.setmode(GPIO.BCM)
 
pino_sensor = 21
 
#while(1):
  
#   umid, temp = Adafruit_DHT.read_retry(sensor, pino_sensor);

#   if umid is not None and temp is not None:
#     print ("Temperatura = {0:0.1f}  Umidade = {1:0.1f}n").format(temp, umid);
#     print ("Aguarda 5 segundos para efetuar nova leitura...n");
#     time.sleep(5)
#   else:
 
#     print("Falha ao ler dados do DHT11 !!!")

def calcula_temp():
	umid, temp = Adafruit_DHT.read_retry(sensor, pino_sensor)
	if umid is not None and temp is not None:
		temps = {}
		temps["temperatura"]= 0
		t = "{0:.2f}".format(temp)
		t = float(t)
		temps["temperatura"] = t
		return temps
	else:
		return None
