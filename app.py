from firebase import firebase 
import RPi.GPIO as GPIO
import time
import json
import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import io
from flask import Flask, render_template, send_file, make_response, request


firebase = firebase.FirebaseApplication('https://projetofinal-d8c56.firebaseio.com/')

app = Flask(__name__)

GPIO.setmode(GPIO.BCM)


#FUNCOES
		
#def max_linhas():
#	hoje = dia()
#	dado = dados[hoje]
#	num_max = len(dado["hora"])
#	return num_max

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


	
#PARA FIREBASE

def diafb():
	geral = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
	geral_separado = geral.split("-")
	hojefb = "{}{}".format(geral_separado[2],geral_separado[1])
	
	global hoje 
	hoje = "{}/{}".format(geral_separado[2],geral_separado[1])
	
	return hojefb
	
global escolhe_dia
hojefb = diafb()
escolhe_dia = hojefb
escolhe_dia_site = hoje 
	
def obter_dados_firebase(escolhe_dia):
	atual = firebase.get(escolhe_dia, None)
	
	hora_inicial = atual["hora"][0]
	hora = atual["hora"][-1]
	temp = atual["tempe"][-1]
	umid = atual["umidade"][-1]
	
	return hora_inicial, hora, temp, umid
	
def historico_dados_firebase():
	atual = firebase.get(escolhe_dia, None)
	
	tempos = atual["hora"]
	temps = atual["tempe"]
	umids = atual["umidade"]

	return tempos, temps, umids
	
tudo = firebase.get('', None)
global datas
datas = []
global datas1 
datas1 = []
global datas_crescentes 
datas_crescentes = []

for data in tudo:
	if len(data) > 4:
		print('data invalida')
	else:
		datas.append(data)

datas1 = sorted(datas, key=str)
		
for data in datas1:
	data = data[:2] + '/' + data[2:]
	datas_crescentes.append(data)


#Definindo pinos led/refrigeracao

pins = {
   23 : {'name' : 'Luz Sala', 'state' : GPIO.HIGH},
   24 : {'name' : 'Porta', 'state' : GPIO.HIGH},
   25 : {'name' : 'Som', 'state' : GPIO.HIGH},
   22 : {'name' : 'Cafeteira', 'state' : GPIO.HIGH},
   12 : {'name' : 'Ventilador', 'state' : GPIO.HIGH},
   17 : {'name' : 'Seguranca', 'state' : GPIO.HIGH},
   }


for pin in pins:
   GPIO.setup(pin, GPIO.OUT)
   GPIO.output(pin, GPIO.HIGH)
   
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

		GPIO.output(changePin, GPIO.LOW)

	if action == "off":
		GPIO.output(changePin, GPIO.HIGH)

	for pin in pins:
		pins[pin]['state'] = GPIO.input(pin)


		templateData = {
		  'pins' : pins,
		}

	return render_template('main_arrumado.html', **templateData)
  
#SENSOR TEMPERATURA

@app.route("/sensores", methods = ['POST'])
def controle_temp():
	
	global escolhe_dia
	
	global temp_max
	
	if request.method == 'POST':
		
		if 'temp_max' in request.form:
	
			temp_max = float(request.form['temp_max'])
			
			firebase.put('temp_max', 'temp_max', temp_max)
			
			tempo_inicio, tempo, temperatura, umidade = obter_dados_firebase(escolhe_dia)
			
		else:
			global escolhe_dia_site
			escolhe_dia_site = str(request.form["dia_escolhido"])
			escolhe_dia = escolhe_dia_site.split("/")
			escolhe_dia = ''.join(escolhe_dia)
			tempo_inicio, tempo, temperatura, umidade = obter_dados_firebase(escolhe_dia)

	templateData = {
      "tempo_inicio": tempo_inicio,
	  "tempo": tempo,
	  "Temperatura": temperatura,
	  "Umid": umidade,
	  "temp_max" : temp_max,
	  "datas_crescentes":datas_crescentes,
	  "escolhe_dia_site":escolhe_dia_site,
	}

	return render_template('sensores.html', **templateData)
	
	
@app.route("/sensores" , methods = ["GET"])
def sensores():	
	
	tempo_inicio, tempo, temperatura, umidade = obter_dados_firebase(escolhe_dia)
	
	templateData = {
      "tempo_inicio": tempo_inicio,
	  "tempo": tempo,
	  "Temperatura": temperatura,
	  "Umid": umidade,
	  "temp_max" : temp_max,
	 "datas_crescentes":datas_crescentes,
      "escolhe_dia_site":escolhe_dia_site,
	}

	return render_template('sensores.html',  **templateData)


@app.route('/sensores/plot/temp')
def plot_temp():
	tempos, temps, umids = historico_dados_firebase()
	ys = temps
	xs = range(len(temps))

	fig = plt.figure()
	fig.add_subplot(1,1,1)
	plt.plot(xs,ys,'r')
	plt.grid(True)
	horario = [0,(len(temps))/6,(len(temps))/3,(len(temps))/2,4*(len(temps))/6, 5*(len(temps))/6,len(temps)-1]
	plt.xticks(horario, [tempos[0], tempos[len(tempos)/6], tempos[len(tempos)/3], tempos[len(tempos)/2], tempos[4*len(tempos)/6], tempos[5*len(tempos)/6], tempos[-1]], rotation = 45)
	
	if escolhe_dia == hojefb:
		plt.title("Temperatura Atual ({}) [C]".format(hoje))
	else:
		plt.title("Temperatura ao longo do dia {} [C]".format(escolhe_dia_site))
		
	plt.xlabel('Horario')
	plt.ylabel('Temperatura [*C]')
	
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response
	
@app.route('/sensores/plot/umid')
def plot_umid():
	tempos, temps, umids = historico_dados_firebase()
	ys = umids
	xs = range(len(umids))

	fig = plt.figure()
	fig.add_subplot(1,1,1)
	plt.plot(xs,ys, 'b')
	plt.grid(True)
	horario = [0,(len(temps))/6,(len(temps))/3,(len(temps))/2,4*(len(temps))/6, 5*(len(temps))/6,len(temps)-1]
	plt.xticks(horario, [tempos[0], tempos[len(tempos)/6], tempos[len(tempos)/3], tempos[len(tempos)/2], tempos[4*len(tempos)/6], tempos[5*len(tempos)/6], tempos[-1]], rotation = 45)
	
	if escolhe_dia == hojefb:
		plt.title("Umidade Atual ({}) [%]".format(hoje))
	else:
		plt.title("Umidade ao longo do dia {} [%]".format(escolhe_dia_site))
		
	plt.xlabel('Horario')
	plt.ylabel('Umidade [%]')


	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response
	
@app.route('/minimas_maximas')
def minimas_maximas():
	
	templateData = {
	 "datas_crescentes":datas_crescentes,
	}
	
	return render_template('minimas_maximas.html',  **templateData)
	
@app.route('/minimas_maximas/plot/tempminmax')
def plot_tempminmax():
	tmin = []
	tmax = []

	
	tudo = firebase.get('', None)
	
	for dia in datas1[-7:]:
		tmin.append(min(tudo[dia]['tempe']))
		tmax.append(max(tudo[dia]['tempe']))
			
	fig = plt.figure()
	fig.add_subplot(1,1,1)
	plt.title("Temperatura Minima e Maxima dos ultimos 7 dias coletados")
	plt.plot(range(len(tmin)),tmax, 'ro--', label = 'Temperatura Maxima')
	plt.plot(range(len(tmin)),tmin, 'bo--', label = 'Temperatura Minima')
	plt.legend()
	plt.grid(True)
	plt.xticks(range(len(tmin)), datas_crescentes[-7:], rotation = 45)
	
		
	plt.xlabel('Data')
	plt.ylabel('Temperatura [*C]')


	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response
	
@app.route('/minimas_maximas/plot/umidminmax')
def plot_umidminmax():
	umin = []
	umax = []

	
	tudo = firebase.get('', None)
	
	
	
	for dia in datas1[-7:]:

		umin.append(min(tudo[dia]['umidade']))
		umax.append(max(tudo[dia]['umidade']))
			
	fig = plt.figure()
	fig.add_subplot(1,1,1)
	plt.title("Umidade Minima e Maxima dos ultimos 7 dias coletados")
	plt.plot(range(len(umin)),umax, 'ro--', label = 'Umidade Maxima')
	plt.plot(range(len(umin)),umin, 'bo--', label = 'Umidade Minima')
	plt.legend()
	plt.axis([-0.3,len(umin)-0.5,20,100])
	plt.grid(True)
	plt.xticks(range(len(umin)), datas_crescentes[-7:], rotation = 45)
	
		
	plt.xlabel('Data')
	plt.ylabel('Umidade [%]')


	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

@app.route('/comofunciona')
def comofunciona():
	return render_template('comofunciona.html')


@app.route('/camera/historico', methods=['GET', 'POST']) 
def historico(): 
	global escolhe_dia_site
	
	with open("historico.json","r") as arquivo:
		leitura = arquivo.read()
		historico = json.loads(leitura)
	dias_foto = []
	
	for dia_foto in historico.keys():
		dias_foto.append(dia_foto)
	nomes_foto = []
	
	if request.method == "POST":
		if 'dia_foto' in request.form:
			escolhe_dia_site = str(request.form["dia_foto"])
		
	for nome in historico[escolhe_dia_site]:
		nomes_foto.append(nome)

		
	templateData = {
	"dias_foto":dias_foto,
	"nomes_foto":nomes_foto,
	"escolhe_dia_site":escolhe_dia_site,
	}
	return render_template("camera_historico.html", **templateData)

@app.route('/cadastre-se')



@app.route('/login')
def login(): 
	
	if request.method == "POST":
		usuario = request.form['email']
		senha_input = request.form['senha']
		 
	return render_template('login.html')


if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5004, debug=True)




   
