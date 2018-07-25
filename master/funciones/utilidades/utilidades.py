
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
import os, json, requests
from osgeo import ogr, osr
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5.QtGui import *
from qgis.core import *
from qgis.utils import *

class Utilidad:

	def __init__(self):
		self.tablas = {'manzana': 'e_manzana', 'predios.geom': 'e_predio', 'construcciones': 'e_construccion',  'horizontales.geom':'e_condominio_horizontal', 'verticales':'e_condominio_vertical', 'cves_verticales':'e_condominio_vert_clave'}

		#pass
		

	#---------------------------------------------------------------------------------

	def mostrarAlerta(self, mensaje, icono, titulo):

		msg = QMessageBox()
		msg.setText(mensaje)
		msg.setIcon(icono)
		msg.setWindowTitle(titulo)
		msg.show()
		msg.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
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
			print(response)
			self.mostrarAlerta('No se ha conseguido token', QMessageBox().Critical, 'Autenticacion')
			return
		##print('no se arma el token')

		#print(json.loads(data)['access_token'])
		return 'bearer ' + json.loads(data.decode('utf-8'))['access_token']
	
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
    
	#---------------------------------------------------------------------------------

	def limpiarCanvas(self):
		grupoLayers =  QgsProject.instance().layerTreeRoot().findGroup('consulta')
		layers = grupoLayers.findLayers()
		for layer in layers:
			layer.layer().startEditing()
			for f in layer.layer().getFeatures():
				layer.layer().dataProvider().deleteFeatures([f.id()])
			layer.layer().triggerRepaint()
			layer.layer().commitChanges()

	#----------------------------------------------------------------------------------

	def guardarCambios(self):

		print('entro al guardar')

		
		root = QgsProject.instance().layerTreeRoot()

		group = root.findGroup('ERRORES DE TOPOLOGIA')
		if not group is None:
			for child in group.children():
				dump = child.dump()
				id = dump.split("=")[-1].strip()
				QgsProject.instance().removeMapLayer(id)
			root.removeChildNode(group)

		for layer in iface.mapCanvas().layers():
			layer.triggerRepaint()

		if QSettings().value('posibleGuardar') == 'True' or True:
			print('fue posible guardar')
			self.listaAGuardar = []

			self.agregarALista('manzana')
			self.agregarALista('predios.geom')
			self.agregarALista('construcciones')
			self.agregarALista('horizontales.geom')
			self.agregarALista('verticales')
			self.agregarALista('cves_verticales')
			self.agregarAListaEliminados()

			
			#Formato para solicitar la peticion
			jsonParaGuardarAtributos = json.dumps(self.listaAGuardar)

			print (jsonParaGuardarAtributos)
			
			#try:
			
			url = self.CFG.urlGuardadoCon
			payload = jsonParaGuardarAtributos
			headers = {'Content-Type': 'application/json', 'Authorization' : self.obtenerToken()}
			try:
				response = requests.post(url, headers = headers, data = payload)
			
			except requests.exceptions.RequestException:
				self.mostrarAlerta("No se ha podido conectar al servidor v1", QMessageBox.Critical, "Guardar Cambios v1")#Error en la peticion de consulta
				

			print(response.json())
			print(response.status_code)
			if response.status_code == 200:
				self.mostrarAlerta("Cambios guardados con exito", QMessageBox.Information, "Guardar Cambios")
				QSettings().setValue('listaEliminada', [])
				#Guardado de datos correcto
			elif response.status_code == 202:

				root.insertGroup(0, 'ERRORES DE TOPOLOGIA')

				capa = QgsVectorLayer('Point?crs=epsg:' + str(QSettings().value('srid')) +'&field=mensaje:string(80)', 'ERRORES PUNTO', 'memory')

				QgsProject.instance().addMapLayers([capa], False)

				props = capa.renderer().symbol().symbolLayer(0).properties()
				props['color'] = '#FF0000'
				capa.renderer().setSymbol(QgsMarkerSymbol.createSimple(props))

				self.etiquetarCapa(capa.name())

				QgsProject.instance().addMapLayer(capa, False)
				grupoErrores = root.findGroup('ERRORES DE TOPOLOGIA')
				capaError = QgsLayerTreeLayer(capa)
				capa.startEditing()

				puntosMalos = response.json()
				#print (type(puntosMalos))

				for malo in puntosMalos:
					
					#print(malo)
					#print(type(malo))
					geom = QgsGeometry.fromWkt(malo["wkt"])
					feat = QgsFeature()
					feat.setGeometry(geom)
					feat.setAttributes([malo['mensaje']])
					capa.dataProvider().addFeatures([feat])
					capa.updateFeature(feat)

				capa.triggerRepaint()
				capa.commitChanges()
				grupoErrores.insertChildNode(0, capaError)

			else:
				self.mostrarAlerta("No se ha podido conectar al servidor v2\n" + str(response.json()[0]['mensaje']), QMessageBox.Critical, "Guardar Cambios v2")
				#Error al guardar datos
			
			#except ValueError:
				#self.mostrarAlerta("No se ha podido conectar al servidor v3", QMessageBox.Critical, "Guardar Cambios v3")
			
		else:
			self.mostrarAlerta("Se debe validar la topologia antes de guardar", QMessageBox.Critical, "Guardar Cambios v4")
		

		QSettings().setValue('posibleGuardar', 'False')

	#-------------------------------------------------------------------------------------------------------------

	def agregarALista(self, idCapa):

		capa = QgsProject.instance().mapLayer( self.ACA.obtenerIdCapa( idCapa))
		listaTemp = []

		for feat in capa.getFeatures():
			campos = {}
			campos['wkt'] = feat.geometry().asWkt()
			campos['srid'] = QSettings().value('srid')
			campos['tabla'] = self.tablas[capa.name()]
			atributos = {}
			nombresAtrbutos = capa.fields()   

			nombres = [campo.name() for campo in nombresAtrbutos]

			for x in range(0, len(nombres)):
				atributo = feat.attributes()[x]
				if str(feat.attributes()[x]) == "NULL":
					atributo = None
				atributos[str(nombres[x])] = atributo
				
				if capa.id() == self.ACA.obtenerIdCapa('predios.geom'):
					punto = self.exteriorPredio(feat.geometry())
					if punto != None:
						atributos['numExt'] = punto['numExt']
						atributos['geom_num'] = punto.geometry().asWkt()

				elif capa.id() == self.ACA.obtenerIdCapa('horizontales.geom'):
					punto = self.exteriorCondom(feat.geometry())
					if punto != None:
						atributos['num_ofi'] = punto['num_ofi']
						atributos['geom_num'] = punto.geometry().asWkt()
					
			campos['attr'] = atributos
			if campos['attr']['id'] == None or campos['attr']['id'] == '':
				campos['nuevo'] = True
				campos['eliminado'] = False
			else:
				campos['nuevo'] = False
				campos['eliminado'] = False
			self.listaAGuardar.append(campos)

	############################################################################################

	def agregarAListaEliminados(self):

		listaTemp = QSettings().value('listaEliminada')

		if listaTemp == None:
			return

		for elemento in listaTemp:
			self.listaAGuardar.append(elemento)

	#####################################################################################################################

	def exteriorPredio(self, predio):

		puntos = QgsProject.instance().mapLayer(self.ACA.obtenerIdCapa('predios.num')).getFeatures()

		for punto in puntos:
			if punto.geometry().intersects(predio):
				return punto

	def exteriorCondom(self, condominio):

		puntos = QgsProject.instance().mapLayer(self.ACA.obtenerIdCapa('horizontales.num')).getFeatures()

		for punto in puntos:
			if punto.geometry().intersects(condominio):
				return punto

	####################################################################################################################

	def extenderCombo(self, combo, signal, modelo):

		combo.setFocusPolicy( Qt.StrongFocus )
		combo.setEditable( True )
		combo.completer = QCompleter(combo )

		# always show all completions
		combo.completer.setCompletionMode( QCompleter.UnfilteredPopupCompletion )
		combo.pFilterModel = QSortFilterProxyModel( combo)
		combo.pFilterModel.setFilterCaseSensitivity( Qt.CaseInsensitive )
		combo.completer.setPopup( combo.completer.popup() )
		combo.setCompleter( combo.completer )
		combo.lineEdit().textEdited.connect( combo.pFilterModel.setFilterFixedString )
		combo.completer.activated.connect(signal)

		combo.setModel( modelo )
		combo.pFilterModel.setSourceModel( modelo )
		combo.completer.setModel(combo.pFilterModel)
		combo.completer.setCompletionColumn( 0 )
		combo.pFilterModel.setFilterKeyColumn( 0 )
		combo.setModelColumn( 0 )

	################################################################################################################
	def strechtTabla(self, tabla):
		header = tabla.horizontalHeader()

		for x in range(0, tabla.columnCount()):
			header.setSectionResizeMode(x, QtWidgets.QHeaderView.Stretch)
			header.setStretchLastSection(True)