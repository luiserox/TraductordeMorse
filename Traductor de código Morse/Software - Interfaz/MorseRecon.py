import matplotlib
matplotlib.use('Qt4Agg')
import sys
from PyQt4 import QtCore, QtGui, uic
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
import time
import serial
qtCreatorFile = "graph3.ui" # my Qt Designer file 

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


i=1
j=0
channels=[0,0,0,0] # Posicion 0 y 1: analogico 1 y 2 respectivamente; Posicion 2 y 3: digital 1 y 2 respectivamente
x = []
y_An1 = []
y_Dig1 = []
y_Dig2 = []
abcmorse=['.-','-...','-.-.','-..','.','..-.','--.','....','..','.---','-.-','.-..','--','-.','---','.--.','--.-','.-.','...','-','..-','...-','.--','-..-','-.--','--..','-----','.----','..---','...--','....-','.....','-....','--...','---..','----.','---...','-.--.-']
abc=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9',':',')']
acumhi=0
acumlo=0
letra=''
espacio = 0
texto=''
contadorelementos=00
font=1



# Inicializacion de puerto serial
ser = serial.Serial('COM5', 115200) # Puerto en la computadora y baud rate
ser.set_buffer_size(rx_size = 128000, tx_size = 128000) # Incrementar tamaño de Buffer


class MyApp(QtGui.QMainWindow, Ui_MainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		Ui_MainWindow.__init__(self)
		self.setupUi(self)
		self.navigation = NavigationToolbar(self.canvas,self)
		self.hlayout.addWidget(self.navigation)
	   
		#Escala de Voltaje
		self.voltbase.setStatusTip("Ajustar escala de voltaje")
		self.voltbase.activated[str].connect(self.changebasevolt)
		
		#Escala de tiempo
		self.timebase.setStatusTip("Ajustar base de tiempo")
		self.timebase.activated[str].connect(self.changebasetime)

		#Canales Analogicos
		#self.analog1.stateChanged.connect(self.ang1)
		#self.analog1.setStatusTip("Canal Analogico 1")
		#self.analog2.stateChanged.connect(self.ang2)
		#self.analog2.setStatusTip("Canal Analogico 2")

		#self.lcdNumber=QtGui.QLCDNUMBER(self.centralWidget)
		number=00;
		self.lcdNumber.display(number)
		text='hola'
		self.label_3.setText(text)
		#Canales Digitales
		#self.digital1.stateChanged.connect(self.digi1)
		#self.digital1.setStatusTip("Canal Digital 1")
		#self.digital2.stateChanged.connect(self.digi2)
		#self.digital2.setStatusTip("Canal Digital 2")

		#Grid
		self.gridstate.stateChanged.connect(self.grid)
		self.gridstate.setStatusTip("Colocar Grid en la grafica")

		#Crear parámetros de funcionamiento
		self.refresh=1/10 #Periodo de actualización de imagen
		self.buffact=1/40 #Periodo de actualización de buffer de datos
		self.buffready = 0 #Variable para indicar el fin de la lectura inicial del buffer de datos
		self.refreshcount = self.refresh*1000
		self.buffactcount = self.buffact*1000

		#Iniciar timer para la graficación
		timergraf = QtCore.QTimer(self)
		timergraf.timeout.connect(self.tickgraf)
		timergraf.start(self.refreshcount)

		#Iniciar timer para actualización de datos
		timerbuff = QtCore.QTimer(self)
		timerbuff.timeout.connect(self.tickbuff)
		timerbuff.start(self.buffactcount)

	def tickgraf(self):
		global i #Contador
		global x #Eje X
		global y_An1 #Datos analog 1
		global y_Dig1 #Datos digital 1
		global y_Dig2 #Datos digital 2
		if(self.buffready):  #Una vez esté listo el buffer de datos
			if(i):  #Primera vez graficando
				i=0 #Terminar la inicialización del buffer
				x.reverse()	 #Para que se grafique de izquierda a derecha	
				self.ax = self.canvas.figure.add_subplot(111)  #Crear la figura para graficar
				self.varAn1,= self.ax.plot(x,y_An1,'r',alpha=1) #Declaración de cada uno de los canales 
				self.varDig1,= self.ax.plot(x,y_Dig1,'g',alpha=channels[2]) #Alpha es el parámetro de la transparencia 
				self.varDig2,= self.ax.plot(x,y_Dig2,'m',alpha=channels[3])	
				x1,x2,y1,y2 = self.ax.axis() #se declaran self.variables para determinar los limites de los ejes
				self.ax.axis((0,1,0,3)) #se establecen los limites para los ejes, primeo el ejex y luego el y.

			else:
				#Actualizacción de los datos de cada canal
				self.varAn1.set_ydata(y_An1) 
				self.varDig1.set_ydata(y_Dig1)
				self.varDig2.set_ydata(y_Dig2)

			#Actualizar la gráfica	
			self.canvas.draw()
			self.canvas.flush_events()

	def tickbuff(self):
				global i #Contador
				global x #Eje X
				global y_An1 #Datos analog 1
				global y_Dig1 #Datos digital 1
				global y_Dig2 #Datos digital 2
				global acumhi
				global acumlo
				global letra
				global espacio
				global texto
				global contadorelementos
				global font

				if(i):  #Para cuando se llena inicialmente el buffer
					i=i+1 
					for cont in range(100):
						x.append(self.buffact*2*((i-2) + (cont)/100)) #Crear el eje x
					if(i > 1/(self.buffact*2)): 
						self.buffready=1

				else:   
					del y_An1[:100];
					del y_Dig1[:100];
					del y_Dig2[:100];

				(dataAnOrg1,dataDigOrg1,dataDigOrg2,filt) =  self.leer()
				if filt:
					dataAn1 = map(lambda x: x*1.4922/32385, dataAnOrg1)
					dataDig1 = map(lambda x: x*3/128, dataDigOrg1)
					dataDig2 = map(lambda x: x*3/128, dataDigOrg2)
					self.label_9.setText('ON')
				else:
					dataAn1 = map(lambda x: x*3/255, dataAnOrg1)
					dataDig1 = map(lambda x: x*3/128, dataDigOrg1)
					dataDig2 = map(lambda x: x*3/128, dataDigOrg2)
					self.label_9.setText('OFF')
				y_An1.extend(dataAn1)
				y_Dig1.extend(dataDig1)
				y_Dig2.extend(dataDig2)

				if(any(dataDigOrg1)):
					texto=''
					self.label_3.setText(texto)
					contadorelementos=0
					self.lcdNumber.display(contadorelementos)
				if(any(dataDigOrg2)):
					if(font):
						self.label_3.setStyleSheet("font: 50pt Comic Sans MS")
						font = 0
					else:
						self.label_3.setStyleSheet("font: 50pt Papyrus")
						font = 1


				for morsecount in range(100):
					if(dataAnOrg1[morsecount]>=43405 or (dataAnOrg1[morsecount]>=175 and not filt)):
						acumhi+=1
				for morsecount in range(99):	
					if((dataAnOrg1[morsecount+1]<40000 and dataAnOrg1[morsecount]<40000 and filt) or (dataAnOrg1[morsecount+1]<125 and dataAnOrg1[morsecount]<125)):
						acumlo+=1
						if(acumlo>350):
							espacio = 1
					else:
						acumlo=0

				if(acumlo>35):
					if(acumlo<80): 
						acumlo=0
					if(25<acumhi<90):
						letra+='.'
						#print('.')
					if(135<acumhi<225):
						letra+='-'
						#print('-')
					acumhi=0

				if(acumlo>250):				
					for m in range(38):
						if(letra==abcmorse[m]):
							if(espacio):
								contadorelementos+=1
								print('')
								texto+=' '
								espacio = 0	
							texto+=abc[m]
							contadorelementos+=1
							print(abc[m])
							acumlo=0
							letra=''

					if(letra!=''):
						letra=''
					if(contadorelementos>0):
						self.lcdNumber.display(contadorelementos-1)
					self.label_3.setText(texto)

	#Graficar Canal digital 1
	def digi1 (self,state):
		
		if state == QtCore.Qt.Checked:
			print("Mostrar Canal Digital 1") #Hace visible la grafica -alpha1-
			self.varDig1.set_alpha(1)          
			
		else:
			print("Ocultar Canal Digital 1") #Hace transparente la grafica -alpha0-
			self.varDig1.set_alpha(0)

	#Graficar Canal digital 2
	def digi2 (self,state):
		
		if state == QtCore.Qt.Checked:
			print("Mostrar Canal Digital 2") #Hace visible la grafica -alpha1-
			self.varDig2.set_alpha(1)          
			
		else:
			print("Ocultar Canal Digital 2") ##Hace transparente la grafica -alpha0-
			self.varDig2.set_alpha(0)

	#Graficar Canal Analogico 1
	def ang1 (self,state):
		
		if state == QtCore.Qt.Checked:
			print("Mostrar Canal Analogico 1") #Hace visible la grafica -alpha1-
			self.varAn1.set_alpha(1)          
			
		else:
			print("Ocultar Canal Analogico 1") #Hace transparente la grafica -alpha0-
			self.varAn1.set_alpha(0)

	#Graficar Canal Analogico 2
	def ang2 (self,state):
		
		if state == QtCore.Qt.Checked:
			print("Mostrar Canal Analogico 2") #Hace visible la grafica -alpha1-
			self.varAn2.set_alpha(1)          
			
		else:
			print("Ocultar Canal Analogico 2") #Hace transparente la grafica -alpha0-
			self.varAn2.set_alpha(0)
		  


	def grid (self,state):
		if state == QtCore.Qt.Checked:
			print("Grid On") #Colocar Grid
			self.ax.grid()
		else:
			self.ax.grid(0)
			print("Grid Off") #Quitar Grid
	
	
	def changebasetime(self,text):
		if text == "10 ms":
			print("time = 10 ms") #Colocar cambio de escala
			self.ax.axes.set_xlim(0,0.01)
		elif text == "100 ms":
			print("time = 100 ms") #Colocar cambio de escala
			self.ax.axes.set_xlim(0,0.1)
		else:
			print("time = 1 s") #Colocar cambio de escala
			self.ax.axes.set_xlim(0,1)

	def changebasevolt(self,text):
		if text == "0.3 V":
			print("Volt= 0.3 V") #Colocar cambio de escala
			self.ax.axes.set_ylim(0,0.3)
		elif text == "1.0 V":
			print("Volt= 1.0 V") #Colocar cambio de escala
			self.ax.axes.set_ylim(0,1)
		else:
			print("Volt= 3.0 V") #Colocar cambio de escala
			self.ax.axes.set_ylim(0,3)

	def leer(self):
		cabec= ser.read()
		while (cabec > b'\x80'):
			cabec = ser.read(1)
		rest = ser.read(299)

		if rest[1]>=192:
			filt=1
			dataAn1 = [((ord(cabec) & 63)<<10)|((rest[0] & 63)<<4)|(rest[1] & 15)]
			dataDig1 = [(ord(cabec) &  0b01000000)]
			dataDig2 = []

			for x in range(99):
				if (rest[3*x+4]&64) != (rest[3*x+1]&64):
					(dataAn1,dataDig1,dataDig2,filt) =  self.leer()
					return (dataAn1,dataDig1,dataDig2,filt)
				dataAn1 += [(((rest[3*x+2] & 63)<<10)|((rest[3*x+3] & 63)<<4)|(rest[3*x+4] & 15))]
				dataDig1 += [(rest[3*x+2] &  0b01000000)]

			for x in range(100):
				dataDig2 += [(rest[3*x] &  0b01000000)]

		else:
			filt=0
			dataAn1 = [((ord(cabec) & 63)<<2)|((rest[0] & 3))]
			dataDig1 = [(ord(cabec) &  0b01000000)]
			dataDig2 = []

			for x in range(99):
				if (rest[3*x+4]&64) != (rest[3*x+1]&64):
					(dataAn1,dataDig1,dataDig2,filt) =  self.leer()
					return (dataAn1,dataDig1,dataDig2,filt)
				dataAn1 += [((rest[3*x+2] & 63)<<2)|((rest[3*x+3] & 3))]
				dataDig1 += [(rest[3*x+2] &  0b01000000)]

			for x in range(100):
				dataDig2 += [(rest[3*x] &  0b01000000)]

		return (dataAn1,dataDig1,dataDig2,filt)
	

#No tocar, requerimientos de Pyqt
if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	window = MyApp()
	window.show()
	sys.exit(app.exec_())        