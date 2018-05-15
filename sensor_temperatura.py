# Carrega as bibliotecas
import Adafruit_DHT
import RPi.GPIO as GPIO
import time
import json
import datetime
from firebase import firebase 

#setando pino ventilador
pino_vent = 12

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pino_vent, GPIO.OUT)
GPIO.output(pino_vent, GPIO.HIGH)
 
frequencia = 20 

sensor = Adafruit_DHT.DHT22
 
pino_sensor = 21

#coletando dados anteriores

#arquivo_in = open("coletas.json", "r")
#leitura = arquivo_in.read()

#if len (leitura) == 0:
#	dados = {}
#else:
#	dados = json.loads(leitura)

#arquivo_in.close()

geral = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
geral_separado = geral.split("-")

hoje = "{}/{}".format(geral_separado[2],geral_separado[1])

#if hoje in dados:
#	dado = dados[hoje]
#else:
#	dados[hoje] = {}
#	dado = dados[hoje]
#	dado["hora"] = []
#	dado["tempe"] = []
#	dado["umidade"] = []
	

#FIREBASE

hojefb = "{}{}".format(geral_separado[2],geral_separado[1])

firebase = firebase.FirebaseApplication('https://projetofinal-d8c56.firebaseio.com/')

try:
	coletas_hoje = firebase.get(hojefb, None)
	temp_hoje = coletas_hoje['tempe']
	hora_hoje = coletas_hoje['hora']
	umidade_hoje = coletas_hoje['umidade']
	
except:
	temp_hoje = []
	hora_hoje = []
	umidade_hoje = []
	


def dadosDHT():
	umid, temp = Adafruit_DHT.read_retry(sensor, pino_sensor)
	if umid is not None and temp is not None:
		temp = "{0:.2f}".format(temp)
		temp = float(temp)
		umid = "{0:.1f}".format(umid)
		umid = float(umid)
		return temp, umid
		
def add_firebase(temp, umid):
	geral = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
	geral_separado = geral.split("-")
	hora = "{}:{}".format(geral_separado[3],geral_separado[4])
	
	temp_hoje.append(temp)
	hora_hoje.append(hora)
	umidade_hoje.append(umid)
	
	firebase.put(hojefb, 'tempe', temp_hoje)
	firebase.put(hojefb, 'hora', hora_hoje)
	firebase.put(hojefb, 'umidade', umidade_hoje)
	
def le_tmax_firebase():
	tmax = firebase.get('temp_max', None)
	temp_max = tmax['temp_max']
	return temp_max
	
#def add_json(temp, umid):
#	arquivo_out = open("coletas.json", "w")
	
#	geral = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
#	geral_separado = geral.split("-")
#	hora = "{}:{}".format(geral_separado[3],geral_separado[4])

#	dado["hora"].append(hora)
#	dado["tempe"].append(temp)
#	dado["umidade"].append(umid)
	
#	arquivo_out.write(json.dumps(dados))
#	arquivo_out.close()
	
#def le_temp_max():
#	arquivo_in = open("temp_max.json", "r")
#	leitura = arquivo_in.read()
#	if len (leitura) == 0:
#		dados = {}
#	else:
#		dados = json.loads(leitura)
#	if "temp_max" not in dados:
#		dados["temp_max"] = 100
#		temp_max = dados["temp_max"]
#	else:
#		temp_max = dados["temp_max"]
	
#	arquivo_in.close()
	
#	return temp_max
	
def principal():
	while True:
		temp, umid = dadosDHT()
		if umid >600 and temp < 14:
			print("Falha nesta coleta") 
		else:
			#temp_max = le_temp_max()
			temp_max = le_tmax_firebase()
			if temp >= temp_max:
				GPIO.output(pino_vent, GPIO.HIGH)
				
			else:
				GPIO.output(pino_vent, GPIO.LOW)
				
#			add_json(temp, umid)
			add_firebase(temp, umid)
			time.sleep(frequencia)
	
principal()
