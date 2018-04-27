import os
import operator

from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMessageBox, QListView

from qgis.utils import iface
from qgis.core import QgsProject

import os, json, requests, sys

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'mainWindow.ui'))

class CedulaMainWindow(QtWidgets.QMainWindow, FORM_CLASS):
    def __init__(self, cveCatas = "0", cond = False, parent=None):
        """Constructor."""
        super(CedulaMainWindow, self).__init__(parent, \
            flags=Qt.WindowMinimizeButtonHint|Qt.WindowMaximizeButtonHint|Qt.WindowCloseButtonHint)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        # clave catastral global
        self.cveCatastral = cveCatas[0:25]

        self.cveCondSel = ''
        if len(cveCatas) > 25:
            self.cveCondSel = cveCatas[25:]

        # es condominio
        self.cond = cond

        # -- canvas --
        self.canvas = iface.mapCanvas()

        # Save reference to the QGIS interface
        self.iface = iface

        self.servidorIP = 'http://127.0.0.1:8080/'
        self.urlPredio = self.servidorIP + 'busquedasimplewkn/api/cedula/predio/'
        self.urlConstr = self.servidorIP + 'featureswkn/api/construccion/getAllByCve/'
        self.urlCatalogos = self.servidorIP + 'configuracion/api/cat/getAllCatalogosEpredio'
        self.urlCatTipoAsentH = self.servidorIP + 'configuracion/api/cat-tipo-asentamiento-humanos?page=0&size=200'
        self.urlCatTipoUsoSuelo = self.servidorIP + 'configuracion/api/cat-tipo-uso-suelos?page=0&size=200'
        self.urlValorTerreno = self.servidorIP + 'configuracion/api/cat-valores-terrenos?page=0&size=200'
        self.urlCatUsoSueloByTipoUso = self.servidorIP + 'featureswkn/api/cat-tipo-uso-suelo/getCatUsoSueloByCve/'
        self.urlUsoConstr = self.servidorIP + 'configuracion/api/cat-uso-construccions?page=0&size=200'
        self.urlDestino = self.servidorIP + 'configuracion/api/cat-destinos?page=0&size=200'
        self.urlEdoConstr = self.servidorIP + 'configuracion/api/cat-estado-construccions?page=0&size=200'
        self.urlCatFactorByTipoFactor = self.servidorIP + 'featureswkn/api/cat-factor/getAllFactorByIdTipoFactor/'
        self.urlCategoriasByIdUsoConst = self.servidorIP + 'featureswkn/api/cat-vuc/getCategoriasByIdConstruccion/'
        self.urlUsoEspecifByIdUsoConst = self.servidorIP + 'featureswkn/api/cat-uso-especifico/getCatUsoEspecificoByIdUsoConstruccion/'
        self.urlRCaracCategoria = self.servidorIP + 'featureswkn/api/cat-vuc/getRCaractCara/'
        self.urlCondominios = self.servidorIP + 'busquedasimplewkn/api/cedula/combo/condo/'
        self.urlCondByCveCatTipoPred = self.servidorIP + 'featureswkn/api/condominios/getByCveCatAndType/'
        self.urlServiciosCalle = self.servidorIP + 'busquedasimplewkn/api/cat-servicio/calle/'
        self.urlServiciosCuenta = self.servidorIP + 'busquedasimplewkn/api/cat-servicio/cuenta/'

        self.headers = {'Content-Type': 'application/json'}

        # -- variable para no preguntar al cerrar
        self.errorCerrar = False

        # -- informacion cargada
        self.cargada = False

        # -- diseño del cursor --
        self.cursorRedondo = QCursor(QPixmap(["16 16 3 1",
                                "      c None",
                                ".     c #FF0000",
                                "+     c #FFFFFF",
                                "                ",
                                "       +.+      ",
                                "      ++.++     ",
                                "     +.....+    ",
                                "    +.     .+   ",
                                "   +.   .   .+  ",
                                "  +.    .    .+ ",
                                " ++.    .    .++",
                                " ... ...+... ...",
                                " ++.    .    .++",
                                "  +.    .    .+ ",
                                "   +.   .   .+  ",
                                "   ++.     .+   ",
                                "    ++.....+    ",
                                "      ++.++     ",
                                "       +.+      "]))

        self.calle = None
        self.eventoCalleActivo = False
        self.indexVolActual = -1
        self.indexFraActual = -1
        self.indexVolActualCondo = -1
        self.indexFraActualCondo = -1

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
        self.twCaracteristicasP.setColumnHidden(0, True)
        self.twCaracteristicasP.setColumnHidden(2, True)
        self.twCaracteristicasP.setColumnHidden(4, True)
        header = self.twCaracteristicasP.horizontalHeader()
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)

        header = self.twVialidades.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

        header = self.twServiciosCalle.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.twServiciosCalle.setColumnHidden(1, True)

        header = self.twServiciosPredio.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.twServiciosPredio.setColumnHidden(1, True)

        header = self.twServiciosCondo.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.twServiciosCondo.setColumnHidden(1, True)
        
        # Diseño - construcciones predios
        self.cmbTipoPredio.setView(self.generaQListView())
        self.cmbTipoAsentH.setView(self.generaQListView())
        self.cmbRegimenProp.setView(self.generaQListView())
        self.cmbOrientacion.setView(self.generaQListView())
        self.cmbTipoUsoSuelo.setView(self.generaQListView())
        self.cmbUsoSuelo.setView(self.generaQListView())
        self.cmbTipoRelieve.setView(self.generaQListView())
        self.cmbFacilComun.setView(self.generaQListView())
        self.cmbValorTerr.setView(self.generaQListView())
        self.cmbFormaPredio.setView(self.generaQListView())
        self.cmbOrientPredMza.setView(self.generaQListView())
        self.cmbUsoConstrP.setView(self.generaQListView())
        self.cmbCondo.setView(self.generaQListView())
        self.cmbUsoEspP.setView(self.generaQListView())
        self.cmbDestinoP.setView(self.generaQListView())
        self.cmbEdoConstrP.setView(self.generaQListView())
        self.cmbCategoriaP.setView(self.generaQListView())
        self.cmbFactorConstrP.setView(self.generaQListView())

        # -- Eventos
        self.pushButton.clicked.connect(self.event_hasAlgo)
        self.btnColinAdd.clicked.connect(self.event_agregaColin)
        self.btnColinRemoveOne.clicked.connect(self.event_remueveColin)
        self.btnColinRemoveAll.clicked.connect(self.event_remTodasColin)
        self.cmbTipoUsoSuelo.currentIndexChanged.connect(self.event_CambioTipoUsoSuelo)
        self.cmbCondo.currentIndexChanged.connect(self.event_cambioCondominio)

        self.btnSelCalle.clicked.connect(self.consultarCalle)
        self.btnCancelSelCalle.clicked.connect(self.cancelarCalle)

        # Eventos - construcciones poredios
        self.cmbVolumenP.currentIndexChanged.connect(self.event_cambioVolPred)
        self.cmbFraccionesP.currentIndexChanged.connect(self.event_cambioFraccPred)
        self.cmbUsoConstrP.currentIndexChanged.connect(self.event_cambioUsoConstr)
        self.cmbCategoriaP.currentIndexChanged.connect(self.event_cambioCategoria)

        # -- Titulo
        self.setWindowTitle(self.descomponeCveCata(self.cveCatastral))

        # -- muestra clave
        self.lbCveCata.setText(self.descomponeCveCata(self.cveCatastral))
        self.muestraClaveGlobal(self.cveCatastral)

        # -- carga informacion en los catalogos
        dataCat = self.consumeWSGeneral(self.urlCatalogos)
        self.cargaCatalogos(dataCat)

        # -- carga informacion en los catalogos CONSTRUCCIONES
        self.cargaCatalogosConstruccionesP(self.cond)

        # -- carga informacion de la cedula segun la clave global
        dataCed = self.consumeWSCedula(self.cveCatastral[0:25])
        self.cargaCedula(dataCed)

        if self.cond: # C O N D O M I N I O S

            self.lbPredioGlobal.hide()

            # diseño de combos
            self.disenioCombosCondos()

            # eventos controles constucciones
            self.eventosConstruccionesCondo()

            # se carga el combo de condominios
            dataCond = self.consumeWSGeneral(self.urlCondominios + self.cveCatastral)
            self.defineComboCond(dataCond)

            # se selecciona el condominio abierto
            if len(self.cveCondSel) > 0:
                index = self.cmbCondo.findText(self.cveCondSel, QtCore.Qt.MatchFixedString)
                if index >= 0:
                    self.cmbCondo.setCurrentIndex(index)
        
        else: # P R E D I O S

            # ocultar condominios
            self.lbPredioGlobal.show()
            self.lbTipoCond.hide()
            self.cmbCondo.hide()

            # quita las tab que corresponden a condominios
            self.tabwCedula.removeTab(3)
            self.tabwCedula.removeTab(3)
            
        # muestra siempre la primer tab
        self.tabwCedula.setCurrentIndex(4)
        self.tabwCedula.setCurrentIndex(0)

        # -- carga informacion de construcciones de PREDIO
        dataConstP = self.consumeWSConstr(self.cveCatastral)

        self.cargaConstrPred(dataConstP)

        self.cargada = True

    # --- M E T O D O S ---

    # -- metodo boton de abrir cedula --
    def consultarCalle(self):

        # se obtienen las capas con el nombre 'Calle'
        capa = QgsProject.instance().mapLayersByName('Calles')

        # si existe ('capa' es una lista de capas llamadas 'Calles')
        # se asocia evento de seleccion con el cursor
        # y se define activo el evento (self.eventoCalleActivo)
        if len(capa) > 0:
            self.calle = capa[0]
            self.calle.selectionChanged.connect(self.event_seleccionaCalle)
            self.eventoCalleActivo = True
        else:
            self.createAlert('No existe la capa "Calles", cargue la capa para seleccionar una calle', icono = QMessageBox().Information, titulo = 'Calles')
            return

        self.iface.actionSelect().trigger()
        self.canvas.setCursor(self.cursorRedondo)
        self.btnSelCalle.setEnabled(False)
        self.abrePredio = True

    # -- metodo boton de cancelar apertura de cedula --
    def cancelarCalle(self):

        if self.calle != None:
            if self.eventoCalleActivo:
                self.calle.selectionChanged.disconnect()
                self.eventoCalleActivo = False

        self.iface.actionSelect().trigger()
        self.btnSelCalle.setEnabled(True)
        self.abrePredio = False

    def disenioCombosCondos(self):
        self.cmbUsoConstrC.setView(self.generaQListView())
        self.cmbUsoEspC.setView(self.generaQListView())
        self.cmbDestinoC.setView(self.generaQListView())
        self.cmbEdoConstrC.setView(self.generaQListView())
        self.cmbCategoriaC.setView(self.generaQListView())
        self.cmbFactorConstrC.setView(self.generaQListView())

    def eventosConstruccionesCondo(self):
        self.cmbVolumenC.currentIndexChanged.connect(self.event_cambioVolCondo)
        self.cmbFraccionesC.currentIndexChanged.connect(self.event_cambioFraccCondo)
        self.cmbUsoConstrC.currentIndexChanged.connect(self.event_cambioUsoConstrCondo)
        self.cmbCategoriaC.currentIndexChanged.connect(self.event_cambioCategoriaCondo)

    def generaQListView(self):
        view = QListView()
        view.setWordWrap(True)
        return view

    # - carga el combo de condominios
    def defineComboCond(self, dataCond):

        for dc in dataCond:

            clave = dc['label'][25:]
            self.cmbCondo.addItem(clave, dc['other'])

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
            tipoUsoSuelo = self.catalogoTipoUsoSuelo()
            # --- SE LLENARA EN UN METODO A PARTE PORQUE NO SE INCLUYE EN LA LISTA DE CATALOGOS
            valTerr = self.catalogoValorTerreno()
            # cmbUsoSuelo = dataCat['catTipoPredios'] --- SE VA A LLENAR A PARTIR DEL TIPO DE USO DE SUELO (cat_tipo_uso_suelo)
            usoPredio = dataCat['catUsoPredios']
            tipoRelieve = dataCat['catTipoRelieves']
            formaPredio = dataCat['catPredioFormas']
            orientPredMza = dataCat['catPredioUbicMznas']

            # -- tipo de predio
            if len(tipoPredio) > 0:
                self.cmbTipoPredio.addItem('', -1)
                for tp in tipoPredio:
                    self.cmbTipoPredio.addItem(str(tp['descripcion']), str(tp['cveTipoPred']))

            # -- orientacion
            if len(orientacion) > 0:
                self.cmbOrientacion.addItem('', -1)
                for ori in orientacion:
                    self.cmbOrientacion.addItem(str(ori['descripcion']), str(ori['id']))

            # -- regimen propiedad
            if len(regimenProp) > 0:
                self.cmbRegimenProp.addItem('', -1)
                for reg in regimenProp:
                    self.cmbRegimenProp.addItem(str(reg['descripcion']), str(reg['id']))

            # -- facilidad de cominicacion
            if len(facilComun) > 0:
                self.cmbFacilComun.addItem('', -1)
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
            if len(tipoRelieve) > 0:
                self.cmbTipoRelieve.addItem('', -1)
                for rel in tipoRelieve:
                    self.cmbTipoRelieve.addItem(str(rel['tipoRelieve']), str(rel['id']))

            # -- forma predio
            if len(formaPredio) > 0:
                self.cmbFormaPredio.addItem('', -1)
                for form in formaPredio:
                    self.cmbFormaPredio.addItem(str(form['descripcion']), str(form['id']))

            # -- orientacion predio dentro de manzana
            if len(orientPredMza) > 0:
                self.cmbOrientPredMza.addItem('', -1)
                for predm in orientPredMza:
                    self.cmbOrientPredMza.addItem(str(predm['descripcion']), str(predm['id']))

            # -- tipo de asentamiento humano
            if len(tipoAsentH) > 0:
                self.cmbTipoAsentH.addItem('', -1)
                for tipa in tipoAsentH:
                    self.cmbTipoAsentH.addItem(str(tipa['descripcion']), str(tipa['id']))

            # -- tipo uso suelo
            if len(tipoUsoSuelo) > 0:
                self.cmbTipoUsoSuelo.addItem('', -1)
                for tipa in tipoUsoSuelo:
                    self.cmbTipoUsoSuelo.addItem(str(tipa['descripcion']), str(tipa['cveTipoUsoSuelo']))

            # -- valor de terreno
            if len(valTerr) > 0:
                self.cmbValorTerr.addItem('', -1)
                for vt in valTerr:
                    self.cmbValorTerr.addItem(str(vt['descripcion']), str(vt['cveVus']))

        except Exception as e:
            self.errorCerrar = True
            self.createAlert('Error durante la carga de informacion "cargaCatalogos()": ' + str(e))

    def catalogoTipoAsentH(self):
        return self.consumeWSGeneral(self.urlCatTipoAsentH)

    def catalogoTipoUsoSuelo(self):
        return self.consumeWSGeneral(self.urlCatTipoUsoSuelo)

    def catalogoValorTerreno(self):
        return self.consumeWSGeneral(self.urlValorTerreno)

    def catalogoUsoConstr(self):
        return self.consumeWSGeneral(self.urlUsoConstr)

    def catalogoDestino(self):
        return self.consumeWSGeneral(self.urlDestino)

    def catalogoEdoConstr(self):
        return self.consumeWSGeneral(self.urlEdoConstr)

    def catalogoFactorByTipoFactor(self):
        return self.consumeWSGeneral(self.urlCatFactorByTipoFactor + '5')

    def consultaCaracter(self, idUsoConst, idCate):
        return self.consumeWSGeneral(self.urlRCaracCategoria + idUsoConst + '/' + idCate)

    def obtieneServiciosCalle(self, idCalle):
        return self.consumeWSGeneral(self.urlServiciosCalle + str(idCalle))

    def obtieneServiciosCuenta(self, cuenta):
        return self.consumeWSGeneral(self.urlServiciosCuenta + cuenta)

    # - carga la informacion de las construcciones
    def cargaConstrPred(self, dataConstP):
        
        try:
            if len(dataConstP) == 0:
                self.createAlert('Sin Resultados', titulo = 'cargaConstrPred')
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
                    fr['codigoConstruccion'] = ''
                    fr['valorConst'] = 0
                    fr['precioM2'] = 0
                    fr['idCatUsoConstruccion'] = -1
                    fr['idCatUsoEspecifico'] = -1
                    fr['idCatDestino'] = -1
                    fr['nombre'] = ''
                    fr['nvlUbica'] = ''
                    fr['anioConstruccion'] = ''
                    fr['idCatEstadoConstruccion'] = -1
                    fr['idCategoria'] = -1
                    fr['idFactor'] = -1
                    fr['caracCategorias'] = []

                    fracciones.append(fr)
                    dcp['fracciones'] = fracciones

                self.cmbVolumenP.addItem(str(dcp['nomVolumen']), dcp)

        except Exception as e:
            self.errorCerrar = True
            self.createAlert('Error durante la carga de informacion "cargaConstrPred()": ' + str(e))

    # - carga la informacion de las construcciones condominios
    def cargaConstrCondo(self, dataConstC):
        
        try:
            if len(dataConstC) == 0:
                self.createAlert('Sin Resultados', titulo = 'cargaConstrCondo')
                return

            self.cmbVolumenC.clear()

            # ordena las construcciones segun el volumen
            construcciones = self.ordenaConstr(dataConstC)

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
                    fr['codigoConstruccion'] = ''
                    fr['valorConst'] = 0
                    fr['precioM2'] = 0
                    fr['idCatUsoConstruccion'] = -1
                    fr['idCatUsoEspecifico'] = -1
                    fr['idCatDestino'] = -1
                    fr['nombre'] = ''
                    fr['nvlUbica'] = ''
                    fr['anioConstruccion'] = ''
                    fr['idCatEstadoConstruccion'] = -1
                    fr['idCategoria'] = -1
                    fr['idFactor'] = -1
                    fr['caracCategorias'] = []

                    fracciones.append(fr)
                    dcp['fracciones'] = fracciones

                self.cmbVolumenC.addItem(str(dcp['nomVolumen']), dcp)

        except Exception as e:
            self.errorCerrar = True
            self.createAlert('Error durante la carga de informacion "cargaConstrCondo()": ' + str(e))

    # - carga catalogos de construcciones
    def cargaCatalogosConstruccionesP(self, condo = False):
        
        # --- SE LLENARA EN UN METODO A PARTE PORQUE NO SE INCLUYE EN LA LISTA DE CATALOGOS
        usoConstr = self.catalogoUsoConstr()
        # --- SE LLENARA EN UN METODO A PARTE PORQUE NO SE INCLUYE EN LA LISTA DE CATALOGOS
        destino = self.catalogoDestino()
        # --- SE LLENARA EN UN METODO A PARTE PORQUE NO SE INCLUYE EN LA LISTA DE CATALOGOS
        edoConstr = self.catalogoEdoConstr()
        # --- SE LLENARA EN UN METODO A PARTE PORQUE NO SE INCLUYE EN LA LISTA DE CATALOGOS
        factor = self.catalogoFactorByTipoFactor()
        
        # -- uso construccion
        if len(usoConstr) > 0:
            self.cmbUsoConstrP.addItem('', -1)
            for uc in usoConstr:
                self.cmbUsoConstrP.addItem(str(uc['descripcion']), str(uc['id']))

            if condo:
                self.cmbUsoConstrC.addItem('', -1)
                for uc in usoConstr:
                    self.cmbUsoConstrC.addItem(str(uc['descripcion']), str(uc['id']))

        # -- destino
        if len(destino) > 0:
            self.cmbDestinoP.addItem('', -1)
            for d in destino:
                self.cmbDestinoP.addItem(str(d['descripcion']), str(d['id']))

            if condo:
                self.cmbDestinoC.addItem('', -1)
                for d in destino:
                    self.cmbDestinoC.addItem(str(d['descripcion']), str(d['id']))

        # -- estado de construccion
        if len(edoConstr) > 0:
            self.cmbEdoConstrP.addItem('', -1)
            for ec in edoConstr:
                self.cmbEdoConstrP.addItem(str(ec['descripcion']), str(ec['id']))

            if condo:
                self.cmbEdoConstrC.addItem('', -1)
                for ec in edoConstr:
                    self.cmbEdoConstrC.addItem(str(ec['descripcion']), str(ec['id']))

        # -- factor
        if len(factor) > 0:
            self.cmbFactorConstrP.addItem('', -1)
            for ec in factor:
                self.cmbFactorConstrP.addItem(str(ec['descripcion']), str(ec['id']))

            if condo:
                self.cmbFactorConstrC.addItem('', -1)
                for ec in factor:
                    self.cmbFactorConstrC.addItem(str(ec['descripcion']), str(ec['id']))

    # - carga la informacion de un predio en el formulario
    def cargaCedula(self, dataCed):

        try:

            if len(dataCed) == 0:
                self.createAlert('Sin Resultados', titulo = 'cargaCedula')
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
            idCalle = 0

            if len(calles) > 0:
                c = calles[0]
                self.lbNomCalle.setText(c['calle'])
                idCalle = c['id']
                self.idCalleSelecc = idCalle

            # vialidades colindantes
            vialidades = cedula['vialidadesColin']

            if len(vialidades) > 0:

                for c in vialidades:
                    rowPosition = self.twVialidades.rowCount()
                    self.twVialidades.insertRow(rowPosition)
                    self.twVialidades.setItem(rowPosition , 0, QtWidgets.QTableWidgetItem(str(c['tipovialidad'])))
                    self.twVialidades.setItem(rowPosition , 1, QtWidgets.QTableWidgetItem(str(c['calle'])))

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

            # cargar servicios de calles
            if idCalle != 0:
                dataServCalle = self.obtieneServiciosCalle(idCalle)

                for dsc in dataServCalle:

                    rowPosition = self.twServiciosCalle.rowCount()
                    self.twServiciosCalle.insertRow(rowPosition)

                    check = QtWidgets.QTableWidgetItem(dsc['descripcion'])
                    check.setFlags(QtCore.Qt.ItemIsEnabled)

                    if dsc['disponible'] == False:
                        check.setCheckState(QtCore.Qt.Unchecked)
                    else:
                        check.setCheckState(QtCore.Qt.Checked)
                    self.twServiciosCalle.setItem(rowPosition, 0, check)

                    self.twServiciosCalle.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(dsc['servicio']))

            # cargar servicios de predio
            dataServCuenta = self.obtieneServiciosCuenta(self.cveCatastral)

            for dsc in dataServCuenta:

                rowPosition = self.twServiciosPredio.rowCount()
                self.twServiciosPredio.insertRow(rowPosition)

                check = QtWidgets.QTableWidgetItem(dsc['descripcion'])
                check.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)

                if dsc['disponible'] == False:
                    check.setCheckState(QtCore.Qt.Unchecked)
                else:
                    check.setCheckState(QtCore.Qt.Checked)
                self.twServiciosPredio.setItem(rowPosition, 0, check)

                self.twServiciosPredio.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(dsc['servicio']))


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

    # - guarda de manera temporal los valores de construcciones
    def constrTemp(self):

        self.fraccTemp()
        dataTemp = self.cmbVolumenP.itemData(self.indexVolActual)

        fracciones = []

        count = self.cmbFraccionesP.count()

        for index in range(0, count):
            fracciones.append(self.cmbFraccionesP.itemData(index))

        dataTemp['fracciones'] = fracciones

        self.cmbVolumenP.setItemData(self.indexVolActual, dataTemp)

    # - guarda de manera temporal los valores de las fracciones
    def fraccTemp(self):

        dataTemp = self.cmbFraccionesP.itemData(self.indexFraActual)

        if dataTemp == None:
            # self.createAlert('fraccion nula: ' + str(dataTemp))
            return

        dataTemp['codigoConstruccion'] = self.lbCveUsoP.text()
        dataTemp['precioM2'] = self.lbValM2P.text()
        dataTemp['valorConst'] = self.lbValConstP.text()
        dataTemp['supConstFraccion'] = self.lbSupConstrFP.text()
        dataTemp['numNivel'] = self.lbNvlFraccP.text()
        dataTemp['nombre'] = self.leNombreP.text()
        dataTemp['nvlUbica'] = self.leNvlUbicaP.text()
        dataTemp['anioConstruccion'] = self.leAnioConsP.text()

        # uso de construccion
        if self.cmbUsoConstrP.count() > 0:
            index = self.cmbUsoConstrP.currentIndex()
            valor = self.cmbUsoConstrP.itemData(index)
            dataTemp['idCatUsoConstruccion'] = valor

        # uso especifico
        if self.cmbUsoEspP.count() > 0:
            index = self.cmbUsoEspP.currentIndex()
            valor = self.cmbUsoEspP.itemData(index)
            dataTemp['idCatUsoEspecifico'] = valor

        # destino
        if self.cmbDestinoP.count() > 0:
            index = self.cmbDestinoP.currentIndex()
            valor = self.cmbDestinoP.itemData(index)
            dataTemp['idCatDestino'] = valor

        # estado de construccion
        if self.cmbEdoConstrP.count() > 0:
            index = self.cmbEdoConstrP.currentIndex()
            valor = self.cmbEdoConstrP.itemData(index)
            dataTemp['idCatEstadoConstruccion'] = valor

        # categoria
        if self.cmbCategoriaP.count() > 0:
            index = self.cmbCategoriaP.currentIndex()
            valor = self.cmbCategoriaP.itemData(index)
            dataTemp['idCategoria'] = valor
            
        # factor
        if self.cmbFactorConstrP.count() > 0:
            index = self.cmbFactorConstrP.currentIndex()
            valor = self.cmbFactorConstrP.itemData(index)
            dataTemp['idFactor'] = valor


        # grupos subgrupos y caracteristicas
        allRows = self.twCaracteristicasP.rowCount()
        caracCategorias = []
        for row in range(0,allRows):
            caract = {}
            twi0 = self.twCaracteristicasP.item(row,0)
            twi1 = self.twCaracteristicasP.item(row,1)
            twi2 = self.twCaracteristicasP.item(row,2)
            twi3 = self.twCaracteristicasP.item(row,3)
            twi4 = self.twCaracteristicasP.item(row,4)
            twi5 = self.twCaracteristicasP.item(row,5)

            caract['idGrupo'] = twi0.text()
            caract['descripcionGrupo'] = twi1.text()
            caract['idSubgrupo'] = twi2.text()
            caract['descripcionSubGrupo'] = twi3.text()
            caract['idCaracteristica'] = twi4.text()
            caract['descripcionCaracteristica'] = twi5.text()

            caracCategorias.append(caract)
        
        dataTemp['caracCategorias'] = caracCategorias

        self.cmbFraccionesP.setItemData(self.indexFraActual, dataTemp)


    # - guarda de manera temporal los valores de construcciones CONDOMINIO
    def constrTempCondo(self):

        #print('entraaaaaaaaaaaaaaaaaaaaaaaaa')
        self.fraccTempCondo()
        dataTemp = self.cmbVolumenC.itemData(self.indexVolActualCondo)

        fracciones = []

        count = self.cmbFraccionesC.count()

        for index in range(0, count):
            fracciones.append(self.cmbFraccionesC.itemData(index))

        dataTemp['fracciones'] = fracciones

        self.cmbVolumenC.setItemData(self.indexVolActualCondo, dataTemp)

    # - guarda de manera temporal los valores de las fracciones CONDOMINIO
    def fraccTempCondo(self):

        dataTemp = self.cmbFraccionesC.itemData(self.indexFraActualCondo)

        if dataTemp == None:
            # self.createAlert('fraccion nula: ' + str(dataTemp))
            return

        dataTemp['codigoConstruccion'] = self.lbCveUsoP.text()
        dataTemp['precioM2'] = self.lbValM2P.text()
        dataTemp['valorConst'] = self.lbValConstP.text()
        dataTemp['supConstFraccion'] = self.lbSupConstrFP.text()
        dataTemp['numNivel'] = self.lbNvlFraccP.text()
        dataTemp['nombre'] = self.leNombreP.text()
        dataTemp['nvlUbica'] = self.leNvlUbicaP.text()
        dataTemp['anioConstruccion'] = self.leAnioConsP.text()

        # uso de construccion
        if self.cmbUsoConstrP.count() > 0:
            index = self.cmbUsoConstrP.currentIndex()
            valor = self.cmbUsoConstrP.itemData(index)
            dataTemp['idCatUsoConstruccion'] = valor

        # uso especifico
        if self.cmbUsoEspP.count() > 0:
            index = self.cmbUsoEspP.currentIndex()
            valor = self.cmbUsoEspP.itemData(index)
            dataTemp['idCatUsoEspecifico'] = valor

        # destino
        if self.cmbDestinoP.count() > 0:
            index = self.cmbDestinoP.currentIndex()
            valor = self.cmbDestinoP.itemData(index)
            dataTemp['idCatDestino'] = valor

        # estado de construccion
        if self.cmbEdoConstrP.count() > 0:
            index = self.cmbEdoConstrP.currentIndex()
            valor = self.cmbEdoConstrP.itemData(index)
            dataTemp['idCatEstadoConstruccion'] = valor

        # categoria
        if self.cmbCategoriaP.count() > 0:
            index = self.cmbCategoriaP.currentIndex()
            valor = self.cmbCategoriaP.itemData(index)
            dataTemp['idCategoria'] = valor
            
        # factor
        if self.cmbFactorConstrP.count() > 0:
            index = self.cmbFactorConstrP.currentIndex()
            valor = self.cmbFactorConstrP.itemData(index)
            dataTemp['idFactor'] = valor


        # grupos subgrupos y caracteristicas
        allRows = self.twCaracteristicasP.rowCount()
        caracCategorias = []
        for row in range(0,allRows):
            caract = {}
            twi0 = self.twCaracteristicasP.item(row,0)
            twi1 = self.twCaracteristicasP.item(row,1)
            twi2 = self.twCaracteristicasP.item(row,2)
            twi3 = self.twCaracteristicasP.item(row,3)
            twi4 = self.twCaracteristicasP.item(row,4)
            twi5 = self.twCaracteristicasP.item(row,5)

            caract['idGrupo'] = twi0.text()
            caract['descripcionGrupo'] = twi1.text()
            caract['idSubgrupo'] = twi2.text()
            caract['descripcionSubGrupo'] = twi3.text()
            caract['idCaracteristica'] = twi4.text()
            caract['descripcionCaracteristica'] = twi5.text()

            caracCategorias.append(caract)
        
        dataTemp['caracCategorias'] = caracCategorias

        self.cmbFraccionesC.setItemData(self.indexFraActualCondo, dataTemp)


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
    def consumeWSGeneral(self, url_cons = ""):

        url = url_cons
        data = ""

        try:
            self.headers['Authorization'] = self.obtenerToken()
            response = requests.get(url, headers = self.headers)
        except requests.exceptions.RequestException as e:
            self.createAlert("Error de servidor, 'consumeWSGeneral()' '" + str(e) + "'", QMessageBox().Critical, "Error de servidor")
            return

        if response.status_code == 200:
            data = response.content
        else:
            self.createAlert('Error en peticion "consumeWSGeneral()":\n' + response.text, QMessageBox().Critical, "Error de servidor")
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

    def event_cambioCondominio(self):

        if self.cmbCondo.count() > 0:
            index = self.cmbCondo.currentIndex()
            tipoCond = self.cmbCondo.itemData(index) # <---- tipo de condominio
            clave = self.cmbCondo.currentText()      # <---- clave de condominio

            # consumir ws de consulta de informacion de condominio
            dataCond = self.consumeWSGeneral(self.urlCondByCveCatTipoPred + self.cveCatastral + clave + '/' + tipoCond)

            if len(dataCond) == 0:
                return

            dc = dataCond[0]

            tC = ''
            if tipoCond == 'H':
                tC = 'Horizontal'
            elif tipoCond == 'V':
                tC = 'Vertical'

            self.lbTipoCond.setText(tC)

            self.leNumOfCond.setText(str(dc['numOfi']))
            self.lbPerimetroCond.setText(str(dc['perimetro']))
            self.leCveCatAntCond.setText(str(dc['cveCatAnt']))
            self.lbIndivisoCond.setText(str(dc['indiviso']))

            # --- construccion
            # - superficies
            self.leSupConstPrivCond.setText(str(dc['supConstruccionPrivada'] or 0))
            self.leSupConstComunCond.setText(str(dc['supConstruccionComun'] or 0))
            self.leSupConstExcCond.setText(str(dc['supConstComunEx'] or 0))

            supC = (dc['supConstruccionPrivada'] or 0) + (dc['supConstruccionComun'] or 0) + (dc['supConstComunEx'] or 0)

            self.leSupConstTotalCond.setText(str(supC))
            # - valores
            self.leValConstPrivCond.setText(str(dc['valorConstruccionPriv'] or 0))
            self.leValConstComunCond.setText(str(dc['valorConstruccionComun'] or 0))
            self.leValConstExcCond.setText(str(dc['valorConstExc'] or 0))

            valC = (dc['valorConstruccionPriv'] or 0) + (dc['valorConstruccionComun'] or 0) + (dc['valorConstExc'] or 0)

            self.leValConstTotalCond.setText(str(valC))

            # --- terreno
            # - superficies
            self.leSupTerrPrivCond.setText(str(dc['supTerPrivada'] or 0))
            self.leSupTerrComunCond.setText(str(dc['supTerComun'] or 0))
            self.leSupTerrExcCond.setText(str(dc['supTerrComunEx'] or 0))

            supT = (dc['supTerPrivada'] or 0) + (dc['supTerComun'] or 0) + (dc['supTerrComunEx'] or 0)

            self.leSupTerrTotalCond.setText(str(supT))
            # - valores
            self.leValTerrPrivCond.setText(str(dc['valorTerrenoPriv'] or 0))
            self.leValTerrComunCond.setText(str(dc['valorTerrenoComun'] or 0))
            self.leValTerrExcCond.setText(str(dc['valorTerrExc'] or 0))

            valT = (dc['valorTerrenoPriv'] or 0) + (dc['valorTerrenoComun'] or 0) + (dc['valorTerrExc'] or 0)

            self.leValTerrTotalCond.setText(str(valT))

            # cargar servicios de condomino
            dataServCuenta = self.obtieneServiciosCuenta(self.cveCatastral + clave)

            self.twServiciosCondo.clearContents()
            self.twServiciosCondo.setRowCount(0)
            
            for dsc in dataServCuenta:

                rowPosition = self.twServiciosCondo.rowCount()
                self.twServiciosCondo.insertRow(rowPosition)

                check = QtWidgets.QTableWidgetItem(dsc['descripcion'])
                check.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)

                if dsc['disponible'] == False:
                    check.setCheckState(QtCore.Qt.Unchecked)
                else:
                    check.setCheckState(QtCore.Qt.Checked)
                self.twServiciosCondo.setItem(rowPosition, 0, check)

                self.twServiciosCondo.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(dsc['servicio']))


            # -- C A R G A   C O N T R U C C I O N E S
            dataConstC = self.consumeWSConstr(self.cveCatastral + clave, tipoCond)
            self.cargaConstrCondo(dataConstC)

    def event_cambioUsoConstr(self):

        if self.cmbUsoConstrP.count() > 0:

            index = self.cmbUsoConstrP.currentIndex()
            idUsoConst = self.cmbUsoConstrP.itemData(index)

            self.cmbCategoriaP.clear()
            self.cmbUsoEspP.clear()

            # -- obtiene categorias
            data = self.consumeWSGeneral(self.urlCategoriasByIdUsoConst + str(idUsoConst))
            data1 = self.consumeWSGeneral(self.urlUsoEspecifByIdUsoConst + str(idUsoConst))
            if data == None and data1 == None:
                return

            lenJson = len(list(data))
            lenJson1 = len(list(data1))

            if lenJson > 0:
                for cate in data:
                    self.cmbCategoriaP.addItem(str(cate['categoria']), cate['id'])

            if lenJson1 > 0:
                for esp in data1:
                    self.cmbUsoEspP.addItem(str(esp['descripcion']), esp['id'])

    def event_CambioTipoUsoSuelo(self):

        if self.cmbTipoUsoSuelo.count() > 0:
            index = self.cmbTipoUsoSuelo.currentIndex()
            idTipoUS = self.cmbTipoUsoSuelo.itemData(index)

            self.cmbUsoSuelo.clear()

            data = self.consumeWSGeneral(self.urlCatUsoSueloByTipoUso + str(idTipoUS))
            if data == None:
                return

            lenJson = len(list(data))

            if lenJson > 0:
                for usos in data:
                    self.cmbUsoSuelo.addItem(str(usos['descripcion']), str(usos['cveUsoSuelo']))

    def event_cambioFraccPred(self):

        if self.cmbFraccionesP.count() > 0:
            index = self.cmbFraccionesP.currentIndex()
            data = self.cmbFraccionesP.itemData(index)

            #print(index)
            #print(data)

            if self.indexFraActual != -1:
                # se manda a llamar el metodo que guarda de manera temporal
                data1 = self.cmbFraccionesP.itemData(self.indexFraActual)
                #print(self.indexFraActual)
                #print(data1)
                self.fraccTemp()

            self.indexFraActual = index

            self.lbCveUsoP.setText(str(data['codigoConstruccion']))
            self.lbValM2P.setText(str(data['precioM2']))
            self.lbValConstP.setText(str(data['valorConst']))
            self.lbSupConstrFP.setText(str(data['supConstFraccion']))
            self.lbNvlFraccP.setText(str(data['numNivel']))
            self.leNombreP.setText(str(data['nombre']))
            self.leNvlUbicaP.setText(str(data['nvlUbica']))
            self.leAnioConsP.setText(str(data['anioConstruccion']))

            # uso de construccion
            if data['idCatUsoConstruccion'] != None:
                index = self.cmbUsoConstrP.findData(data['idCatUsoConstruccion'])
                if index >= 0:
                    self.cmbUsoConstrP.setCurrentIndex(index)
            else:
                self.cmbUsoConstrP.setCurrentIndex(0)

            # uso especifico
            if data['idCatUsoEspecifico'] != None:
                index = self.cmbUsoEspP.findData(data['idCatUsoEspecifico'])
                if index >= 0:
                    self.cmbUsoEspP.setCurrentIndex(index)
            else:
                self.cmbUsoEspP.setCurrentIndex(0)

            # destino
            if data['idCatDestino'] != None:
                index = self.cmbDestinoP.findData(data['idCatDestino'])
                if index >= 0:
                    self.cmbDestinoP.setCurrentIndex(index)
            else:
                self.cmbDestinoP.setCurrentIndex(0)

            # estado de construccion
            if data['idCatEstadoConstruccion'] != None:
                index = self.cmbEdoConstrP.findData(data['idCatEstadoConstruccion'])
                if index >= 0:
                    self.cmbEdoConstrP.setCurrentIndex(index)
            else:
                self.cmbEdoConstrP.setCurrentIndex(0)

            # categoria
            if data['idCategoria'] != None:
                index = self.cmbCategoriaP.findData(data['idCategoria'])
                if index >= 0:
                    self.cmbCategoriaP.setCurrentIndex(index)
            else:
                self.cmbCategoriaP.setCurrentIndex(0)

            # factor
            if data['idFactor'] != None:
                index = self.cmbFactorConstrP.findData(data['idFactor'])
                if index >= 0:
                    self.cmbFactorConstrP.setCurrentIndex(index)
            else:
                self.cmbFactorConstrP.setCurrentIndex(0)

            self.twCaracteristicasP.clearContents()
            self.twCaracteristicasP.setRowCount(0)
            
            for row in range(0, self.twCaracteristicasP.rowCount()):        
                self.twCaracteristicasP.removeRow(row)

            # grupos subgrupos y caracteristicas
            caracteristicas = data['caracCategorias']
            if len(caracteristicas) > 0:

                for carac in caracteristicas:
                    # agrega un renglon a las coindancias
                    idGrupo = carac['idGrupo']
                    descGpo = carac['descripcionGrupo']
                    idSubGp = carac['idSubgrupo']
                    descSub = carac['descripcionSubGrupo']
                    idCarac = carac['idCaracteristica']
                    descCar = carac['descripcionCaracteristica']

                    rowPosition = self.twCaracteristicasP.rowCount()
                    self.twCaracteristicasP.insertRow(rowPosition)
                    self.twCaracteristicasP.setItem(rowPosition , 0, QtWidgets.QTableWidgetItem(str(idGrupo)))
                    self.twCaracteristicasP.setItem(rowPosition , 1, QtWidgets.QTableWidgetItem(descGpo))
                    self.twCaracteristicasP.setItem(rowPosition , 2, QtWidgets.QTableWidgetItem(str(idSubGp)))
                    self.twCaracteristicasP.setItem(rowPosition , 3, QtWidgets.QTableWidgetItem(descSub))
                    self.twCaracteristicasP.setItem(rowPosition , 4, QtWidgets.QTableWidgetItem(str(idCarac)))
                    self.twCaracteristicasP.setItem(rowPosition , 5, QtWidgets.QTableWidgetItem(descCar))

    def event_cambioVolPred(self):

        if self.cmbVolumenP.count() > 0:

            index = self.cmbVolumenP.currentIndex()
            data = self.cmbVolumenP.itemData(index)

            if self.indexVolActual != -1:
                # se manda a llamar el metodo que guarda de manera temporal
                self.constrTemp()

            self.indexVolActual = index

            # carga construcciones
            self.lbSupConstrP.setText(str(data['supConst']))
            self.lbNumNivP.setText(str(data['numNiveles']))
            self.lbTipoConstP.setText(str(data['constTipo']))

            # oculta los niveles y muestra claves de const. especial
            # cuando se trate de construccion especial
            if data['cveConstEsp'] != None:
                self.lbCveConstEspP_2.show()
                self.lbCveConstEspP.show()
                self.lbCveConstEspP.setText(str(data['cveConstEsp']))
            else:
                self.lbCveConstEspP_2.hide()
                self.lbCveConstEspP.hide()

            # ---- CARGA DE FRACCIONES
            self.cmbFraccionesP.clear()
            fra = data['fracciones']

            #self.indexFraActual = -1
            for f in fra:
                self.cmbFraccionesP.addItem(str(f['volumen']), f)
            
            
    def event_cambioCategoria(self):
        
        idUsoConst = 0
        idCate = 0

        # obtener el uso de construccion
        if self.cmbUsoConstrP.count() > 0:
            index = self.cmbUsoConstrP.currentIndex()
            idUsoConst = self.cmbUsoConstrP.itemData(index)

        # obtener la categoria
        if self.cmbCategoriaP.count() > 0:
            index = self.cmbCategoriaP.currentIndex()
            idCate = self.cmbCategoriaP.itemData(index)

        # consume ws para obtener las caracteristicas
        data = self.consultaCaracter(str(idUsoConst), str(idCate))

        self.twCaracteristicasP.clearContents()
        self.twCaracteristicasP.setRowCount(0)
            
        for row in range(0, self.twCaracteristicasP.rowCount()):        
            self.twCaracteristicasP.removeRow(row)


        if len(data) > 0:

            for carac in data:
                # agrega un renglon a las coindancias
                idGrupo = carac['idCatGrupo']
                descGpo = carac['descripcionCatGrupo']
                idSubGp = carac['idCatSubgrupo']
                descSub = carac['descripcionCatSubgrupo']
                idCarac = carac['idCatCaracteristica']
                descCar = carac['descripcionCatCaracteristica']

                rowPosition = self.twCaracteristicasP.rowCount()
                self.twCaracteristicasP.insertRow(rowPosition)
                self.twCaracteristicasP.setItem(rowPosition , 0, QtWidgets.QTableWidgetItem(str(idGrupo)))
                self.twCaracteristicasP.setItem(rowPosition , 1, QtWidgets.QTableWidgetItem(descGpo))
                self.twCaracteristicasP.setItem(rowPosition , 2, QtWidgets.QTableWidgetItem(str(idSubGp)))
                self.twCaracteristicasP.setItem(rowPosition , 3, QtWidgets.QTableWidgetItem(descSub))
                self.twCaracteristicasP.setItem(rowPosition , 4, QtWidgets.QTableWidgetItem(str(idCarac)))
                self.twCaracteristicasP.setItem(rowPosition , 5, QtWidgets.QTableWidgetItem(descCar))

    def event_cambioUsoConstrCondo(self):

        if self.cmbUsoConstrC.count() > 0:
            index = self.cmbUsoConstrC.currentIndex()
            idUsoConst = self.cmbUsoConstrC.itemData(index)

            self.cmbCategoriaC.clear()
            self.cmbUsoEspC.clear()

            # -- obtiene categorias
            data = self.consumeWSGeneral(self.urlCategoriasByIdUsoConst + str(idUsoConst))
            data1 = self.consumeWSGeneral(self.urlUsoEspecifByIdUsoConst + str(idUsoConst))
            if data == None and data1 == None:
                return

            lenJson = len(list(data))
            lenJson1 = len(list(data1))

            if lenJson > 0:
                for cate in data:
                    self.cmbCategoriaC.addItem(str(cate['categoria']), cate['id'])

            if lenJson1 > 0:
                for esp in data1:
                    self.cmbUsoEspC.addItem(str(esp['descripcion']), esp['id'])

    def event_cambioFraccCondo(self):

        if self.cmbFraccionesC.count() > 0:

            index = self.cmbFraccionesC.currentIndex()
            data = self.cmbFraccionesC.itemData(index)

            if self.indexFraActualCondo != -1:
                # se manda a llamar el metodo que guarda de manera temporal
                self.fraccTempCondo()

            self.indexFraActualCondo = index

            self.lbCveUsoC.setText(str(data['codigoConstruccion']))
            self.lbValM2C.setText(str(data['precioM2']))
            self.lbValConstC.setText(str(data['valorConst']))
            self.lbSupConstrFC.setText(str(data['supConstFraccion']))
            self.lbNvlFraccC.setText(str(data['numNivel']))
            self.leNombreC.setText(str(data['nombre']))
            self.leNvlUbicaC.setText(str(data['nvlUbica']))
            self.leAnioConsC.setText(str(data['anioConstruccion']))

            # uso de construccion
            if data['idCatUsoConstruccion'] != None:
                index = self.cmbUsoConstrC.findData(data['idCatUsoConstruccion'])
                if index >= 0:
                    self.cmbUsoConstrC.setCurrentIndex(index)
            else:
                self.cmbUsoConstrC.setCurrentIndex(0)

            # uso especifico
            if data['idCatUsoEspecifico'] != None:
                index = self.cmbUsoEspC.findData(data['idCatUsoEspecifico'])
                if index >= 0:
                    self.cmbUsoEspC.setCurrentIndex(index)
            else:
                self.cmbUsoEspC.setCurrentIndex(0)

            # destino
            if data['idCatDestino'] != None:
                index = self.cmbDestinoC.findData(data['idCatDestino'])
                if index >= 0:
                    self.cmbDestinoC.setCurrentIndex(index)
            else:
                self.cmbDestinoC.setCurrentIndex(0)

            # estado de construccion
            if data['idCatEstadoConstruccion'] != None:
                index = self.cmbEdoConstrC.findData(data['idCatEstadoConstruccion'])
                if index >= 0:
                    self.cmbEdoConstrC.setCurrentIndex(index)
            else:
                self.cmbEdoConstrC.setCurrentIndex(0)

            # categoria
            if data['idCategoria'] != None:
                index = self.cmbCategoriaC.findData(data['idCategoria'])
                if index >= 0:
                    self.cmbCategoriaC.setCurrentIndex(index)
            else:
                self.cmbCategoriaC.setCurrentIndex(0)

            # factor
            if data['idFactor'] != None:
                index = self.cmbFactorConstrC.findData(data['idFactor'])
                if index >= 0:
                    self.cmbFactorConstrC.setCurrentIndex(index)
            else:
                self.cmbFactorConstrC.setCurrentIndex(0)

            self.twCaracteristicasC.clearContents()
            self.twCaracteristicasC.setRowCount(0)
            
            for row in range(0, self.twCaracteristicasC.rowCount()):        
                self.twCaracteristicasC.removeRow(row)

            # grupos subgrupos y caracteristicas
            caracteristicas = data['caracCategorias']
            if len(caracteristicas) > 0:

                for carac in caracteristicas:
                    # agrega un renglon a las coindancias
                    idGrupo = carac['idGrupo']
                    descGpo = carac['descripcionGrupo']
                    idSubGp = carac['idSubgrupo']
                    descSub = carac['descripcionSubGrupo']
                    idCarac = carac['idCaracteristica']
                    descCar = carac['descripcionCaracteristica']

                    rowPosition = self.twCaracteristicasC.rowCount()
                    self.twCaracteristicasC.insertRow(rowPosition)
                    self.twCaracteristicasC.setItem(rowPosition , 0, QtWidgets.QTableWidgetItem(str(idGrupo)))
                    self.twCaracteristicasC.setItem(rowPosition , 1, QtWidgets.QTableWidgetItem(descGpo))
                    self.twCaracteristicasC.setItem(rowPosition , 2, QtWidgets.QTableWidgetItem(str(idSubGp)))
                    self.twCaracteristicasC.setItem(rowPosition , 3, QtWidgets.QTableWidgetItem(descSub))
                    self.twCaracteristicasC.setItem(rowPosition , 4, QtWidgets.QTableWidgetItem(str(idCarac)))
                    self.twCaracteristicasC.setItem(rowPosition , 5, QtWidgets.QTableWidgetItem(descCar))

    def event_cambioVolCondo(self):

        if self.cmbVolumenC.count() > 0:
        
            index = self.cmbVolumenC.currentIndex()
            data = self.cmbVolumenC.itemData(index)

            if self.indexVolActualCondo != -1:
                # se manda a llamar el metodo que guarda de manera temporal
                self.constrTempCondo()

            self.indexVolActualCondo = index

            # carga construcciones
            self.lbSupConstrC.setText(str(data['supConst']))
            self.lbNumNivC.setText(str(data['numNiveles']))
            self.lbTipoConstC.setText(str(data['constTipo']))
            
            # oculta los niveles y muestra claves de const. especial
            # cuando se trate de construccion especial
            if data['cveConstEsp'] != None:
                self.lbCveConstEspC_2.show()
                self.lbCveConstEspC.show()
                self.lbCveConstEspC.setText(str(data['cveConstEsp']))
            else:
                self.lbCveConstEspC_2.hide()
                self.lbCveConstEspC.hide()

            # ---- CARGA DE FRACCIONES
            self.cmbFraccionesC.clear()
            fra = data['fracciones']
            
            for f in fra:
                self.cmbFraccionesC.addItem(str(f['volumen']), f)
            
    def event_cambioCategoriaCondo(self):
        
        idUsoConst = 0
        idCate = 0

        # obtener el uso de construccion
        if self.cmbUsoConstrC.count() > 0:
            index = self.cmbUsoConstrC.currentIndex()
            idUsoConst = self.cmbUsoConstrC.itemData(index)

        # obtener la categoria
        if self.cmbCategoriaC.count() > 0:
            index = self.cmbCategoriaC.currentIndex()
            idCate = self.cmbCategoriaC.itemData(index)

        # consume ws para obtener las caracteristicas
        data = self.consultaCaracter(str(idUsoConst), str(idCate))

        self.twCaracteristicasC.clearContents()
        self.twCaracteristicasC.setRowCount(0)
            
        for row in range(0, self.twCaracteristicasC.rowCount()):        
            self.twCaracteristicasC.removeRow(row)


        if len(data) > 0:

            for carac in data:
                # agrega un renglon a las coindancias
                idGrupo = carac['idCatGrupo']
                descGpo = carac['descripcionCatGrupo']
                idSubGp = carac['idCatSubgrupo']
                descSub = carac['descripcionCatSubgrupo']
                idCarac = carac['idCatCaracteristica']
                descCar = carac['descripcionCatCaracteristica']

                rowPosition = self.twCaracteristicasC.rowCount()
                self.twCaracteristicasC.insertRow(rowPosition)
                self.twCaracteristicasC.setItem(rowPosition , 0, QtWidgets.QTableWidgetItem(str(idGrupo)))
                self.twCaracteristicasC.setItem(rowPosition , 1, QtWidgets.QTableWidgetItem(descGpo))
                self.twCaracteristicasC.setItem(rowPosition , 2, QtWidgets.QTableWidgetItem(str(idSubGp)))
                self.twCaracteristicasC.setItem(rowPosition , 3, QtWidgets.QTableWidgetItem(descSub))
                self.twCaracteristicasC.setItem(rowPosition , 4, QtWidgets.QTableWidgetItem(str(idCarac)))
                self.twCaracteristicasC.setItem(rowPosition , 5, QtWidgets.QTableWidgetItem(descCar))

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

        # agrega un renglon a las colindancias
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

    # evento de seleccion de calle
    def event_seleccionaCalle(self):
        
        # se obtiene los features seleccionados
        features = self.calle.selectedFeatures()

        if len(features) == 0:
            self.createAlert("Seleccione una geometria")
            return
        if len(features) != 1:
            self.createAlert("Seleccione una sola geometria")
            return
        else:
            feat = features[0]

            nombreCalle = feat['calle']
            self.idCalleSelecc = feat['id']
            self.lbNomCalle.setText(nombreCalle)

            # busca los servicios asociados a la calle
            dataServCalle = self.obtieneServiciosCalle(self.idCalleSelecc)
            
            self.twServiciosCalle.clearContents()
            self.twServiciosCalle.setRowCount(0)
            
            for dsc in dataServCalle:

                rowPosition = self.twServiciosCalle.rowCount()
                self.twServiciosCalle.insertRow(rowPosition)

                check = QtWidgets.QTableWidgetItem(dsc['descripcion'])
                check.setFlags(QtCore.Qt.ItemIsEnabled)

                if dsc['disponible'] == False:
                    check.setCheckState(QtCore.Qt.Unchecked)
                else:
                    check.setCheckState(QtCore.Qt.Checked)
                self.twServiciosCalle.setItem(rowPosition, 0, check)

                self.twServiciosCalle.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(dsc['servicio']))

            # desactivar seleccion de calles
            if self.eventoCalleActivo:
                self.calle.selectionChanged.disconnect()
                self.eventoCalleActivo = False

            self.cancelarCalle()

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
