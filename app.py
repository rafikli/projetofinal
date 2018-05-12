import RPi.GPIO as GPIO
import time
import json
import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import picamera 
import cv2
import socket 
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
	
global escolhe_dia
hoje = dia()
escolhe_dia = hoje   	

def obter_dados (escolhe_dia):
	arquivo_in = open("coletas.json", "r")
	leitura = arquivo_in.read()
	dados = json.loads(leitura)
#	hoje = dia()
	dado = dados[escolhe_dia]
	arquivo_in.close()
	
	hora_inicial = dado["hora"][0]
	hora = dado["hora"][-1]
	temp = dado["tempe"][-1]
	umid = dado["umidade"][-1]
	return hora_inicial, hora, temp, umid
	
def historico_dados():
	arquivo_in = open("coletas.json", "r")
	leitura = arquivo_in.read()
	dados = json.loads(leitura)
#	hoje = dia()
	dado = dados[escolhe_dia]
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
   26 : {'name' : 'Luz Quarto', 'state' : GPIO.LOW},
   12 : {'name' : 'Ventilador', 'state' : GPIO.LOW}
   }


for pin in pins:
   GPIO.setup(pin, GPIO.OUT)
   GPIO.output(pin, GPIO.LOW)
   
global temp_max
temp_max = 100
   
@app.route("/")
def main():
	for pin in pins:
		pins[pin]['state'] = GPIO.input(pin)
		templateData = {
			'pins' : pins,
			}

	return render_template('main_arrumado.html', **templateData)
	

@app.route("/<changePin>/<action>")
def action(changePin, action):
	
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
		}

	return render_template('main_arrumado.html', **templateData)
  
#SENSOR TEMPERATURA

@app.route("/sensores", methods = ['POST'])
def controle_temp():
	
	tempo_inicio, tempo, temperatura, umidade = obter_dados(escolhe_dia)
	
	global temp_max
	
	global escolhe_dia
	
	if request.method == 'POST':
		
		if 'temp_max' in request.form:
	
			temp_max = float(request.form['temp_max'])
			
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
		
		else:
			
			escolhe_dia = str(request.form["dia_escolhido"])

	templateData = {
      "tempo_inicio": tempo_inicio,
	  "tempo": tempo,
	  "Temperatura": temperatura,
	  "Umid": umidade,
	  "temp_max" : temp_max,
	  "datas":datas,
	  "escolhe_dia":escolhe_dia,
	}

	return render_template('sensores.html', **templateData)
	
@app.route("/sensores" , methods = ["GET"])
def sensores():	
	
	tempo_inicio, tempo, temperatura, umidade = obter_dados(escolhe_dia)
	
	arquivo_in = open("coletas.json", "r")
	leitura = arquivo_in.read()
	dados = json.loads(leitura)
	
	global datas
	datas = []
	
	for data in dados:
		datas.append(data)
	arquivo_in.close()


	templateData = {
      "tempo_inicio": tempo_inicio,
	  "tempo": tempo,
	  "Temperatura": temperatura,
	  "Umid": umidade,
	  "temp_max" : temp_max,
	  "datas":datas,
      "escolhe_dia":escolhe_dia,
	}

	return render_template('sensores.html',  **templateData)


@app.route('/sensores/plot/temp')
def plot_temp():
	tempos, temps, umids = historico_dados()
	ys = temps
	fig = Figure()
	axis = fig.add_subplot(1,1,1)
	if escolhe_dia == hoje:
		axis.set_title("Temperatura Atual ({}) [C]".format(hoje))
	else:
		axis.set_title("Temperatura ao longo do dia {} [C]".format(escolhe_dia))
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
	if escolhe_dia == hoje:
		axis.set_title("Umidade Atual ({}) [%]".format(hoje))
	else:
		axis.set_title("Umidade ao longo do dia {} [%]".format(escolhe_dia))
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


vc = cv2.VideoCapture(0) 
@app.route('/') 
def camera(): 
   return render_template('camera.html') 
def gen(): 
   while True: 
       rval, frame = vc.read() 
       cv2.imwrite('pic.jpg', frame) 
       yield (b'--frame\r\n' 
              b'Content-Type: image/jpeg\r\n\r\n' + open('pic.jpg', 'rb').read() + b'\r\n') 
@app.route('/video_feed') 
def video_feed(): 

   return Response(gen(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame') 

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5004, debug=True)




   
