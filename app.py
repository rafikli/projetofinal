import RPi.GPIO as GPIO
import time
import json
import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
from flask import Flask, render_template, send_file, make_response, request

app = Flask(__name__)

GPIO.setmode(GPIO.BCM)

#FUNCOES
def dia():
	geral = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
	geral_separado = geral.split("-")
	hoje = "{}/{}".format(geral_separado[2],geral_separado[1])
	return hoje
	

def obter_dados ():
	arquivo_in = open("coletas.json", "r")
	leitura = arquivo_in.read()
	dados = json.loads(leitura)
	hoje = dia()
	dado = dados[hoje]
	arquivo_in.close()
	
	hora = dado["hora"][-1]
	temp = dado["tempe"][-1]
	umid = dado["umidade"][-1]
	return hora, temp, umid
	
def historico_dados():
	arquivo_in = open("coletas.json", "r")
	leitura = arquivo_in.read()
	dados = json.loads(leitura)
	hoje = dia()
	dado = dados[hoje]
	tempos = dado["hora"]
	temps = dado["tempe"]
	umids = dado["umidade"]

	return tempos, temps, umids
		
def max_linhas():
	hoje = dia()
	dado = dados[hoje]
	num_max = len(dado["hora"])
	return num_max
	
#def freq_coleta():
#	tempos, temps, umids = historico_dados(2)
#	fmt = '%Y-%m-%d %H:%M:%S'
#	tstamp0 = datetime.strptime(tempos[0], fmt)
#	tstamp1 = datetime.strptime(tempos[1], fmt)
#	freq = tstamp1 - tstamp0
#	freq = int(round(freq.total_seconds()/60))
#	return freq

#global numcoletas	
#numcoletas = max_linhas()
#if numcoletas > 101:
#	numcoletas = 100

#global freqcoletas
#freqcoletas = freq_coleta()

#global atu_tempo
#atu_tempo = 100


#Definindo pinos led/refrigeracao

pins = {
   23 : {'name' : 'Luz Sala', 'state' : GPIO.LOW},
   24 : {'name' : 'Porta', 'state' : GPIO.LOW},
   25 : {'name' : 'Som', 'state' : GPIO.LOW},
   26 : {'name' : 'Luz Quarto', 'state' : GPIO.LOW}
   }


for pin in pins:
   GPIO.setup(pin, GPIO.OUT)
   GPIO.output(pin, GPIO.LOW)
   
global temp_max
temp_max = 100
   
@app.route("/")
def main():
	tempo, temperatura, umidade = obter_dados()
	for pin in pins:
		pins[pin]['state'] = GPIO.input(pin)
		templateData = {
			'pins' : pins,
			"tempo": tempo,
			"Temperatura": temperatura,
			"Umid": umidade,
			"temp_max" : temp_max,
#			"numcoletas": numcoletas,
#			"freq": freqcoletas,
#			"atu_tempo": atu_tempo,
			}

	return render_template('main_arrumado.html', **templateData)
	

@app.route("/<changePin>/<action>")
def action(changePin, action):
	
	tempo, temperatura, umidade = obter_dados()

	changePin = int(changePin)

	deviceName = pins[changePin]['name']

	if action == "on":

		GPIO.output(changePin, GPIO.HIGH)

		message = "Turned " + deviceName + " on."
	if action == "off":
		GPIO.output(changePin, GPIO.LOW)
		message = "Turned " + deviceName + " off."

	for pin in pins:
		pins[pin]['state'] = GPIO.input(pin)


		templateData = {
		  'pins' : pins,
		  "tempo": tempo,
		  "Temperatura": temperatura,
		  "Umid": umidade,
		  "temp_max" : temp_max,
		}

	return render_template('main_arrumado.html', **templateData)
   
  
  
#SENSOR TEMPERATURA

@app.route("/sensores", methods = ['POST'])
def controle_temp():
	
	tempo, temperatura, umidade = obter_dados()
	
	global temp_max
	
	temp_max = int(request.form['temp_max'])
	
	arquivo_in = open("temp_max.json", "r")
	arquivo_out = open("temp_max.json", "w")
	leitura = arquivo_in.read()
	if len (leitura) == 0:
		dados = {}
	else:
		dados = json.loads(leitura)
	if "temp_max" not in dados:
		dados["temp_max"] = 0
		dados["temp_max"] = temp_max
	else:
		dados["temp_max"] = temp_max
	arquivo_out.write(json.dumps(dados))
	arquivo_out.close()
	arquivo_in.close()
	
	for pin in pins:
		pins[pin]['state'] = GPIO.input(pin)


		templateData = {
		  'pins' : pins,
		  "tempo": tempo,
		  "Temperatura": temperatura,
		  "Umid": umidade,
		  "temp_max" : temp_max,
		}

	return render_template('sensores.html', **templateData)
	
@app.route("/sensores")
def sensores():	
	
	tempo, temperatura, umidade = obter_dados()
	


	templateData = {
	  "tempo": tempo,
	  "Temperatura": temperatura,
	  "Umid": umidade,
	  "temp_max" : temp_max,
	}

	return render_template('sensores.html',  **templateData)


@app.route('/sensores/plot/temp')
def plot_temp():
	tempos, temps, umids = historico_dados()
	ys = temps
	fig = Figure()
	axis = fig.add_subplot(1,1,1)
	axis.set_title("Temperatura *C")
	axis.set_xlabel("Coletas")
	axis.grid(True)
	xs = range(len(temps))
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response
	
@app.route('/sensores/plot/umid')
def plot_umid():
	tempos, temps, umids = historico_dados()
	ys = umids
	fig = Figure()
	axis = fig.add_subplot(1,1,1)
	axis.set_title("Umidade [%]")
	axis.set_xlabel("Coletas")
	axis.grid(True)
	xs = range(len(umids))
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response	



if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5004, debug=True)




   
