from PyQt5.QtWidgets import QAction, QMessageBox
import os, json, requests
from osgeo import ogr, osr



class Utilidad:

	def __init__(self, CFG):
		self.CFG = CFG

	#---------------------------------------------------------------------------------

	def mostrarAlerta(self, mensaje, icono, titulo):

		msg = QMessageBox()
		msg.setText(mensaje)
		msg.setIcon(icono)
		msg.setWindowTitle(titulo)
		msg.show()
		result = msg.exec_()

	#------------------------------------------------------------------------------------------------

	def obtenerToken(self):

		url = self.CFG.urlAutenticacion
		payload = {"username" : "user", "password" : "user"}
		payload = json.dumps(payload)
		headers = {'Content-Type': 'application/json'}

		response = requests.post(url, headers = headers, data = payload)
		if response.status_code == 200:
			#print('habemus token')
			data = response.content
		else:
			self.createAlert('Error de autenticacion', QMessageBox().Critical, 'Autenticacion')
			return
		##print('no se arma el token')

		#print(json.loads(data)['access_token'])
		return 'bearer ' + json.loads(data)['access_token']
	
	#-----------------------------------------------------------------------------------------------------

	def esEntero(self, num): #Funcion para checar si una variable es un entero numerico
		try: 
			int(num)
			return True
		except ValueError:
			return False

	#--------------------------------------------------------------------------------

	def esFloat(self, num): #Funcion para checar si una variable es un entero numerico
		try: 
			float(num)
			return True
		except ValueError:
			return False
    
