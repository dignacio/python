import os
import operator

from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMessageBox

import os, json, requests, sys


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'mainWindow.ui'))

class CedulaMainWindow(QtWidgets.QMainWindow, FORM_CLASS):
    def __init__(self, cveCatas = "0", parent=None):
        """Constructor."""
        super(CedulaMainWindow, self).__init__(parent, \
            flags=Qt.WindowMinimizeButtonHint|Qt.WindowMaximizeButtonHint|Qt.WindowCloseButtonHint)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect


        self.cveCatastral = cveCatas

        self.servidorIP = 'http://127.0.0.1:8080/'
        self.urlPredio = self.servidorIP + 'busquedasimplewkn/api/cedula/predio/'
        self.urlConstr = self.servidorIP + 'featureswkn/api/construccion/getAllByCve/'
        self.urlCatalogos = self.servidorIP + 'configuracion/api/cat/getAllCatalogosEpredio'
        self.urlCatTipoAsentH = self.servidorIP + 'configuracion/api/cat-tipo-asentamiento-humanos'
        self.urlCatTipoUsoSuelo = self.servidorIP + 'configuracion/api/cat-tipo-uso-suelos'
        self.urlValorTerreno = self.servidorIP + 'configuracion/api/cat-valores-terrenos'
        self.urlCatUsoSueloByTipoUso = self.servidorIP + 'featureswkn/api/cat-tipo-uso-suelo/getCatUsoSueloByCve/'
        self.urlCatEdoConstr = self.servidorIP + 'configuracion/api/cat-estado-construccions'

        self.headers = {'Content-Type': 'application/json'}

        # -- variable para no preguntar al cerrar
        self.errorCerrar = False

        # -- informacion cargada
        self.cargada = False

        self.setupUi(self)

    def closeEvent(self,event):

        if self.errorCerrar:
            event.accept()
            self.errorCerrar = False
        else:
            reply = QMessageBox.question(self,'Message',"Are you sure to quit? - " + self.windowTitle(), QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()

    def showEvent(self, event):
        if self.cargada:
            return

        # -- Diseño
        self.leDispPerim.setMaxLength(10)
        self.leDescripcion.setMaxLength(60)
        self.leDispPerim.setValidator(QDoubleValidator(0.99,99.99,2))
        self.twColindancias.setColumnHidden(0, True)
        header = self.twColindancias.horizontalHeader()
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.leSupTerr.setValidator(QDoubleValidator(0.99,99.99,2))
        self.leFondo.setValidator(QDoubleValidator(0.99,99.99,2))
        self.leFrente.setValidator(QDoubleValidator(0.99,99.99,2))
        self.lbUsoPredioEtiqueta.hide()
        self.cmbUsoPredio.hide()

        # -- Eventos
        self.pushButton.clicked.connect(self.event_hasAlgo)
        self.btnColinAdd.clicked.connect(self.event_agregaColin)
        self.btnColinRemoveOne.clicked.connect(self.event_remueveColin)
        self.btnColinRemoveAll.clicked.connect(self.event_remTodasColin)
        self.cmbTipoUsoSuelo.currentIndexChanged.connect(self.event_obtenerUsoSuelo)
        self.cmbVolumenP.currentIndexChanged.connect(self.event_cambioVolPred)

        # -- Titulo
        self.setWindowTitle(self.descomponeCveCata(self.cveCatastral))

        # -- muestra clave
        self.lbCveCata.setText(self.descomponeCveCata(self.cveCatastral))
        self.muestraClaveGlobal(self.cveCatastral)

        # -- carga informacion en los catalogos
        dataCat = self.consumeWSCatalogosPredios(self.urlCatalogos)
        self.cargaCatalogos(dataCat)

        # -- carga informacion en los catalogos CONSTRUCCIONES
        #dataCat = self.consumeWSCatalogosConstrucciones(self.urlCatalogos)
        #self.cargaCatalogos(dataCat)

        # -- carga informacion de la cedula
        dataCed = self.consumeWSCedula(self.cveCatastral)
        self.cargaCedula(dataCed)

        # -- carga informacion de construcciones de PREDIO
        dataConstP = self.consumeWSConstr(self.cveCatastral)
        print('todo bien')
        self.cargaConstrPred(dataConstP)

        self.cargada = True

    # --- M E T O D O S ---

    # - carga la informacion de los catalogos
    def cargaCatalogos(self, dataCat):

        try:
            if len(dataCat) == 0:
                self.createAlert('Sin Resultados')
                return

            # UBICACION
            tipoPredio = dataCat['catTipoPredios']
            # --- SE LLENARA EN UN METODO A PARTE PORQUE NO SE INCLUYE EN LA LISTA DE CATALOGOS
            tipoAsentH = self.catalogoTipoAsentH() 
            orientacion = dataCat['catColindacias'] # --- CAT_ORIENTACION
            regimenProp = dataCat['catRegimenPropiedades']
            # TERRENO
            facilComun = dataCat['catFacilidadComunicacions']
            # --- SE LLENARA EN UN METODO A PARTE PORQUE NO SE INCLUYE EN LA LISTA DE CATALOGOS
            # --- C A M B I A R A   L A   I P   CUANDO SE AGREGUE A LOS MICROSERVICIOS
            # --- SE LLENARA EN UN METODO A PARTE PORQUE NO SE INCLUYE EN LA LISTA DE CATALOGOS
            tipoUsoSuelo = self.catalogoTipoUsoSuelo()
            # --- SE LLENARA EN UN METODO A PARTE PORQUE NO SE INCLUYE EN LA LISTA DE CATALOGOS
            valTerr = self.catalogoValorTerreno()
            # cmbUsoSuelo = dataCat['catTipoPredios'] --- SE VA A LLENAR A PARTIR DEL TIPO DE USO DE SUELO (cat_tipo_uso_suelo)
            usoPredio = dataCat['catUsoPredios']
            tipoRelieve = dataCat['catTipoRelieves']
            formaPredio = dataCat['catPredioFormas']
            orientPredMza = dataCat['catPredioUbicMznas']

            # -- tipo de predio
            if len(tipoPredio) > 1:
                self.cmbTipoPredio.addItem('', '-1')
                for tp in tipoPredio:
                    self.cmbTipoPredio.addItem(str(tp['descripcion']), str(tp['cveTipoPred']))

            # -- orientacion
            if len(orientacion) > 1:
                self.cmbOrientacion.addItem('', '-1')
                for ori in orientacion:
                    self.cmbOrientacion.addItem(str(ori['descripcion']), str(ori['id']))

            # -- regimen propiedad
            if len(regimenProp) > 1:
                self.cmbRegimenProp.addItem('', '-1')
                for reg in regimenProp:
                    self.cmbRegimenProp.addItem(str(reg['descripcion']), str(reg['id']))

            # -- facilidad de cominicacion
            if len(facilComun) > 1:
                self.cmbFacilComun.addItem('', '-1')
                for fac in facilComun:
                    self.cmbFacilComun.addItem(str(fac['descripcion']), str(fac['id']))

            # -- uso predio
            # -- SE DESHABILITA PORQUE NO SE VA A USAR
            '''
            if len(usoPredio) > 1:
                self.cmbUsoPredio.addItem('', '-1')
                for usop in usoPredio:
                    self.cmbUsoPredio.addItem(str(usop['descripcion']), str(usop['id']))
            '''

            # -- tipo relieve
            if len(tipoRelieve) > 1:
                self.cmbTipoRelieve.addItem('', '-1')
                for rel in tipoRelieve:
                    self.cmbTipoRelieve.addItem(str(rel['tipoRelieve']), str(rel['id']))

            # -- forma predio
            if len(formaPredio) > 1:
                self.cmbFormaPredio.addItem('', '-1')
                for form in formaPredio:
                    self.cmbFormaPredio.addItem(str(form['descripcion']), str(form['id']))

            # -- orientacion predio dentro de manzana
            if len(orientPredMza) > 1:
                self.cmbOrientPredMza.addItem('', '-1')
                for predm in orientPredMza:
                    self.cmbOrientPredMza.addItem(str(predm['descripcion']), str(predm['id']))

            # -- tipo de asentamiento humano
            if len(tipoAsentH) > 1:
                self.cmbTipoAsentH.addItem('', '-1')
                for tipa in tipoAsentH:
                    self.cmbTipoAsentH.addItem(str(tipa['descripcion']), str(tipa['id']))

            # -- tipo uso suelo
            if len(tipoUsoSuelo) > 1:
                self.cmbTipoUsoSuelo.addItem('', '-1')
                for tipa in tipoUsoSuelo:
                    self.cmbTipoUsoSuelo.addItem(str(tipa['descripcion']), str(tipa['cveTipoUsoSuelo']))

            # -- valor de terreno
            if len(valTerr) > 1:
                self.cmbValorTerr.addItem('', '-1')
                for vt in valTerr:
                    self.cmbValorTerr.addItem(str(vt['descripcion']), str(vt['cveVus']))

        except Exception as e:
            self.errorCerrar = True
            self.createAlert('Error durante la carga de informacion "cargaCatalogos()": ' + str(e))

    def catalogoTipoAsentH(self):
        return self.consumeWSCatalogosPredios(self.urlCatTipoAsentH)

    def catalogoTipoUsoSuelo(self):
        return self.consumeWSCatalogosPredios(self.urlCatTipoUsoSuelo)

    def catalogoValorTerreno(self):
        return self.consumeWSCatalogosPredios(self.urlValorTerreno)

    # - carga la informacion de las construcciones
    def cargaConstrPred(self, dataConstP):
        
        try:
            if len(dataConstP) == 0:
                self.createAlert('Sin Resultados')
                return

            # ordena las construcciones segun el volumen
            construcciones = self.ordenaConstr(dataConstP)

            for dcp in construcciones:
                fracciones = dcp['fracciones']
                fr = {}

                # - crear fraccion en caso de que no las tenga
                if len(fracciones) == 0:
                    fr['volumen'] = 1
                    fr['numNivel'] = dcp['numNiveles']
                    fr['supConstFraccion'] = dcp['supConst']
                    fr['idConstruccion'] = dcp['id']
                    fr['idPredio'] = dcp['idPredio']
                    fr['cveCatastral'] = dcp['cveCatastral']

                    fracciones.append(fr)
                    dcp['fracciones'] = fracciones

                self.cmbVolumenP.addItem(str(dcp['nomVolumen']), dcp)

        except Exception as e:
            self.errorCerrar = True
            self.createAlert('Error durante la carga de informacion "cargaConstrPred()": ' + str(e))

    # - carga la informacion de un predio en el formulario
    def cargaCedula(self, dataCed):

        try:

            if len(dataCed) == 0:
                self.createAlert('Sin Resultados')
                return

            cedula = dataCed[0]

            # -- UBICACION -- 
            self.lbNoExt.setText(cedula['numExt'])
            self.leNoExteriorAlf.setText(cedula['numExteriorAlf'])
            self.leNoExteAnt.setText(cedula['numExteriorAnt'])
            self.leNumPredio.setText(cedula['numPredio'])
            self.lbCodigoPostal.setText(cedula['cp'])
            self.lbColonia.setText(cedula['colonia'])
            self.lbCveCatAnt.setText(cedula['cveCatAnt'])

            # tipo de predio
            if cedula['cveTipoPred'] != None:
                index = self.cmbTipoPredio.findData(cedula['cveTipoPred'])
                if index >= 0:
                    self.cmbTipoPredio.setCurrentIndex(index)

            # asentamiento humano
            if cedula['idTipoAsentamiento'] != 0:
                index = self.cmbTipoAsentH.findData(cedula['idTipoAsentamiento'])
                if index >= 0:
                    self.cmbTipoAsentH.setCurrentIndex(index)
            
            # regimen de propiedad
            if cedula['idRegimenPropiedad'] != 0:
                index = self.cmbRegimenProp.findData(cedula['idRegimenPropiedad'])
                if index >= 0:
                    self.cmbRegimenProp.setCurrentIndex(index)

            # calle
            calles = cedula['calles']

            if len(calles) > 0:
                c = calles[0]
                self.lbNomCalle.setText(c['calle'])

            # colindancias
            colin = cedula['colindancias']

            if len(colin) > 0:
                for c in colin:
                    rowPosition = self.twColindancias.rowCount()
                    self.twColindancias.insertRow(rowPosition)
                    self.twColindancias.setItem(rowPosition , 0, QtWidgets.QTableWidgetItem(str(c['idCatColindancia'])))
                    self.twColindancias.setItem(rowPosition , 1, QtWidgets.QTableWidgetItem(str(c['catColindancia'])))
                    self.twColindancias.setItem(rowPosition , 2, QtWidgets.QTableWidgetItem(str(c['superficieColindacia'])))
                    self.twColindancias.setItem(rowPosition , 3, QtWidgets.QTableWidgetItem(str(c['desscripcion'])))

            # -- TERRENO --
            self.leSupTerr.setText(str(cedula['supTerr']))
            self.leFondo.setText(str(cedula['fondo']))
            self.leFrente.setText(str(cedula['frente']))

            # tipo uso de suelo
            if cedula['cveTipoUsoSuelo'] != None:
                index = self.cmbTipoUsoSuelo.findData(cedula['cveTipoUsoSuelo'])
                if index >= 0:
                    self.cmbTipoUsoSuelo.setCurrentIndex(index)

            # uso de predio
            # -- SE DESHABILITA PORQUE NO SE VA A USAR
            '''
            if cedula['idUsoPredio'] != 0:
                index = self.cmbUsoPredio.findData(cedula['idUsoPredio'])
                if index >= 0:
                    self.cmbUsoPredio.setCurrentIndex(index)
            '''

            # tipo relieve
            if cedula['idTipoRelieve'] != 0:
                index = self.cmbTipoRelieve.findData(cedula['idTipoRelieve'])
                if index >= 0:
                    self.cmbTipoRelieve.setCurrentIndex(index)

            # facilidad de comunicacion
            if cedula['idFacilidadComunicacion'] != 0:
                index = self.cmbFacilComun.findData(cedula['idFacilidadComunicacion'])
                if index >= 0:
                    self.cmbFacilComun.setCurrentIndex(index)

            # forma de predio
            if cedula['idPredioForma'] != 0:
                index = self.cmbFormaPredio.findData(cedula['idPredioForma'])
                if index >= 0:
                    self.cmbFormaPredio.setCurrentIndex(index)

            # orientacion
            if cedula['idPredioUbicacion_manzana'] != 0:
                index = self.cmbOrientPredMza.findData(cedula['idPredioUbicacion_manzana'])
                if index >= 0:
                    self.cmbOrientPredMza.setCurrentIndex(index)

            # valor de terreno
            if cedula['cveVus'] != None:
                index = self.cmbValorTerr.findData(cedula['cveVus'])
                if index >= 0:
                    self.cmbValorTerr.setCurrentIndex(index)

            '''
            self.cmbTipoPredio.clear()
            self.cmbTipoPredio.clear()
            self.cmbTipoPredio.clear()
            self.cmbTipoPredio.clear()
            self.cmbTipoPredio.clear()
            self.cmbTipoPredio.clear()
            '''
        except Exception as e:
            self.errorCerrar = True
            self.createAlert('Error durante la carga de informacion "cargaCedula()": ' + str(e))

    # - descomone clave
    def descomponeCveCata(self, cveCata):

        clave = cveCata[0:2] + '-'
        clave += cveCata[2:5] + '-'
        clave += cveCata[5:8] + '-'
        clave += cveCata[8:10] + '-'
        clave += cveCata[10:14] + '-'
        clave += cveCata[14:17] + '-'
        clave += cveCata[17:20] + '-'
        clave += cveCata[20:25]

        return clave

    # - muestra clave global
    def muestraClaveGlobal(self, cveCata):

        self.lbEdo.setText(cveCata[0:2])
        self.lbRegCat.setText(cveCata[2:5])
        self.lbMpio.setText(cveCata[5:8])
        self.lbSecc.setText(cveCata[8:10])
        self.lbLoc.setText(cveCata[10:14])
        self.lbSec.setText(cveCata[14:17])
        self.lbMza.setText(cveCata[17:20])
        self.lbPredio.setText(cveCata[20:25])

    # --- M E T O D O S   CIERRA ---

    # --- S E R V I C I O S   W E B ---

    # - consume ws para informacion de construcciones
    def consumeWSConstr(self, cveCatastral, tipoCta = 'P'):

        url = self.urlConstr + cveCatastral + '/' + tipoCta
        data = ""

        try:
            self.headers['Authorization'] = self.obtenerToken()
            response = requests.get(url, headers = self.headers)
        except requests.exceptions.RequestException as e:
            self.createAlert("Error de servidor 'consumeWSConstr()', '" + str(e) + "'")
            return

        if response.status_code == 200:
            data = response.content
        else:
            self.createAlert('Error en peticion "consumeWSConstr()":\n' + response.text)
            return

        return json.loads(data)

    # - consume ws para informacion de predios
    def consumeWSCedula(self, cveCatastral):

        url = self.urlPredio + cveCatastral
        data = ""

        try:
            self.headers['Authorization'] = self.obtenerToken()
            response = requests.get(url, headers = self.headers)
        except requests.exceptions.RequestException as e:
            self.createAlert("Error de servidor 'consumeWSCedula()', '" + str(e) + "'")
            return

        if response.status_code == 200:
            data = response.content
        else:
            self.createAlert('Error en peticion "consumeWSCedula()":\n' + response.text)
            return

        return json.loads(data)

    # - consume ws para informacion de catalogos
    def consumeWSCatalogosPredios(self, url_cons = ""):

        url = url_cons
        data = ""

        try:
            self.headers['Authorization'] = self.obtenerToken()
            response = requests.get(url, headers = self.headers)
        except requests.exceptions.RequestException as e:
            self.createAlert("Error de servidor, 'consumeWSCatalogosPredios()' '" + str(e) + "'", QMessageBox().Critical, "Error de servidor")
            return

        if response.status_code == 200:
            data = response.content
        else:
            self.createAlert('Error en peticion "consumeWSCatalogosPredios()":\n' + response.text, QMessageBox().Critical, "Error de servidor")
            return

        return json.loads(data)

    # --- S E R V I C I O S   W E B   CIERRA ---

    # --- E V E N T O S   Widget ---

    # -- metodo general que se puede usar para cualquier cosa
    # * cerrar la ventana
    def event_hasAlgo(self):
        self.errorCerrar = True
        self.close()
        # clave = "-";

        # for llave, valor in self.lista.items():
        #    if valor.isActiveWindow():
        #        clave = llave

        #self.createAlert('Clave: ' + self.cveCatastral, QMessageBox.Information, 'Cedula Catastral')
        #self.createAlert('Clave: ' + clave, QMessageBox.Information, 'Cedula Catastral')

    def event_obtenerUsoSuelo(self):

        if self.cmbTipoUsoSuelo.count() > 0:
            index = self.cmbTipoUsoSuelo.currentIndex()
            idTipoUS = self.cmbTipoUsoSuelo.itemData(index)

            self.cmbUsoSuelo.clear()

            data = self.consumeWSCatalogosPredios(self.urlCatUsoSueloByTipoUso + idTipoUS)
            if data == None:
                return

            lenJson = len(list(data))

            if lenJson > 0:
                for usos in data:
                    self.cmbUsoSuelo.addItem(str(usos['descripcion']), str(usos['cveUsoSuelo']))

    def event_cambioVolPred(self):

        if self.cmbTipoUsoSuelo.count() > 0:
            index = self.cmbVolumenP.currentIndex()
            data = self.cmbVolumenP.itemData(index)

            '''
            string = constr.replace("'", "\"")
            string = string.replace("None", "\"None\"")
            string = string.replace("False", "\"False\"")
            string = string.replace("True", "\"True\"")

            data = json.loads(string)
            '''

            self.lbSupConstrP.setText(str(data['supConst']))
            self.lbNumNivP.setText(str(data['numNiveles']))
            self.lbTipoConstP.setText(str(data['constTipo']))
            if data['cveConstEsp'] != None:
                self.lbCveConstEspP_2.show()
                self.lbCveConstEspP.show()
                self.lbCveConstEspP.setText(str(data['cveConstEsp']))
            else:
                self.lbCveConstEspP_2.hide()
                self.lbCveConstEspP.hide()

            # self.lbTipoConstP.setText(str(data['constTipo'])) --- no se carga por mientras hasta que se acomoden los ws

            # ---- CARGA DE FRACCIONES
            self.cmbFraccionesP.clear()
            fra = data['fracciones'][0]
            self.cmbFraccionesP.addItem(str(fra['volumen']), fra)
            


    def event_agregaColin(self):

        # obtiene el indice actual del combo, los valores de los campos
        index = self.cmbOrientacion.currentIndex()
        distanci = self.leDispPerim.text()
        descripc = self.leDescripcion.text()

        # validaciones
        if index == -1 or index == 0:
            self.createAlert('Seleccione una orientacion')
            return

        if len(distanci) == 0:
            self.createAlert('Defina una distancia')
            return

        if len(descripc) == 0:
            self.createAlert('Defina una descripcion')
            return

        # agrega un renglon a las coindancias
        idOrient = self.cmbOrientacion.itemData(index)
        orientac = self.cmbOrientacion.currentText()
        distanci = self.leDispPerim.text()
        descripc = self.leDescripcion.text()

        rowPosition = self.twColindancias.rowCount()
        self.twColindancias.insertRow(rowPosition)
        self.twColindancias.setItem(rowPosition , 0, QtWidgets.QTableWidgetItem(str(idOrient)))
        self.twColindancias.setItem(rowPosition , 1, QtWidgets.QTableWidgetItem(orientac))
        self.twColindancias.setItem(rowPosition , 2, QtWidgets.QTableWidgetItem(distanci))
        self.twColindancias.setItem(rowPosition , 3, QtWidgets.QTableWidgetItem(descripc))

        # regresa a valores por defecto
        self.cmbOrientacion.setCurrentIndex(0)
        self.leDispPerim.setText('')
        self.leDescripcion.setText('')
        
    def event_remueveColin(self):

        # obtiene los indices de todas los renglones seleccionados
        indices = self.twColindancias.selectionModel().selectedRows()

        if len(indices) == 0:
            self.createAlert('Seleccione una orientacion a eliminar (seleccione todo el renglon)')

        # elimina el renglon de la lista
        for index in indices:
            self.twColindancias.removeRow(index.row())

    def event_remTodasColin(self):
        self.twColindancias.clearContents()
        self.twColindancias.setRowCount(0)
            
        for row in range(0, self.twColindancias.rowCount()):        
            self.twColindancias.removeRow(row) 

    # --- CERRAR E V E N T O S   Widget ---

    # --- U T I L I D A D E S ---

    # - ordena las construcciones por volumen
    def ordenaConstr(self, dataConstP):

        temp = []
        result = []

        # obtiene los numeros de volumne (solo los numeros, ej. V1 - 1, V2 - 2, etc)
        for d in dataConstP:
            temp.append(int(d['nomVolumen'][1:]))

        # se ordenan de menor a mayor
        temp.sort()

        # recorre la lista ordenada (temp)
        # para buscar 'V' + el numero en la lista de construcciones
        # y asi conseguir las construcciones ordenadas
        for t in temp:
            for d in dataConstP:
                if d['nomVolumen'].upper() == 'V' + str(t):
                    result.append(d)

        return result

    # - Crea una alerta para ser mostrada como ventana de advertencia
    def createAlert(self, mensaje, icono = QMessageBox().Critical, titulo = 'Cedula'):
        #Create QMessageBox
        self.msg = QMessageBox()
        #Add message
        self.msg.setText(mensaje)
        #Add icon of critical error
        self.msg.setIcon(icono)
        #Add tittle
        self.msg.setWindowTitle(titulo)
        #Show of message dialog
        self.msg.show()
         # Run the dialog event loop
        result = self.msg.exec_()

    # - obtiene el token del servidor
    def obtenerToken(self):
        #return ""
        url= self.servidorIP + '/auth/login'
        payload = {"username" : "user", "password" : "user"}
        payload = json.dumps(payload)
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, headers = headers, data = payload)
        if response.status_code == 200: 
            data = response.content
        else:
            print('no se arma el token')

        return 'bearer ' + json.loads(data)['access_token']

    # --- U T I L I D A D E S   CERRAR ---
