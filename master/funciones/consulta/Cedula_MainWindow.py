import os
import operator

from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMessageBox, QListView, QGraphicsView, QGraphicsScene, QFileDialog, QVBoxLayout

from qgis.utils import iface
from qgis.core import QgsProject
from .fusion_dialog import fusionDialog

import os, json, requests, sys, datetime, base64, time

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'mainWindow.ui'))

class CedulaMainWindow(QtWidgets.QMainWindow, FORM_CLASS):
    def __init__(self, cveCatas = "0", cond = False, parent=None, CFG=None, UTI = None):
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
        self.CFG = CFG
        self.UTI = UTI
        self.cveCondSel = ''
        if len(cveCatas) > 25:
            self.cveCondSel = cveCatas[25:]

        # es condominio
        self.cond = cond

        # -- canvas --
        self.canvas = iface.mapCanvas()

        # Save reference to the QGIS interface
        self.iface = iface

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

        # almacena la cedula de la clave global
        self.cedula = {}
        self.padron = {}
        self.calle = None
        self.eventoCalleActivo = False
        self.indexVolActual = -1
        self.indexFraActual = -1
        self.indexVolActualCondo = -1
        self.indexFraActualCondo = -1
        self.idCalleSelecc = -1
        self.valorCalle = 0

        self.indexCondoActual = -1

        self.usoConstr = []
        self.usoConstrC = []
        self.cateConstP = []
        self.cateConstC = []

        self.seRealiza = True
        self.seRealizaC = True

        self.condominios = []
        self.constrCond = []
        self.servCuentaCond = []

        self.bloqueado = True

        self.indivisos = []

        self.scaleFactor = 1
        self.listZoom = {}

        self.idsMzaIma = []
        self.idsFacIma = []
        self.idsDocIma = []

        self.countIM = 0
        self.countIF = 0
        self.countID = 0

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
        # sin edicion en QTableWidget
        self.twCaracteristicasP.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.twColindancias.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.twVialidades.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.twCaracteristicasC.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.twPropFiscal.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.twPropPred.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        
        self.leSupConstPrivCond.setValidator(QDoubleValidator(0.999,99.999,3))
        self.leSupConstComunCond.setValidator(QDoubleValidator(0.999,99.999,3))
        #self.leSupConstExcCond.setValidator(QDoubleValidator(0.999,99.999,3))
        self.leSupConstTotalCond.setValidator(QDoubleValidator(0.999,99.999,3))
        self.leValConstPrivCond.setValidator(QDoubleValidator(0.99,99.9,2))
        self.leValConstComunCond.setValidator(QDoubleValidator(0.99,99.99,2))
        #self.leValConstExcCond.setValidator(QDoubleValidator(0.99,99.99,2))
        self.leValConstTotalCond.setValidator(QDoubleValidator(0.99,99.99,2))
        self.leSupTerrPrivCond.setValidator(QDoubleValidator(0.999,99.999,3))
        self.leSupTerrComunCond.setValidator(QDoubleValidator(0.999,99.999,3))
        #self.leSupTerrExcCond.setValidator(QDoubleValidator(0.999,99.999,3))
        self.leSupTerrTotalCond.setValidator(QDoubleValidator(0.999,99.999,3))
        self.leValTerrPrivCond.setValidator(QDoubleValidator(0.99,99.99,2))
        self.leValTerrComunCond.setValidator(QDoubleValidator(0.99,99.99,2))
        #self.leValTerrExcCond.setValidator(QDoubleValidator(0.99,99.99,2))
        self.leValTerrTotalCond.setValidator(QDoubleValidator(0.99,99.99,2))

        self.lePrivadaC.setValidator(QDoubleValidator(0.999,99.999,3))
        self.leComunC.setValidator(QDoubleValidator(0.999,99.999,3))
        self.lePrivadaT.setValidator(QDoubleValidator(0.999,99.999,3))
        self.leComunT.setValidator(QDoubleValidator(0.999,99.999,3))
        
        self.leDispPerim.setValidator(QDoubleValidator(0.99,99.99,2))
        self.twColindancias.setColumnHidden(0, True)
        header = self.twColindancias.horizontalHeader()
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        #self.leSupTerr.setValidator(QDoubleValidator(0.99,99.99,2))
        self.leFondo.setValidator(QDoubleValidator(0.99,99.99,2))
        self.leFrente.setValidator(QDoubleValidator(0.99,99.99,2))
        self.lbUsoPredioEtiqueta.hide()
        self.cmbUsoPredio.hide()
        self.lFacConstP.hide()
        self.cmbFactorConstrP.hide()
        self.lFacConstC.hide()
        self.cmbFactorConstrC.hide()
        self.twCaracteristicasP.setColumnHidden(0, True)
        self.twCaracteristicasP.setColumnHidden(2, True)
        self.twCaracteristicasP.setColumnHidden(4, True)
        self.twCaracteristicasP.setColumnHidden(6, True)
        self.twCaracteristicasP.setColumnHidden(7, True)
        header = self.twCaracteristicasP.horizontalHeader()
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)

        header = self.twIndivisos.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
        
        self.twCaracteristicasC.setColumnHidden(0, True)
        self.twCaracteristicasC.setColumnHidden(2, True)
        self.twCaracteristicasC.setColumnHidden(4, True)
        self.twCaracteristicasC.setColumnHidden(6, True)
        self.twCaracteristicasC.setColumnHidden(7, True)
        header = self.twCaracteristicasC.horizontalHeader()
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

        self.twIndivisos.cellChanged.connect(self.event_updateIndivisos)

        header = self.twPropFiscal.horizontalHeader()
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.twPropFiscal.setColumnHidden(0, True)
        self.twPropFiscal.itemClicked.connect(self.event_itemClicked)

        header = self.twPropPred.horizontalHeader()
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.twPropPred.setColumnHidden(0, True)
        self.twPropPred.itemClicked.connect(self.event_itemClickedProp)
        


        self.leNivPropP.setAlignment(Qt.AlignCenter)
        self.leNivPropP.setValidator(QIntValidator(0,99,None))
        self.leAnioConsP.setValidator(QIntValidator(0,9999,None))
        self.leNvlUbicaP.setValidator(QIntValidator(0,9999,None))

        self.leNivPropC.setValidator(QIntValidator(0,99,None))
        self.leAnioConsC.setValidator(QIntValidator(0,9999,None))
        self.leNvlUbicaC.setValidator(QIntValidator(0,9999,None))

        self.leSupConstrFP.setValidator(QDoubleValidator(0.99,99.99,2))
        self.leSupConstPrivCond.setValidator(QDoubleValidator(0.9999,99.9999,4))

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
        # self.cmbFactorConstrP.setView(self.generaQListView()) --- SE deshabilito, ya no se va usar

        # -- Eventos
        self.btnDelConstrP.clicked.connect(self.event_elimConstrC)
        self.btnAddConstP.clicked.connect(self.event_nuevaConstrC)
        self.btnGuardarCed.clicked.connect(self.event_guardarPredio)
        self.btnGuardarCedCond.clicked.connect(self.event_guardarCondominio)

        self.btnGuardaVolP.clicked.connect(self.event_guardarVolP)
        self.btnGuardaVolC.clicked.connect(self.event_guardarVolC)
        self.pushButton.clicked.connect(self.event_hasAlgo)
        self.btnColinAdd.clicked.connect(self.event_agregaColin)
        self.btnColinRemoveOne.clicked.connect(self.event_remueveColin)
        self.btnColinRemoveAll.clicked.connect(self.event_remTodasColin)
        self.cmbTipoUsoSuelo.currentIndexChanged.connect(self.event_CambioTipoUsoSuelo)
        self.cmbCondo.currentIndexChanged.connect(self.event_cambioCondominio)

        self.btnSelCalle.clicked.connect(self.event_consultarCalle)
        self.btnCancelSelCalle.clicked.connect(self.event_cancelarCalle)

        self.btnCalcValCatP.clicked.connect(self.event_calcularValorConstrPred)
        self.btnCalcValCatC.clicked.connect(self.event_calcularValorConstrCond)
        self.btnSubdividirP.clicked.connect(self.event_subdividirFraccPred)
        self.btnSubdividirC.clicked.connect(self.event_subdividirFraccCond)
        self.btnFusionarP.clicked.connect(self.event_fusionarFraccPred)
        self.btnFusionarC.clicked.connect(self.event_fusionarFraccCond)

        self.btnBlocDesbloc.clicked.connect(self.event_bloqDesbloc)
        self.btnActualizaInfo.clicked.connect(self.event_actualizaInfo)


        #self.pteObservaciones.keyPressEvent(self.event_keyPressObservaciones)
        self.lePrivadaC.textChanged.connect(self.event_textoCambioPrivC)
        self.leComunC.textChanged.connect(self.event_textoCambioPrivC)
        self.lePrivadaT.textChanged.connect(self.event_textoCambioPrivC)
        self.leComunT.textChanged.connect(self.event_textoCambioPrivC)

        # Eventos - construcciones predios
        self.cmbVolumenP.currentIndexChanged.connect(self.event_cambioVolPred)
        self.cmbFraccionesP.currentIndexChanged.connect(self.event_cambioFraccPred)
        self.cmbUsoConstrP.currentIndexChanged.connect(self.event_cambioUsoConstr)
        self.cmbCategoriaP.currentIndexChanged.connect(self.event_cambioCategoria)

        # Eventos - imagenes
        self.btnZoomOut.clicked.connect(self.event_zoomOutIma)
        self.btnZoomIn.clicked.connect(self.event_zoomInIma)
        self.rbManzana.toggled.connect(self.event_radioButtonImagenesPress)
        self.rbFachada.toggled.connect(self.event_radioButtonImagenesPress)
        self.rbDocumento.toggled.connect(self.event_radioButtonImagenesPress)
        self.btnAtrasImage.clicked.connect(self.event_atrasImagen)
        self.btnAdelanteImagen.clicked.connect(self.event_adelanteImagen)

        # -- Titulo
        self.setWindowTitle(self.descomponeCveCata(self.cveCatastral))

        # -- muestra clave
        self.lbCveCata.setText(self.descomponeCveCata(self.cveCatastral))
        self.muestraClaveGlobal(self.cveCatastral)

        # -- carga informacion en los catalogos
        dataCat = self.consumeWSGeneral(self.CFG.urlCedCatalogos)
        self.cargaCatalogos(dataCat)

        # -- carga informacion en los catalogos CONSTRUCCIONES
        self.cargaCatalogosConstruccionesP(self.cond)

        # -- carga informacion de la cedula segun la clave global
        dataCed = self.consumeWSCedula(self.cveCatastral[0:25])
        self.cargaCedula(dataCed)

        # -- carga informacion de PADRON
        dataPadron = self.obtienePadron(self.cedula['id'])
        self.cargaPadron(dataPadron)

        # -- carga propietarios de PREDIOS
        dataPropPredio = self.obtienePropPredio(self.cedula['id'])
        self.cargaPropPredio(dataPropPredio)

        if self.cond: # C O N D O M I N I O S

            self.lbPredioGlobal.hide()

            # diseño de combos
            self.disenioCombosCondos()

            # eventos controles constucciones
            self.eventosConstruccionesCondo()

            # se carga el combo de condominios
            dataCond = self.consumeWSGeneral(self.CFG.urlCedCondominios + self.cveCatastral)
            self.defineComboCond(dataCond)

            # carga indivisos
            self.cargaIndivisos()

            # se selecciona el condominio abierto
            if len(self.cveCondSel) > 0:
                index = self.cmbCondo.findText(self.cveCondSel, QtCore.Qt.MatchFixedString)
                if index >= 0:
                    self.cmbCondo.setCurrentIndex(index)

            self.event_bloqDesbloc()
            # indivisos
            self.factorIndiviso()
        
        else: # P R E D I O S

            # ocultar condominios
            self.lbPredioGlobal.show()
            # self.lbTipoCond.hide()
            self.lbTipoCond.setText('')
            self.cmbCondo.hide()
            self.btnGuardarCedCond.hide()

            # quita las tab que corresponden a condominios
            self.tabwCedula.removeTab(3)
            self.tabwCedula.removeTab(3)
            self.tabwCedula.removeTab(4)

            # quitar las superficies privadas y comunes del comparativo
            # ya que se muestra informacion del predio
            # Superficie
            self.lbPrivadaTerrS.hide()
            self.lbSupTerrPrivC.hide()
            self.lbSupTerrPrivF.hide()
            self.lbComunTerrS.hide()
            self.lbSupTerrComC.hide()
            self.lbSupTerrComF.hide()

            self.lbPrivadaConsS.hide()
            self.lbSupConsPrivC.hide()
            self.lbSupConsPrivF.hide()
            self.lbComunConsS.hide()
            self.lbSupConsComC.hide()
            self.lbSupConsComF.hide()

            # valores catastrales
            self.lbPrivadaTerrV.hide()
            self.lbValTerrPrivC.hide()
            self.lbValTerrPrivF.hide()
            self.lbComunTerrV.hide()
            self.lbValTerrComC.hide()
            self.lbValTerrComF.hide()

            self.lbPrivadaConsV.hide()
            self.lbValConsPrivC.hide()
            self.lbValConsPrivF.hide()
            self.lbComunConsV.hide()
            self.lbValConsComC.hide()
            self.lbValConsComF.hide()


        # define lista de porcentaje de zoom
        self.listZoom = {1:1, 2:1.5, 3:2, 4:2.5}
        # -- carga imagenes
        self.idsMzaIma = self.descargaIdsImag('M', self.cveCatastral)
        self.idsFacIma = self.descargaIdsImag('F', self.cveCatastral)
        self.idsDocIma = self.descargaIdsImag('D', self.cveCatastral)

        self.rbManzana.setChecked(True)

        # muestra siempre la primer tab
        self.tabwCedula.setCurrentIndex(0)

        # -- carga informacion de construcciones de PREDIO
        dataConstP = self.consumeWSConstr(self.cveCatastral)

        self.cargaConstrPred(dataConstP)

        self.cargada = True

        self.tabwCedula.blockSignals(True)
        self.tabwCedula.currentChanged.connect(self.event_cambioPestania)
        self.tabwCedula.blockSignals(False)


        '''
        #self.progressBar.hide()
        #self.pushButton_2.hide()
        self.pushButton_2.clicked.connect(self.progressbar)
        #self.pushButton.hide()





        self.movie = QMovie("C:\\Users\\cianet45\\Downloads\\qnvjMmA.gif", QByteArray(), self)

         # Create the layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label_9)

        self.setLayout(main_layout)

        # Add the QMovie object to the label
        self.movie.setCacheMode(QMovie.CacheAll)
        self.movie.setSpeed(100)
        self.label_9.setMovie(self.movie)
        #self.movie.start()


        '''

    # --- M E T O D O S ---

    def progressbar(self):

        
        self.completed = 0

        self.movie.start()
        while self.completed < 100:
            self.completed += 0.0001
            self.progressBar.setValue(self.completed)
        #self.movie.stop()

        '''
        print('Before: %s' % time.ctime())

        time.sleep(20)

        print('After: %s\n' % time.ctime())
        '''

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

    # - carga los indivisos de los condominios
    def cargaIndivisos(self):

        self.indivisos.clear()
        # consume ws para obtener info
        # llena self.indivisos
        self.indivisos = self.obtieneIndivisos(self.cveCatastral)

        supConstPriv = 0
        supConstComun = 0
        supTerrPriv = 0
        supTerrComun = 0

        for ind in self.indivisos:
            supConstPriv += ind['supConstPriv'] or 0
            supConstComun += ind['supConstComun']or 0
            supTerrPriv += ind['supTerrPriv'] or 0
            supTerrComun += ind['supTerrComun'] or 0

        '''
        self.lbPrivadaC.setText(str(supConstPriv))
        self.lbComunC.setText(str(supConstComun))
        self.lbPrivadaT.setText(str(supTerrPriv))
        self.lbComunT.setText(str(supTerrComun))
        '''
        self.lePrivadaC.setText(str(round(supConstPriv, 3)))
        self.leComunC.setText(str(round(supConstComun, 3)))
        self.lePrivadaT.setText(str(round(supTerrPriv, 3)))
        self.leComunT.setText(str(round(supTerrComun, 3)))

        # carga informacion en la tabla
        for ind in self.indivisos:

            rowPosition = self.twIndivisos.rowCount()
            self.twIndivisos.insertRow(rowPosition)

            # cuenta
            item0 = QtWidgets.QTableWidgetItem(ind['cuenta'])
            item0.setFlags(QtCore.Qt.ItemIsEnabled)

            self.twIndivisos.setItem(rowPosition, 0, item0)

            # % indiviso
            #self.twIndivisos.setCellWidget(rowPosition, 1, self.spinBoxQTableWidgetItem(0, 100, 5, ind['factor']))
            self.twIndivisos.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(ind['factor'])))

            # condominio (tipo)
            item2 = QtWidgets.QTableWidgetItem(ind['tipo'])
            item2.setFlags(QtCore.Qt.ItemIsEnabled)

            self.twIndivisos.setItem(rowPosition, 2, item2)

            # superficie de Construccion Privada
            #self.twIndivisos.setCellWidget(rowPosition, 3, self.spinBoxQTableWidgetItem(0, 999999, 3, ind['supConstPriv']))
            self.twIndivisos.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(str(ind['supConstPriv'])))

            # superficie de Construccion comun
            #self.twIndivisos.setCellWidget(rowPosition, 4, self.spinBoxQTableWidgetItem(0, 999999, 3, ind['supConstComun']))
            self.twIndivisos.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(str(ind['supConstComun'])))

            # superficie de terreno privada
            #self.twIndivisos.setCellWidget(rowPosition, 5, self.spinBoxQTableWidgetItem(0, 999999, 3, ind['supTerrPriv']))
            self.twIndivisos.setItem(rowPosition, 5, QtWidgets.QTableWidgetItem(str(ind['supTerrPriv'])))

            # superficie de terreno comun
            #self.twIndivisos.setCellWidget(rowPosition, 6, self.spinBoxQTableWidgetItem(0, 999999, 3, ind['supTerrComun']))
            self.twIndivisos.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem(str(ind['supTerrComun'])))


    # - carga la informacion de los catalogos
    def cargaCatalogos(self, dataCat):

        try:
            if len(dataCat) == 0:
                self.createAlert('Sin Resultados', icono = QMessageBox().Warning)
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
                    self.cmbRegimenProp.addItem(str(reg['descripcion']), reg['id'])

            # -- facilidad de cominicacion
            if len(facilComun) > 0:
                self.cmbFacilComun.addItem('', -1)
                for fac in facilComun:
                    self.cmbFacilComun.addItem(str(fac['descripcion']), fac['id'])

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
                    self.cmbTipoRelieve.addItem(str(rel['tipoRelieve']), rel['id'])

            # -- forma predio
            if len(formaPredio) > 0:
                self.cmbFormaPredio.addItem('', -1)
                for form in formaPredio:
                    self.cmbFormaPredio.addItem(str(form['descripcion']), form['id'])

            # -- orientacion predio dentro de manzana
            if len(orientPredMza) > 0:
                self.cmbOrientPredMza.addItem('', -1)
                for predm in orientPredMza:
                    self.cmbOrientPredMza.addItem(str(predm['descripcion']), predm['id'])

            # -- tipo de asentamiento humano
            if len(tipoAsentH) > 0:
                self.cmbTipoAsentH.addItem('', -1)
                for tipa in tipoAsentH:
                    self.cmbTipoAsentH.addItem(str(tipa['descripcion']), tipa['id'])

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

    def obtienePadron(self, idPredio):
        return self.consumeWSGeneral(self.CFG.urlGetPadron + str(idPredio))

    def obtienePropPredio(self, idPredio):
        return self.consumeWSGeneral(self.CFG.urlGetPropPredio + str(idPredio))

    def catalogoTipoAsentH(self):
        return self.consumeWSGeneral(self.CFG.urlTipoAsentamiento)

    def catalogoTipoUsoSuelo(self):
        return self.consumeWSGeneral(self.CFG.urlCedCatTipoUsoSuelo)

    def catalogoValorTerreno(self):
        return self.consumeWSGeneral(self.CFG.urlValoresTerrenos)

    def catalogoUsoConstr(self):
        return self.consumeWSGeneral(self.CFG.urlCedUsoConstr)

    def catalogoDestino(self):
        return self.consumeWSGeneral(self.CFG.urlCedDestino)

    def catalogoEdoConstr(self):
        return self.consumeWSGeneral(self.CFG.urlCedEdoConstr)

    def catalogoFactorByTipoFactor(self):
        return self.consumeWSGeneral(self.CFG.urlCedCatFactorByTipoFactor + '5')

    def consultaCaracter(self, idUsoConst, idCate):
        return self.consumeWSGeneral(self.CFG.urlCedRCaracCategoria + idUsoConst + '/' + idCate)

    def obtieneServiciosCalle(self, idCalle):
        return self.consumeWSGeneral(self.CFG.urlServCalle + str(idCalle))

    def obtieneServiciosCuenta(self, cuenta):
        return self.consumeWSGeneral(self.CFG.urlCedServiciosCuenta + cuenta)

    def obtieneValorUsoConstr(self, idUsoC, idCate):
        return self.consumeWSGeneral(self.CFG.urlCedCatVuc + idUsoC + '/' + idCate)

    def obtieneCatMpio(self):
        return self.consumeWSGeneral(self.CFG.urlMunicipio)

    def obtieneIndivisos(self, cveCata):
        return self.consumeWSGeneral(self.CFG.urlIndivisos + cveCata)

    def guardaIndivisos(self, listaInd):
        return self.consumeWSGuardadoIndiv(listaInd, self.CFG.urlGuardaIndivisos)

    def obtieneImagen(self, idImagen, tipo):

        if tipo == 'M':
            return self.consumeWSGeneral(self.CFG.urlImagenByIdAndCveCata + str(idImagen) + '/' + self.cveCatastral[0:20])
        elif tipo == 'F' or tipo == 'D':
            return self.consumeWSGeneral(self.CFG.urlImagenByIdAndCveCata + str(idImagen) + '/' + self.cveCatastral)


    def descargaIdsImag(self, tipo, cveCata):

        listaResult = []
        result = []
        if tipo == 'M':
            result = self.consumeWSGeneral(self.CFG.urlObtIdsImagenes + tipo + '/' + cveCata[0:20])

        elif tipo == 'F' or tipo == 'D':
            result = self.consumeWSGeneral(self.CFG.urlObtIdsImagenes + tipo + '/' + cveCata)

        for r in result :
            imagen = {}
            imagen[r] = None
            listaResult.append(imagen)

        return listaResult

    # - carga la informacion de las construcciones
    def cargaConstrPred(self, dataConstP):
        
        try:


            if len(dataConstP) == 0:
                #self.createAlert('Sin Resultados', titulo = 'cargaConstrPred', icono = QMessageBox().Warning)
                # se llama el metodo deshabilitar construcciones 
                # solo se deja agregar nuevas
                self.deshabilitaConstr()
                return

            # ordena las construcciones segun el volumen
            construcciones = self.ordenaConstr(dataConstP)

            for dcp in construcciones:

                dcp['accion'] = 'update'
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
                    # fr['idFactor'] = -1
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
                self.createAlert('Sin Resultados', titulo = 'cargaConstrCondo', icono = QMessageBox().Warning)
                return

            self.cmbVolumenC.clear()
            self.cmbFraccionesC.clear()

            # ordena las construcciones segun el volumen
            construcciones = self.ordenaConstr(dataConstC)

            for dcp in construcciones:

                dcp['accion'] = 'update'
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
                    # fr['idFactor'] = -1
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
                self.cmbUsoConstrP.addItem(uc['descripcion'], uc['id'])
                d = {uc['id']: uc}
                self.usoConstr.append(d)

            if condo:
                self.cmbUsoConstrC.addItem('', -1)
                for uc in usoConstr:
                    self.cmbUsoConstrC.addItem(uc['descripcion'], uc['id'])
                    d = {uc['id']: uc}
                    self.usoConstrC.append(d)
        
        # -- destino
        if len(destino) > 0:
            self.cmbDestinoP.addItem('', -1)
            for d in destino:
                self.cmbDestinoP.addItem(d['descripcion'], d['id'])

            if condo:
                self.cmbDestinoC.addItem('', -1)
                for d in destino:
                    self.cmbDestinoC.addItem(d['descripcion'], d['id'])

        # -- estado de construccion
        if len(edoConstr) > 0:
            self.cmbEdoConstrP.addItem('', -1)
            for ec in edoConstr:
                self.cmbEdoConstrP.addItem(ec['descripcion'], ec['id'])

            if condo:
                self.cmbEdoConstrC.addItem('', -1)
                for ec in edoConstr:
                    self.cmbEdoConstrC.addItem(ec['descripcion'], ec['id'])

        # -- factor  --- SE deshabilito, ya no se va usar
        '''
        if len(factor) > 0:
            self.cmbFactorConstrP.addItem('', -1)
            for ec in factor:
                self.cmbFactorConstrP.addItem(ec['descripcion'], ec['id'])

            if condo:
                self.cmbFactorConstrC.addItem('', -1)
                for ec in factor:
                    self.cmbFactorConstrC.addItem(ec['descripcion'], ec['id'])
        '''

    # - carga la informacion de un predio en el formulario
    def cargaCedula(self, dataCed):

        try:

            if len(dataCed) == 0:
                self.createAlert('Sin Resultados', titulo = 'cargaCedula', icono = QMessageBox().Warning)
                return

            self.cedula = dataCed[0]
            # -- UBICACION -- 
            self.lbNoExt.setText(self.cedula['numExt'])
            self.leNoExteriorAlf.setText(self.cedula['numExteriorAlf'])
            self.leNoExteAnt.setText(self.cedula['numExteriorAnt'])
            self.leNumPredio.setText(self.cedula['numPredio'])
            self.lbCodigoPostal.setText(self.cedula['cp'])
            self.lbColonia.setText(self.cedula['colonia'])
            self.lbCveCatAnt.setText(self.cedula['cveCatAnt'])
            self.lbNumNivel.setText(self.cedula['nivel'])
            self.lbUltFechaAct.setText(None if self.cedula['fechaAct'] is None else self.cedula['fechaAct'][0:19])
            self.pteObservaciones.setPlainText(self.cedula['observaciones'])
            self.lbRevisor.setText(self.cedula['usuarioActual'])
            self.lbRevisorAnt.setText(self.cedula['usuarioAnterior'])

            # tipo de predio
            if self.cedula['cveTipoPred'] != None:
                index = self.cmbTipoPredio.findData(self.cedula['cveTipoPred'])
                if index >= 0:
                    self.cmbTipoPredio.setCurrentIndex(index)

            # asentamiento humano
            if self.cedula['idTipoAsentamiento'] is not None:
                index = self.cmbTipoAsentH.findData(self.cedula['idTipoAsentamiento'])
                if index >= 0:
                    self.cmbTipoAsentH.setCurrentIndex(index)
            
            # regimen de propiedad
            if self.cedula['idRegimenPropiedad'] is not None:
                index = self.cmbRegimenProp.findData(self.cedula['idRegimenPropiedad'])
                if index >= 0:
                    self.cmbRegimenProp.setCurrentIndex(index)

            # municipio
            dataMpio = self.obtieneCatMpio()
            self.lbNomMpio.setText('' if len(dataMpio) == 0 else dataMpio[0]['descripcion'])

            # calle
            calles = self.cedula['calles']
            idCalle = 0

            if len(calles) > 0:
                c = calles[0]
                self.lbNomCalle.setText(c['calle'])
                idCalle = c['id']
                self.idCalleSelecc = idCalle
                self.valorCalle = c['valor']
            else:
                self.lbNomCalle.setText('')

            # vialidades colindantes
            vialidades = self.cedula['vialidadesColin']

            if len(vialidades) > 0:

                for c in vialidades:
                    rowPosition = self.twVialidades.rowCount()
                    self.twVialidades.insertRow(rowPosition)
                    self.twVialidades.setItem(rowPosition , 0, QtWidgets.QTableWidgetItem(str(c['tipovialidad'])))
                    self.twVialidades.setItem(rowPosition , 1, QtWidgets.QTableWidgetItem(str(c['calle'])))

            # colindancias
            colin = self.cedula['colindancias']

            if len(colin) > 0:
                for c in colin:
                    rowPosition = self.twColindancias.rowCount()
                    self.twColindancias.insertRow(rowPosition)
                    self.twColindancias.setItem(rowPosition , 0, QtWidgets.QTableWidgetItem(str(c['idCatColindancia'])))
                    self.twColindancias.setItem(rowPosition , 1, QtWidgets.QTableWidgetItem(str(c['catColindancia'])))
                    self.twColindancias.setItem(rowPosition , 2, QtWidgets.QTableWidgetItem(str(c['superficieColindacia'])))
                    self.twColindancias.setItem(rowPosition , 3, QtWidgets.QTableWidgetItem(str(c['desscripcion'])))

            # localidad
            if self.cedula['localidad'] is not None:
                localidad = self.cedula['localidad']
                self.lbLocalidad.setText(localidad['nombre'])
            else:
                self.lbLocalidad.setText('')

            # -- TERRENO --
            self.lbSupTerr.setText(str(self.cedula['supTerr']))
            self.leFondo.setText(str(self.cedula['fondo']))
            self.leFrente.setText(str(self.cedula['frente']))
            self.leNombre.setText(self.cedula['nombre'])


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
            if self.cedula['cveTipoUsoSuelo'] != None:
                index = self.cmbTipoUsoSuelo.findData(self.cedula['cveTipoUsoSuelo'])
                if index >= 0:
                    self.cmbTipoUsoSuelo.setCurrentIndex(index)

            # uso de predio
            # -- SE DESHABILITA PORQUE NO SE VA A USAR
            '''
            if self.cedula['idUsoPredio'] != 0:
                index = self.cmbUsoPredio.findData(self.cedula['idUsoPredio'])
                if index >= 0:
                    self.cmbUsoPredio.setCurrentIndex(index)
            '''

            # tipo relieve
            if self.cedula['idTipoRelieve'] is not None:
                index = self.cmbTipoRelieve.findData(self.cedula['idTipoRelieve'])
                if index >= 0:
                    self.cmbTipoRelieve.setCurrentIndex(index)

            # facilidad de comunicacion
            if self.cedula['idFacilidadComunicacion'] is not None:
                index = self.cmbFacilComun.findData(self.cedula['idFacilidadComunicacion'])
                if index >= 0:
                    self.cmbFacilComun.setCurrentIndex(index)

            # forma de predio
            if self.cedula['idPredioForma'] is not None:
                index = self.cmbFormaPredio.findData(self.cedula['idPredioForma'])
                if index >= 0:
                    self.cmbFormaPredio.setCurrentIndex(index)

            # orientacion
            if self.cedula['idPredioUbicacion_manzana'] is not None:
                index = self.cmbOrientPredMza.findData(self.cedula['idPredioUbicacion_manzana'])
                if index >= 0:
                    self.cmbOrientPredMza.setCurrentIndex(index)

            # valor de terreno
            if self.cedula['cveVus'] != None:
                index = self.cmbValorTerr.findData(self.cedula['cveVus'])
                if index >= 0:
                    self.cmbValorTerr.setCurrentIndex(index)

        except Exception as e:
            self.errorCerrar = True
            self.createAlert('Error durante la carga de informacion "cargaCedula()": ' + str(e))

    # - carga informacion de padron junto con propietarios
    def cargaPadron(self, dataPadron):

        try:

            if len(dataPadron) == 0:
                self.muestraComparativoFiscal()
                return

            self.padron = dataPadron[0]

            # -- CARGA PADRON --
            # - carga ubicacion
            self.lbCallePF.setText(self.padron['eUbCalle'])
            self.lbNumExtPF.setText(self.padron['eUbNumexterior'])
            self.lbNumInteriorPF.setText(self.padron['eUbNuminterior'])
            self.lbCodPostalPF.setText(self.padron['eUbCodigoPostal'])
            self.lbColoniaPF.setText(self.padron['eUbColonia'])

            # - carga comparativo
            # superficies terreno
            self.lbSupTerrPrivF.setText(str(self.padron['eSupTerPriv']))
            self.lbSupTerrComF.setText(str(self.padron['eSupTerComun']))

            supTerrTotal = (self.padron['eSupTerPriv'] or 0) + (self.padron['eSupTerComun'] or 0)
            self.lbSupTerrTotalF.setText(str(supTerrTotal))

            # superficies construccion
            self.lbSupConsPrivF.setText(str(self.padron['eSupConstPriv']))
            self.lbSupConsComF.setText(str(self.padron['eSupConstComun']))

            supConsTot = (self.padron['eSupConstPriv'] or 0) + (self.padron['eSupConstComun'] or 0)
            self.lbSupConsTotalF.setText(str(supConsTot))

            self.lbValTerrPrivF.setText('-')
            self.lbValTerrComF.setText('-')
            self.lbValTerrTotalF.setText('${:,.2f}'.format(self.padron['eValorTer']))
            self.lbValConsPrivF.setText('-')
            self.lbValConsComF.setText('-')
            self.lbValConsTotalF.setText('${:,.2f}'.format(self.padron['eValorConst']))
            self.lbValorCTotalF.setText('${:,.2f}'.format(self.padron['eValorCat']))

            valC = (self.padron['eValorCat'] or 0)

            self.lbImpPredF.setText('${:,.2f}'.format(round(((valC * 12) / 1000), 2)))

            # - carga propietarios
            self.propPadron = self.padron['propietarios']

            if len(self.propPadron) > 0:

                for prop in self.propPadron:
                    # agrega un renglon a las coindancias
                    claveProp = prop['claveProp']
                    nombre = prop['razonSocial'] if not prop['nombre'] else prop['nombre'] + ' ' + prop['apellidop'] + ' ' + prop['apellidom']
                    persona = prop['personafisicamoral']
                    tipo = prop['propocop']
                    porcentaje = prop['porcProp']

                    rowPosition = self.twPropFiscal.rowCount()
                    self.twPropFiscal.insertRow(rowPosition)

                    item1 = QtWidgets.QTableWidgetItem(str(claveProp))
                    item1.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

                    item2 = QtWidgets.QTableWidgetItem(nombre.strip())

                    item3 = QtWidgets.QTableWidgetItem(persona)
                    item3.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

                    item4 = QtWidgets.QTableWidgetItem(tipo)
                    item4.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    
                    item5 = QtWidgets.QTableWidgetItem(str(porcentaje))
                    item5.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

                    self.twPropFiscal.setItem(rowPosition , 0, item1)
                    self.twPropFiscal.setItem(rowPosition , 1, item2)
                    self.twPropFiscal.setItem(rowPosition , 2, item3)
                    self.twPropFiscal.setItem(rowPosition , 3, item4)
                    self.twPropFiscal.setItem(rowPosition , 4, item5)

                self.twPropFiscal.setCurrentCell(0, 1)
                self.event_itemClicked(None)

        except Exception as e:
            self.errorCerrar = True
            self.createAlert('Error durante la carga de informacion "cargaPadron()": ' + str(e))

    # - carga informacion sobre los propietarios de un predio
    def cargaPropPredio(self, dataPropPredio):

        try:

            if len(dataPropPredio) == 0:
                self.muestraPropPredio()
                return

            # - carga propietarios
            self.propPropPred = dataPropPredio

            if len(self.propPropPred) > 0:

                for prop in self.propPropPred:
                    # agrega un renglon a las coindancias
                    ident = prop['id']
                    nombre = prop['nombre'] + ' ' + prop['aPaterno'] + ' ' + prop['aMaterno']
                    tipo = prop['tipo']
                    porcentaje = prop['porcentaje']

                    rowPosition = self.twPropPred.rowCount()
                    self.twPropPred.insertRow(rowPosition)

                    item1 = QtWidgets.QTableWidgetItem(str(ident))
                    item1.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

                    item2 = QtWidgets.QTableWidgetItem(nombre.strip())

                    item3 = QtWidgets.QTableWidgetItem(tipo)
                    item3.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

                    item4 = QtWidgets.QTableWidgetItem(str(porcentaje))
                    item4.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    
                    self.twPropPred.setItem(rowPosition , 0, item1)
                    self.twPropPred.setItem(rowPosition , 1, item2)
                    self.twPropPred.setItem(rowPosition , 2, item3)
                    self.twPropPred.setItem(rowPosition , 3, item4)

                self.twPropPred.setCurrentCell(0, 1)
                self.event_itemClickedProp(None)

        except Exception as e:
            self.errorCerrar = True
            self.createAlert('Error durante la carga de informacion "cargaPadron()": ' + str(e))

    # - limpia los constroles de construcciones
    def limpiaConstrucciones(self):

        self.cmbFraccionesP.clear()
        self.leNivPropP.setText('')
        self.cmbConP.clear()

        self.cmbUsoConstrP.setCurrentIndex(0)
        self.cmbDestinoP.setCurrentIndex(0)
        self.cmbEdoConstrP.setCurrentIndex(0)

        self.leNombreP.setText('')
        self.leSupConstrFP.setText('')
        self.lbSupConstrFP.setText('')
        self.leAnioConsP.setText('')
        self.leNvlUbicaP.setText('')

    # - deshabilitar contrucciones de predio
    def deshabilitaConstr(self):

        self.wFraccionP.setEnabled(False)
        self.wCaracConstr.setEnabled(False)
        self.wDescrConstr.setEnabled(False)

        self.btnGuardaVolP.setEnabled(False)
        self.cmbVolumenP.setEnabled(False)
        self.btnDelConstrP.setEnabled(False)
        self.btnGuardaVolP.setEnabled(False)

        self.lbSupConstrP.setText('')
        self.lbNumNivP.setText('')
        self.lbTipoConstP.setText('')
        self.lbCveConstEspP.setText('')
        self.lbNvlFraccP.setText('')

        self.lbCveUsoP.setText('')
        self.lbValM2P.setText('')
        self.lbValConstP.setText('')

    # - hbilitar construcciones de predio
    def habilitaConstr(self):

        self.wFraccionP.setEnabled(True)
        self.wCaracConstr.setEnabled(True)
        self.wDescrConstr.setEnabled(True)

        self.btnGuardaVolP.setEnabled(True)
        self.cmbVolumenP.setEnabled(True)
        self.btnDelConstrP.setEnabled(True)
        self.btnGuardaVolP.setEnabled(True)

    # - deshabilita manejo de imagenes
    def deshabilitaBotImages(self):

        self.btnAtrasImage.setEnabled(False)
        self.btnZoomIn.setEnabled(False)
        self.btnZoomOut.setEnabled(False)
        self.btnAdelanteImagen.setEnabled(False)

    # - habilita manejo de imagenes
    def habilitaBotImages(self):

        self.btnAtrasImage.setEnabled(True)
        self.btnZoomIn.setEnabled(True)
        self.btnZoomOut.setEnabled(True)
        self.btnAdelanteImagen.setEnabled(True)

    # - guarda de manera temporal los valores de construcciones
    def constrTemp(self):

        if not self.seRealiza:
            self.seRealiza = True
            return

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
            return

        dataTemp['codigoConstruccion'] = self.lbCveUsoP.text()
        dataTemp['precioM2'] = self.lbValM2P.text().replace('$', '').replace(',', '')
        dataTemp['valorConst'] = self.lbValConstP.text().replace('$', '').replace(',', '')
        dataTemp['supConstFraccion'] = self.leSupConstrFP.text()
        dataTemp['numNivel'] = self.lbNvlFraccP.text()
        dataTemp['nombre'] = self.leNombreP.text()
        dataTemp['nvlUbica'] = self.leNvlUbicaP.text()
        dataTemp['anioConstruccion'] = self.leAnioConsP.text()

        # uso de construccion
        if self.cmbUsoConstrP.count() > 0:
            index = self.cmbUsoConstrP.currentIndex()
            valor = self.cmbUsoConstrP.itemData(index)
            dataTemp['idCatUsoConstruccion'] = valor
        else:
            dataTemp['idCatUsoConstruccion'] = -1

        # uso especifico
        if self.cmbUsoEspP.count() > 0:
            index = self.cmbUsoEspP.currentIndex()
            valor = self.cmbUsoEspP.itemData(index)
            dataTemp['idCatUsoEspecifico'] = valor
        else:
            dataTemp['idCatUsoEspecifico'] = -1

        # destino
        if self.cmbDestinoP.count() > 0:
            index = self.cmbDestinoP.currentIndex()
            valor = self.cmbDestinoP.itemData(index)
            dataTemp['idCatDestino'] = valor
        else:
            dataTemp['idCatDestino'] = -1

        # estado de construccion
        if self.cmbEdoConstrP.count() > 0:
            index = self.cmbEdoConstrP.currentIndex()
            valor = self.cmbEdoConstrP.itemData(index)
            dataTemp['idCatEstadoConstruccion'] = valor
        else:
            dataTemp['idCatEstadoConstruccion'] = -1

        # categoria
        if self.cmbCategoriaP.count() > 0:
            index = self.cmbCategoriaP.currentIndex()
            valor = self.cmbCategoriaP.itemData(index)
            dataTemp['idCategoria'] = valor
        else:
            dataTemp['idCategoria'] = -1
            
        # factor  --- SE deshabilito, ya no se va usar
        '''
        if self.cmbFactorConstrP.count() > 0:
            index = self.cmbFactorConstrP.currentIndex()
            valor = self.cmbFactorConstrP.itemData(index)
            dataTemp['idFactor'] = valor
        '''


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
            twi6 = self.twCaracteristicasP.item(row,6)
            twi7 = self.twCaracteristicasP.item(row,7)

            caract['idGrupo'] = twi0.text()
            caract['descripcionGrupo'] = twi1.text()
            caract['idSubgrupo'] = twi2.text()
            caract['descripcionSubGrupo'] = twi3.text()
            caract['idCaracteristica'] = twi4.text()
            caract['descripcionCaracteristica'] = twi5.text()
            caract['idUsoConstruccion'] = twi6.text()
            caract['idCategoria'] = twi7.text()

            caracCategorias.append(caract)
        
        dataTemp['caracCategorias'] = caracCategorias

        self.cmbFraccionesP.setItemData(self.indexFraActual, dataTemp)

    # - guarda de manera temporal los valores de los condominios
    def condoTemp(self, claveCata):

        condos = []
        dataTemp = []

        # quita el condominio a guardar, para poder actualizar sus datos
        for cond in self.condominios:
            if cond['cveCat'] == claveCata:
                dataTemp = cond
            condos.append(cond)

        dataTemp['numOfi'] = self.leNumOfCond.text()
        dataTemp['cveCatAnt'] = self.leCveCatAntCond.text()

        # construccion
        dataTemp['supConstruccionPrivada'] = float(0 if self.leSupConstPrivCond.text() == '' else self.leSupConstPrivCond.text().replace(',', '').replace('$', ''))
        dataTemp['supConstruccionComun'] = float(0 if self.leSupConstComunCond.text() == '' else self.leSupConstComunCond.text().replace(',', '').replace('$', ''))
        # dataTemp['supConstComunEx'] = float(0 if self.leSupConstExcCond.text() == '' else self.leSupConstExcCond.text().replace(',', '').replace('$', ''))
        dataTemp['valorConstruccionPriv'] = float(0 if self.leValConstPrivCond.text() == '' else self.leValConstPrivCond.text().replace(',', '').replace('$', ''))
        dataTemp['valorConstruccionComun'] = float(0 if self.leValConstComunCond.text() == '' else self.leValConstComunCond.text().replace(',', '').replace('$', ''))
        #dataTemp['valorConstExc'] = float(0 if self.leValConstExcCond.text() == '' else self.leValConstExcCond.text().replace(',', '').replace('$', ''))

        # terreno
        dataTemp['supTerPrivada'] = float(0 if self.leSupTerrPrivCond.text() == '' else self.leSupTerrPrivCond.text().replace(',', '').replace('$', ''))
        dataTemp['supTerComun'] = float(0 if self.leSupTerrComunCond.text() == '' else self.leSupTerrComunCond.text().replace(',', '').replace('$', ''))
        #dataTemp['supTerrComunEx'] = float(0 if self.leSupTerrExcCond.text() == '' else self.leSupTerrExcCond.text().replace(',', '').replace('$', ''))
        dataTemp['valorTerrenoPriv'] = float(0 if self.leValTerrPrivCond.text() == '' else self.leValTerrPrivCond.text().replace(',', '').replace('$', ''))
        dataTemp['valorTerrenoComun'] = float(0 if self.leValTerrComunCond.text() == '' else self.leValTerrComunCond.text().replace(',', '').replace('$', ''))
        #dataTemp['valorTerrExc'] = float(0 if self.leValTerrExcCond.text() == '' else self.leValTerrExcCond.text().replace(',', '').replace('$', ''))

        # servicios de cuenta
        servicios = []

        for serv in self.servCuentaCond:
            if serv['cveCatastral'] != claveCata:
                servicios.append(serv)

        # -- GUARDADO DE SERVICIOS DE PREDIO
        if self.twServiciosCondo.rowCount() > 0:       

            tablaServicios = self.twServiciosCondo

            listaServicios = []
            for x in range(0, tablaServicios.rowCount()):

                servicio = {}
                servicio['descripcion'] = tablaServicios.item(x,0).text()
                servicio['disponible'] = True if tablaServicios.item(x,0).checkState() == 2 else False
                servicio['servicio'] = tablaServicios.item(x,1).text()
                servicio['cveCatastral'] = claveCata
                servicios.append(servicio)

        # -- GUARDADO DE CONSTRUCCIONES

        self.constrTempCondo()

        # obtner las construcciones actuales
        volumen = self.cmbVolumenC.currentText()

        construccionesTemp = []
        count = self.cmbVolumenC.count()

        for indx in range(0, count):
            dt = self.cmbVolumenC.itemData(indx)

            construccionesTemp.append(dt)

        condTemp = []

        # quitar las construcciones a modificar
        for cc in self.constrCond:
            if cc['cveCatastral'] != claveCata:
                condTemp.append(cc)

        for ct in construccionesTemp:
            condTemp.append(ct)

        # temporal CONSTRUCCIONES
        self.constrCond = []
        self.constrCond = list(condTemp)

        # temporal CONDOMINIOS
        condos.append(dataTemp)
        self.condominios = []
        self.condominios = list(condos)

        # temporal SERVICIOS
        self.servCuentaCond = []
        self.servCuentaCond = list(servicios)

    # - guarda de manera temporal los valores de construcciones CONDOMINIO
    def constrTempCondo(self):
        
        if not self.seRealizaC:
            self.seRealizaC = True
            return

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
            return

        dataTemp['codigoConstruccion'] = self.lbCveUsoC.text()
        dataTemp['precioM2'] = self.lbValM2C.text().replace('$', '').replace(',', '')
        dataTemp['valorConst'] = self.lbValConstC.text().replace('$', '').replace(',', '')
        dataTemp['supConstFraccion'] = self.lbSupConstrFC.text()
        dataTemp['numNivel'] = self.lbNvlFraccC.text()
        dataTemp['nombre'] = self.leNombreC.text()
        dataTemp['nvlUbica'] = self.leNvlUbicaC.text()
        dataTemp['anioConstruccion'] = self.leAnioConsC.text()

        # uso de construccion
        if self.cmbUsoConstrC.count() > 0:
            index = self.cmbUsoConstrC.currentIndex()
            valor = self.cmbUsoConstrC.itemData(index)
            dataTemp['idCatUsoConstruccion'] = valor
        else:
            dataTemp['idCatUsoConstruccion'] = -1

        # uso especifico
        if self.cmbUsoEspC.count() > 0:
            index = self.cmbUsoEspC.currentIndex()
            valor = self.cmbUsoEspC.itemData(index)
            dataTemp['idCatUsoEspecifico'] = valor
        else:
            dataTemp['idCatUsoEspecifico'] = -1

        # destino
        if self.cmbDestinoC.count() > 0:
            index = self.cmbDestinoC.currentIndex()
            valor = self.cmbDestinoC.itemData(index)
            dataTemp['idCatDestino'] = valor
        else:
            dataTemp['idCatDestino'] = -1

        # estado de construccion
        if self.cmbEdoConstrC.count() > 0:
            index = self.cmbEdoConstrC.currentIndex()
            valor = self.cmbEdoConstrC.itemData(index)
            dataTemp['idCatEstadoConstruccion'] = valor
        else:
            dataTemp['idCatEstadoConstruccion'] = -1

        # categoria
        if self.cmbCategoriaC.count() > 0:
            index = self.cmbCategoriaC.currentIndex()
            valor = self.cmbCategoriaC.itemData(index)
            dataTemp['idCategoria'] = valor
        else:
            dataTemp['idCategoria'] = -1
            
        # factor
        #if self.cmbFactorConstrC.count() > 0:
            #index = self.cmbFactorConstrC.currentIndex()
            #valor = self.cmbFactorConstrC.itemData(index)
            #dataTemp['idFactor'] = valor


        # grupos subgrupos y caracteristicas
        allRows = self.twCaracteristicasC.rowCount()
        caracCategorias = []
        for row in range(0,allRows):
            caract = {}
            twi0 = self.twCaracteristicasC.item(row,0)
            twi1 = self.twCaracteristicasC.item(row,1)
            twi2 = self.twCaracteristicasC.item(row,2)
            twi3 = self.twCaracteristicasC.item(row,3)
            twi4 = self.twCaracteristicasC.item(row,4)
            twi5 = self.twCaracteristicasC.item(row,5)
            twi6 = self.twCaracteristicasC.item(row,6)
            twi7 = self.twCaracteristicasC.item(row,7)

            caract['idGrupo'] = twi0.text()
            caract['descripcionGrupo'] = twi1.text()
            caract['idSubgrupo'] = twi2.text()
            caract['descripcionSubGrupo'] = twi3.text()
            caract['idCaracteristica'] = twi4.text()
            caract['descripcionCaracteristica'] = twi5.text()
            caract['idUsoConstruccion'] = twi6.text()
            caract['idCategoria'] = twi7.text()

            caracCategorias.append(caract)
        
        dataTemp['caracCategorias'] = caracCategorias

        self.cmbFraccionesC.setItemData(self.indexFraActualCondo, dataTemp)

    def muestraComparativoFiscal(self):

        # SUPERFICIES
        # terreno
        self.lbSupTerrPrivF.setText('0')
        self.lbSupTerrComF.setText('0')

        self.lbSupTerrTotalF.setText('0')

        # construcciones
        self.lbSupConsPrivF.setText('0')
        self.lbSupConsComF.setText('0')

        self.lbSupConsTotalF.setText('0')


        # VALORES
        # terreno
        self.lbValTerrPrivF.setText('${:,.2f}'.format(0))
        self.lbValTerrComF.setText('${:,.2f}'.format(0))

        self.lbValTerrTotalF.setText('${:,.2f}'.format(0))

        # construcciones
        self.lbValConsPrivF.setText('${:,.2f}'.format(0))
        self.lbValConsComF.setText('${:,.2f}'.format(0))

        self.lbValConsTotalF.setText('${:,.2f}'.format(0))


        # totales
        self.lbValorCTotalF.setText('${:,.2f}'.format(0))

        # impuesto
        self.lbImpPredF.setText('${:,.2f}'.format(0))

        # diferencia
        self.lbImpPredC.setText('')
        impCatastro = 0 if self.lbImpPredC.text() == '' else float(self.lbImpPredC.text().replace('$', '').replace(',', ''))
        self.lbDiferencia.setText('${:,.2f}'.format(impCatastro - 0))

        # ---- limpia ubicacion fiscal ----
        self.lbCallePF.setText('')
        self.lbNumExtPF.setText('')
        self.lbNumInteriorPF.setText('')
        self.lbCodPostalPF.setText('')
        self.lbColoniaPF.setText('')
        self.lbNumeroPPad.setText('')

        # ---- limpia ubicacion fiscal ----
        self.lbNombrePPad.setText('')
        self.lbRazonSocPPad.setText('')
        self.lbCallePPad.setText('')
        self.lbColoniaPPad.setText('')
        self.lbCodPosPPad.setText('')

        self.lbRFCPPad.setText('')
        self.lbTelefonoPPad.setText('')
        self.lbCorreoElecPPad.setText('')
        self.lbCiudadPPad.setText('')
        self.lbMunicipioPPad.setText('')
        self.lbEstadoPPad.setText('')

        self.lbCalleNPPad.setText('')
        self.lbNumOfiNPPad.setText('')
        self.lbNumInteriorNPPad.setText('')
        self.lbColoniaNPPad.setText('')
        self.lbCodPostNPPad.setText('')
        self.lbEstadoNPPad.setText('')
        self.lbCiudadNPPad.setText('')

    def muestraPropPredio(self):

        self.lbNombrePPred.setText('')
        self.lbApPaternoPPred.setText('')
        self.lbApMaternoPPred.setText('')
        self.lbCallePPred.setText('')
        self.lbNumExtPPred.setText('')
        self.lbNumInteriorPPred.setText('')

        self.lbColoniaPPred.setText('')
        self.lbCodPosPPred.setText('')
        self.lbMunicipioPPred.setText('')
        self.lbEstadoPPred.setText('')
        self.lbPaisPPred.setText('')

    # --- M E T O D O S   CIERRA ---

    # --- S E R V I C I O S   W E B ---

    # - consume ws para informacion de construcciones
    def consumeWSConstr(self, cveCatastral, tipoCta = 'P'):

        url = self.CFG.urlCedConstr + cveCatastral + '/' + tipoCta
        data = ""

        try:
            self.headers['Authorization'] = self.UTI.obtenerToken()
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

        url = self.CFG.urlCedPredio + cveCatastral
        data = ""

        try:
            self.headers['Authorization'] = self.UTI.obtenerToken()
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

    # - consume ws que verifica si una construccion tiene geometria
    def verificaSiTieneGeomWS(self, idConst, url):

        data = ""
        
        try:
            self.headers['Authorization'] = self.UTI.obtenerToken()
            response = requests.get(url + str(idConst), headers = self.headers)
        except requests.exceptions.RequestException as e:
            self.createAlert("Error de servidor, 'guardaConstrPredWS()' '" + str(e) + "'", QMessageBox().Critical, "Error de servidor")
            return str(e)

        if response.status_code == 200:
            data = response.content
        else:
            self.createAlert('Error en peticion "guardaConstrPredWS()":\n' + response.text, QMessageBox().Critical, "Error de servidor")
            return response.text

        return json.loads(data)

    # - consume ws para informacion de catalogos
    def consumeWSGeneral(self, url_cons = ""):

        url = url_cons
        data = ""

        try:
            self.headers['Authorization'] = self.UTI.obtenerToken()
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

    def consumeWSGuardadoIndiv(self, listaInd, url):

        data = ""
        jsonListInd = json.dumps(listaInd)

        try:
            self.headers['Authorization'] = self.UTI.obtenerToken()
            response = requests.put(url, headers = self.headers, data = jsonListInd)
        except requests.exceptions.RequestException as e:
            self.createAlert("Error de servidor, 'consumeWSGuardadoIndiv()' '" + str(e) + "'", QMessageBox().Critical, "Error de servidor")
            return

        if response.status_code == 200:
            data = response.content
        else:
            self.createAlert('Error en peticion "consumeWSGuardadoIndiv()":\n' + response.text, QMessageBox().Critical, "Error de servidor")
            return response.text

        return 'OK'

    # - manda al ws un predio a guardar
    def guardaPredioWS(self, predio, url):
        data = ""
        
        jsonGuardaPred = json.dumps(predio)
        
        try:
            self.headers['Authorization'] = self.UTI.obtenerToken()
            response = requests.post(url, headers = self.headers, data = jsonGuardaPred)
        except requests.exceptions.RequestException as e:
            self.createAlert("Error de servidor, 'guardaPredioWS()' '" + str(e) + "'", QMessageBox().Critical, "Error de servidor")
            return str(e)

        if response.status_code == 200:
            data = response.content
        else:
            self.createAlert('Error en peticion "guardaPredioWS()":\n' + response.text, QMessageBox().Critical, "Error de servidor")
            return response.text

        return 'OK'

    # - manda al ws los servicios de un predio para ser guardados
    def guardaServiciosPredWS(self, servicios, cveCata, url):
        data = ""
        
        jsonGuardaServPred = json.dumps(servicios)
        try:
            self.headers['Authorization'] = self.UTI.obtenerToken()
            response = requests.post(url + cveCata, headers = self.headers, data = jsonGuardaServPred)
        except requests.exceptions.RequestException as e:
            self.createAlert("Error de servidor, 'guardaServiciosPredWS()' '" + str(e) + "'", QMessageBox().Critical, "Error de servidor")
            return str(e)

        if response.status_code == 200:
            data = response.content
        else:
            self.createAlert('Error en peticion "guardaServiciosPredWS()":\n' + response.text, QMessageBox().Critical, "Error de servidor")
            return response.text

        return 'OK'

    # - manda al ws un volumen para ser guardado
    def guardaConstrPredWS(self, volumen, accion, url):
        data = ""
        
        jsonGuardaVolumen = json.dumps(volumen)
        try:
            self.headers['Authorization'] = self.UTI.obtenerToken()
            response = requests.post(url + accion, headers = self.headers, data = jsonGuardaVolumen)
        except requests.exceptions.RequestException as e:
            self.createAlert("Error de servidor, 'guardaConstrPredWS()' '" + str(e) + "'", QMessageBox().Critical, "Error de servidor")
            return str(e)

        if response.status_code == 200:
            data = response.content
        else:
            self.createAlert('Error en peticion "guardaConstrPredWS()":\n' + response.text, QMessageBox().Critical, "Error de servidor")
            return response.text

        return 'OK'

    # - manda al ws un condominio para ser guardado
    def guardaCondominioWS(self, condominio, tipo, url):
        data = ""
        
        jsonGuardaCond = json.dumps(condominio)
        try:
            self.headers['Authorization'] = self.UTI.obtenerToken()
            response = requests.post(url + tipo, headers = self.headers, data = jsonGuardaCond)
        except requests.exceptions.RequestException as e:
            self.createAlert("Error de servidor, 'guardaCondominioWS()' '" + str(e) + "'", QMessageBox().Critical, "Error de servidor")
            return str(e)

        if response.status_code == 200:
            data = response.content
        else:
            self.createAlert('Error en peticion "guardaCondominioWS()":\n' + response.text, QMessageBox().Critical, "Error de servidor")
            return response.text

        return 'OK'

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

    # -- Cambio de condominios
    # -- se consulta la informacion del WS cada vez que se selecciona uno en el combo
    # -- pero si ya se habia consultado antes, ya no es necesario hacerlo de nuevo
    def event_cambioCondominio(self):

        if self.cmbCondo.count() > 0:
            index = self.cmbCondo.currentIndex()
            tipoCond = self.cmbCondo.itemData(index) # <---- tipo de condominio
            clave = self.cmbCondo.currentText()      # <---- clave de condominio

            claveAnt = self.cmbCondo.itemText(self.indexCondoActual)
            
            if self.indexCondoActual != -1:
                # se manda a llamar el metodo que guarda de manera temporal
                # data1 = self.cmbFraccionesP.itemData(self.indexFraActual)
                self.condoTemp(self.cveCatastral + claveAnt)

            self.indexCondoActual = index
            
            dataCond = []
            consume = True
            # se busca si ya se habia consumido informacion del condominio seleccionado
            for condo in self.condominios:

                if condo['cveCat'] == (self.cveCatastral + clave):
                    consume = False
                    dataCond.append(condo)
                    break

            if consume:
                # consumir ws de consulta de informacion de condominio
                dataCond = self.consumeWSGeneral(self.CFG.urlCedCondByCveCatTipoPred + self.cveCatastral + clave + '/' + tipoCond)

                if len(dataCond) == 0:
                    return

                self.condominios.append(dataCond[0])

            if len(dataCond) == 0:
                return

            dc = dataCond[0]

            tC = ''
            if tipoCond == 'H':
                tC = 'Horizontal'
            elif tipoCond == 'V':
                tC = 'Vertical'

            self.lbTipoCond.setText(tC)

            self.leNumOfCond.setText(dc['numOfi'])
            self.lbPerimetroCond.setText(None if dc['perimetro'] is None else str(dc['perimetro']))
            self.leCveCatAntCond.setText(dc['cveCatAnt'])
            self.lbIndivisoCond.setText(None if dc['indiviso'] is None else str(dc['indiviso']))

            # --- construccion
            # - superficies
            self.leSupConstPrivCond.setText(str(dc['supConstruccionPrivada'] or 0))
            self.leSupConstComunCond.setText(str(dc['supConstruccionComun'] or 0))
            # self.leSupConstExcCond.setText(str(dc['supConstComunEx'] or 0))

            supC = (dc['supConstruccionPrivada'] or 0) + (dc['supConstruccionComun'] or 0)# + (dc['supConstComunEx'] or 0)

            self.leSupConstTotalCond.setText(str(round(supC, 3)))
            # - valores
            self.leValConstPrivCond.setText('${:,.2f}'.format(dc['valorConstruccionPriv'] or 0))
            self.leValConstComunCond.setText('${:,.2f}'.format(dc['valorConstruccionComun'] or 0))
            #self.leValConstExcCond.setText('${:,.2f}'.format(dc['valorConstExc'] or 0))

            valC = (dc['valorConstruccionPriv'] or 0) + (dc['valorConstruccionComun'] or 0)# + (dc['valorConstExc'] or 0)

            self.leValConstTotalCond.setText('${:,.2f}'.format(round(valC, 2)))

            # --- terreno
            # - superficies
            self.leSupTerrPrivCond.setText(str(dc['supTerPrivada'] or 0))
            self.leSupTerrComunCond.setText(str(dc['supTerComun'] or 0))
            #self.leSupTerrExcCond.setText(str(dc['supTerrComunEx'] or 0))

            supT = (dc['supTerPrivada'] or 0) + (dc['supTerComun'] or 0)# + (dc['supTerrComunEx'] or 0)

            self.leSupTerrTotalCond.setText(str(round(supT, 3)))
            # - valores
            self.leValTerrPrivCond.setText('${:,.2f}'.format(dc['valorTerrenoPriv'] or 0))
            self.leValTerrComunCond.setText('${:,.2f}'.format(dc['valorTerrenoComun'] or 0))
            #self.leValTerrExcCond.setText('${:,.2f}'.format(dc['valorTerrExc'] or 0))

            valT = (dc['valorTerrenoPriv'] or 0) + (dc['valorTerrenoComun'] or 0)# + (dc['valorTerrExc'] or 0)

            self.leValTerrTotalCond.setText('${:,.2f}'.format(round(valT, 2)))

            # cargar servicios de condomino
            dataServCuenta = []
            consume = True

            for sc in self.servCuentaCond:
                if sc['cveCatastral'] == (self.cveCatastral + clave):
                    consume = False
                    dataServCuenta.append(sc)

            if consume:
                dataServCuenta = self.obtieneServiciosCuenta(self.cveCatastral + clave)
                for dcc in dataServCuenta:

                    dcc['cveCatastral'] = self.cveCatastral + clave
                    self.servCuentaCond.append(dcc)

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
            # busca si no se habian consultado antes las construcciones
            dataConstC = []
            consume = True

            for cc in self.constrCond:
                if cc['cveCatastral'] == (self.cveCatastral + clave):
                    consume = False
                    dataConstC.append(cc)

            if consume:
                # consume de ws las construcciones de condominio
                dataConstC = self.consumeWSConstr(self.cveCatastral + clave, tipoCond)
                for dcc in dataConstC:
                    self.constrCond.append(dcc)


            self.indexVolActualCondo = -1
            self.indexFraActualCondo = -1

            # - CARGA LAS CONSTRUCCIONES
            self.cargaConstrCondo(dataConstC)

            # - VALIDACIONES PARA MANEJO DE CONSTRUCCIONES 
            # si es vertical, NO se permiten agregar ni eliminar construcciones

            if tipoCond == 'H': # <---------- HORIZONTAL
                self.btnAddConstC.setEnabled(True)
                self.btnDelConstrC.setEnabled(True)

            elif tipoCond == 'V': # <-------- VERTICAL
                self.btnAddConstC.setEnabled(False)
                self.btnDelConstrC.setEnabled(False)

            currentIndex = self.tabwCedula.currentIndex()
            self.event_cambioPestania(index = currentIndex)

    def event_cambioUsoConstr(self):

        if self.cmbUsoConstrP.count() > 0:

            index = self.cmbUsoConstrP.currentIndex()
            idUsoConst = self.cmbUsoConstrP.itemData(index)

            self.cmbCategoriaP.clear()
            self.cmbUsoEspP.clear()

            # -- obtiene categorias
            data = self.consumeWSGeneral(self.CFG.urlCedCategoriasByIdUsoConst + str(idUsoConst))
            data1 = self.consumeWSGeneral(self.CFG.urlCedUsoEspecifByIdUsoConst + str(idUsoConst))
            if data == None and data1 == None:
                return

            lenJson = len(list(data))
            lenJson1 = len(list(data1))

            self.cateConstP.clear()

            if lenJson > 0:
                for cate in data:
                    self.cmbCategoriaP.addItem(str(cate['categoria']), cate['id'])
                    d = {cate['id']: cate}
                    self.cateConstP.append(d)

            if lenJson1 > 0:
                for esp in data1:
                    self.cmbUsoEspP.addItem(str(esp['descripcion']), esp['id'])

    def event_CambioTipoUsoSuelo(self):

        if self.cmbTipoUsoSuelo.count() > 0:
            index = self.cmbTipoUsoSuelo.currentIndex()
            idTipoUS = self.cmbTipoUsoSuelo.itemData(index)

            self.cmbUsoSuelo.clear()

            data = self.consumeWSGeneral(self.CFG.urlCedCatUsoSueloByTipoUso + str(idTipoUS))
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

            if index == -1:
                return
            if self.indexFraActual != -1:
                # se manda a llamar el metodo que guarda de manera temporal
                data1 = self.cmbFraccionesP.itemData(self.indexFraActual)
                self.fraccTemp()

            self.indexFraActual = index

            self.lbCveUsoP.setText(data['codigoConstruccion'])

            self.lbValM2P.setText('${:,.2f}'.format(0) if data['precioM2'] is None else '${:,.2f}'.format(float(data['precioM2'])))
            self.lbValConstP.setText('${:,.2f}'.format(0) if data['valorConst'] is None else '${:,.2f}'.format(float(data['valorConst'])))
            self.lbSupConstrFP.setText(str(0) if data['supConstFraccion'] is None else str(data['supConstFraccion']))
            self.leSupConstrFP.setText(str(0) if data['supConstFraccion'] is None else str(data['supConstFraccion']))
            self.lbNvlFraccP.setText(str(1) if data['numNivel'] is None else str(data['numNivel']))
            self.leNombreP.setText('' if data['nombre'] is None else str(data['nombre']))
            self.leNvlUbicaP.setText('' if data['nvlUbica'] is None else str(data['nvlUbica']))
            self.leAnioConsP.setText('' if data['anioConstruccion'] is None else str(data['anioConstruccion']))

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

            # factor  --- SE deshabilito, ya no se va usar
            '''
            if data['idFactor'] != None:
                index = self.cmbFactorConstrP.findData(data['idFactor'])
                if index >= 0:
                    self.cmbFactorConstrP.setCurrentIndex(index)
            else:
                self.cmbFactorConstrP.setCurrentIndex(0)
            '''

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
                    self.twCaracteristicasP.setItem(rowPosition , 6, QtWidgets.QTableWidgetItem(str(data['idCatUsoConstruccion'])))
                    self.twCaracteristicasP.setItem(rowPosition , 7, QtWidgets.QTableWidgetItem(str(data['idCategoria'])))


            # se llena las fracciones a fusionar
            self.cmbConP.clear()

            indexV = self.cmbVolumenP.currentIndex()
            dataV = self.cmbVolumenP.itemData(indexV)
            fra = dataV['fracciones']

            for f in fra:
                fraccionAct = int(self.cmbFraccionesP.currentText())

                if fraccionAct != int(f['volumen']):

                    self.cmbConP.addItem(str(f['volumen']))

        # deshabilitar subdivision y fusion
        self.deshFusionSubdiv()

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
            self.lbTipoConstP.setText(data['constTipo'])

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

            # -- subdivision y fusion de fracciones
            self.cmbNvaFraccP.clear()
            #self.cmbConP.clear()
            '''
            nivConst = data['numNiveles']
            resultado = []

            for i in range(0, nivConst):
                flag = False
                for f in fra:
                    if (i + 1) == f['volumen']:
                        flag = True
                        break

                if flag:
                    continue

                resultado.append(str(i + 1))

            if len(resultado) > 0:
                self.leNivPropP.setText('1')
                self.cmbNvaFraccP.addItems(resultado)

            for f in fra:
                fraccionAct = int(self.cmbFraccionesP.currentText())

                if fraccionAct != int(f['volumen']):
                    self.cmbConP.addItem(str(f['volumen']))
            '''
            self.subdiv_fusion()
            # deshabilitar subdivision y fusion
            self.deshFusionSubdiv()

            if data['accion'] == 'new':
                self.leSupConstrFP.show()
            else:
                self.leSupConstrFP.hide()

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
                self.twCaracteristicasP.setItem(rowPosition , 6, QtWidgets.QTableWidgetItem(str(idUsoConst)))
                self.twCaracteristicasP.setItem(rowPosition , 7, QtWidgets.QTableWidgetItem(str(idCate)))

    def event_cambioUsoConstrCondo(self):

        if self.cmbUsoConstrC.count() > 0:
            index = self.cmbUsoConstrC.currentIndex()
            idUsoConst = self.cmbUsoConstrC.itemData(index)

            self.cmbCategoriaC.clear()
            self.cmbUsoEspC.clear()

            # -- obtiene categorias
            data = self.consumeWSGeneral(self.CFG.urlCedCategoriasByIdUsoConst + str(idUsoConst))
            data1 = self.consumeWSGeneral(self.CFG.urlCedUsoEspecifByIdUsoConst + str(idUsoConst))
            if data == None and data1 == None:
                return

            lenJson = len(list(data))
            lenJson1 = len(list(data1))

            self.cateConstP.clear()

            if lenJson > 0:
                for cate in data:
                    self.cmbCategoriaC.addItem(str(cate['categoria']), cate['id'])
                    d = {cate['id']: cate}
                    self.cateConstC.append(d)

            if lenJson1 > 0:
                for esp in data1:
                    self.cmbUsoEspC.addItem(str(esp['descripcion']), esp['id'])

    def event_cambioFraccCondo(self):

        if self.cmbFraccionesC.count() > 0:

            index = self.cmbFraccionesC.currentIndex()
            data = self.cmbFraccionesC.itemData(index)

            if index == -1:
                return

            if self.indexFraActualCondo != -1:
                # se manda a llamar el metodo que guarda de manera temporal
                self.fraccTempCondo()

            self.indexFraActualCondo = index

            self.lbCveUsoC.setText(data['codigoConstruccion'])

            self.lbValM2C.setText('${:,.2f}'.format(0) if data['precioM2'] is None else '${:,.2f}'.format(float(data['precioM2'])))
            self.lbValConstC.setText('${:,.2f}'.format(0) if data['valorConst'] is None else '${:,.2f}'.format(float(data['valorConst'])))
            self.lbSupConstrFC.setText(str(0) if data['supConstFraccion'] is None else str(data['supConstFraccion']))
            self.leSupConstrFC.setText(str(0) if data['supConstFraccion'] is None else str(data['supConstFraccion']))
            self.lbNvlFraccC.setText(str(1) if data['numNivel'] is None else str(data['numNivel']))
            self.leNombreC.setText('' if data['nombre'] is None else str(data['nombre']))
            self.leNvlUbicaC.setText('' if data['nvlUbica'] is None else str(data['nvlUbica']))
            self.leAnioConsC.setText('' if data['anioConstruccion'] is None else str(data['anioConstruccion']))

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
            #if data['idFactor'] != None:
                #index = self.cmbFactorConstrC.findData(data['idFactor'])
                #if index >= 0:
                    #self.cmbFactorConstrC.setCurrentIndex(index)
            #else:
                #self.cmbFactorConstrC.setCurrentIndex(0)

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
                    self.twCaracteristicasC.setItem(rowPosition , 6, QtWidgets.QTableWidgetItem(str(data['idCatUsoConstruccion'])))
                    self.twCaracteristicasC.setItem(rowPosition , 7, QtWidgets.QTableWidgetItem(str(data['idCategoria'])))

            # se llena las fracciones a fusionar
            self.cmbConC.clear()
            
            indexV = self.cmbVolumenC.currentIndex()
            dataV = self.cmbVolumenC.itemData(indexV)
            fra = dataV['fracciones']

            for f in fra:
                fraccionAct = int(self.cmbFraccionesC.currentText())

                if fraccionAct != int(f['volumen']):
                    self.cmbConC.addItem(str(f['volumen']))
            
        # deshabilitar subdivision y fusion
        self.deshFusionSubdiv(condo = True)

    # - evento de cambio de volumen en condominios 
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
            self.lbTipoConstC.setText(data['constTipo'])
            
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

            # -- subdivision y fusion de fracciones
            self.cmbNvaFraccC.clear()

            self.subdiv_fusion(condo = True)
            # deshabilitar subdivision y fusion
            self.deshFusionSubdiv(condo = True)

            if data['accion'] == 'new':
                self.leSupConstrFC.show()
            else:
                self.leSupConstrFC.hide()
            
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
                self.twCaracteristicasC.setItem(rowPosition , 6, QtWidgets.QTableWidgetItem(str(idUsoConst)))
                self.twCaracteristicasC.setItem(rowPosition , 7, QtWidgets.QTableWidgetItem(str(idCate)))

    def event_agregaColin(self):

        # obtiene el indice actual del combo, los valores de los campos
        index = self.cmbOrientacion.currentIndex()
        distanci = self.leDispPerim.text()
        descripc = self.leDescripcion.text()

        # validaciones
        if index == -1 or index == 0:
            self.createAlert('Seleccione una orientacion', icono = QMessageBox().Warning)
            return

        if len(distanci) == 0:
            self.createAlert('Defina una distancia', icono = QMessageBox().Warning)
            return

        if len(descripc) == 0:
            self.createAlert('Defina una descripcion', icono = QMessageBox().Warning)
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
            self.createAlert('Seleccione una orientacion a eliminar (seleccione todo el renglon)', icono = QMessageBox().Warning)

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
            self.createAlert("Seleccione una geometria", icono = QMessageBox().Warning)
            return
        if len(features) != 1:
            self.createAlert("Seleccione una sola geometria", icono = QMessageBox().Warning)
            return
        else:
            feat = features[0]

            nombreCalle = feat['calle']
            self.idCalleSelecc = feat['id']
            self.valorCalle = feat['valor']
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

            self.event_cancelarCalle()

    # -- metodo boton de seleccion de calle --
    def event_consultarCalle(self):

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

    # -- metodo boton de cancelar seleccion de calle --
    def event_cancelarCalle(self):

        if self.calle != None:
            if self.eventoCalleActivo:
                self.calle.selectionChanged.disconnect()
                self.eventoCalleActivo = False

        self.iface.actionSelect().trigger()
        self.btnSelCalle.setEnabled(True)
        self.abrePredio = False

    # -- metodo para calcular valor de construccion
    def event_calcularValorConstrPred(self):

        if self.cmbUsoConstrP.count() > 0:

            # se obtienen los ids de uso de construccion y categoria para obtener el precio por M2
            indexUC = self.cmbUsoConstrP.currentIndex()
            idUsoConst = self.cmbUsoConstrP.itemData(indexUC)
            if idUsoConst == -1:
                self.createAlert('Seleccione un uso de construccion', icono = QMessageBox().Warning)
                self.lbValM2P.setText('${:,.2f}'.format(0))
                self.lbValConstP.setText('${:,.2f}'.format(0))
                self.lbCveUsoP.setText('00')
                return

            indexC = self.cmbCategoriaP.currentIndex()
            idCate = self.cmbCategoriaP.itemData(indexC)

            if idCate is None:
                self.createAlert('Seleccione una categoria', icono = QMessageBox().Warning)
                self.lbValM2P.setText('${:,.2f}'.format(0))
                self.lbValConstP.setText('${:,.2f}'.format(0))
                self.lbCveUsoP.setText('00')
                return

            # se obtienen las claves de uso de construccion y categoria

            cveUso = ''
            for uc in self.usoConstr:
                l = list(uc.keys())

                if l[0] == idUsoConst:
                    values = list(uc.values())
                    cveUso = values[0]['codigo']
                    break

            cveCat = ''
            for cc in self.cateConstP:
                l = list(cc.keys())

                if l[0] == idCate:
                    values = list(cc.values())
                    cveCat = values[0]['clave']
                    break

            # consume el ws para obtener el valor de uso de construccion
            data = self.obtieneValorUsoConstr(str(idUsoConst), str(idCate))

            if len(data) == 0:
                self.createAlert('Sin informacion necesaria para calculo de valor de contruccion', icono = QMessageBox().Information)

            # calculos de valor catastral de construccion
            precioM2 = data[0]['precioM2']
            supConst = self.leSupConstrFP.text()

            valor = precioM2 * float(supConst)

            # asignacion de resultados
            self.lbValM2P.setText('${:,.2f}'.format(precioM2))
            self.lbValConstP.setText('${:,.2f}'.format(round(valor, 2)))
            self.lbCveUsoP.setText(cveUso + cveCat)

    # -- metodo para calcular valor de construccion
    def event_calcularValorConstrCond(self):

        if self.cmbUsoConstrC.count() > 0:

            # se obtienen los ids de uso de construccion y categoria para obtener el precio por M2
            indexUC = self.cmbUsoConstrC.currentIndex()
            idUsoConst = self.cmbUsoConstrC.itemData(indexUC)
            if idUsoConst == -1:
                self.createAlert('Seleccione un uso de construccion', icono = QMessageBox().Warning)
                self.lbValM2C.setText('${:,.2f}'.format(0))
                self.lbValConstC.setText('${:,.2f}'.format(0))
                self.lbCveUsoC.setText('00')
                return

            indexC = self.cmbCategoriaC.currentIndex()
            idCate = self.cmbCategoriaC.itemData(indexC)

            if idCate is None:
                self.createAlert('Seleccione una categoria', icono = QMessageBox().Warning)
                self.lbValM2C.setText('${:,.2f}'.format(0))
                self.lbValConstc.setText('${:,.2f}'.format(0))
                self.lbCveUsoC.setText('00')
                return

            # se obtienen las claves de uso de construccion y categoria

            cveUso = ''
            for uc in self.usoConstrC:
                l = list(uc.keys())

                if l[0] == idUsoConst:
                    values = list(uc.values())
                    cveUso = values[0]['codigo']
                    break

            cveCat = ''
            for cc in self.cateConstC:
                l = list(cc.keys())

                if l[0] == idCate:
                    values = list(cc.values())
                    cveCat = values[0]['clave']
                    break

            # consume el ws para obtener el valor de uso de construccion
            data = self.obtieneValorUsoConstr(str(idUsoConst), str(idCate))

            if len(data) == 0:
                self.createAlert('Sin informacion necesaria para calculo de valor de contruccion', icono = QMessageBox().Information)

            # calculos de valor catastral de construccion
            precioM2 = data[0]['precioM2']
            supConst = self.leSupConstrFC.text()

            valor = precioM2 * float(supConst)

            # asignacion de resultados
            self.lbValM2C.setText('${:,.2f}'.format(precioM2))
            self.lbValConstC.setText('${:,.2f}'.format(round(valor, 2)))
            self.lbCveUsoC.setText(cveUso + cveCat)

    # -- subdividir fracciones PREDIOS
    def event_subdividirFraccPred(self):

        self.constrTemp()
        
        if self.leNivPropP.text() == '':
            self.createAlert('Llene el campo \'Nivel. Prop\' para continuar con la subdivision', icono = QMessageBox().Warning)
            return

        newFracc = int(self.leNivPropP.text())

        if newFracc == 0:
            self.createAlert('Defina un numero mayor de niveles para la nueva fraccion', icono = QMessageBox().Warning)
            return

        # se obtiene la fraccion seleccionada
        indexFrSel = self.cmbFraccionesP.currentIndex()
        if indexFrSel == -1:
            return

        # fraccion actual seleccionada
        data = self.cmbFraccionesP.itemData(indexFrSel)

        nivActualF = data['numNivel']

        if int(nivActualF) == 1:
            self.createAlert('No se puede subdividir una fraccion con un solo nivel', icono = QMessageBox().Warning)
            return

        nivActualC = self.leNivPropP.text()
        if int(nivActualC) >= int(nivActualF):
            self.createAlert('EL Nivel propuesto es mayor o igual al nivel global', icono = QMessageBox().Warning)
            return

        # sumatoria de las superficie de contruccion de todas las fracciones del volumen Y
        # numero de niveles de todas las fracciones del volumen
        count = self.cmbFraccionesP.count()
        sumSupConstxFracc = 0
        sumNumNivelConstxFracc = 0
        for indx in range(0, count):
            dataTemp = self.cmbFraccionesP.itemData(indx)
            sumSupConstxFracc += float(dataTemp['supConstFraccion'])
            sumNumNivelConstxFracc += int(dataTemp['numNivel'])

        # quitar nivel a la fraccion a subdividir
        # calcular la nueva superficie del nivel a subdividir
        # 'nivActualF' -> nivel de la fraccion
        # 'nivActualC' -> nivel propuesto (en el line edit)
        newNum = int(nivActualF) - int(nivActualC)
        newSuper = (sumSupConstxFracc / sumNumNivelConstxFracc) * newNum
        data['supConstFraccion'] = round(newSuper, 2)
        data['numNivel'] = newNum
        data['precioM2'] = 0
        data['valorConst'] = 0

        self.lbNvlFraccP.setText(str(newNum))
        self.lbSupConstrFP.setText(str(round(newSuper, 2)))
        self.lbValM2P.setText('${:,.2f}'.format(0))
        self.lbValConstP.setText('${:,.2f}'.format(0))

        # nueva fraccion
        fr = {}
        fr['volumen'] = int(self.cmbNvaFraccP.currentText())
        fr['numNivel'] = int(nivActualC)
        fr['supConstFraccion'] = round((sumSupConstxFracc / sumNumNivelConstxFracc) * int(nivActualC), 2)
        fr['idConstruccion'] = data['idConstruccion']
        fr['idPredio'] = data['idPredio']
        fr['cveCatastral'] = data['cveCatastral']
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
        # fr['idFactor'] = -1
        fr['caracCategorias'] = []

        # realizar el cambio en la fraccion
        self.cmbFraccionesP.setItemData(indexFrSel, data)
        # agregar la nueva fraccion
        self.cmbFraccionesP.addItem(str(fr['volumen']), fr)

        # actualizar combo para fusionar y subdividir
        # ---- CARGA DE FRACCIONES

        indexVolSel = self.cmbVolumenP.currentIndex()
        dataV = self.cmbVolumenP.itemData(indexVolSel)

        # -- subdivision y fusion de fracciones
        self.cmbNvaFraccP.clear()
        self.cmbConP.clear()
        '''
        nivConst = dataV['numNiveles']
        resultado = []

        fra = []
        count = self.cmbFraccionesP.count()
        for indx in range(0, count):
            dataTemp = self.cmbFraccionesP.itemData(indx)
            fra.append(dataTemp)

        for i in range(0, nivConst):
            flag = False
            for f in fra:
                if (i + 1) == f['volumen']:
                    flag = True
                    break

            if flag:
                continue

            resultado.append(str(i + 1))

        if len(resultado) > 0:
            self.leNivPropP.setText('1')
            self.cmbNvaFraccP.addItems(resultado)

        # se llena las fracciones a fusionar
        for f in fra:
            fraccionAct = int(self.cmbFraccionesP.currentText())

            if fraccionAct != int(f['volumen']):
                self.cmbConP.addItem(str(f['volumen']))
        '''
        self.subdiv_fusion()
        self.constrTemp()

        # deshabilitar subdivision y fusion
        self.deshFusionSubdiv()

    # -- subdividir fracciones CONDOMINIOS
    def event_subdividirFraccCond(self):

        # autoguardado
        self.constrTempCondo()

        if self.leNivPropC.text() == '':
            self.createAlert('Llene el campo \'Nivel. Prop\' para continuar con la subdivision', icono = QMessageBox().Warning)
            return

        newFracc = int(self.leNivPropC.text())

        if newFracc == 0:
            self.createAlert('Defina un numero mayor de niveles para la nueva fraccion', icono = QMessageBox().Warning)
            return

        # se obtiene la fraccion seleccionada
        indexFrSel = self.cmbFraccionesC.currentIndex()
        if indexFrSel == -1:
            return

        # fraccion actual seleccionada
        data = self.cmbFraccionesC.itemData(indexFrSel)

        nivActualF = data['numNivel']

        if int(nivActualF) == 1:
            self.createAlert('No se puede subdividir una fraccion con un solo nivel', icono = QMessageBox().Warning)
            return

        nivActualC = self.leNivPropC.text()
        if int(nivActualC) >= int(nivActualF):
            self.createAlert('EL Nivel propuesto es mayor o igual al nivel global', icono = QMessageBox().Warning)
            return

        # sumatoria de las superficie de contruccion de todas las fracciones del volumen Y
        # numero de niveles de todas las fracciones del volumen
        count = self.cmbFraccionesC.count()
        sumSupConstxFracc = 0
        sumNumNivelConstxFracc = 0
        for indx in range(0, count):
            dataTemp = self.cmbFraccionesC.itemData(indx)
            sumSupConstxFracc += float(dataTemp['supConstFraccion'])
            sumNumNivelConstxFracc += int(dataTemp['numNivel'])

        # quitar nivel a la fraccion a subdividir
        # calcular la nueva superficie del nivel a subdividir
        # 'nivActualF' -> nivel de la fraccion
        # 'nivActualC' -> nivel propuesto (en el line edit)
        newNum = int(nivActualF) - int(nivActualC)
        newSuper = (sumSupConstxFracc / sumNumNivelConstxFracc) * newNum
        data['supConstFraccion'] = round(newSuper, 2)
        data['numNivel'] = newNum
        data['precioM2'] = 0
        data['valorConst'] = 0

        self.lbNvlFraccC.setText(str(newNum))
        self.lbSupConstrFC.setText(str(round(newSuper, 2)))
        self.lbValM2C.setText('${:,.2f}'.format(0))
        self.lbValConstC.setText('${:,.2f}'.format(0))

        # nueva fraccion
        fr = {}
        fr['volumen'] = int(self.cmbNvaFraccC.currentText())
        fr['numNivel'] = int(nivActualC)
        fr['supConstFraccion'] = (sumSupConstxFracc / sumNumNivelConstxFracc) * int(nivActualC)
        fr['idConstruccion'] = data['idConstruccion']
        fr['idPredio'] = data['idPredio']
        fr['cveCatastral'] = data['cveCatastral']
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
        # fr['idFactor'] = -1
        fr['caracCategorias'] = []

        # realizar el cambio en la fraccion
        self.cmbFraccionesC.setItemData(indexFrSel, data)
        # agregar la nueva fraccion
        self.cmbFraccionesC.addItem(str(fr['volumen']), fr)

        # actualizar combo para fusionar y subdividir
        # ---- CARGA DE FRACCIONES

        indexVolSel = self.cmbVolumenC.currentIndex()
        dataV = self.cmbVolumenC.itemData(indexVolSel)

        # -- subdivision y fusion de fracciones
        self.cmbNvaFraccC.clear()
        self.cmbConC.clear()

        self.subdiv_fusion(condo = True)
        self.constrTempCondo()

        # deshabilitar subdivision y fusion
        self.deshFusionSubdiv(condo = True)

    # -- fusionar fracciones PREDIO
    def event_fusionarFraccPred(self):

        # se guarda la fraccion
        #self.constrTemp()
        self.fraccTemp()

        # se obtiene la fraccion seleccionada
        indexFrSel = self.cmbFraccionesP.currentIndex()
        data1 = self.cmbFraccionesP.itemData(indexFrSel)

        # se busca la fraccion que se selecciono como segunda parte de la fusion
        numFracc = int(self.cmbConP.currentText())
        data2 = None
        indexFrSel2 = -1

        count = self.cmbFraccionesP.count()
        for indx in range(0, count):
            dataTemp = self.cmbFraccionesP.itemData(indx)

            if dataTemp['volumen'] == numFracc:
                data2 = dataTemp
                indexFrSel2 = indx
                break

        obj = fusionDialog(data1, data2)
        
        # regresa un 0 o un 1
        # 0 = RECHAZADO = CANCELAR
        # 1 = ACEPTADO  = ACEPTAR
        resultado = obj.exec()

        if resultado == 0:
            self.createAlert('Accion Cancelada', icono = QMessageBox().Warning)
            return

        # sumatoria de las superficie de contruccion de todas las fracciones del volumen Y
        # numero de niveles de todas las fracciones del volumen
        count = self.cmbFraccionesP.count()
        sumSupConstxFracc = 0
        sumNumNivelConstxFracc = 0
        for indx in range(0, count):
            dataTemp = self.cmbFraccionesP.itemData(indx)
            sumSupConstxFracc += float(dataTemp['supConstFraccion'])
            sumNumNivelConstxFracc += int(dataTemp['numNivel'])

        # obj._seleccion booleano
        # TRUE  = se selecciono una fraccion: se intercambia la fraccion seleccionada por la que esta seleccionada
        # FALSE = no se selecciono ninguna: se crea una fraccion vacia y se queda en el lugar actual
        if obj._seleccion:

            newData = obj._seleccionada
            oldData = obj._noSeleccionada

            newNivel = int(data1['numNivel']) + int(data2['numNivel'])
            newData['numNivel'] = newNivel
            newData['supConstFraccion'] = (sumSupConstxFracc / sumNumNivelConstxFracc) * int(newNivel)
            newData['precioM2'] = 0
            newData['valorConst'] = 0

            # realizar el cambio en la fraccion
            # self.cmbFraccionesP.setItemData(indexFrSel, newData)
            fraccionesTemp = []
            count = self.cmbFraccionesP.count()
            for indx in range(0, count):
                dataTemp = self.cmbFraccionesP.itemData(indx)

                if int(dataTemp['volumen']) == int(oldData['volumen']):
                    continue

                if int(dataTemp['volumen']) == int(newData['volumen']):
                    fraccionesTemp.append(newData)
                else:
                    fraccionesTemp.append(dataTemp)

            self.cmbFraccionesP.clear()

            for ft in fraccionesTemp:
                self.cmbFraccionesP.addItem(str(ft['volumen']), ft)


        else:
            # nueva fraccion
            newNivel = int(data1['numNivel']) + int(data2['numNivel'])

            fr = {}
            fr['volumen'] = int(data1['volumen'])
            fr['numNivel'] = newNivel
            fr['supConstFraccion'] = (sumSupConstxFracc / sumNumNivelConstxFracc) * int(newNivel)
            fr['idConstruccion'] = data1['idConstruccion']
            fr['idPredio'] = data1['idPredio']
            fr['cveCatastral'] = data1['cveCatastral']
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
            # fr['idFactor'] = -1
            fr['caracCategorias'] = []

            # realizar el cambio en la fraccion
            fraccionesTemp = []
            fraccionesTemp.append(fr)
            count = self.cmbFraccionesP.count()
            for indx in range(0, count):
                dataTemp = self.cmbFraccionesP.itemData(indx)

                if int(dataTemp['volumen']) == int(data2['volumen']):
                    continue

                if int(dataTemp['volumen']) == int(data1['volumen']):
                    continue

                fraccionesTemp.append(dataTemp)

            self.cmbFraccionesP.clear()

            for ft in fraccionesTemp:
                self.cmbFraccionesP.addItem(str(ft['volumen']), ft)

        # eliminar la fraccion anterior
        #self.cmbFraccionesP.removeItem(indexFrSel2)
        self.cmbConP.clear()
        self.cmbNvaFraccP.clear()

        self.constrTemp()
        self.subdiv_fusion()
        self.deshFusionSubdiv()

    # -- fusionar fracciones CONDOMINIO
    def event_fusionarFraccCond(self):

        # se guarda la fraccion
        self.fraccTempCondo()

        # se obtiene la fraccion seleccionada
        indexFrSel = self.cmbFraccionesC.currentIndex()
        data1 = self.cmbFraccionesC.itemData(indexFrSel)

        # se busca la fraccion que se selecciono como segunda parte de la fusion
        numFracc = int(self.cmbConC.currentText())
        data2 = None
        indexFrSel2 = -1

        count = self.cmbFraccionesC.count()
        for indx in range(0, count):
            dataTemp = self.cmbFraccionesC.itemData(indx)

            if dataTemp['volumen'] == numFracc:
                data2 = dataTemp
                indexFrSel2 = indx
                break

        obj = fusionDialog(data1, data2)

        # regresa un 0 o un 1
        # 0 = RECHAZADO = CANCELAR
        # 1 = ACEPTADO  = ACEPTAR
        resultado = obj.exec()

        if resultado == 0:
            self.createAlert('Accion Cancelada', icono = QMessageBox().Warning)
            return

        # sumatoria de las superficie de contruccion de todas las fracciones del volumen Y
        # numero de niveles de todas las fracciones del volumen
        count = self.cmbFraccionesC.count()
        sumSupConstxFracc = 0
        sumNumNivelConstxFracc = 0
        for indx in range(0, count):
            dataTemp = self.cmbFraccionesC.itemData(indx)
            sumSupConstxFracc += float(dataTemp['supConstFraccion'])
            sumNumNivelConstxFracc += int(dataTemp['numNivel'])

        # obj._seleccion booleano
        # TRUE  = se selecciono una fraccion: se intercambia la fraccion seleccionada por la que esta seleccionada
        # FALSE = no se selecciono ninguna: se crea una fraccion vacia y se queda en el lugar actual
        if obj._seleccion:

            newData = obj._seleccionada
            oldData = obj._noSeleccionada

            newNivel = int(data1['numNivel']) + int(data2['numNivel'])
            newData['numNivel'] = newNivel
            newData['supConstFraccion'] = round(((sumSupConstxFracc / sumNumNivelConstxFracc) * int(newNivel)), 2)
            newData['precioM2'] = 0
            newData['valorConst'] = 0

            # realizar el cambio en la fraccion
            # self.cmbFraccionesP.setItemData(indexFrSel, newData)
            fraccionesTemp = []
            count = self.cmbFraccionesC.count()
            for indx in range(0, count):
                dataTemp = self.cmbFraccionesC.itemData(indx)

                if int(dataTemp['volumen']) == int(oldData['volumen']):
                    continue

                if int(dataTemp['volumen']) == int(newData['volumen']):
                    fraccionesTemp.append(newData)
                else:
                    fraccionesTemp.append(dataTemp)

            self.cmbFraccionesC.clear()

            for ft in fraccionesTemp:
                self.cmbFraccionesC.addItem(str(ft['volumen']), ft)

        else:
            # nueva fraccion
            newNivel = int(data1['numNivel']) + int(data2['numNivel'])

            fr = {}
            fr['volumen'] = int(data1['volumen'])
            fr['numNivel'] = newNivel
            fr['supConstFraccion'] = round(((sumSupConstxFracc / sumNumNivelConstxFracc) * int(newNivel)), 2)
            fr['idConstruccion'] = data1['idConstruccion']
            fr['idPredio'] = data1['idPredio']
            fr['cveCatastral'] = data1['cveCatastral']
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
            # fr['idFactor'] = -1
            fr['caracCategorias'] = []

            # realizar el cambio en la fraccion
            fraccionesTemp = []
            fraccionesTemp.append(fr)
            count = self.cmbFraccionesC.count()
            for indx in range(0, count):
                dataTemp = self.cmbFraccionesC.itemData(indx)

                if int(dataTemp['volumen']) == int(data2['volumen']):
                    continue

                if int(dataTemp['volumen']) == int(data1['volumen']):
                    continue

                fraccionesTemp.append(dataTemp)

            self.cmbFraccionesC.clear()

            for ft in fraccionesTemp:
                self.cmbFraccionesC.addItem(str(ft['volumen']), ft)

        # eliminar la fraccion anterior
        self.cmbConC.clear()
        self.cmbNvaFraccC.clear()

        self.constrTempCondo()
        self.subdiv_fusion(condo = True)
        self.deshFusionSubdiv(condo = True)

    # -- nueva construccion PREDIO
    def event_nuevaConstrC(self):

        count = self.cmbVolumenP.count()
        if count == 0:
            self.seRealiza = False

        # autoguardado
        self.constrTemp()
        
        volumen = ''

        # se obtienen todos los volumenes de predios
        # en forma de una cadena (v1v2v3v4)
        idPredio = None
        for index in range(0, count):
            volumen += self.cmbVolumenP.itemData(index)['nomVolumen']
            idPredio = self.cmbVolumenP.itemData(index)['idPredio']
        # obtener el numero maximo de volumen
        maxVol = 0
        if volumen != '':

            # se obtienen, en forma de lista, los numeros de los volumenes
            lVolT = volumen.lower().split('v')

            maxVol = int(max(lVolT))

        # creacion de la nueva construccion
        
        construccion = {}

        construccion['accion'] = 'new'
        construccion['anioConstruccion'] = None
        construccion['caracCategoriaEConstruccion'] = []
        construccion['catUsoEspecificos'] = []
        construccion['codigoConstruccion'] = None
        construccion['constTipo'] = 'Construccion'
        construccion['cveCatastral'] = self.cveCatastral
        construccion['cveConstEsp'] = None
        construccion['fechaAct'] = None
        construccion['guardado'] = False
        construccion['id'] = None
        construccion['idCatDestino'] = None
        construccion['idCatEstadoConstruccion'] = None
        construccion['idCatUsoConstruccion'] = None
        construccion['idCategoria'] = None
        construccion['idCondominioHorizontal'] = None
        construccion['idCondominioVertical'] = None
        construccion['idFactor'] = None
        construccion['idPredio'] = idPredio
        construccion['idTipoConstruccion'] = 1
        construccion['nomVolumen'] = 'V' + str(maxVol + 1)
        construccion['nombre'] = None
        construccion['numNiveles'] = 1
        construccion['precioM2'] = None
        construccion['supConst'] = 0
        construccion['tipoCalculo'] = None
        construccion['valorConst'] = None
        construccion['volumen'] = None

        fra = []

        fr = {}
        fr['anioConstruccion'] = None
        fr['caracCategorias'] = []
        fr['codigoConstruccion'] = None
        fr['cveCatastral'] = self.cveCatastral
        fr['fechaAct'] = None
        fr['idCatDestino'] = None
        fr['idCatEstadoConstruccion'] = None
        fr['idCatUsoConstruccion'] = None
        fr['idCatUsoEspecifico'] = None
        fr['idCategoria'] = None
        fr['idConstruccion'] = None
        fr['idFactor'] = None
        fr['idPredio'] = idPredio
        fr['idTipoFactor'] = None
        fr['nombre'] = None
        fr['numNivel'] = 1
        fr['nvlUbica'] = None
        fr['precioM2'] = None
        fr['supConstFraccion'] = 0
        fr['tipoCalculo'] = None
        fr['valorConst'] = None
        fr['volumen'] = 1

        fra.append(fr)

        construccion['fracciones'] = fra
        
        self.cmbVolumenP.addItem(str(construccion['nomVolumen']), construccion)

        self.createAlert('Proceso Concluido', QMessageBox.Information)

        if count == 0:
            self.habilitaConstr()
        
    # -- eliminacion de construccion PREDIO
    # - se permite eliminar la construccion si y solo si 
    # - la construccion NOOOO tiene geometria asociada
    def event_elimConstrC(self):
        
        # autoguardado
        self.constrTemp()
        
        # se obtienen todos los volumenes de predios
        # en forma de una cadena (v1v2v3v4)
        count = self.cmbVolumenP.count()

        if count == 0:
            return

        # se obtiene la construccion actual
        index = self.cmbVolumenP.currentIndex()
        data = self.cmbVolumenP.itemData(index)

        idConst = data['id']
        elimina = False

        if idConst is not None:

            # consumir ws para saber si la construccion tiene geometria
            tieneGeom = self.verificaSiTieneGeomWS(idConst, self.CFG.urlVerifSiTieneGeomConstP)
            elimina = not tieneGeom
        else:
            elimina = True

        # - SI se eliminara la construccion
        if elimina:

            # si cuenta con un indentificador (id) significa que la informacion se encuentra en la base de datos
            # si NOOO tiene id, solo se elimina de memoria
            if idConst is not None:

                # la construccion se borrara directamente de la base de datos
                # por eso se espera confirmacion del usuario
                reply = QMessageBox.question(self,'Construccion', 'La construccion se eliminara definitivamente, ¿desea continuar?', QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    
                    # se envia al ws la construccion a eliminar
                    data['accion'] = 'delete'

                    payload = []
                    payload.append(data)

                    resp = self.guardaConstrPredWS(payload, data['accion'], url = self.CFG.urlGuardaVolumenP)

                    if resp == 'OK':
                        self.createAlert('Eliminacion correcta', QMessageBox.Information)

                        # se elimina del combo de construcciones

                        '''
                        construccionesTemp = []
                        count = self.cmbVolumenP.count()
                        for indx in range(0, count):
                            dataTemp = self.cmbVolumenP.itemData(indx)

                            if str(dataTemp['nomVolumen']) == str(data['nomVolumen']):
                                continue

                            construccionesTemp.append(dataTemp)

                        self.cmbVolumenP.clear()

                        for ct in construccionesTemp:
                            self.cmbVolumenP.addItem(str(ct['nomVolumen']), ct)
                        '''
                        self.seRealiza = False
                        self.cmbVolumenP.removeItem(index)

                else:
                    return
            else:

                reply = QMessageBox.question(self,'Construccion', '¿Desea eliminar la construccion?', QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.seRealiza = False
                    self.cmbVolumenP.removeItem(index)
                else:
                    return
            
        else: # <- NOOO se elimina, debido a que cuenta con geometria asociada
            self.createAlert('La construccion no se permite eliminar ya que cuenta con informacion cartografica')

        # si ya no hay construcciones
        # se limpia el formulario y se deshabilitan los controles

        count = self.cmbVolumenP.count()

        if count == 0:
            self.deshabilitaConstr()
            self.limpiaConstrucciones()




    # -- GUARDAR   P R E D I O 
    def event_guardarPredio(self):
        data = self.cedula
        
        self.event_cambioPestania(index = 3)

        # --- VALIDACIONES --- 
        texto = self.pteObservaciones.toPlainText()
        if len(texto) >= 200:
            self.createAlert('Las longitud de las observaciones sobrepasa el limite permitido (200 caracteres)', QMessageBox.Information)

        # prepara PREDIO para guardado

        # -- UBICACION --
        # tipo predio
        index = self.cmbTipoPredio.currentIndex()
        cveTipoPred = self.cmbTipoPredio.itemData(index)
        data['cveTipoPred'] = None if str(cveTipoPred) == '-1' else cveTipoPred

        # num predio
        data['numPredio'] = None if self.leNumPredio.text() == '' else self.leNumPredio.text()

        # regimen de propiedad
        index = self.cmbRegimenProp.currentIndex()
        idRegProp = self.cmbRegimenProp.itemData(index)
        data['idRegimenPropiedad'] = None if int(idRegProp) == -1 else idRegProp

        # no exterior alf
        data['numExteriorAlf'] = None if self.leNoExteriorAlf.text() == '' else self.leNoExteriorAlf.text()

        # no exterior ant
        data['numExteriorAnt'] = None if self.leNoExteAnt.text() == '' else self.leNoExteAnt.text()

        # observaciones
        data['observaciones'] = None if self.pteObservaciones.toPlainText() == '' else self.pteObservaciones.toPlainText()

        # uso de suelo (cveUsoSuelo)
        index = self.cmbTipoAsentH.currentIndex()
        idTipoAsH = self.cmbTipoAsentH.itemData(index)
        data['idTipoAsentamiento'] = None if int(idTipoAsH) == -1 else idTipoAsH

        data['calles'] = []

        if self.idCalleSelecc != -1:

            calle = {}
            calle['valor'] = None
            calle['longitud'] = None
            calle['idCveVialidad'] = None
            calle['cveVialidad'] = None
            calle['tipoVectorCalle'] = None
            calle['calle'] = None
            calle['id'] = self.idCalleSelecc
            calle['tipovialidad'] = None
            calle['abreviatura'] = None
            calle['categoria'] = None

            data['calles'].append(calle)

        # grupos subgrupos y caracteristicas
        allRows = self.twColindancias.rowCount()
        colindancias = []
        for row in range(0,allRows):
            caract = {}
            twi0 = self.twColindancias.item(row,0)
            twi1 = self.twColindancias.item(row,1)
            twi2 = self.twColindancias.item(row,2)
            twi3 = self.twColindancias.item(row,3)

            caract['id'] = None
            caract['cveCatastral'] = None
            caract['superficieColindacia'] = twi2.text()
            caract['desscripcion'] = twi3.text()
            caract['claveProp'] = None
            caract['idCatColindancia'] = twi0.text()
            caract['catColindancia'] = twi1.text()

            colindancias.append(caract)
        
        data['colindancias'] = colindancias

        # -- TERRENO --
        # fondo
        data['fondo'] = None if self.leFondo.text() == '' else float(self.leFondo.text())

        # frente
        data['frente'] = None if self.leFrente.text() == '' else float(self.leFrente.text())

        # valor de terreno (cveVus)
        index = self.cmbValorTerr.currentIndex()
        cveVus = self.cmbValorTerr.itemData(index)
        data['cveVus'] = None if str(cveVus) == '-1' else cveVus

        # uso de suelo (cveUsoSuelo)
        index = self.cmbUsoSuelo.currentIndex()
        cveUsoSuelo = self.cmbUsoSuelo.itemData(index)
        data['cveUsoSuelo'] = None if str(cveUsoSuelo) == '-1' else cveUsoSuelo

        # facilidad de comunicacion
        index = self.cmbFacilComun.currentIndex()
        idFacCom = self.cmbFacilComun.itemData(index)
        data['idFacilidadComunicacion'] = None if idFacCom == -1 else idFacCom

        # predio forma
        index = self.cmbFormaPredio.currentIndex()
        idPredForm = self.cmbFormaPredio.itemData(index)
        data['idPredioForma'] = None if int(idPredForm) == -1 else idPredForm

        # predio ubicacion manzana
        index = self.cmbOrientPredMza.currentIndex()
        idPredUbicMza = self.cmbOrientPredMza.itemData(index)
        data['idPredioUbicacion_manzana'] = None if int(idPredUbicMza) == -1 else idPredUbicMza

        # tipo relieve
        index = self.cmbTipoRelieve.currentIndex()
        idTipoRelieve = self.cmbTipoRelieve.itemData(index)
        data['idTipoRelieve'] = None if int(idTipoRelieve) == -1 else idTipoRelieve

        # valores catastrales
        data['valorCatastral'] = self.lbValorCTotalC.text().replace('$', '').replace(',', '')
        data['valorConstruccion'] = self.lbValConsTotalC.text().replace('$', '').replace(',', '')
        data['valorTerreno'] = self.lbValTerrTotalC.text().replace('$', '').replace(',', '')

        # nombre
        data['nombre'] = None if self.leNombre.text() == '' else self.leNombre.text()

        # --- G U A R D A   P R E D I O S ---
        resp = self.guardaPredioWS(predio = data, url = self.CFG.urlGuardaPredio)

        if resp == 'OK':

            # -- GUARDADO DE SERVICIOS DE PREDIO
            if self.twServiciosPredio.rowCount() > 0:       

                tablaServicios = self.twServiciosPredio

                listaServicios = []
                for x in range(0, tablaServicios.rowCount()):

                    if tablaServicios.item(x,0).checkState() == 2:
                        servicio = {}
                        servicio['descripcion'] = tablaServicios.item(x,0).text()
                        servicio['disponible'] = True
                        servicio['servicio'] = tablaServicios.item(x,1).text()
                        listaServicios.append(servicio)

                # consumir ws para guardar los servicios
                resp = self.guardaServiciosPredWS(listaServicios, cveCata = self.cveCatastral, url = self.CFG.urlGuardaServiciosP)

                if resp != 'OK':
                    return

            self.createAlert('Guardado correcto', QMessageBox.Information)

            # - refresca fecha de actualizacion
            # - y revisores
            self.lbRevisorAnt.setText(self.lbRevisor.text())
            now = datetime.datetime.now()
            self.lbUltFechaAct.setText(str(now)[0:19])

    # -- GUARDAR   V O L U M E N   SELECCIONADO
    def event_guardarVolP(self):

        # autoguardado
        self.constrTemp()

        countVol = self.cmbVolumenP.count()

        if countVol == 0:
            return

        # se obtiene el volumen
        indexC = self.cmbVolumenP.currentIndex()
        volumen = self.cmbVolumenP.itemData(indexC)
        frTemp = volumen['fracciones']
        fracciones = []

        idPredio = self.cedula['id']

        supConst = 0

        for fr in frTemp:

            if volumen['accion'] == 'new':
                fr['idPredio'] = idPredio

            # destino
            fr['idCatDestino'] = None if str(fr['idCatDestino']) == '-1' else fr['idCatDestino']

            # estado de construccion
            fr['idCatEstadoConstruccion'] = None if str(fr['idCatEstadoConstruccion']) == '-1' else fr['idCatEstadoConstruccion']

            # uso de construccion
            fr['idCatUsoConstruccion'] = None if str(fr['idCatUsoConstruccion']) == '-1' else fr['idCatUsoConstruccion']

            # uso especifico
            fr['idCatUsoEspecifico'] = None if str(fr['idCatUsoEspecifico']) == '-1' else fr['idCatUsoEspecifico']
            
            # categoria
            fr['idCategoria'] = None if str(fr['idCategoria']) == '-1' else fr['idCategoria']
            
            # factor
            # fr['idFactor'] = None if str(fr['idFactor']) == '-1' else fr['idFactor']
            
            # tipo de factor
            # fr['idTipoFactor'] = None if str(fr['idTipoFactor']) == '-1' else fr['idTipoFactor']

            supConst += float(fr['supConstFraccion'])

            fracciones.append(fr)

        volumen['fracciones'] = fracciones

        if volumen['accion'] == 'new':
            volumen['supConst'] = round(supConst, 2)
            volumen['idPredio'] = idPredio


        payload = []
        payload.append(volumen)

        resp = self.guardaConstrPredWS(payload, volumen['accion'], url = self.CFG.urlGuardaVolumenP)

        if resp == 'OK':
            self.createAlert('Guardado correcto', QMessageBox.Information)

    # GUARDAR   V O L U M E N   SELECCIONADO (C O N D O M I N I O)
    def event_guardarVolC(self):

        # autoguardado
        self.constrTempCondo()

        countVol = self.cmbVolumenC.count()

        if countVol == 0:
            return

        # se obtiene el volumen
        indexC = self.cmbVolumenC.currentIndex()
        volumen = self.cmbVolumenC.itemData(indexC)
        frTemp = volumen['fracciones']
        fracciones = []

        supConst = 0

        for fr in frTemp:

            # destino
            fr['idCatDestino'] = None if str(fr['idCatDestino']) == '-1' else fr['idCatDestino']

            # estado de construccion
            fr['idCatEstadoConstruccion'] = None if str(fr['idCatEstadoConstruccion']) == '-1' else fr['idCatEstadoConstruccion']

            # uso de construccion
            fr['idCatUsoConstruccion'] = None if str(fr['idCatUsoConstruccion']) == '-1' else fr['idCatUsoConstruccion']

            # uso especifico
            fr['idCatUsoEspecifico'] = None if str(fr['idCatUsoEspecifico']) == '-1' else fr['idCatUsoEspecifico']
            
            # categoria
            fr['idCategoria'] = None if str(fr['idCategoria']) == '-1' else fr['idCategoria']
            
            # factor
            # fr['idFactor'] = None if str(fr['idFactor']) == '-1' else fr['idFactor']
            
            # tipo de factor
            # fr['idTipoFactor'] = None if str(fr['idTipoFactor']) == '-1' else fr['idTipoFactor']

            supConst += float(fr['supConstFraccion'])

            fracciones.append(fr)


        volumen['fracciones'] = fracciones

        if volumen['accion'] == 'new':
            volumen['supConst'] = round(supConst, 2)

        payload = []
        payload.append(volumen)

        resp = self.guardaConstrPredWS(payload, volumen['accion'], url = self.CFG.urlGuardaVolumenP)

        if resp == 'OK':
            self.createAlert('Guardado correcto', QMessageBox.Information)

    # -- GUARDAR   C O N D O M I N I O   SELECCIONADO
    def event_guardarCondominio(self):

        # seleccion del condominio actual
        index = self.cmbCondo.currentIndex()
        tipoCond = self.cmbCondo.itemData(index) # <---- tipo de condominio
        clave = self.cmbCondo.currentText()      # <---- clave de condominio

        self.event_cambioPestania(index = 5)

        # guardado temporal
        self.condoTemp(self.cveCatastral + clave)

        condSave = None

        for cond in self.condominios:
            if cond['cveCat'] == self.cveCatastral + clave:
                condSave = cond
                break

        if condSave is None:
            self.createAlert('Nada para guardar (condominios)', QMessageBox.Information)
            return

        payload = []
        payload.append(condSave)

        '''
        condSave['valorConstruccionPriv'] = condSave['valorConstruccionPriv'].replace('$', '').replace(',', '')
        condSave['valorConstruccionComun'] = condSave['valorConstruccionComun'].replace('$', '').replace(',', '')
        condSave['valorConstExc'] = condSave['valorConstExc'].replace('$', '').replace(',', '')

        condSave['valorTerrenoPriv'] = condSave['valorTerrenoPriv'].replace('$', '').replace(',', '')
        condSave['valorTerrenoComun'] = condSave['valorTerrenoComun'].replace('$', '').replace(',', '')
        condSave['valorTerrExc'] = condSave['valorTerrExc'].replace('$', '').replace(',', '')
        '''
        # --- G U A R D A D O   D E   C O N D O M I N I O S ---
        resp = self.guardaCondominioWS(payload, tipoCond, url = self.CFG.urlGuardaCondominio)

        if resp == 'OK':

            # -- GUARDADO DE SERVICIOS DE PREDIO
            if self.twServiciosCondo.rowCount() > 0:       

                tablaServicios = self.twServiciosCondo

                listaServicios = []
                for x in range(0, tablaServicios.rowCount()):

                    if tablaServicios.item(x,0).checkState() == 2:
                        servicio = {}
                        servicio['descripcion'] = tablaServicios.item(x,0).text()
                        servicio['disponible'] = True
                        servicio['servicio'] = tablaServicios.item(x,1).text()
                        listaServicios.append(servicio)

                # consumir ws para guardar los servicios
                resp = self.guardaServiciosPredWS(listaServicios, cveCata = self.cveCatastral + clave, url = self.CFG.urlGuardaServiciosP)

                if resp != 'OK':
                    return

            # - guardado de servicios de condominio
            self.createAlert('Guardado correcto', QMessageBox.Information)

    # -- cambio de pestania para detectar cuando se abra la del COMPARATIVO
    # -- para realizar calculos cada vez que se entre a dicha pestania
    def event_cambioPestania(self, index): #changed!

        # index = 5: se trata de la posicion de la pestania del COMPARATIVO cuando se abra un CONDOMINIO
        # index = 3: se trata de la posicion de la pestania del COMPARATIVO cuando se abra un PREDIO
        if index == 5 or index == 3:

            # -- TRUE  -> es condominio
            # -- FALSE -> NO es condominio
            if self.cond:

                # carga condominios en pestania 3 (Condominio)


                # seleccion del condominio actual
                index = self.cmbCondo.currentIndex()
                tipoCond = self.cmbCondo.itemData(index) # <---- tipo de condominio
                clave = self.cmbCondo.currentText()      # <---- clave de condominio

                condSave = None

                for cond in self.condominios:
                    if cond['cveCat'] == self.cveCatastral + clave:
                        condSave = cond
                        break

                if condSave is None:
                    return

                # autoguardado condominio
                self.condoTemp(self.cveCatastral + clave)

                # --- SUPERFICIES
                # - TERRENO
                self.lbSupTerrPrivC.setText(str(condSave['supTerPrivada'] or 0))
                self.lbSupTerrComC.setText(str(condSave['supTerComun'] or 0))

                supT = (condSave['supTerPrivada'] or 0) + (condSave['supTerComun'] or 0)

                self.lbSupTerrTotalC.setText(str(round(supT, 2)))
                # self.leSupConstTotalCond.setText(str(round(supT + (condSave['supTerrComunEx'] or 0), 2)))
                self.leSupConstTotalCond.setText(str(round(supT)))

                # - CONSTRUCCION
                self.lbSupConsPrivC.setText(str(condSave['supConstruccionPrivada'] or 0))
                self.lbSupConsComC.setText(str(condSave['supConstruccionComun'] or 0))

                supC = (condSave['supConstruccionPrivada'] or 0) + (condSave['supConstruccionComun'] or 0)

                self.lbSupConsTotalC.setText(str(round(supC, 2)))
                #self.leSupConstTotalCond.setText(str(round(supC + (condSave['supConstComunEx'] or 0), 2)))
                self.leSupConstTotalCond.setText(str(round(supC)))

                # --- VALORES CATASTRALES
                # - TERRENO
                self.lbValTerrPrivC.setText('${:,.2f}'.format(condSave['valorTerrenoPriv']))
                self.lbValTerrComC.setText('${:,.2f}'.format(condSave['valorTerrenoComun']))

                valT = (condSave['valorTerrenoPriv'] or 0) + (condSave['valorTerrenoComun'] or 0)

                self.lbValTerrTotalC.setText('${:,.2f}'.format(round(valT, 2)))
                # self.leValTerrTotalCond.setText('${:,.2f}'.format(round(valT + (condSave['valorTerrExc'] or 0), 2)))
                self.leValTerrTotalCond.setText('${:,.2f}'.format(round(valT)))

                # - CONSTRUCCION




                fracciones = []
                valorConst = 0

                # guardado temporal
                self.constrTempCondo()
                # se obtienen todos los volumenes de predios
                count = self.cmbVolumenC.count()
                for index in range(0, count):
                    
                    fracciones = self.cmbVolumenC.itemData(index)['fracciones']
                    
                    if len(fracciones) == 0:
                        continue

                    for fr in fracciones:
                        valorConst += float(fr['valorConst'] or 0)

                valorPRIVADO = '${:,.2f}'.format(round(valorConst, 2))


                self.lbValConsTotalC.setText(valorPRIVADO)






                # self.lbValConsPrivC.setText(str(condSave['valorConstruccionPriv']))
                self.lbValConsPrivC.setText(valorPRIVADO)
                self.leValConstPrivCond.setText(valorPRIVADO)

                self.lbValConsComC.setText('${:,.2f}'.format(condSave['valorConstruccionComun']))

                # valC = (condSave['valorConstruccionPriv'] or 0) + (condSave['valorConstruccionComun'] or 0)
                valC = valorConst + (condSave['valorConstruccionComun'] or 0)

                self.lbValConsTotalC.setText('${:,.2f}'.format(round(valC, 2)))
                # self.leValConstTotalCond.setText('${:,.2f}'.format(round(valC + (condSave['valorConstExc'] or 0), 2)))
                self.leValConstTotalCond.setText('${:,.2f}'.format(round(valC)))

                # - TOTAL 
                valorTotal = valT + valC
                self.lbValorCTotalC.setText('${:,.2f}'.format(round(valorTotal, 2)))

                self.lbImpPredC.setText('${:,.2f}'.format(round(((valorTotal * 12) / 1000), 2)))


                #self.createAlert('es un condominio', QMessageBox.Information ) #changed!
            else:

                # --- S U P E R F I C I E S
                # - TERRENO
                self.lbSupTerrTotalC.setText(str(self.cedula['supTerr']))
                # - CONSTRUCCION
                count = self.cmbVolumenP.count()
                superficie = 0

                for index in range(0, count):
                    superficie += self.cmbVolumenP.itemData(index)['supConst'] or 0

                self.lbSupConsTotalC.setText(str(0 if superficie is None else round(superficie, 2)))

                # --- VALORES CATASTRALES
                # - TERRENO
                superficie = self.cedula['supTerr']
                valorTerr = self.valorCalle * superficie

                valorTerrS = '${:,.2f}'.format(round(valorTerr, 2))

                self.lbValTerrTotalC.setText(valorTerrS)

                # - CONSTRUCCIONES
                fracciones = []
                valorConst = 0

                # guardado temporal
                if count == 0:
                    self.seRealiza = False

                self.constrTemp()

                # se obtienen todos los volumenes de predios
                count = self.cmbVolumenP.count()
                idPredio = None
                for index in range(0, count):
                    
                    fracciones = self.cmbVolumenP.itemData(index)['fracciones']
                    
                    if len(fracciones) == 0:
                        continue

                    for fr in fracciones:
                        valorConst += float(fr['valorConst'] or 0)

                valorS = '${:,.2f}'.format(round(valorConst, 2))
                self.lbValConsTotalC.setText(valorS)

                # totales 
                valorTotal = valorTerr + valorConst
                self.lbValorCTotalC.setText('${:,.2f}'.format(round(valorTerr + valorConst, 2)))
                # impuesto predial
                self.lbImpPredC.setText('${:,.2f}'.format(round(((valorTotal * 12) / 1000), 2)))

                # self.createAlert('NOOOOO es un condominio', QMessageBox.Information ) #changed!

            # --- calcula y muestra informacion del fiscal ----> Deshabilitado por mientras, no se cuenta con la info de padron <----
            #self.muestraComparativoFiscal()

            impCatastro = 0 if self.lbImpPredC.text() == '' else float(self.lbImpPredC.text().replace('$', '').replace(',', ''))
            impFiscal = 0 if self.lbImpPredF.text() == '' else float(self.lbImpPredF.text().replace('$', '').replace(',', ''))
            self.lbDiferencia.setText('${:,.2f}'.format(impCatastro - impFiscal))

    # --- INDIVISOS ---
    # - bloquear o desbloquear la tabla de indivisos
    def event_bloqDesbloc(self):

        if self.bloqueado:
            self.btnBlocDesbloc.setText('Bloquear')
            self.twIndivisos.setEnabled(False)
            self.lePrivadaC.show()
            self.leComunC.show()
            self.lePrivadaT.show()
            self.leComunT.show()
            self.bloqueado = False
        else:

            if self.lePrivadaC.text() == '' or self.lePrivadaC.text() == '' or self.lePrivadaC.text() == '' or self.lePrivadaC.text() == '':
                self.createAlert('Defina todas las superficies')
                return

            self.btnBlocDesbloc.setText('Desbloquear')
            self.twIndivisos.setEnabled(True)
            self.lePrivadaC.hide()
            self.leComunC.hide()
            self.lePrivadaT.hide()
            self.leComunT.hide()

            self.lbPrivadaC.setText(self.lePrivadaC.text())
            self.lbComunC.setText(self.leComunC.text())
            self.lbPrivadaT.setText(self.lePrivadaT.text())
            self.lbComunT.setText(self.leComunT.text())

            self.bloqueado = True

    # - evento que se lanza cuando se edita un elemento
    def event_updateIndivisos(self):

        col = self.twIndivisos.currentColumn()
        row = self.twIndivisos.currentRow()

        if row == -1 or col == -1:
            return

        item = self.twIndivisos.item(row, col).text()

        flotante = self.detectFloats(item)

        if not flotante:
            self.twIndivisos.setItem(row, col, QtWidgets.QTableWidgetItem('0'))

        # indivisos
        self.factorIndiviso()

    # - seleccion del item del propietario
    def event_itemClicked(self, item):

        row = self.twPropFiscal.currentRow()
        claveProp = self.twPropFiscal.item(row,0)
        nombre = self.twPropFiscal.item(row,1)

        propietario = None
        # buscar entre todos los propietarios el seleccionado para imprimir sus valores
        for prop in self.propPadron:

            if str(prop['claveProp']) == claveProp.text():
                propietario = prop
                break

        # muestra informacion completa de propietarios
        if propietario is not None:

            self.lbNombrePPad.setText(propietario['nombre'] + ' ' + propietario['apellidop'] + ' ' + propietario['apellidom'])
            self.lbRazonSocPPad.setText(propietario['razonSocial'])
            self.lbCallePPad.setText(propietario['calle'])
            self.lbColoniaPPad.setText(propietario['colonia'])
            self.lbCodPosPPad.setText(propietario['cp'])
            self.lbNumeroPPad.setText(propietario['numExt'])

            self.lbRFCPPad.setText(propietario['rfc'])
            self.lbTelefonoPPad.setText(propietario['telefono'])
            self.lbCorreoElecPPad.setText(propietario['eMail'])
            self.lbCiudadPPad.setText(propietario['ciudad'])
            self.lbMunicipioPPad.setText(propietario['municipio'])
            self.lbEstadoPPad.setText(propietario['estado'])

            self.lbCalleNPPad.setText(propietario['calleNotificacion'])
            self.lbNumOfiNPPad.setText(propietario['numofNotificacion'])
            self.lbNumInteriorNPPad.setText(propietario['numintNotificacion'])
            self.lbColoniaNPPad.setText(propietario['coloniaNotificacion'])
            self.lbCodPostNPPad.setText(propietario['cpNotificacion'])
            self.lbEstadoNPPad.setText(propietario['estadoNotificacion'])
            self.lbCiudadNPPad.setText(propietario['ciudadNotificacion'])

    def event_itemClickedProp(self, item):

        row = self.twPropPred.currentRow()
        ident = self.twPropPred.item(row,0)
        nombre = self.twPropPred.item(row,1)

        propietario = None
        # buscar entre todos los propietarios el seleccionado para imprimir sus valores

        for prop in self.propPropPred:

            if str(prop['id']) == ident.text():
                propietario = prop
                break

        # muestra informacion completa de propietarios
        if propietario is not None:

            self.lbNombrePPred.setText(propietario['nombre'])
            self.lbApPaternoPPred.setText(propietario['aPaterno'])
            self.lbApMaternoPPred.setText(propietario['aMaterno'])
            self.lbCallePPred.setText(propietario['calle'])
            self.lbNumExtPPred.setText(propietario['numExt'])
            self.lbNumInteriorPPred.setText(propietario['numInt'])

            self.lbColoniaPPred.setText(propietario['colonia'])
            self.lbCodPosPPred.setText(propietario['cp'])
            self.lbMunicipioPPred.setText(propietario['municipio'])
            self.lbEstadoPPred.setText(propietario['estado'])
            self.lbPaisPPred.setText(propietario['pais'])

    def event_spinBox(self, cadena):

        col = self.twIndivisos.currentColumn()
        row = self.twIndivisos.currentRow()

    def event_textoCambioPrivC(self, texto):
        self.totalesSuperf(self.lePrivadaC.text(), self.leComunC.text(), 'C')
        self.totalesSuperf(self.lePrivadaT.text(), self.leComunT.text(), 'T')

    def event_actualizaInfo(self):

        # calcula los porcentajes de indivisos
        if self.twIndivisos.rowCount() > 0:       

            totalInd = 0 if self.lbTotal.text() == '' else float(self.lbTotal.text())

            if self.lbTotal.text() != '1.0':
                reply = QMessageBox.question(self,'Condominios', 'EL total de los indivisos no es la unidad ¿Desea continuar con el guardado?', QMessageBox.Yes, QMessageBox.No)
                if reply != QMessageBox.Yes:
                    return

            tablaIndivisos = self.twIndivisos
            listaInd = []

            for x in range(0, tablaIndivisos.rowCount()):

                indiviso = {}
                indiviso['cuenta'] = tablaIndivisos.item(x,0).text()
                indiviso['factor'] = 0 if tablaIndivisos.item(x,1).text() == '' else float(tablaIndivisos.item(x,1).text())
                indiviso['tipo'] = tablaIndivisos.item(x,2).text()
                indiviso['supConstPriv'] = 0 if tablaIndivisos.item(x,3).text() == '' else float(tablaIndivisos.item(x,3).text())
                indiviso['supConstComun'] = 0 if tablaIndivisos.item(x,4).text() == '' else float(tablaIndivisos.item(x,4).text())
                indiviso['supTerrPriv'] = 0 if tablaIndivisos.item(x,5).text() == '' else float(tablaIndivisos.item(x,5).text())
                indiviso['supTerrComun'] = 0 if tablaIndivisos.item(x,6).text() == '' else float(tablaIndivisos.item(x,6).text())

                listaInd.append(indiviso)

            respuesta = self.guardaIndivisos(listaInd)

            if respuesta == 'OK':
                self.createAlert('Proceso Concluido', QMessageBox.Information)

    # evento xoom out
    def event_zoomOutIma(self):
        
        self.scaleFactor -= 1
        self.aplicaZoom()

    # evento zoom in
    def event_zoomInIma(self):

        self.scaleFactor += 1 
        self.aplicaZoom()

    # evento para cambio de imagenes, manzanas, fachados y docomuentos
    def event_radioButtonImagenesPress(self, checked):
        
        if not checked:
            return

        self.scaleFactor = 1
        self.countID = 0
        self.countIM = 0
        self.countIF = 0

        # carga imagenes de manzanas
        if self.rbManzana.isChecked():

            if len(self.idsMzaIma) > 0:
                data = self.idsMzaIma[self.countIM]
                self.habilitaBotImages()

            else:
                self.lbImage.clear()
                self.deshabilitaBotImages()
                return

            self.mostrarImagen(data, 'M')
            self.lbNumImages.setText(str(self.countIM + 1) + ' de ' + str(len(self.idsMzaIma)))


        # carga imagenes de fachadas
        elif self.rbFachada.isChecked():

            if len(self.idsFacIma) > 0:
                data = self.idsFacIma[self.countIF]
                self.habilitaBotImages()
            else:
                self.lbImage.clear()
                self.deshabilitaBotImages()
                return

            self.mostrarImagen(data, 'F')
            self.lbNumImages.setText(str(self.countIF + 1) + ' de ' + str(len(self.idsFacIma)))

        # carga imagenes de documentos
        elif self.rbDocumento.isChecked():

            if len(self.idsDocIma) > 0:
                data = self.idsDocIma[self.countID]
                self.habilitaBotImages()
            else:
                self.lbImage.clear()
                self.deshabilitaBotImages()
                return

            self.mostrarImagen(data, 'D')
            self.lbNumImages.setText(str(self.countID + 1) + ' de ' + str(len(self.idsFacIma)))

        self.btnZoomIn.setEnabled(self.listZoom[self.scaleFactor] < 2.5)
        self.btnZoomOut.setEnabled(self.listZoom[self.scaleFactor] > 1.0)

    # evento que retocede una imagen, una posicion
    def event_atrasImagen(self):

        self.scaleFactor = 1

        # manzana
        if self.rbManzana.isChecked():

            if self.countIM == 0:
                self.countIM = (len(self.idsMzaIma) - 1)
            else:
                self.countIM -= 1

            if len(self.idsMzaIma) > 0:
                data = self.idsMzaIma[self.countIM]
            else:
                self.lbImage.clear()
                return

            self.mostrarImagen(data, 'M')
            self.lbNumImages.setText(str(self.countIM + 1) + ' de ' + str(len(self.idsMzaIma)))

        # fachadas
        elif self.rbFachada.isChecked():
            if self.countIF == 0:
                self.countIF = len(self.idsFacIma) - 1
            else:
                self.countIF -= 1

            if len(self.idsFacIma) > 0:
                data = self.idsFacIma[self.countIF]
            else:
                self.lbImage.clear()
                return

            self.mostrarImagen(data, 'F')
            self.lbNumImages.setText(str(self.countIF + 1) + ' de ' + str(len(self.idsFacIma)))

        # documentos
        elif self.rbDocumento.isChecked():
            if self.countID == 0:
                self.countID = len(self.idsDocIma) - 1
            else:
                self.countID -= 1

            if len(self.idsDocIma) > 0:
                data = self.idsDocIma[self.countID]
            else:
                self.lbImage.clear()
                return

            self.mostrarImagen(data, 'D')
            self.lbNumImages.setText(str(self.countID + 1) + ' de ' + str(len(self.idsDocIma)))

        self.btnZoomIn.setEnabled(self.listZoom[self.scaleFactor] < 2.5)
        self.btnZoomOut.setEnabled(self.listZoom[self.scaleFactor] > 1.0)

    # evento que avanza una imagen, una posicion
    def event_adelanteImagen(self):

        self.scaleFactor = 1

        # manzanas
        if self.rbManzana.isChecked():
            if self.countIM == (len(self.idsMzaIma) - 1):
                self.countIM = 0
            else:
                self.countIM += 1

            if len(self.idsMzaIma) > 0:
                data = self.idsMzaIma[self.countIM]
            else:
                self.lbImage.clear()
                return

            self.mostrarImagen(data, 'M')
            self.lbNumImages.setText(str(self.countIM + 1) + ' de ' + str(len(self.idsMzaIma)))

        # fachadas
        elif self.rbFachada.isChecked():

            if self.countIF == (len(self.idsFacIma) - 1):
                self.countIF = 0
            else:
                self.countIF += 1

            if len(self.idsFacIma) > 0:
                data = self.idsFacIma[self.countIF]
            else:
                self.lbImage.clear()
                return

            self.mostrarImagen(data, 'F')
            self.lbNumImages.setText(str(self.countIF + 1) + ' de ' + str(len(self.idsFacIma)))

        # documentos
        elif self.rbDocumento.isChecked():      

            if self.countID == (len(self.idsDocIma) - 1):
                self.countID = 0
            else:
                self.countID += 1

            if len(self.idsDocIma) > 0:
                data = self.idsDocIma[self.countID]
            else:
                self.lbImage.clear()
                return

            self.mostrarImagen(data, 'D')
            self.lbNumImages.setText(str(self.countID + 1) + ' de ' + str(len(self.idsDocIma)))

        self.btnZoomIn.setEnabled(self.listZoom[self.scaleFactor] < 2.5)
        self.btnZoomOut.setEnabled(self.listZoom[self.scaleFactor] > 1.0)

    # --- CERRAR E V E N T O S   Widget ---

    # --- U T I L I D A D E S ---

    # mostrar imagen
    def mostrarImagen(self, data, tipo):

        v = list(data.values())
        k = list(data.keys())

        imagen = {}
        if v[0] is None:

            # consume ws para obtener la imagen
            imagen = self.obtieneImagen(k[0], tipo)
            if tipo == 'M':
                self.idsMzaIma[self.countIM] = {k[0]: imagen}
            elif tipo == 'F':
                self.idsFacIma[self.countIF] = {k[0]: imagen}
            elif tipo == 'D':
                self.idsDocIma[self.countID] = {k[0]: imagen}

        else:
            imagen = v[0]

        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(base64.b64decode(imagen['archivo']))

        size = QSize(453, 255)

        smaller_pixmap = pixmap.scaled(self.listZoom[self.scaleFactor] * size, Qt.KeepAspectRatio, Qt.FastTransformation)

        self.lbImage.setPixmap(smaller_pixmap)

        self.lbImage.setScaledContents(True)
        self.lbImage.show()


    # aplica zoom a la imagen
    def aplicaZoom(self):

        pixmap = self.lbImage.pixmap()

        size = QSize(453, 255)

        smaller_pixmap = pixmap.scaled(self.listZoom[self.scaleFactor] * size, Qt.KeepAspectRatio, Qt.FastTransformation)

        self.lbImage.setPixmap(smaller_pixmap)

        self.lbImage.setScaledContents(True)

        self.lbImage.show()

        self.btnZoomIn.setEnabled(self.listZoom[self.scaleFactor] < 2.5)
        self.btnZoomOut.setEnabled(self.listZoom[self.scaleFactor] > 1.0)

    # calculo indivisos
    def factorIndiviso(self):

        # calcula los porcentajes de indivisos
        if self.twIndivisos.rowCount() > 0:       

            tablaIndivisos = self.twIndivisos

            indiviso = 0

            for x in range(0, tablaIndivisos.rowCount()):

                indiviso += 0 if tablaIndivisos.item(x,1).text() == '' else float(tablaIndivisos.item(x,1).text())

            ind = round((indiviso / 100), 3)
            self.lbTotal.setText(str(ind))
            self.lbResiduo.setText(str(round(1 - ind, 3)))

    # - total Construcciones de condominio
    def totalesSuperf(self, priv = '0', comu = '0', tipo = 'C'):

        total = 0

        try:
            privada = float(priv)
        except Exception:
            privada = 0

        try:
            comun = float(comu)
        except Exception:
            comun = 0

        total = round((privada + comun), 3)

        if tipo == 'C':
            self.lbTotalC.setText(str(total))
        elif tipo == 'T':
            self.lbTotalT.setText(str(total))

    # - detectar flotantes
    def detectFloats(self, number):

        try:
            number = float(number)
        except Exception:
            return False
        
        return True

    # - spinBox
    def spinBoxQTableWidgetItem(self, rangeInit, rangeEnd, decimals, sBValue):

        spinvalue = QtWidgets.QDoubleSpinBox()
        spinvalue.setRange(rangeInit, rangeEnd)
        spinvalue.setDecimals(decimals)
        spinvalue.setSingleStep(0.01);
        spinvalue.setValue(sBValue)

        spinvalue.valueChanged.connect(self.event_spinBox)

        return spinvalue

    def subdiv_fusion(self, condo = False):

        # -- subdivision y fusion de fracciones
        indexVolSel = self.cmbVolumenP.currentIndex() if not condo else self.cmbVolumenC.currentIndex()
        dataV = self.cmbVolumenP.itemData(indexVolSel) if not condo else self.cmbVolumenC.itemData(indexVolSel)

        nivConst = dataV['numNiveles']
        resultado = []

        fra = []
        count = self.cmbFraccionesP.count() if not condo else self.cmbFraccionesC.count()
        for indx in range(0, count):
            dataTemp = self.cmbFraccionesP.itemData(indx) if not condo else self.cmbFraccionesC.itemData(indx)
            fra.append(dataTemp)

        for i in range(0, nivConst):
            flag = False
            for f in fra:
                if (i + 1) == f['volumen']:
                    flag = True
                    break

            if flag:
                continue

            resultado.append(str(i + 1))

        if len(resultado) > 0:
            if not condo:
                self.leNivPropP.setText('1')
                self.cmbNvaFraccP.addItems(resultado)
            else:
                self.leNivPropC.setText('1')
                self.cmbNvaFraccC.addItems(resultado)   

        return

        # se llena las fracciones a fusionar
        for f in fra:
            fraccionAct = int(self.cmbFraccionesP.currentText()) if not condo else int(self.cmbFraccionesC.currentText())

            if fraccionAct != int(f['volumen']):
                if not condo:
                    self.cmbConP.addItem(str(f['volumen']))
                else:
                    self.cmbConC.addItem(str(f['volumen']))

    # - habilita la subdivision y fusion (botones)
    def deshFusionSubdiv(self, condo = False):

        if not condo:
            # deshabilitar subdivision y fusion
            # fusion
            if self.cmbConP.count() == 0:
                self.btnFusionarP.setEnabled(False)
                self.cmbConP.setEnabled(False)
            else:
                self.btnFusionarP.setEnabled(True)
                self.cmbConP.setEnabled(True)            

            # subdivision
            if self.cmbNvaFraccP.count() == 0:
                self.btnSubdividirP.setEnabled(False)
                self.cmbNvaFraccP.setEnabled(False)
                self.leNivPropP.setEnabled(False)
            else:            
                self.btnSubdividirP.setEnabled(True)
                self.cmbNvaFraccP.setEnabled(True)
                self.leNivPropP.setEnabled(True)

        if condo:
            # deshabilitar subdivision y fusion
            # fusion
            if self.cmbConC.count() == 0:
                self.btnFusionarC.setEnabled(False)
                self.cmbConC.setEnabled(False)
            else:
                self.btnFusionarC.setEnabled(True)
                self.cmbConC.setEnabled(True)            

            # subdivision
            if self.cmbNvaFraccC.count() == 0:
                self.btnSubdividirC.setEnabled(False)
                self.cmbNvaFraccC.setEnabled(False)
                self.leNivPropC.setEnabled(False)
            else:            
                self.btnSubdividirC.setEnabled(True)
                self.cmbNvaFraccC.setEnabled(True)
                self.leNivPropC.setEnabled(True)

    # - ordena las construcciones por volumen
    def ordenaConstr(self, dataConstP):

        temp = []
        result = []

        # obtiene los numeros de volumne (solo los numeros, ej. V1 - 1, V2 - 2, etc)
        for d in dataConstP:
            if d['nomVolumen'][1:] == '':
                continue
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
                    break

        return result

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


'''
class progressThread(QThread):

    progress_update = QtCore.Signal(int) # or pyqtSignal(int)

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()


    def run(self):
        # your logic here
        while 1:      
            maxVal = 1 # NOTE THIS CHANGED to 1 since updateProgressBar was updating the value by 1 every time
            self.progress_update.emit(maxVal) # self.emit(SIGNAL('PROGRESS'), maxVal)
            # Tell the thread to sleep for 1 second and let other things run
            time.sleep(1)


    def updateProgressBar(self, maxVal):
        self.progressBar.setValue(self.ui.progressBar.value() + maxVal)
        if maxVal == 0:
            self.ui.progressBar.setValue(100)
'''