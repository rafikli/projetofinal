import time
import Adafruit_DHT

frequencia = 120

def dadosDHT():
	sensor = Adafruit_DHT.DHT22
	pino_sensor = 21

	umid, temp = Adafruit_DHT.read_retry(sensor, pino_sensor)
	
	if umid is not None and temp is not None:
		umid = "{0:.2f}".format(umid)
		temp = "{0:.2f}".format(temp)
	return temp, umid


print(1)
print(dadosDHT())
print(2)
