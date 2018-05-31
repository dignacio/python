import os
import operator

from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMessageBox, QListView, QGraphicsView, QGraphicsScene, QFileDialog

from qgis.utils import iface
from qgis.core import QgsProject
from .fusion_dialog import fusionDialog

import os, json, requests, sys, datetime, base64

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


        # -- carga imagenes
        self.idsMzaIma = self.descargaIdsImag('M', self.cveCatastral)
        self.idsFacIma = self.descargaIdsImag('F', self.cveCatastral)
        self.idsDocIma = self.descargaIdsImag('D', self.cveCatastral)
        #image = QImage('C:/Users/cianet45/Pictures/imagenesTab/dos.jpg')

        #pixmap = QPixmap().fromImage(image)


        # str_image = "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"
        str_image = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAHZAsYDASIAAhEBAxEB/8QAHAAAAgMBAQEBAAAAAAAAAAAAAgMBBAUGAAcI/8QARBAAAgIBAwIFAQUHAgQDBwUAAQIAAxEEEiEFMRMiQVFhBhQycYGRBxUjQlJioTPRJHKxwQg14RY0NkNjgpJTc7Lw8f/EABoBAAMBAQEBAAAAAAAAAAAAAAABAgMEBQb/xAAsEQEAAwACAgMAAgMAAQMFAAAAAQIRAxIhMQQTQSJRBTJhFBVCgSNxkaHR/9oADAMBAAIRAxEAPwD88hZPrHNp7PYwG09nsZyTWXk7od09me8Cz2nhTZ7SJrI8IJ4gmM8GzPaeNNnsZPWRsEmDGmmz2geC+e3MeK2BIcmWquImqizP3Zbqoc/ymRaGV5gYM8TGCiw/ymeamwfymR5c6s/MURzLD1vz5TFit8/dMPLWJRWuZcprgVUvn7pl2qp8fdMqI/tleZkyquG1eAY1EYAeUwbFf+kymERsqF68TPuE070c8bTiZ99b+qkSZdPHGKFsUoO6PsVs/dMiupifumXE5DqicgdY4j1HEiupvVTLC0t/SZEsL2LxxPR/hH2gOhA7RM4tEqzxTDmOdT7QCp9oQ2rIAIxQZKrzH115imStbCgkIIZbSqMWn4k+ZYzywprWfWOSsy0Ku3EIV8jiaVqznl0pE4lqpMTyJzHVjE2iCiNNrEsoeO8rBsCSLMHmUPr1YdpXtbgyHt7+0rXXd5Mqij1tnHxKd1sjUW8yhbaSTM5lpXjMstzEM/MENlgG4z6z1ish57ehk5rWK4NbOZYrt+fylAExiMcjiEC1GrXb2zH1uSYPTel6nVMp2MFPriddpfpqqlEa0bmPp6zWER8e1/TE01DuASCo94d+hvdxs85n0LovR0Z0q+y5Hrk9p29PQtPXWN2nXPodsJs7Kf4/tHt8Io6fq6rfu+vadJ0vol7XL4lTrVZ3x6T66nQKXOfCrVvTKy3X0m6o/wCijL8YMO0z+Onj+FFP18yo+nLBYRdV/DH3XPrNCn6f07j+Kufwn0CzQpcCllfn9B2lW3o/hnyhsfJkTEuuvFSPbi//AGZ0quSlb5/xLNHRaaEA2c++Z12m0WM4BDQ7tPYFIKgj3xzDJV9dY/HI/ZWQgJUMDtxGHSWBgXUEn4nRU6JGJKYB9QfeWxpcDY4GfT1hESrIcvVsT79SbRx5lgXaPR6k/wCmPwxOjs0dRYh0we4IEA6FWU+GvbvxDJLIchf0igEhakYDupEr29A01yixKMe86rVaPGCBhxGaNAi8rlD6iKN9FNKz+OGt6Bo73C3aVDx3xA1H0j0y1P4FZX3Pedzr9DtO/A5HllXTaVhuOOAcSslM8VJ9w+f3/QzJetmlv3H+lxMm36W6pprGDaVygP3lGRPr9WnK3K6t5CJ1fS7KrKNtlQyPeaUpE+Jc/J8Ws/6+H52r6Zch86EfGJa+ytpkDmrzn7uR/mfom3pfTNUNl1FR+cTE6h9DaO7c2md0PsDmafR/Tkt8a0enwa267OGOPwnk7/E+m9U+hXUMAocfhgzkeo/TGr05PhqWx6SJpaHPNLV9suiael7iZtenvrbDoQRNDTBgRxHWDrLd0fpNegdpjaLdgcTb0ynIyJ0VbQu1KMciEah+UmtTjtGqp9prEKI8LI7SPBlwJxPCuGDFRKeY5K5YFXxDFZhhxBQSSVjdpxPbDKwydsBllgoYJT9IBX2yDHlJBriBE9GlP1kFIAueh7J6Afng6MeogHQrntOgOnkDS/ExwoowPsK/0z32Ee06Aab3Ej7Lz2jwTSGD9gH9MkaBf6ZvjTY9IQ0ufSTiejnj09f6Z4dNXjyzovsp9oa6X4h1T0YFfTl48ssJ09QPu8TcXSduI1dIfaTNUzSGINCuO0F9ApB4E6FdJn0k/ZAPST1hPSHMHpy5+7IXpq5+7OlOl78SBpfiPpCusMOvp68cSzXoF44mumm+I9NP24j6pnjZK6FcdpD6BSO3M3Fo+MTx0/xF0KONzj9OX2lW3piH+WdU+n47RTaXJ7Soq0irkm6QhP3RG19GT+kZnUDR89o1NJj0h1g5q5lOkJ/SI0dITH3ROmXS/EL7Lx2imsMLUcq3SEP8oiH6On9M7E6XjtEW6bA7Q6QmOLXG29IQZ8olK7piDOFxOv1FB54mfdQfaRaIPpjkn0O08CQNMVPadDbRyeIh6JhakOXl2GYlPxHLVLS04PPaNWoAcyMxyzMyomvAkrX7y41XPaCUwJULpE6rivB+J7bGPxFEyol10prxGYGMHmMHpIZZboihLGVrQTnEsmssf9oyvTFscSZjTijHal2MZXoN3cTdTQ59Jap0JzjEcca442DX0tTjiXKuloqYs5X+nGZv1aNc+scdEeDtmsUhXRzS9FotOK2ZD7MvE1tD9OLWybmW1j22nyiael0LeMgQcmd50LpKacK3hgseT7SLxFW3FwxafSj0TooWiveqL8zq+n9DorfetDO/9Rl/R6YAAtgt7ATXpAQDf/gzOPPl3144iEaLS0Iq5oAb5WaIoqfhQQfbHEitkZRtVR8xmHU535HzNYg/QkA2jy8e0JtOGOQvPpPZGIAZtxFbf7SsSTZg5SzuO2ZV53kBjz+ctOzFs2LuZfaC9e7+Ivf1EiYXCq+UcMVHziWbakvpJ9cdxDNe4EYB9wYCKUUgDKex9IQbNrp2kj1jjUwAKnj0lmykbgy9oa14PGOYoqauq+JgXKM+88dMoxjKn/EdYm1wFz8wQrqTg/liPCVdRovFXsC3uJn+Aamw6/iZtrk8so/FeD+kCxDYuMbx7HuIusDWf4I1NLUn8VI9JSo0zK7pYu2wDH4iahQ12ZXhuxBjLKxcMny2CLCZtCgKgIyCPb1lvTHwbgG7GQ9Xh4+TnOPWG2cZxmVEheALAEDBh/aLKj5Wb8JW09oDbC2Cfu57Swy+U57CbROplZp1C6ishsFh6Slrul0apSyja3xJC17gynDe4llGIbd+suJZ2rEuI6n0e2tyTUto/DmZDdPXdl9M2P6k7j8p9M1Fa3KRjIMwtf0u3fvpC5PfdDIct+H9hy9fTyOa8kfImjXUVC5UiWDodRU27yBfUZhpeVYBm3fEqPCega8COAGIa6ihhhqxIfYeaifwMuD648AO09xF7uZ4tzGD1YQsiVg8nxIBZyJBIlfxJ7xOIaD8jmCSIjxJBsjM4kQSREmz5izZxEFgsIJYSsbIs28nmIsXNwnpTF3zPRnj5sNP8QhphLirDC/EheKI0454kjTDHaaCqMySsY6s8aX4hjTD2l9UhKg/KIuqium+OIxdMPyl1V+IaqOOIYU1U10vxGjTj2lxVEMARYjopjT/ABIOnHtL2OJG0Seo6KB0/wASPsvE0goxJCD2lRU4ozV00aun+JfFcIV8iPrA6QpLp/iT9nl5axDCZPaLD6M46b4Mj7J8TUCCEE+I8PqzBpRntCGk57TTCD2hBBCYhM0Zw0wHYQvs3xNEIPSTsEOqejLbTZHaVr9Px2m2yCVtQmBJmB0c3fp+/Ezr6PidFqUyeJmXr3mdoZ2qwracZ4lK2vnjgzZ1C95nXCc13FzVURXkmF4fHbmPC8/MMJjvM3B0nVYpx2i3rl0JnvPNX8RxDs4uPWU9R54gpQTNNqc+kbVphxkTStXdSjLGmJ/CM+ynHabKab4jV0vxNYo26QwqtFz2l+jQ9uJrVaQZ7TQ0+lAxxHFB1xlVdOJA4lqrpx5yvPpNpKO0sV08y+p4xtN09mPlTOJrp0keEGfv3ImpVTis44A5xJpDai8kEkDlj7CK3iGtKK/T+lKzBqq1Vf5mab9QSmtFUZyM8Sv4yrQlbcO43YHosfSws07PjbtP+Jx3t2d1KdYaFVpyF24A5Ms1XruyeT7TJ8TCAqTuf5h16gVHFjKD7ZirbFTDoKrkzlQVMt1k2Dhh+cy9JqQUxsBGPfmaFZZhla1/Wb1siYWVUg8ruHuIxeB5QAZFRIA3ow/OOGzjhv1msIlUevLEk8yVQFjjiWnqV1xkgypdS3GMj8IphUSFxtbH80HbsG7GfiNIygV1/OAMLkNynoZEqCwJBCLnPYxSl1O2zufWXNq42hue4IlZ2ZWJYjMQeyHUjPm9DEkNwW24B9TgyfE4GR5c54gNjzAkgnsY9M5cEgMCy/Iz/mMIrJ2q+D7MP+8oKxUj7wPviV7rdrli1n4e8el11pupsQC5EYjjhs4/7yqatrfwSSf6WHP6zN1GqtpsLIARwTkf7Ql6qKwWs4X8eIpmJ9jpP41VIbh179wYBr2tg/6eeDKtfUamfAYKO/PaXatQpzmGFOwXdp1Y+3tn/eMR3qH8TlR+sdsDAlPu+0S3kHAOPUSvSfZ4VXG4AZPrPEOMcce8UqIAGr3IT/SeP0jA7p3yfkS4lOFmxj7HEDcHGFYBvkx7LXbgkRdmlRs+Un8eYyZ163AglCy+6+aZ+oprfzYKt8rmaz6Ij7jHPtnmVNRTexwytYPn736x6mYhQ2BOGCQSyr2gajdUMMWwPRhgiVGuwfXBlxLKatAsCAcxTWcSiL/N3gm7BxniXqZqveJPGwTPN/PeD4/IAMCxom3EE3fMzn1Az3izqPmAxpm6R40y21PzB+0/MNPGqbvmLa4ZmadT8wDquIaOrSa3vzFtd8iZx1PPeLfU/MR40jdj1npkNqee89AYxl1EaNQJXWqGtUXloet/xCF4iRVCFR4h5B63iGLgfSVhWfyjBVF5LIWFvEMXiVhX3hiuMZCwL15heOJXFRheEcwGQsC5cfEJbViBUYS1GBZCyLFwIYsWVlqMNajGeQsCxOIXiLEioyRUYyP8RYYsTMreE0NajEMWRYsnxElYVHEkVMIDFrxU95IsWVRWYQqPEYxZ8RfeSbF95V8JhPeGYhkHmxcd4m11I7xbI2Iq1GxJkdSNQVOeZl6nAl+6tuZSuqMyt5ZWqyr+c4lN6pq2U94lqOe0wtVy3499s0VeuIXh9pd8A+0IU/Enqy+mFRKowUZltKDntHpQc9pdat6ceKC6fmOr03biaKaftxLNel+JrFXRWijVpwR2lhNIPaX69LjHEtV6b4mkVXjOr0gzLNdGB2l9NN8Rq6f4ldSxUrp7S3TQuMxq0EekfXUcESsEIVkrO4jK4iNLhd9Q4ax/N+HtF620Vqyeqj1itPqlTVU2jDMTu5z3E4Oa+zjs4qZGtDypa7svmJwM+gE8uoLVuTkK3EpavX1WJkWruIPAHrmEm0gAkeQc57TnmXTEeFi3VWM5WkcnsP6Y3QaYLcr3WK5J9ZVbUmt2UqQPjuY/S6oO2CGx/VjG2KJPPDpa08NvIOD2zNLS+YYf8jMbTXr4IDWeIG7FfQy/Q5dCoHC/qJvWWUw1qiV+8wx+MYblweefaZyXFSCvJ9jDsvTPmr5M0iyeq82oGDtBMD7QM8qZSNo9AwAheKrcEgH5j2R1XBajDGePYxNqbgfDcL+Mr7d2fMmfiLajxD5mIP8AaYziFgCynLHH/wBvrPFksVj6+vxF7mU4LHb6HPMr2razB0bI9wOZMx/R4KxDWDgbkgs48IFSeDjE8trMCHQqZ59pzsJz7RACMHztPb55EXfuQ5zu/EZgMNhPfJgo1iucPkezQ08VtR4bENscYP8AJ/tKzLU4K1OpIzkMOZq7q2wLEGT6iA+jrLlq9vPuIHrN+z+HSreGTjjg+kTW70j+FaSh7BppvXcv3dhf47RFwK48asH1xjtHIiQ0dWdOATn2Paa2j6lp9VgWEKxmKdPTdnnHt8ShqNN4VilWOfT5hswU0rLtVTac1lXX+mCPMTjPyJymn6tqNLYN5DKe2TN3T9Tq1C53eb4PaV2hE8cwvhs53DmeNm31Kys9zMpIYEY74/6iU9TrX01Ya2otUfVOcx98T11qvYrDkBvwle0VuCAzo3wZlpqdPrxnS6gF/wCljgyq+s1Nd3hufys/7GPuXRo3FlU7nFqdsMsxNVptOWbw3COeQpGP0MN9Y3LNkDOCDK1zi5WekZx6RxYpozLHKPtbPBg6iw1gEmFafFswB/6QNXQ25Qw7TSltZWrhH2gnPtAOpxwsmyrsB2ijSZoz8PNqYttSczxp+IBp/WB+EHUHMj7QZ408wTSc8iLBGPNqD+UBtQZJqgmr4hh7CDeeYtrj7wzVANUMkbADe3vPSTV8T0MkbCytMMU/E0E0/wAQxRLxLOFMIUzS+z/E8un+IYNZ60wxTL/2eMTT/EMLVBafiGKe2BL4o+IxdPDBrPWn4hij4mgNPDGn+IYNZwp4HENaPiaK6fntGfZ8QwazhT8Q1p+JorR8Qhp+e0Z6z/A+JIp+JpijI7SRRz2gWs7weO0IUZPaaQo47SVp47RDWd4GM8SfA+JpeDz2k+DxAazRT8SRT8TSFPMnweO0BrL8HjtBNM1DTBNPxAay2piHp78TYNPES1HeI9Ylun+JVs03xOgfT57iJbTfEialPlzb6bvxFnS/E6JtJ8QDpPiRNETDnTpPiGuk+J0A0fxCGj+DF0Lqwk0vxHppfibK6P4jV0nPaOKqiGTXpfiWq9Pz2mkmm55Eaun+JpFT1QTTduI9NPLy0/EYtPHaXg1TWiNWmXVp+Ia0/EeDVEUyt1DULpKmI+9jtNW6vbWTkicp1qwswXPlPHzMea/SrTip2lnXbtRZud2JZi3ljHRaxU2HzX359YFGmaqr+GzY9TDvK01gKpYkeZm5nly9CsFbkXLVth2buw5AjWWxqSqulYPd3zkysaWCBgniEHy5/wBpd6dQy2btS5LHjAihpi/StjU1KxW5wOHK5I/3l2jTeONlxX4ZMriCWqpqNtVmSP5RMXqXVdULgtiKKT/Q3eViqUm3p1umbT6EYazn55MeNamN9L5Ye5nGU68hVHnQe/ciXqdc1YzlH+MYP5yomGk/HdStz2pvUge4HMXdqLNmTnImPpuoUKSSHqY98HymadWoqtUDdvX0xNInUTxzX8KTqFifdbPxmPHUy5Csp/MRd/T63ZrNO5UnggCVq9K1RO1iQPeHlWUloDUPuDFUx7g4lxNSMZOce+ZjgMWHnQSSgz98/wD5R6meOJbiajbggMf8iOTU7hnG35zOfFhUAVs6/OcyTdYCN3nHvmPsmeJuWW0uRvfLfpKupu2keGNo+BKIuJC5Qn/M8NU3iYZbAPQhIpko48OquIzlxg+hjBYjcN3HtEtatpwy/wD5DEALVjHOPYxaU1WyCR2yPiAWKDzDiKTgfw2yPbMJbAM+Yr8GPU4eG4HmIEC/xW4BDD9YkXrnuCfWe8Sp8BWGT8wLqrXKyk8D59JTsbPv7e82GRjWdrbh6gmZ9uzONhBH9Jh6OGbcgsyO4PcYlMO2nDGskYPaaT0rtJU7T380qXIlibT5X94mkf0s09UNag2FgM8MJfq6mLFxlG989j+M5yw7EwWDASrl1fdWSrDt+ENTNIlt6jT6f7V4tLmiwc7fT8pZXVO4C3LhvcjKtMayyxkXxF4PaW9Dd4ljVEnae4PoZVUWjw0NtJBW1fBY/mIg5rbL4CY+8vr+UaWC0kOvmA8pbk495V19Fjpmx82EblA7kTT0yUNSHYtdUCFLY7QqWRqsg72/xG6yweDXWpy55OPSJ0dbL4it2UZ/GXT2y5PSRWXLEyDT8TSoo/gg98iH9n+J0w5ZljtT8cwGp57TYOn+IL6c47RlrGNPxANM2Tp/iA2n+IsGsc0wDT8TXbT/ABAOn+IYNZBpxBNPxNdtP8SPs/xDD1jmiemq2m57T0MGr1dI9oYoGe0JXGIW8SggUjE8tIyIe4YEkNzASHwB7RiUD2k7hDR4EHwBmNWgY7T2/tGhhAAWgZjBSJKtDDcCIAWiM8GErwt8YClI9oYp5EIP27Qg0AhafiF4Ihh+OISuIHAPAElaOO0ZvhBoGV4AhCgRgbmFugChQPSQaf1jg08WgFc0D2gmjMsFoJb8IgrGjv7RbUy0zQC0Aqmj4gnT/EtE8yciIKR0/wAT32Ye0ugiSMQwsUfsvxCGmGO0ujEnjMWEprp8ekMaf4lr0hAx4FQaf45jBp/iPyMw1IgCFohinntGgww0YKFPPEMVYyT2jA3JlPq+pamjFY5aFp6xsnWNnFLquoXwmVW49ZzV22y1rGRSP5fwl7V6hLQEPY8fnKwCtsC5yB2nncl5vLv46RWEWr/DA7A84EpaheAgWbAG5eRkypqiiKRkZ9cTK0OirP067chcr7k9vzjBdSoc1stSJy1mMiVrrC21AOT2HoInULlgtf8ALzhvU+5+JMNq10rdYb/GW91rX7oC8k/MufbKMf8AGJ4jjjKDj85m23PeRXVnbnuO7GWBpvuj0X/Jimf6ddeL+1p9JXZ/E0d+4n+UnBlc6bU1t5qyPwj69OVIKg5MsoHZQpJ49cxNojFOmy5eHR8+8fRddRYvh2eT5ltK3wNr5/GT4ZVSWI2/8seFi9o+o3qAWYEH0zzHtrFuytgcA/zKZlC0Ag7c49YRv3DsB+EfZlbhiZ2IaRrUc1uG9txirSynkEn4MzzZYDx5k7zw1XPkcgezCE2KOOYXFvuyVC5HpzDJfAx3Pu0os42cp39oVBywwm0D5hEnNF1C5by3sg/5o8VagnJvsdfgyoGXClkb8TC3t/KWlxjOaytM9gBFoKgepMrW2qmWN4x74nmFhBFtyFfkyqTpkb+Gysw/MCKZEUObVCtA2/v+pk19RdnCu2V9iJl3EbzYzl2PoTgSq9xUjcAR8SZtivqiXSLqK2tzvXnsDGpeg5KBhOWR2V8emc5jxqbVYHeR+McciZ4HTVa2tDhAQI5tVTZ/qV5/uWc1Xq2OQ6gf3Ay0LRYo2sMzSLaxtwZLStWmxt2+xG+e0o3UjJG9G/DiLWwOTzjHHM9ZhgB3x7GCekwrPWhs+9gwhQu7ccH8Imxgr5dT+cbW67sqRkemSIQmYmD3UeHy5wORE7CdlqHLAkxm/wAUFSo2+pzzLlFBZRg4TsPn8JcRrK3hPi6jUL4dSBBnkgSz9jZVYmwszDvNHTaSuisqR5mGYLBFUo3H9M16/wBuebf056ysVq4QcdjKuleyx2wchPT3Ed1K7w7rNvC4lX6aazfc1g8hbEdP9sRyetdVp612YC8emIzwhB0zfwFPuI7cJ1uOSTSM9pDUj17RjNj8J7cIyJ8EQGpEfmAzDMAQ1IAi/BGe0eWEDcIAlqRANI5jnYZglh78xArwRmeh7xmegGIuqHvDGq+Zyy9Q+Ywa/wBm4k61x066oe8Iakcc8TmV1494Q1494aU1dOupHvGLqR7zmF14x3hrrx7x6WOoXUD3hpqR7zmBr/niGNf8w08dONSPeMXUj3nLrr+O8YOocd4aMdONQPeF9pHvOZHUB7wh1H5hpY6hdQMd+ZI1A45nMjqHzDHUB7w0Y6b7QPeEuo+ZzI6gPeGOoAesYx0v2n5hDUfM5kdQB9eYY6gPeIY6X7QM94X2gehnNDqA94Q1/wDdA8dGNR35kHUfM54a/wCZ46/5gMdAdRx3gnUfMwDr/mAddz3iGN86ge8jxxjvMA64H1kfbf7uIDG/4495Jv4PMwPtw94f20Y7wKW4Lh7w/H7czBGsGe8P7YMd4Dy3Rdx3nvGHMxBrB7wvtg94Dy2/GGO88LhMM6we899t+eIE3fHki8e8wjrRjuJ4awe4gG+LxmENRg95gDWjHeENYPeMY3xeJjdW6kg1S1MeIv7aMHmcd1u9tRq2LbwfcTD5Fsq24K7Z0ytQ6D4bOP8AvHipVAsU7l9xOT0tzoBwzEerHEunrldNRTB3n0U8Tzu70Yo2NReFQ+izH1FviEk9pWfWWXcsm317yKl53WZ59IptrWtT1YVpn+dh6xfgtZnnzHj/AHMOqovYGf73oJrU6MqM4yYOziopaXRBG37RgDCyxRp1L4/xNFaSF2+3pJTTui7vbvCIdEFV6dFBLdopqQXwo9My+AGAHOR8yHqHALNn4lnEeVBqiMeXmRajhf5iD7DtLhUcbzg5xB1KrgDPaKV5rPSpwfvOB+HeGyNy2V/OPsV0AOMr6YiGsVlI5z+EzOaq6bwSGCyfEOCNg/OEyEqNqfBGZB3KdqqFx3zDRFITWrEbnAQfELfsYMrfqYl3Kg7nBHeJa4sygbMGLR0habWneRktj2ibNS7oR5s/Jg5BHh8/j7wVrAJ3E7fniONLpBQ1BU4AP5niSWJGVGPj3Mc1FTYKCSa2ReWLD8I/SZqz7d7v/EHI9jGKFIwQDLArDZPHeA1LFySNqyS6lvTuCsjEH/EJSwxlN4/tMh95UqnIHrBUlRnBK+uRAsPIRgDzU0JXetuWG38oD1K43Kv+YpxZWME5X2jicTNNXlsLZYHPxGptYbm4/CZ4UnBQy/p33V+ceYek1rOs5oVqNOHX+HcMnnmZl1ZDkNeTj0E3iiPX5GCsPQyhdpLNx3FffynmaY57RhGlYKwOTgehnQ9OY2MrE5I7ZnNvSVbJsVfgmb3RycIxO9fcSq+3NyenTU2K9RJ4ZuBM7qjkVKV7iWGsAUseJT1bC2t1LZPoDNpcmY5Trmow6tnarjv8xvSLjX0+wA+fdMb6kscacoeSrcRXQOoeMFXAwPvD2xJ45/kXLH8X0Ou8LWq57CF9pA9Zz32/2wB+Mj94D3GZ2a4ph0J1I94H2gY7zn21494J1/8AdDR1dD9qHvzFnUj34mA2v/uizrx7w0Y321I94ttUPec+3UBz5op9fxw0NGOiOqHvFtqh7znDr+3MW3UOe8NGOkOrGe89OZPUPmeh2PHEDqPbnmMXqPH3pxw1p94Q1x95zd3V0dj+8fmGOpcfenGjXHPeSNcR6mH2F0dovUf7owdR/unFDXnjmF9vPvD7D6O1HUuPvQl6l8zivt594Q6gfeP7C6O3HUufvcwx1PkZacR+8D7mEOon35+YfYOjuB1P+6SOqf3TiB1E/wBXEkdROO8PsHR3H70/uhDqn904YdRP9Un95HjmP7C+t3a9U/uhfvTn704QdSOO8IdSI9eY/sH1u7HVP7oQ6pz96cKOpH3hDqR94vsH1u7HVP7oX71+Zwg6kfeGOpcfe5h9g+t3X70/unv3p8zhh1I+8n95HHeH2D63bnqnzI/enzOJHUT/AFSV6kfeLuPrdv8AvP55nv3l2804n94kesIdRP8AVH3HR2w6lx3hDqQ/qnEjqPzJ/ePHfmHcdHcDqXzC/eX904f95cd5795fMfcvrdx+8+PvSf3n/dOH/eRz3nv3mf6ody6O5/en93+Z795/3Thv3kcd5I6kcd4dx9buP3n/AHSR1P8AunEjqXbkz37y+Ydx9buB1P8AuhDqX904YdS57w06gzsFU5Jh3P63eabWNdYFXmMsAvvK7eAO8ofTtJbTG2xtuZp05B2icvNft4b8VM8gGiAIBDEmNPSVUB8YM09Mo25fHEZfkg7hmZRSHTEsX7Eg3MzeX8YlhyNo8o7fMuaiuwsN+FT+meqq3bT6gybVx1cVdO6Zo2Y+I/vN+irkY7yrSjPiuvOfUy2jGkgEj9IoyHbFcjwO2sBsEHJ9oVdfABHc94PjZ3FT+nP/AEj9PtclmODj+b/aVE6PRT6fa4OzIzxJtqVgNynj5lt2KjJwy+hEFww5K4Uc7pWHEsu1SH8gJIPeJZCMm4Dk+g5mhagfJG8c9twiWdK8Aoyt65/6yJhvH/FKwFcqoOGPGZXbNZCshJ+JosvfJV1PoJXtpZwTwefeTMGo2rZWScnaW44yZBossybNwWWSxD4s2Y7EyGt2krQM594YFE6dAW27yFgJp9rKSuW+R2hWXbAzWOFx6QqfFZSxIH4ycVifCQ2DcDu/CPWnwzkgMPwzA2Wld7dvXiNDbQN7E+vMqCmBsoasEoefaVgWZtpTbj3HEa14KjlCnpgzwYFjtJ9+8U+UT4gltNnLYXP4iVnqwD5MfImha4BwoJUwKt7LwoAEnEKSKVbIHI/qGY9WFm3BXHrLdVdjZCpx77YbaTcp8RMH4HMSZlnXaZTlkbY3+JTZ2rbZcOD6zSt0FtRLUtvU+hlZlW5fDu4b59ICFc1lSGobI9Vl1GAzjviUlD6dwM7l9DLIQ7lZT27iXUsWWfKgY7zM1KsreUkK3pNWtFZdwzu9YjVacODu5B9ROmI1yck4xW3q6q2Pgza6EzBmDcN6xX2EXaZkxutXzISZY6arV2ecYfE0rXHJyWiYbF923Tlm5A4nPazqlNdliuDuHsZb6jqc12KrbSfScV1q5vGVvQrhorWYdVrrF1d9FrVsSwXs05/p+s+z3j/6i5PxGDVDZYM5AU/9Jyml1Ni3M9jc52j8JNbZOptHjHcfvE+8g9S/unK36wpYQD8xJ1xHrN/tYfW609S/ugnqXzOSOuPPME64+8PsL63XHqXzFt1H+6cmdcfeA2ub3h9p/W6tuo/PMUeo/M5VtYfeLbWH3i+w/rdU3UfmKbqPzOWbWNjvFtrD7w+wfW6r95exnpyJ1h956L7D+tkSRCZeIKjmQ0F6Tx4hqvHtPFeIgEQ/aCF5jFWADPesMr+sDHMAYCZ4nHaSqyduIAO7mEDBIjFEAgk5nt0IrAI5gBgnHzCBOPeCixhHEAAE57xik+5gY5hoOIHg8me3HPcyT2g4gMGpOIRJkIO0JhxEA7jmEGMHHPxGVrxGScnHeeDH3klZG2OAIE+8LJkKsMrKgA3H3hBjII5kgR4ScniQWPvD2wWWPAjcfeEGOO5ghcxgTtFgTk4yJClie5hhSO0kBc8iLA9hvxlnRWOloNa7mnqHqU+asn8TN7pmk02tpZPF8F/TEBLrOkalW6ehswbAPurL2mIsfGdoMxumdNbR17fE3j3E3+k6drbRnhB3MxmuzjWvps10hakxyTLP2EhQznYD6nufwEuaOs7coqqP63/7Rzmqkbi+9v6p0VpEQXad8MKzRfeLAgH1ME1CsYQZMv6ly47YX2iDWS45zntOfm/49D4/rZO07jT1Zf7x7yQtmoG4I2w9hjvHaXSB7N7jJHYTZrROA36TCI11zbGKa7qgfCTHwJXL37iezf8ANidQ1QchVBPyOJm6rpJZm8NrFJ9TNI45/ERyR+sn7QUH8Ss5HBy0OvWL90kAHuC2Z7XaB6kVXZiT2MxtRp7kfyZJH9KxzEw3pMS6D7TXyXwFzjn1iHsD/e9e2JlVWWIo3ZyR92F4zEBSuD6Of+8W62iuLr2ogUE+VvLx6GC6sWUNkoPXMqDUBvI5AJ5EK26wMy+u3j5kriNQ9zKxravjPBEk1sVHnUYGcnjMXXZZtBzliMFVGYgte942WLgjzAiJP6T1imsIjvYNoIyPeMr/AIaI2fOR2PoZH1BQPs1K5+/Yo3D15ll9JuvrVdpIxiL9HaIODswWsjcxHpBfR2eIwYH85coq/jK7DEf4qm0nPPzHEb7YzzRDP/dbsUaokYluvptiDLebPEspq0Q7axgHuxPH5Rq6tDYGJLkekqIhz2559QqDpoyNpxj0JlxKalq5Ubuw+Z6/XpsJ2ceq+0pWaprnArUKPYnbH4j0ieXfZ9urqpYq64IgrrKbPu/9ZTs0/iAtcGA9OQMymdBTuNi2MD7hsmTMSqOWjYehCCyttb4mdq9Ot2N422Ds3oYq263Q7CxZ0Y+2PwzC1VztWtiLgZ8wzMpaVnfMKtZFbsly5/GSpVQR/wD0xrbdRjd3HqJ77K24YORKqcyKuseCSgxn1ihvRirL5WEv0oijZYpwR6RGrrFNmFbkTrpHjXFyzs4PpZXcpQAjs6GN1VK6cKynOCdrfHtKlOa71sq4Y8MJodY/i6b+GOWXKj5m344r+3Ddc1e2zKnGCQf+05rqmqZ6Mt94jv7iXOtaktbaG74Bx8ic9bZ46qS3lSc0+1E6S110thcHLZVD7yn9lZiLSNlY5YmPa+pLAbjuI7LngQOoaw6mtMjbWOyjtCGVlG9/EtZh2iTGEAnOIDDmMBzIzJA5khYABMWTGOIsLAIMBu0dtzFuveAIaLMcy8wSuIAhjPQis9AtKYTyjmNK8SFXmaE8qySIxRzJ2xYCFXmOVeJKpGBYYCivBg7eZY25HaQE5iAVWSVjVTiEU4gFULzGKsZ4fMYqcQCuV4+YO3mWmSCK4YAIslljVTEkrAK4HMYq9pIWMUQAGHaQFjCJ4LzAa8iyWWGiwiOY8BQXmMReZIWNVcRgtl5kbeI5l7TwXiPCAi/EMiEo5HtJIjiAURzJUQ8fpCVYyCFkFY0LxPFeYwUq9o1VhInMYq5gCSskLzGlYQXtECgstaPdXapBwIKpL/S9Kb9UiFfL6xTH6btvpvT336QM7EJ7zrtEiphVRcL7zH0bKmmSqgAFR2Es1eMceYVj1Jk196uIbV2qrrybHL2+ij/aAN1hD25X2XMq6Za0z4QLue9hlpdRVWSMhnmh1jycV4IVRCrTI5Az2EDS2+MwGcntLWAiZHJE5uTy9DjjIGtuzbXX94xtTFwQFyR3OYnR+J4jvsXHYFvSPt1brgbK9nbgyK1/V35evjAvqHTPn/HntLlWq3BN2WEz31i5IzXWBxjGTIHVlprY1uLjnbgrNK+P1jbm38bNoFlZYVDI45lTwjYCPDVf+XuZQXrtLMBseqz+nPGYz986atguqUoW7NmX2if0qcsx+PWdNrZdyphv8zN1ulqrQhSPE9iJf1nWa1UCu+o+mHmHq9crPiwqX7+UyJz8dPHy2n2ra6tPUYK8AjtB8jVA52sv5yp4zv4rKfKWi6rTRaxYnOOJM+XXxX3wsdNZ21moBH8MFeTNYqtb78IfTEx+j6j+NfYwBRmA59PmW7dYDbsrOQfUyfEQ0mNlPW136UNlcqQ4HoOZapevwd3CvjjEyNTqiVeoEAlSB8zPq6oxqrV9qWKu3nsIQy5J/G/qtatKkLncRhc+szatU4U7j93ncTMDqfULycg9vUMJjX9UuZNhY4zmOYc0uuu6wRdlG3g8c85lpfqAV/6r01DsBnzT5+NbYPKow3vKzalwSVG0nvzFjK0a+kv9SDUEcb0+F/3hr1BNwf8AiNZ7d/8AM+eabVWEYZmOPma2l1CAjcxLe0mdRFHZnVO6hmB5/qPGJbqutStSwGz+1eP1mB0/UbiHA2n0yJtVm5hvdl2Dtgyog+uNGvbdWQy7tw5yJmGp9Pc9Gd1R7e4Es0ahvGCqFVu5GOI7UllCNbUmR2OZNq7DWLTDJUslg55mjTZuUgys4BcMRx7SxUOQT2kx4a7orMGoYbGPeKtbxlrLfdbys3zJ1Y3Danb1lfTFgGrbkNyJ10ly8lf1coqY3Ff5sZzJ6tcDS4J2unIPwRGdPY2eG47jykzH65YBqwWPGdrD5mkzkOK3mXDfVg3XNamAzqc49T6zi69YULIysB/MJ13WWJcbvu5bE5nXUhX3Vg898TnnzJz6VNteobdk4lzVUqNBV4f8pkDTijTbnz4j/dX2EMeINOocHMcM7M7HHEhl5lu2ra2V7HtFMsMSrY5hY4h7PaSVjwEMPaDjmPZfjiDshgKxAdZY2frBZYYNVSsFllkpAKcRYNVWWejSk9HgVwvHtC294YWTt4lgAEILCCwwsAALDAhbYarAkBcieCcxqLwPSM2wBIT2hbY4LDCRYFbZJCSz4fHae2YMYV9nEjZLG2QV4iGk7eZG3/8A2O2z20QCvthARhWCRA0ETwWSBCCwDyjmEBn8JKiGF4EZBVe0YBCCwgscAsrIxHbe89tjIAWeI5jNuJ4LGJLCwwveEFhgcGMtABJ2wwvvGBIHpariMVYapGKkC0nZCCcR4SEK4AqussQBNrQIulqZ7m5+JnVqVORLlr/8KWb85NvSqeZdH0rqGjeru42+jd5o2dUopGaq97enqBPm9erNeqzu8s19L1TTBwPE2P6gzKt280dgvVbdSQu4g+3tNXR1jZlnyfwnK6PVVuc1lG/Ob2ku+6bD+CiV2acdfPh0fS1CsSBkHsZolN6AdveZ2hbgFZo+LsBZs7cTKfLrnwKtiinw0Z17fjMHqurWs7WrC/HiZljq2stQtXU23Pb3Ey7NOLFJf/8AJoe/EIim+ZZOo6g219nf0UmZWs19oqUMGr5/l5m2+mQA7mTafWJs0+h7u4/WLq0+uHL2dU6gG/h6qwqPYz1H1Dr6Xfx3DgjA2nJH5dpq6o9IUsptp4+RMfU/u6x8U3IW9g0MwdMN/wDaWxqwtyBlHbHlM8v1CjVhGqfI5DFpnvoq2YbXBz7Spdp2TIUDv3hEKjHQ6brJdW3tnPPEdbr1szaxwV+Zx4vFLkMcfM0dIi3GuywsV9B6GHlpW2T4dX0/UMNKHPBclsZjm1TG0FffvKGlV7CO3HxL6aIgg5Zuc8DtM7e3ZWfAdQllzMyOEfGDkesxepXXeIFuVUs9T6NOmfR2DJw+FHBMxOqVuylGGUHc4lww5Izyxcl2w33YOxUsIAyh4zEai/wlCgjBljQ1tdXng4/zLisy5LWR4GRnBJ+I2rp/iMCMER2ouq0tOSNr9lA95Tqq1mtt5u8Ff/pjn9Y+spidatfSjtBXBPxzH09OtqIbbvU/EZ03ouqzkdSt/wDuCzdp6TrwB9n11bE991YMfWf6aZijpK3wSCpx6FZoU6s7OLAmPYd4i3S9a0zlm0+n1Cj1Q7TBo1NGoZ67KX0+qXk1v6/hJnx7ExB76qyx1IsXIPqgzNNbXt0/cq3ue052vVK27DDcGxiaulssOmLMPKPnmSMyFh2Ph4cYYfMalyqqDvM3furDZwfxjaQfLYSR+MzxdYXidpY+8otdm3aDjHEfdYBjn8Zms2204OcHM1rZN6+HRdLz4N3YEDd/vOW6vab9feR9wn/oJ0mnY10WPuwACR+YnG33btZYFGFOT/ia3n1Dz88zLC1bjxyB2X1lI6Wpc3WDI/lH9RmvZpgwZ7ANoPb3lbU0+KN7AhF9JlBWYeoqs1DtYBz6SBZYK7KnXIUd5obHrDX2ELUvCriJpsrdyWXAPpKZWhm7c1lT3U5iSk0tSqtcxUeXEqFJTNWKcwSsslYJWMlcrI28xxWQViMkrBKx5Xme2wJWKQGTiXCsWywCkyT0slJ6AUtk9tjwneEK5eHpGyEF4jtkkJDASqxirGBIxUhgAq8RoWMVe0atcASEhiuPWvmMFcMCtskbJbFfHxINeYYNVCkBk7y41fxAKd4YFQpIKyyyRZSIElYO2PK9p7w+IgRthBY7w4QSAKCxiLiMVIxa5WAsL+skJHqvEILHEFqvshbO0ftkhOYxqsUkhJZFc8K40kBJOyWVr+JIrgFcJGKn6x4r+IxK4DSVSGqcywtcMV/EBpC18xq18R4rjFrgSqtfxD1VTfYXwJcSvkGPOHrZCvlIitGwqs5OuIwWYYHmmhpOntqwGsGw+80dNoUe1xUOczrek9JVaVJUbiPWc1a57d8R2ZHTdF4LIije06rS6Zl28ec/4j9D0xRZuOOJqWUABdnE1mvjVU8WN0yFE78y416VVDfn4latguFjXFbVbLfun/ExdVo2IZ2uuq8Rsod3uTmc/wBe60mi0hKY4E0eqV2afIJzUR98CfM/qUarqWsGm0CtaQefb8IbPqBWIiNWT1S7Xfx9dqDptKeyK3maUtX9Q9K0JULR4px3fzkzx+g+uX+HbfcbEHJqAwPwkfUH0lqrtPp7NLpHW2rIYLxxN6cc/rLknkivavlWq/aH00eVtGAg/wDpiNq670Hq9ZCitHbnDLicf1P6F6jdcrUaK6o+oK5mhoPoPWDw0OkuRB99m9ZrPG5q8/LM5NW8NPZpiLNE7eEf5WOVMsrrEuXa3lK9wYu7pPVenBW0NZZPWt24MjSMNY+3V6a7TWj12+X9Zn0z26/PtndUwykIPMO83PpLfqtMQyjKNiBqfp+9VzUfHrbkFZv/AEp0t9PSVKEFmk2iIhXH5s6fomkS0qGQED4nS0aAfdRVCgZOPeVOlacKoVBxNutGUdznPtMa/wDXXMsjV6Pco3KTicv17TbNDe9Y5Hed5cAwY7hkes5TrNXjae5K/MG7y4yE32YfIOokeKi5xLVOoSmkEH8x3ljqPQL7tUrV/dMG/p9PSUHjtvuYf6Y5MuZcnWVatXttN1jHjsX9JW6j9St02hjpqvFY+UNjjMVX9u6xql04ptr0oPmwPT8ptfUfRa/3dp/Bq/0TkjHeVSk2nyz5bTx1/j7cdqvqXr1hDrbWCR9wOOB+ctaT6s67QwbT3JqNi7nVCTs/EzF690N9VqFu0ljKSNrKczR6D0jUaNPs+h8W3UXeUle02+qn9PP/API5t9vpHRPrTqVFNNmtqLUuoYP3H5zd1HVNB1mlbEIS8cjHpC6d0Uafo+m0aJ47rUFbAyMzNo+gdVpNWdYuo8PccmlRxOfkpP8A7fL1KdpjbxjPp3jVapbCMqd2ROh6TdsoBFnOccyjZ0+2rqviY3Usu1x6gia/2LpWawA2O+d0wiFefS2uqrZS2xB+A5i1K2OSM/Ek06IjdSpXaewY8yGZaxkIAT7SbS6Kx4TcuF5OQeZmgA6mxvyl+9gyFh39ZVRQoJ9M5jpKOT00tTcun0DKR5mrxORSl3beHG3bzn1nQ9RsLABj/KJlNS1NbJWvlf8AxNZ8vPxUILArtH5RRWqsD7QuQD933lu21alBUHPqT3mXaGtcknmL0mY0vW6YagAq/H9JHaYrUrW7eIwH4CdIqqtWD99vSIu0C3klsBfUw1FoY71q2n3r2ziUyvM2DpGdxXTgVCUtRT4drKe0uvlz28KRWLZZaZIsrHidVyv6wdscVkBeYHpO2e2x22RtgNI2wGXvLO2CU5jKVUrPR5WeiwlQVwhXLIrhiuahV2cSdnxLQrnvDiGqwrzGqnPzGhPiMWuMaBEj1rhV18/EsV19ohpQrjPDjxX8Rgr+IDVXw/eCa8/jLxr4gmuMaoFO8ApLz1xTV8xHEqJSAa+ZeNfxB8LmLBqn4fPzCFctivjtJ8KGDVQ1zy1y54cjZ8QiD1WCQ1SPWvJ7Q/DjLVcJyIxU7R61wxXxAtV9kIJzHhIa1/EY1W8OGtcsivtxzDFXxAlUVw1r+JaFcYtUrC1TWviMSvmWxT8Q0p/OGDVZa+0MVcy2KYxa+O0WDVVao1afiWhX8Ri1/ErBqslPEIVYlytMHtxGGoZyITBawfDbS64Oo4YzSv6oKHR+x7YzG6vS+IoIHmEzep9OdSjP2nJyR1l6nw/5xjsek6p9QiDjzd/idAlIKEswCjt8zmuhU7NHXx2HOZupaSUB/IS4t4aWpMT4FZtDmJdGcDNpVfeWLDlucAzw05uYKrgMe5xOa3t1x6U7a/s2ndbB9tRxgVhfNLH090fT1g6izTip34VMfdmiNIvT6C9eXc8szccSvX1Nnywx3z29JvSYifLK0TMeFqyvw3IIIX4GZQ1a1ucqpP4cf9ZF3VUAY5P5TOs65k7SQM+s3jkqyiLRJz111g8kN7bYg02YHmOfRcQj1tAeGDfjKdvWgSzIQDL71XEWl7qGhLqEsOd3PeZwqo02FLKzdsReu6nZc+AxUH2k9E0t1uqNjk7B7+sU8jWtN9tanS0ppv4SAFo7p2lCsoC4E0G0vCsfvL/mM0e1PI6859ZzzstYpFWloKAibie3pLvJrJ24OfeIoICANwJYNqjIz3EnB5lSvrCUkt2mDqlBZivYzf1rhqSmM/hMrwdwK4/HMz1rT15ZA0ebCQvl7zC11el8WxTpx4hPLEcztaayuFxu9DMrrHTK3BvUEMDyAuZtSYidYXp58Oc01apYDQUU+o2zTrbUKgFlK2jPcLK6rXp7csyOD7jE1NLrNPWvkbt7HM37xKLR1DXptM7A3aFCP+SaWmo6fWciitDj+jEBNcnZbdoPuI5danH8ZY+//WPlo6XUKyhdNWT844l0IorPiMGbuTMVdcG48XC+wjUvrLKGO5PvHnvM5uUxMq1+he/UW6irwgmcbXHc/jFarQUWacHVaZdy/wDzK3/2l/7UHsVKRuUdpX1FJtBZWAsz9z/tOe0t4ic8slqNOpXwlcD3zmLetmsG5xges0X01e0c+HZ6j2/KZ+qqZWxncvbM55a1lWuUIWAORJUK9AC8+k9YuV9olOHVc4IPaXSU8kbAdSxaxlI52iBbeGrZscjsIWo3V6nznykYyYk1m1XC+VZs4Le2dczW2qccf9osJXSfEuYY/lX3jNddVp0K1fxG9/SYOpuuttzu8xhpdZajamlrCzIXb0jazZewDKFp9piC58gLyfcTe6PQ9zK1pwnrmJFo8L1fT99Oa17zn+r6cVajYOdonb23JXRsr4AGMzm+tab+AluOScTWkOS7mmr5MUyd5fav4iWrl4z1SKcSNktGvntI2RTA1V2TxSWfD7T2yPDVdkEp7S3sglIYNVPDnpYKcz0MGkLXDFcsBIYSUSuK+O0Hw5cCcQSkArhIapzHBPiMSuBaCuvGJZrr4hJXLNdfaBFrXGCqWErjRXzHg1T8PiCa5oeFANffgR4NZ7VxLV89ppNX3iXrwO3EUwah4c94Uu+HzJ8OIKQq94XhS34cgrxDApNXIFfxxLhryZ7w/iB6qrXC8PmWVT4hhOe0CVhX24jFr4lha+B6Ri1/EAqiqMWrPpLS1Ry1QwapimGKe0uiniF4XHaVEFqmKoa1S0K4xa+0vC1UFUYtUteHDWuGErrXDWr4lla+e3MatfxDDVlq+IxapZWvntGCriPCVhX2hCv4lta4Xh8R4atVX5hxB6vXuqXjgS4q7YzqAB0Q45xOX5FfD0f8bP8A9SYR0gk6VeOTLjttcCI6dirSqxHb0iH1yPrERuMnEw7fj0b1yZbTdgfiW+moAQ/cyleRsBB4I4l/p3lrBzM59nH+q/fpkurJYO39u7iZGs0SPvFClWX0Qd5tJusBc+VfTmIs3MfJhR/Via+oTX3jitZptTQcPQ20jkTI1KsQwqqfd8CfU6whUjZn5Yd5T1C0rljWufaKfC4rr5NZ4ofAqsLDv5YVel1+oXCadlGfUYn1E6dSABUPN6x1OhrrQF8Z/COqpjIfPumfSVrsLNRaSe4Udp1ei0lVVqVKows6CulCrbAAD6iZoVBaT6zQVn2O6tB/6SuMNcjNgDMZapYnJwe0ZVpw3hDHKxnFmhpqvIcqcd4TVdxtIEtUptqG48Ygt249fWTMFFmFe+xmXk4iarAwzH9RQ+IxUjnmZhY1MmON3Myxt+L6HIOTyTJVTluCSPeIpc7AcA5lgHLc5z7R1TLD670SvXk26fyWjuROKv0+t0LFHDKM8NPp65V8swC57Q7NJp9SnnRSfkTTGd6Pl1Wvdf8AUYEGXKdUbMbU/Cdlq+gaMvk0Vn17dozTdM0tZH8FMjtgSJ2JKK65nTi7xQpRiT2CqeZu6HpeqsYPYwUH09cTXFVVBG1FB/CS+ofw/L974MU2j9EVn8UTp1043U43L94ZzmMXFwB5DgcH3lgEO7FwoK9sxNlY3Zq+796TJ4VqG3KGbv8AMzNQm5jnv6YmtqNpTt3mPqFKn1/2mUnCk+ccRC14sBPMsudrE98wKlG8kwr7O/oWorFmnDEeYZEybSUDLnj/ALzaVttWcZxzMrqZFN/IwGOROqYefnliautWUgZy3tKb0ikhSuSZp2XVjUlFAU98mRZUmcsNx7gyF5rNppv8ULWqqo7mb+jsUYH38dsepnN9UOocBVcpX7LNX6dqIoDWMQYoRfj/AIzLeRAw33HbKPViHVVJ49BLljUVr5n3GUdY1bAFAczajzORiOkUyS+9cS1c1ZapGv4kGuW9nJkCuIKvh/Ejw+O0uFPiQa+Iz1SNfxBNf5S4UgFIgp7J6Wdk9GCgneFs4jQvMLbxLwE7YOyWNnaSEiwaQtcclcaEjEr7RYJkNdfxLVdcmuvGJZrQSohIUrjgnEJFjdvEoEFIspzLe2CV7wCoUi2rzLZWAwiw9VDXICcSwwgHvxzJmBpJWBszn2lgLJVIYekCviQa5bCcQdn6RYNV9n5wgkeK4S18wwy1rjVrjUSGK48LQKkalfMYlcfXXKiCmSxXwJ41ektCuF4YjJUFcNa+ZY8P4hiuUFYV9oS18yxszCVIAta+0atfxGqkaqxjShXz2hpXg9o9U7Q1SAJCSSksBP0khIBV2ciTeoaoLLG3mQqZeY8te1XV8Tk+vliSb12aUY7TBrpss142jJ3Azo9cNtB9sSh9NV+N1N2PYTiiPL3r/wCsy1r1K1qpHMfpHGNpz2kawbrW+DKlVmHOewkW8WRx+YbdVxYkHGF4EY1jMygABh+ky6Lxkc8zQUnIbkyolXXB2V2AFsE49IFGnwM2LuszxkyzW3l8xwDB3Ickjzdsx+DiZ9G0oEUlhknjIjm2Y88qWuFQlCpI/WUb9TYNMR3ZvX0ErtEFFZlf1FyqhFO0EczB1+sWkM7MN3cY9Yp9YyjYG59T7znOu61hUwrCvn7w9pFr/wBL6dXRdM6iNZYMkZ9hOo6XTyWY8Ynz79nense63VXturU4H4z6ci7alYHAx2m3HMzHllefwa2qFIJxiIttDMQnlB/mERc63EquVIk0bEAUY+JcnFcUuo07WycYI7+8y9WFNALEDaOJv9QyasKgJxg5nN61XLuQuQvpMp940rOwrabWLu27sFe+ZoafVefD+ZTOH1+os0vUWDDarHIm10fXMwGWzn/Ez3Ja9YmNdUm2xSducw9ONpIzKNCkYZXz+cYzjxCGxkjGRNolnMfkLdp8m72lG2w79wZQvpxPPqBtA+8g9YC2KzYYYHpM7zoiuBFn8Qbmy3cQ1sOwshOPSVbzuLOTjb7ykHBfyZBHJmPbFddavikjJcn34hN94FTkTNbUeImdw3+3vPHUYwO0rsnrJt9h8QgEj2lDUsAD755g26g7x97k4la1ixJzxM59lMYYwDEFfwkBcBuO8KkblAhE/wANiRz2jE+nh/7s5X0mJ9RNZ9jygHibcLn3m0DnTvt/mxKnWdF4uibcDkczprOuKa+Xz3TXWXsi3HFqnvOn0NWFVWcPOdsqsruYNgMjZ5HpNnQ2uzA54is1rXWjr0qqr5rWy30HoJQrW1Bl2OW5xNZkW01qBk+sra0FtWFHpxJ9o546U0Va7gpb0Eixc+ksLXhQBIZeJ1UrkPCvbZUnWKZJdZIpklzCFM18yPD5lopn8Z7Z+sWGq+HzPGuWdv5SCsMCmycwCn5S2yxbJDAqFJ6WCvvPQwyRXD2SwEk7JckrbOYQSWBXC8OAVwkaido1U57RqJFgCi4EsovaeRI9V7SogAVYzEILxJMADEW/aNJinMAUYBhMeYv1iMLesELmMCnMaqfpAFKkYtcctcctceEq+HkyPD/WXDXx2g7OYBVFcMVyytcM19oYFZVxGonMMJz8RtScwwISviWK64apHokASE/SFs4jwkkpKwK+yTtj9uZ7bzGJICRipGBY1EhqdAqdo1EjETmOVIApUhBI5UhhIGSE9oWyOCSSsAr7Oe0HbhgZaKwCvIkWVWcmAPSLqGBHMp9DqXT6233M1tMVVyr8bu08vTzTa12cg8zjir6OLbXFbVr/ABj8zPf+GznI5mld5rczPsXJJI4ExtHk+P0nTtyvPLTWS0LUCZihhWAfSELio8p4kbjaI1u+ONpOMkRb6ohCzjj295mpqTuBbgTzWKR97yjvH2VFIj2a2rLbmGcmZd19rWZYeX09oeo1RDKK8bZj9Svahw2cofSTutKwLqGpVK2YNsPz6znaRqOp9RTS6dwzWHzf2j1Mq9a1+QfP+E0P2eamtG1mruPmChEzKjzPlN7Z4h9C0C06HT06akAV1rz8n3mt+9CUCLjcPSfOh9QKNTYm7zA/qJbPWq9y2A4bHpNK3yWMVifbsbeojcwC7ie/EbptSiHcRicCOtE2MVs5z2zLp64wC73H4SvtaTSM8Oz6hrWsUqVAX+uUKHS5m5GAMZnMXdeUUnc2YjSdaV22hv8AMz7+dRNYjwu/WXSTdovHrHCnJYe05LpfUG0eUySfmfQqeoV6yvwbCCCMbfefOPqLS/uzqtyVH+EDlT7D2lWy0bB0tMe3Z9J6n4p8zKF7TTN4Ppx7+k+ddK1Z3cMMzq9HrtwVbPvH85MWn02yJ8w3Q7FNucmVrLMEnkn5lRtS6t24xBFxsIBH6ybWKIWLLWdRj7p7/ETYwYcttxxBJ2nhiQZXY5JI5X2mWmm0kEspwvpPJYcEsOfiJyNw/wB4G4g+VcqeDHBSY9hZgcSPEFnlkjhRtGYoLwSBHjKfK5SoUZ9Y23hMH2i6VO38pFjksdy8H2lEbUuCfwjeoAPpGA79ohGNYBPYybdQvjLVkZ7zasue0eXMdZ6cDssH5w+maElRtycTX6oC9aJWpxLfR9OyUkEYmkxsto8QrLUKXr29x3mea/E1zsO007gx1TZ7KDKmiQkucSaRtnF8++UwWzjtBZZZ2QWWdsQ8OZU3WLZfiWmWKZYsGq5WQU7R+2eCwBBWCyyyVgMseBVZe8W68GWWXvFleIpgKrLPRxHxPSTSE7QwnEYBDA4lkUqQ1SMAhAQMsV8xiJDUcwsx4HguMQhiCWgl8QBuYLNgRYaCxOIB53iyeJ4g5khZIARzIC8xu3MNa4ACJ2j0rhVpz2j1WOAhEjRXxDrSPRO0o1Y195Ar5l01wGTAhhK4TEBhjiWCvEBliwE45jKx2ngv6xta9oYDq1jlWCi8SxWvaMPKuJ7bGBYe2BTJBWeCx22ewIyLC/lGonM8oEcggEqsYqyVA4jRiACFhBYSjmGIGDE8VjJ6BlMIDL/iOgkCRIJNJtsrC/nNolPB8Mn0mfS3hqzeoi0vD5ezvOW3iXucFu/HEq2oXFjgekpMeG+Zbsfe7nGMyqVzzmYWdVCLzt2n4lFWJcnGNpmhaBtweZnWeVvKO/MxtLaFhWOG3Dmedgqbify95TYtuLBs44PMTqL1JyRwO3MmZaC1mqrRc9j8TmOr9UOCv+TLXUNUF5Y8icx1K82MNuDk8RxJTbCFV9fqQnp6zrdP06zS9Pt+zIxOATgd5X+melrtzYp3Hmdtp9MTVtHHyZtSI/WX/XxXr+qtqLMrMli+vqJHSOvW6ilRcdtw4z6NO++qfo+nqW65CVZe+PWc5X9Jpp6DtU5hjK26o2a+xSSc5hprr7RjeQvvA1HSdRpiQrRCabUXN4YPBkzBbLK+ouq65gatDayL6v6mVvp3rut09y1ay1nP8rmdhR9M7seICcwL/okWWA0sR8S4jxhdZ3Wt0zr9p2hDyOxmzrNHZrk8a08uMET30r9I/YgLNSS7AZGZ1b6Lcg2kAevxHWueXRH/AF8rZX6frPDcHHp+E6LpuqyVbdx6Zlr6r6SDSba1zt5P4TndCWrYD9ZFoxdLZ4djVYzgt6xoYlDkGU9BYt1YBOGHbEtMyraFCMcjtI/Fb5wS2HBVhgD1le6whirnke09vYndgJg9oVqqw3PggD0kGXX5bAcZBz+sOv8AiEkHtxiCCvYKQTGpWMbTkGVVMp8qjIOcwV8pAB9YTABtqenJMr2sVcD0lJmGjUw2HB2mLvJFSYMQtoxnviHa3lGYR5ThniEgDvK3SdDqrupvfqUZVZvLn2h0vsPuBOkqvLLWahkkTav/AFnPiR26RUXhM4lUttznyhRLY1prJSzlz3lfW0m8Vj7ufvfhHE6jzHti3t/w9th7ucLBor21r8xvUdtmqrpXhE9Iw+gA4m/DX9eV8/k7WisfhW2A6x5HHEFhxOh5yqyxRWWmHEUwiIgrPBY3EiBlkRbCPaKaBwQw5i2HeOb4iyIpBDD8Z6MIxPRYEqYYMqK8YHlGsAwg0qhzDVowfv7yN0VnMkQMwniD7QgMwgsZAUQwuYSpGBeIYCgmYSpHBIxa4YCdnxCVOI7ZDVIsBaLzLCJ8SUTtHInEeB5E7SwicSEWPURgG3iJsWWT2iXgIVysWRHtiJbvEYAI+teRFD8o+rvALFa8R6JBqHAlhBAkKskiMxAaBFmBmS8UxjKTQ0bW3EqBo2toBdVowNKytDB5gSwGhBuIlWhBoLO3SC0XmezEB59oJaCTkyCZMkDUW7KzC0exsborUL4lZEw9T1I6Nyj8H5mHJ48vY+BeLU+v9dBrCrXEJ2AmeWOzHuZW6Rrhq67GBzg4jrPMw9BOW/ny9CIzwi4MyMM+X3mXgqzFsYPzNC5ju2r2xmUrFXtnJ7cTCzSFS1WC+Q4J7TO1VuwEWHmamsOyteefQTntey1hlLDe3eJW+GT1O/I+8Tj/ADD+numnXavxLR5F9JXNL6jVbE5yZ3PSdANNpq0V8H1IlVhHtc0emWsqEUGbFKhayDjI9pU0eC23nPG3ImgoOCoXucHHtNoK0qttQbCoDubvKluhRUKFRumwy4tBVtuJV1HhOGZx3lxDGfLAt6XTe/mA2jgxA6Lpq7MjGPQzVIC7QhPbtFEjcBt5xzFMLiHq9HX4ijAzjiX6NH/FUlOPmJ01irw2TzkH2mjTfufh/KYoOdg5Kj5sLjB/SEFVgcA88wXvI3s58kN7c15UFto5xK2D1S6lpksqIxyfSfMuqaF9HrLEGQM5X2In06+5iWU+XHrOU+qNG2q0jPWP4lPIP9Q9pnfyvPGsTpuoatscibtD+IRuOR6H1E5PSOCeCRjnE2dHdsw2T4Z9MTE4lrL4hsIccqOPmeYNtJVfgiDtFm10GB2+Y0Ix27mIB4zHiyahvwXPm9vaW1AWsb85WINPhufb8IW8lc+/aOE/oLSN52EjMr288tyw94VuPE5Pr2Eg55BGfWL9KZAmVCrjk+kZbaDx6+sSucBmOD7QG/1tvo01iCmcX9EoNwQ9ptFXpJFTYX0nPaW5adQXY9jibdWtV1wxyJdcxGbJm2wnfu83zBGuas5PLCU9X1Guryq/MrVapdU7Ej4zCM1nzXildk+ljbqHtbvH5g11+GnHrPZnbSMh89yW7WmRE8QGPBniYBlskMYomEc+kWxiGPZgk8CQxgE8wPBMYomSxzFkwkIYwDJOYO1iexk6Ameh+E59J6LQzQ/EMPKIc/lDV5UGvhvmGr8TPFhENbDHoaIYQkYSmrw1Ykx6GgjDEYMYlNGMcrRhYXEcpHErL3jVJjCwuIwAYiE7Ro4gDeMSVxxAEIH9IgcuIxCJVDQhZzFoXlYcRmZRSzmPV4wc0U+MmSW494t2jEFuYljDYxTGKQle4lik8yqDLFZGRCA0Ke0tJ2lKppaRoA3jEUxhFopmjILxJMNjFmBPRiGK/wCkanaAPQ9o0GJWMHxzAjAYYMWIQgcDBk5gj0k+8RpMEyZGIggyj1Hp1GuQi4c+4l8wCJMxqq2ms7DH0HTKulIy1MSHOeY+1zjykZljXcVA+glJmXHE4uauS934fJN+OJn28xJQ54bMr2Y2gSypDKARARSzsfvBDzOWXZHtn6lWZC1h2lc8e85nW5y2RhvQYnVa3LMdxIwJy3UgTdtqUn3PvBU+nugaUWObGbIzz8TqkdfFC58o4BEyOmVGrTISNrHzECX6nKOA6kse34SoRMxENbTOqWBVYHPrL1NwTcAfWYKHfcMHaBLN+srqrPIBm1Wf+zTvssOAtbMp/wARng1WqFZhu/Gcpq/qC7Z/DYAZmZqPqCxXO7/rLV0iP1350FSAbjx7RX2CmzhTgf8AWcZR9R2oQ3jDOMcz1n1RaWJrcZ9RL2Ij0qvFv66zU6dKFQKeIuqzw25AyeTzOTT6mfduZsmX6OspqAvjYB95jPlXT810W4eGVByG52xiXiusb24Zs4HvMtLa713oxLDnvDZh4as3DDgYmfmJTNR6okNwOCc5ld7vERlPn9MSLtUcCvIyfmUTuySveEyqLfjk+q1fY+pFQP4VmSvx8S5oWfOM7l9pb+pNGNRo924CxfMszOi6gMiKThwTxIL9dJprMgJ5l4xLpAas8nHbt6yhpnwRle/bE0KGwpB7n0zHDSPSvcrIuDkjMSN+07uwPBlu9mYEFFC/jKrqdvcgGL9TIVXylyuDAV9yvkYz2hbiXJYce8WzhWZB+sZSUW2IpJGPWe3KEWzgkt3itQyljuHOO0RVZ51XGVErUyq/UWpu09FTUIW3Plpnp1+0ALtcNNvXpuWheOSTM7qWnFY3BeZVfTG3JNdwmjVX6mxd45M6npNBWqsH15mH02gtXUyjktOx0lO1M+wxNeKm2eZ8nmmY8mMIB7RzCDtJPAna88kwDLApYntDXRs3pFNogslQbtFlSZsr09m9I5OmfEzty1hUVlz/AIbMe0IaZ2A4nT19L47SynTBx5czKfkxC445ckuhcjtHJ0xm9J2CdNA7rLFfTgPSY2+UuOFx6dJJI8ssJ0j+2divTxxxGLoQPSYz8mVxwuQXpPHaenaLo1A7T0j75V9T8+AQgI/w5Hh8z2ccZQBhrDCQ1TtJCUzLCL2gIvI95arTiVAQiyxWpnkTmWErlBCLGheYSrxDAAEYeVf0hyMz2YBJMgtiCxgE/jEBFpG+LJgluZMharfmPSzmUkbtDD/rCAvB8yHbiV0fiSzjErTSzcwGPMAtILQIYPMfXxKgaPrccQNerbtLVbcd5n1vLKPxGUrJbiCzQQ3E8WBgnAmQYXeQR3geBHeNrEgLzHIkBHgSgxiiSqQ1SAQBCAhBIYWAwGJOIwLJCcwBeJG2P2SCsRk4gkR+yCVikKesr3adh2OJiCzy/I950jplSDOXvBq1T1mcvyI/Xp/46+bU8WYUK3rPLnaQuRk8xAsyhC8cSSTsAJ7ckzhl6xeoU7WJIK/MyTQHYHO0j/M0HO+3zE7QvENavGYbsDHrCIVKtdXtUADD8esR4yizKNyPee17bA/nB5mHeLbs+CzbfgSojyy5J8NDqvWq9HX7OR6Gcf1D6tp05Lai9ce2eTA6/wBF6zcu4ZSsDIyO8+edb+nOpKG1LIbB6gDtOqnH/bG97UrtY10Or/aBSpK6ap3HzwJmWfW2quYjwUVT/d2nJaTR36rULRUhLsfWdBR9FdYufbUlZGM5LYm31vP/APL5Jny3qfqTSOgJ1TJ8MDJs+q9KrKEv7n0B4mI30L1zeUWmtyPZ4n/2M6ytux6VU98luIuiv/KvDpK/qbSqS41Kn1xtmx0/6v6fqCFZ1Vx7nGZ8/v8ApLqtLhSiEkejTN1nStbpHC21HJ7FeRDoqvzL19xr73oOq4UWaW5ceozNjpnX67yy2DYR6z84dP6rr+m2barGx/8AptyDO40X1FYaK7b62qY+hEyvTHZxfJryR/19lIW1PEU8nkY9oqtg2RluD79pxfQvquu9NosDY/xN5eoC0A8Y9/mc9oxpF51b1SeKrgHdu8oM5/R0PTqnRh51b1nQ06kWoVfHHvMm1NutdwDsPfmTENN8tzRWeUNyeORjmaFAFhVyCAOOR3mLpHzhqxx2PzNFLi+cAhRFDTssamwKQNpI+ZWdlbIJ5k2kNYBk4PzF5G8rzmIi3sXaSAT6ERJsU5yePSSW5sDevaVWYNax47cSiky3n057SrU2LgP5sz112Kzkc+8XS4LZznIjZzLSsrLW1d8BYGq0psqYAZl2oAqD8TW6Loxq7wmOJcMOScrMqH05092ry68DtOiTSNjGJvaXpa1JtVcCXV0AOOJrHLFIePeJvOuaTQE+ks1dO4+7Okr0I9pYTRfEzt8mRXic5X0/txLNegGO06BdIOOI1dKPac9uaZbRxsFND8R6aEccTbXTgQ1pA9JjPJMrikQyU0QHpHLpBjtNIVgScASJsrrCiumHtGCge0skiQWxJ08goVD2ntghM0AtFoTtUT0AtPRaePzzPcRAs4nvEn08vLO4hIRKxskiyRIXlYAxyOOJmC2MW3HrCCa6WD8o0WjEykuxiGtxlG1Bdx3k+LzM0WwhbDQ0RbPG35md4s94phoXzdAN3HeU/EPrFtYYgtPd8wRdz3lKywxQuxEGqbuO88Lue8zWu4gpdzDQ21v4HMLx8jvMkXTwvj0NRrfmLN3zzKZuysUbDGGkt3zCW/nvM1bDiT4pzANqq6WFv57zEqtPvHC/HrDQ3EvyBGeLx3mNXf8AMcLuBHoagt+YzfMtLZYSyBtFGzLFbcTMrs+ZaSyBL6tGBpRW35jFt+YEuhoYaUhbx34hC2MauhpIYSoLZPiwC4G4niZUFknxIHqwWgE8xJsgmyTIPJnL/US+FrkcHAadB4kyPqOvxNFvHdJlyRtW/wAW/TkhmpYo7n8xAfUKqsOc57yilq4Xce8C+3cQcbecDmedaH0FZ2GgtiAluNvtmeNoJZtuQBn85n6fz2NnsPWHbYQpGR8xQtV1rNdaWLKBkcTU6RUtduAqknknEyqamttKtkHPrOk0ZSnajJjiaUKa6tWV13Ia7FDccZmBf0Wuy1wHVDjsyzW1lrqA1a9pX+1JefD1GQe+e06ePliPEr47dXE9Q+jk0fURqdPWvidyV+7GaC0aPUudRUQpHcczv9PUjK6gqytxwYi/6fovYWMSB6zpif6F/jfH5fN4yf8Ajjqeq6evqT7hihk7/wB2ZX1fUNK3UN4b+CU+8PedjX9M6fwCTRnn09Yq36U0oO1UAbbF5c//AKf8ffc//pwup1FWo1QNaMyKuDxzmZ+t6XZ1IqtdRSsHuRyZ9O0n0jQG5wR3mmmh0umYrtRNoznHeKbZ7V/4fxaTvmXynpH0PXWxvajLjszibmp+kar1Aauv8l4nYavVaQEeHzjvn1if3h4qkIAqj09ZjbkrDfaRXK1xya/QmgUCwfw7R2KjEq6/p13Tn8u56174WdmFJIYnhpX1NCPUWc5J+ZzWv2YTx/sOd6dqQ+CQQcd5fc7gHRQdvJ4lRtEtZzp/L34zGpaxp8x8475EyOP+pD+G/wDT65lrT3NYQGHA95nX2bsBDye4+Iyh2QkA7mPElbUtYZO3lsY/GV92QAGyR96QbCEwVyAPeJbB8wP/AKysCH1A3MCGz8RW7PJPESW5LHjOeINlnByPLGm04TcbGZ8kBM+sbofMxPr2i2I53ZyZY0gC4Pc5l4zjy3KCDtBne/Qmg8RXuK8dhmcBpRyOZ9o+jdItPRKcfebkyeS3WGHP/ri2ulHPEamnHtL2wYnsATmm8y4orCstA9oQpHtxHkwC0zmVYHYBIOBPFuYJMnTeJkZgkwWaLTiEs0Et3gseYJMSsSWgs0gmATEMEWgM0FjFkxTIM3T0STPRDH54E9iQDCE+rx5GhxJCyRCAiwagLGKs8sNRzDBqUWNVe08o4hgR4WoCmEFhgQgIYegC8T209owDiTjMWDStsgrHYkYhg1WdIhq+ZeYZHMU6c8RdRqmyGBg5l01wGrMOp6UpM9zGCsyRWYYQAxnskw/CMJazHgQpOJ4nmF4Z5hLWeIYHkJEZuOZArOIYrMMA625jgx4i0rPEeiGGGZUxllCeImtDHophg0+tpZVpWQRix4WrCvCDxI/OGBHhHBzDVzEjmEIYNPV4QbiKUQxDC0wNzJ3GABJiwaktI3cwLLUrHmYCZ2q6vp6QfMCYYetMNFarZZQ6OR5hOW1/1RXWD5wJzHUPratMhGLmVHHNi+yK+WvYfCvetj2PEVqLCGwpJ9c+kwOm9a/etrsRtdefxmq9+cAgZ9DPN5uKaW6y+g+Ny/ZSLQspey4QMcH3llT4pUK2ee8yltO5SMciaWh073urJgY74M58ddZ1saejbh85A53S9U62AHOD8xuhoCAF9mCOxXiFZQEbdXs2+m2XC4ItTf7frMbqGntUseRjsMd5suXUnnzH2lfUWVkbSTjuTCfKZhz/AO9m0pAZiGHoeIafVFobOQB2wYrqWnSx23jjv25mBqNDtwVckRRaY9HF7VdvpPrEIQrEExeq+sF3MeBPnttFwJK+kWdHqLmAYH8vSVN7f2X2edx3Fn1c5OA5VPTBlaz6ga1sbyZzuj6WpP8AEdvzm/odDRSw4H6yJmZ9yJtNjdN4uqJYBsk+k2NJpRSc2Eke3tBrZEQBeDPG0lw+T/8Ab2iwRC8zcDbkn8ZStXKnDDOfWO3mz/T2n1gupVSbE4+YlRDC1tDKdyMFU4xzlf8A0lLxShKsc++DN67Rm4kjBQDOd2f8TE1qKlmE5T55xCIRbwXqr9qcE5HI45MOi4kZY/IMpX2cYZlO37sJLmWsAgNHEI7L5t3cgkj8Ywsy15Ud5Rpbfla1Jzz+El7LOdxwe2BKVFhWPtYgnufX3iBYSGz6GDa7WYUjEBQwUEjAzCGdp09GwuTkk/Mu6AF3UAeWZ6DNwx90TV0LJvOwduBLgb4e671FemdNtv3YZR5fxnc/sZ+va+o9KXT6y0eOnByZ8V/asdXpLNHTcNldo3Bfecj0Tqmo6fcH01jVsPYzpn4n2ceT4l5PyPlbyfx9Q/eVWsquAKODGlp+U/p79qHUtFtXUHxUE+o/Tn7VtBrdqX2bH/unncvwuXj85sCnPSz6yWgk95k9O65pNcitVapz7GaO4MODxOOfHtvHkRMEmQxgExHEJJgkwS0gmBpJgk94JMgmIPE94BM8Wiy0UmljAJkMYJMQSTPQcz0A/PyrDVTLK0HA4jFp+J9djw9VFrhiuXRRxDFHxDBqkK/0jFTBlsUfENafiHUarBO3EIJxLXgn2hCk+0fUtVwkLbLS0/EMU8doYNU9kkJLfgn2kikw6jVXbB2fEu+Fj0nvB+IYeqJTiQa8y/4J9p7wfiLBrN8LntPeFNLwPie+zw6jszfB+OJPhcfE0hp4S6aGHrLFPaGKcek0xpfiF9mhg1l+F8QlpmkNMfaGNNDqNZvhZhCn4mkNN8Q103xxDBrPWvntzGrXLy6eMXT/ABHhaprXgdo1U+JaWiMFPxDBqqqcQwsseCcQhT8QwaQq9oYEeKe09sC94YNKCwgvxAu1VFIJZxMbX/Uul0+fMOI8LW+AB3i7dVRSCXcT5z1X634YVNzOU131RqryfOcSo45lPaIfXtZ9R6TTg4cEznOofWYG4VnifLbup3ufvnMp26h2PmYmaRw/2U8n9O56h9XsxPnJPxOd1v1HqLiRWSPnMwGYkwWJxLjjrCZtMrd+suuObLGMT3Mr5JMPdgd5eljT6PqvsmurbOFJwZ3lNisQeMdwZ8rezHY8zs/pjqQ1WlFTt/FrnnfO4+0doer/AI/l6z0l1gUMF2hQp9ZpdOYKwUfeB9OMzH0l6L5WPl95e01zVWA7wZ5eY9mtsl2emZXqwzlh89oyx+yKpJ9pj9O1judjBd+fL6TXpu7Dy+3HJ/WOHTWfBJSxmbybTjucyi1JFoyquTyMnkTXtbBCueT2weJKafw3+4GduMgdoTVfjGAOmanUuz4XaTx4mYFn049i/wAS9VX+xeZ1TvtwDt3ewMralsMpRh35HqRLjjj9REOYP0ymRuutYHt2jF+nwq5a1+OwwBN7e4XzBsFiB8TyuDWEKlj754j6wuKwwj9P1lCz2PjGPwhJ0O1GVvFF1HvjBE3arkyvBKnjIEKux1ZlK4rxkn2kzSBMMAdMat2Ad8A5x/tDr01qvttKDHxOgCpZWRX5T3AJibai6birYA5zM+peGVVSq7wu3dnI4jlqJXLL39JcGCirgr7c9om/k4GG/OE1TMqOsQFAq+c+4Ex9dSLxhSNyjOD6TW1ToVYNwSOx9DMjVWKqghgXX+n/ALycRZiarTCtyrE9/biVEUvcA3APAl/qNjPWAnBfAAM9TQlNY/iE2kZ344lYyiHh/DTCcnAyMwLGIYMwBee3ADBPmMqX3ZbG3JHP4wwTODvzkkGRXjks2D7QEUsPNwZZ2JtyTn2jiEDDhK8qe87b9mf0+3VNaNTcn/DVHP8AzGcT03S39U6lTpNMmbHOPwE/R/050uro3R6tNUACi+Y+5nX8bi7T2lx/M5/rr1j3L8yf+I+1T9Y6elMBa6ewnyipsHvO5/bjrhrP2ia7acrUAk+fq+DPRt7eLT1rWptK9pYS84yDzMyqzI5jlf8ASECYdb0H6u6n0ewGm5mUfykz619JftapuKVa47G9zPz8GyIQbHY8zn5vicXN7jy0pzX458S/aXS/qPRdQrVqrkJPsZqixW5VgRPxb0r6h6h0yxW02ocAemZ9G+mf2taih0r6gPL6tPJ5v8ZyU808w7afLrPi3h+jMwSZxvQvrvpnU0G29Nx+Z1FGqqvXdW4YH2M861bUnLQ6omLeljPeAWgkyCZGqeJgkyCe8EmI0sYBM8TFseYEImegZnojx8oWgRq6f4lta/iMCcT7R8+qLpx7Ri0fEtKkNViCoKB7SRRz2lzZC2YgFMU8QxSPaWgsMLGFQUj2hin4loKIYXmIKYoHtJ8EH0l0LzJCQCiaJ40/EvbOZ7ZAKPgfE94MvBBJ2CA1R8Ae0kUD2l3ZJ2QGqYp+IS0/EuBBJCQGqgp+IXg/HMuqsIJ8QPVHwe3EIU/Eu7JISBapimGtMt7RAstrr+8whgJFI9oYp+JU1HVtPSOWEydV9V6arPnEfWS10XhDiTtUdyJwWs+uKUzteY2r+vODtMfSR2fUntpT7zCVLuqaanOXE+Paz621FgIQmYmq+odZd3sIBlRxl3fZdf8AVOmpBw68TlOq/XAGRW0+Z3ay6wktYxlZrcyo44LtLqOo/VGq1BO1iAZh6jXXXHzuZRNv6xbWGXERCZmVgsT3PMHMr+JPbjmNOHmC3MXu4MgkgQ1QiQBFPZk4EGxvSLHf5iVBwPEB3kExbtJmVRCHb9Ze+nG1L9c09OkG6yw42+8yywnafsb0f2/680oxkV+aZ528SuLTT+UOm1FN2mcLehrs9VYRiXptCMx3T7Z+0/6RTXdDTW6OofaaVycD7wnwSxdtm05DfM8nm4uk493g545K7+tTS66ym3ZnI3d/Wdt0jXi5FAP+OTPmwfdkMPzl/pnUrdHYBnytMcdfHyecl9LfUDdsUhm7ydRqVWkCy4gn0Wc5T1L+EHBxb6Exmm6jVZYV1IXcxzkdhHrp2GmmpsUgIfzbiXBrV3qrbCfXAnPavUNVl1cFTwF+JQs19rOobKYG7vK7NK5Pt2V+orYMpfbngFZRV9rPUX7eY/MyNPd9oXeCqFRjvjd+Ebfegryt2xscgHvDsceGnp9QtePEKE/yiWftiMQbFRF7n3zOYfx/I4dFrbnMbXqamzXeSWXtu9fzi7SVsdMt/iqti8IvEUmqLuynBAPv6Tnl6lrBZiqsvWPT4j11DWllLmsk/d7An8ZMyz2GvqXrHK5QnufSZ/UNWNLtPz98GVl6gqBqmwD8zC6lrV58PbxJmdTM4t9U14bzsykDsAcTLbW4BZ2Xntn1mI1zNc3is2z0HvLmnpWt1ZyGYnhTziEVc832VyhM3eNd2IwBDvt3IVIAY+0rC4PlQwyOfaKsuDORnbjtHIicFdYRwSAuOTKzWA85De0VfcCSi8j3ikJzg9okzbZaNGAnnOcz1tgAwOBKotwpXcJe+m9Dd9Qdb0ugoB87eZvZfUyq1mZyCtaKxsvrX7Hvp0VaU9W1CfxLeKs+3vPo/VNQuk6dqLmOAiEyOm6WvRaOnT0riutQqicZ+2vrg6N9Da9w2LLE2L+JnscdIrEVh8/8jlm8zZ+QPqvqB6l9R9R1ZORZcxH4ZmQG5kMxbJPcnMhZUymIyMWan4+ZYVxKAbn4jUfmBL6txIe3bArYYg2+YH2jI6u4GQ9vPeUkYqxEdyTGD9Pr9RprA1NroR7Gdx9NftM6p0x0W6w21D3nAFMxT+SZcnFTkjLRq63mvqX6m+lP2o9P6psrucV2HjDT6HptXTqUD0uGHwZ+GtNqnrcNWxVh6ifQvpD9o/UOkMldztbSPczyfkf4v94v/wAOzi+X+XfqgmCTzOF+mv2h9M6rWga1UsI7EzsKNZTqF3VWKwPsZ49+O3HOWh3VtFo2JPY8QSZ4mCxmZvEz0AmegbhFEYBIUQx8T7V888ohgSBCHMAkCSBPCEO8Agf4hSPWF7wCRDEEekIQCQIYgQhAamEBIEIDmBoxPYhY5kiCf0BEnHEIieAgP14CEBPDt8QXuSsEswiMwCFwO5mPreuafTqfOMzlOrfWldYIVx+seFMu+s1VNQ8zCZms6/p6AfMJ8i6n9a3WEitjOc1fXNXqGObCPjMuKJmz691L6zpqB2uJyXVPrd3yK2JPxPntl1lhy7EwS/6y4pEFMt3W/Uer1BOHIEy7tbdZy1jfrKe+CXlYRxsJPJzPGyV2fviCzxhYL8QN/v2iC8AvAHtZ8xficxRbtBLcxDDi2RBLRZaeDQODN3MMNE5hDEBh26CW4gZkEwEQhviQJ4mDnESoE7YEQ7Qnbj5iGMm0qh4tjJn1n/w1ab7R9V33EfcAE+Ru2EM+2/8AhZ2/vfWE98iTX2d/T9XWVrZQa3GVZcEGfnT9q30o/RuqPqqEP2O45BA+6Z+jSeBMn6h6Xp+sdPt0uqQMjj19JhekXjJdHDyzxW1+RRaQdrAkR7OGUbTyPSbv1v8ASmq+n9e6sC1BPkcDuJzK2EfiJ51qzWcl69LxaNhb0+ueoqucH5M0F1pcsq483LGc7d5wT/NENdaFAycfjM8bxyY6m7WuzIjWfwh7CEdXQ5w7YVexJ7Tl69dhhk4PxIfqWzcuQfkiOGleV0r9RFVflBKKeIr7UblLqzYM5hdexU5ft6CXNP1P+C2W7+g9Y8hp9uup0nUX2+ExGz+6WU1NCgWmksR654nDWa9m1BtViuPSefqLZ27yT8niThW5Yx3w6kOVVgT+My7+qHxQEfgH9Jyh6lZjG7AHfEE9RbvWCGPc5imrGeV0ep6gMli7M57SqLGucuxwPQTGTVNdZk8tLaXFQGZvN8QiMTN9a1KrSzNhWtbt6jEG24K+e35TLfWMAdrKgERZrG2MxO4ntxKTMr7anzlVJx+ES9+5vMcY7SgtjDnPp6QfEPPcmLCmy21jM3lOPmWKmGCXb9JSrcBR6mRZc20BcZ7BRDBE/qzbblwtQJZuBPv37IPpM9F6WddrE/47UjPPdF9pyn7J/oJmsr6x1urH81FLf/yM+3VDAE7vj8PX+UvO+X8jt/CpynAn5t/8UXX99uj6VU/rvcT9D9T1S6LQ23OQAikz8O/tJ643Xvq7W6otuRWKr+AnZHiNedPm0Q5d++JIg+vpJUyWgs8j2hrzA9YS94ylZrJA4jc5ERW3p6Q88SklupDn2ho20jMVc5BBMlWBAga1uHpzF3YI+Yokj14g785BMCDjB7xi2YGIh3wYIbmI8aWn1VlThq7GVvcGdd0H686t0t1/jtZWPQmcKhwPmPVuJF+OvJGWjTi018w/RX0p+1XSa3bXrj4b/M+kaDqem19QfT2qwPsZ+MVfHIM6T6d+sOpdFtU03M1Q/lJnlfI/xVZ/lxT/APDs4vmTHi79aZnp8s+m/wBqWi1el/4xhXao5zPTybfF5qzk1l2RzUmN10Cw8QVhCfWa8MQHEkdp7vJHpAkyZEIRm8JInoQH6RE8JIkAQsRAQ7wgJAhCMJEIDiQIQ7QNOJ4cCI1Opr06EuZy3V/qyjTFhvH6xxGlM47Hj8oi/U1UglmE+bt9e04IWwZ/Gc71v61e3K1MTHFZGvpXV/qajTKQHE4PrX1uSWFbzgdb1XUapsu5wfaUS2T8y4qWtzX9f1WqY+cgH5mTZdZYSXYkxQMEtzLhMmbuZBPMUW+ZBfkyiN34/GQWiHfnvAZ4A8vALRJeRviOINZ4JeLZoJbkwB2/iCzRRaCWi1RhaCWgEyB2gDQfmSDFrCB/SM8MzJDdswCZ4nIMRYYW4EHPMHJxPevEYwZJxBzPZ4gEyZN5+TEt3hE94pmkSdUXfczPsH/hi1Qr+otTWTwwE+Oalia59A/YDrfsv1kgJwH4k1n+WKvH8dfuBWyiwH7Reks30IfiMPMQYf1F0jS9X0Vmn1dYZWHB9RPz79a/R9/Q9SzhWfSsfKwHb8Z+l7VzMbrHT6ddp3q1FYdGHYzPk44vDfh5p45fkq5WqYhs7TEuu5TtJn0z63+jbOmu92lQ2aU9wP5Z841enaliV5ScF+Oa+JepTki8bCjZkZ3KD/iVbNo7hsS61wOQ4/WV3CjP8uZC4UmYZXDAYkNYUcMriPdVJz6RLJx2grQeJubJbn2kmzJwuQskJ2yBPNtz35gmReKPYsZKuW7nA9hFf9PmSGAPvFJavUPsyR3hNqCy+UnEqB++cgSS54wML7RYcSsWWsnJIMFH3nnJi1VrDg94TOEGKxk9swwaMt5hzGjJwWPMRWp3Zzkn0nTfT/0l1Dq1iMymjTHu7ev4SorM+kzaK+2NotNqdfeun0tTW2Meyifaf2ffs4o0TVa7rAF2pHK1fyqf+81/o36X0fSal+z1Df8AzWN94zu9NXtUcTs4uGI8y4eb5E28V9LWnQKAAOBLYOAJXTgCK6jrE0mle2wgKozOrHFac8vnP7d/qlejfTF1NT4vuG1eZ+QWYtlmOWY5M779sn1S/wBQ/UttddmdPQdo54zPnzR2/ouON/lP68JMhYYkrSIxT+sWIS9/iOCk4HtCHrFZwZIbkytIvUHtzIRuJ6/0zBHxEf4NninJAzJPMCzIGIpOISPMM5hI20xKtiQW5i3Dxc8UfnDWwN68SgrRitCLaU1aA/xJDcfEpCwjsYa3YIzK1OLitj1npXWxTPQD9ZL2hjtFqYwSEJkjtPCSO0An09oXrIEKM0ycSIY7RE8BzJx2nh2hDtAnhCAnsZnhA0jtF6rULp6izGN7DmcR9ddZGmodVYdo48hz/wBafVXhb1R+Z8p6j1S/WXEvYce2ZHWeoNqb3sZuPSY9TlnmsePBZ+tOtuM5hk8xCtgfEndK0Gbp4NFbsT2+MsP3wS8SX4gl4DDS3eAWit0gt3gMEzSN0AmRmGjBFuZAaBmQTiLQYWg7oGeZOYtAsyAYJPM8D+sNMUlYPrDBjgkj/MnMjmEvbmMxD1ns4nvznjAPCe9J6RmGhJPaAZ45xBJimRAXPeJPJxCZvmeVeczOVwr3g7fidN+yy86b6q01meNwnOao9hN36BUr1epx3DCRHi8Kt/pL93dCu8XQVN6FRNPM5f6LvNnSNPznyidMO0q0ZLOs7GoMr3JnMs/9Iu3tEthdR0iXVstihlPoZ8b+u/o46Zn1OhTdUTll9p90vTIMx9fpVsrZXAKnuJF6ReMa8XJNJ2H5O6jpXpdlYcTOdgVx6z7F9f8A0fZV4mp0abqu5X2nyDWV7GYFSMe88/kpNJx63HeLxsKz/d+YhrSB3ksfY8StcwAOJk1wNuoLOMGFW3ByZXqrL2ZI4loV7QMw0oGpyOTGrjHaLrB44jdyjJOMCAmBIBu55lmmvc2Pj9IikNYwWoZPuZtaDpWp1bCnSVlm/mb0lxGomcZVrtkog49fmbfQPpfW9RZH8M10/wBTTsug/R9GlKW6r+Nb3x/KJ2ul0oACquB7ATWvFvtz354jxVz/AEP6S0GhKu1fjXD+Zxx+k7npmg3kErhRD6f08sQWHE6HTUBFAxxOqnHjivyTYWkpFYAAmig4iEGMR6nE1Y6MttHM+P8A7cvrAdK6Nbp6LMXWeUYn0n6g6kmh0VljNjAn46/aj9QP1z6isAbNVRwOZcfxjszn+durki7WMzsSWY5JMie9MCRM24xPZkCFKS8DDHeCveEMcxh7PeSDIPeCTxAsTZ2igeYbcgxcRwIHn5kPz+MjMkniBkHuZEJuIBmc+1CEkHvA9YYiiTGrfpJDfhAkj5lxKcMBnoInpRY/XSmMU/rKiPkRyPEyWFMMGVw0YrQB4xmTFK0MGBGCEsWDDUxAwQh25i1MPPECEJMEGFmI1fqF40+ldyecT4J+0Dq51GrapW/GfVvrvqQ0uicbscT879T1R1OrtsY5BM0oJUNa5wYvSD1i9VZkw9M+FlRPlUx/FdzgfEEvFGyRmWzOLfpPBovdPboaBlpGYBbvPZhoETBzIzPZ/SGhOZG6QTIPeIxZ4kGRmezEePSDPepnoDHpMiSIEkSfX4kD/EMenpGAMxU/EMNuEC3lYup+cQ3JGLI7wsxQMYDHoEJ7HEg4zBLYhoEeImxoLP6DvBUE95MzqoeVc8mGJAMnMRq2qPmnUfQNedah+ZympPnnb/s8rzqFOPWRX/ZVv9X60/Z/YT0qpfYTtFPE4T6BbGiQfE7lfSXyf7MqejIDiFBaQuFewd5SurzLzgcxFi94HDE12lWxGVhkH0nx36/+gi72arpq892rn3K6sYPvMbqoqpod7iFUDJJmfJSLxktuLltxzsPyPr9DqtNYyW0OpH9sx70YtjGCJ9K+vPrTpg6m2n0KeIFOHsA4nIajqPQbvNYrhz3nn2pETmvWryTMbMM2pQqDmHkEd+Iu/qnSKyBXVe+PTM7n6H0XSOuaXfQB4o+9W3dYo45lM89Y8OPrVjwi8S5o+k6vW2BaqGYfhPr2k+mNLWAVoQH/AJZr6fpa1gBVAHwJpHDP6zt8mPxwnQPo814fW4z/AELO40PT66ECVVhF+BNXT9PYgeWaml6fjuOZvTjxycnNNmZptGW9OJt6LQKhBI5lyjShQOJeqqA9JvFYhhNtRVSFA4llFkqsYo4lpl4T1lgrrJbgCQSFnN/VPVl0elc7hkCOsbLO1usPnX7afqsaPp1tVb+ZuBzPzLY5tdnflmOTOs/aV11+rdadN2a6z/mcgTFyW2chXFXI2f1K98QxFCNBkw1kQnpAk+kpKZIMH854HmMkkyM8T0g9vmASe0UeIZgN3EUnCMyc8SPWeiOQsYEJoJmdlPSZGZ6ICkwZOZUSQwZ6QDPSxj9WJZGrZzM5bI1bO0IYNJLIxXmetsatkA0FfiMVpRSztHLZxAlsNDVpWV4atALQMIN2lYN2jA3EAcDJLYUmKDdovV2bNPYc+kMD5L+1rqRVWrU8scT5Da87L9pmrNvU9ueATOGsbgy49KiNVb2y0bQ3llaz70dQeJnWf5NbR4Wg0ZniIBhBprrLDcyc94vdxJzHqZgWczxMEniCTzADniYG6ez+MBg8z2eIvM8Whp4LPeeBgA5/GTkw0xjvJ9YGZOYEKT7wAYQMCkY7Tx7SMyCYEhjKzZV8jtLLcxVq5EUqrJ1TZGYTPKlbEcRwye5homo2txxALFpDYBwO/vIHAhp4NRg/Mk8QMmSD3gBek96d5GYLNwYpEK1xzZxPo/7OKf4lZnzVjmwT6z+zWvmqTx+bLv4q/SH0ONtCD4ncjsJxP0gMVpO1XsJfJ7Y09CzIJnoJMhQGi2HJ94ZaZ/WOpafpmjs1GrsVK0GSSYlR5L6rrNP0/SPfqbFrrQZJJn5t/ad+0S/rtluh6RZ4WhB2tZ23/hPftI+uNT9UauzT6aw1dNQ4x28T/wBJw1ldSqtQAB/DicXNz/8Atq+q/wAZ/hvEc3P/APEf/wBY99QG0DaPXB5zM+2tWsIAHHxzNnVUkOSSc+gPr+EzzSWU5DA+x7zlel8jiifUM3wuSTjEvdB6hqeia6vWaRiGU8qDwwkOiVrhzkn1MPwwqgKrY+BKi0w86fixb2/S30H1rTfU3TK76WAsxh09VM7Sjp6jBxzPyt9J9d1n0z1WrV6RWNJI8VM8ET9UfSfW9J1/pdWr0dgYMOR6gzt4bxeP+vF+b8W3x7f8XqtMo9JZSnHpHBcQwO06HBMlrWIxVxCHpPf9Yy14zxOBBZpXvuFaEk8QKZK6lqlpqY55nxL9qX1J9n0d2H5xO8+qerCupzuwBPzR+0brB13UvBVsqvLfjNJ/hXWUR3s5K21rbWsc+ZzkwPWR6T0wh1J/KSpwYMISgZn9J6Ap5xC9Y0iHpPT3/SeMCRPeokT0DTn8oNmIXEg4/OHsAzIJ4kHgyCZMzikGDmeJkGZTJvCTInotMWZMGelaQgZ6eno9D9MLZDWzmVR3ja5US58Wksj0s47ymvaNX0jiSXUtj0slFZYrjC2lkctkqJGr3EIC2r8Q1fiVljF9YBYDdpQ67f4XT3PriWpkfVH/AJa/4QD88/V+q+0dYuOeFOJzztmaXXv/ADLUf88ymj/GtYJc8xlRinjKfWZV/wBmk+lkHMmAvaF7TdkPMnME+k8IEnM9niQZB7QLEg8TxMiQYCISTPAwRPCChZk5/KD7zwgQiZIgmEPSBJBhAwJPtHpYPMjM96SDAknvIkGeMNCGIHaeBwMwWnj92JaM5aHmKHcxnpA5TJEH2kwLE5gs3lMkxb9jEcErzaPxn2L9m6/6XE+O1/6o/GfZv2cdqvyi4v8AYuX0/RP0oMVJOzT7gnG/Sv8ApJOxX7gmnJ7ZU9PGLbiMMW/3pmtT6lradDpXvvcIqjJJn5W/az+0a7r3VH0WkcroK2wf7zPvP7Wv/hbV/wDLPxx1H/Vb8Zz/ACLTFcej/jqx9nafxo0Xu3lD43ej9ppVONpBJQY/m+6ZgaP/AEzNPU/+WflODH2fBzT12Srsop8JNxbuN3/eVrFNla534H9P8v4mN13/AJdo/wD9yK1P+sYT4ZWt3tMf/YO5FYVkgN7AZ3QgW8RV8Jiv8pJ/xAr/APea5e1vp/zGKPSM85P9kJv8TBRPgkzrf2cfVuq+lerBnsVtBYf4iA5x8zitJ/8AN/5poab/AEh/zSq2ms7DK/HX5HH1tHvX7N6P1DT9U0FWq0rq9Vi5BEtMMH4nzv8AYf8A/CVP4mfR7OwnqxOxr4zkr1tNf6LJglpJ7iA0aNBY+ASZg9Z1wVCAZs6j7pnHde+480pGyz5J8Pm37QOtijTXNu4UT4HqLmvvstc5ZzmfTv2nf+52/wDNPlnoJHNOy04a5GvSZAnjMm6ZOYK95PrGHj/mErfrBbuJHtDSOzIJ9JHtPCUSexnj/mQPWeb1jJOeBPZg+88IGF+8Aw7OwijMryqEmRPGekG9PSPaTAPCTmRPQCcz08J6UH//2Q=="

        '''
        str_image = "UXQgaXMgZ3JlYXQh"

        print(type(str_image))

        bytearray = QByteArray.fromBase64(str_image)
        bytearray = qUncompress(bytearray)
        image = QImage.fromData(bytearray, 'PNG')
        '''
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(base64.b64decode(str_image))

        #pixmap = QPixmap('C:/Users/cianet45/Pictures/imagenesTab/tres.jpg')
        #pixmap.scaledToWidth(400)
        #pixmap.scaledToHeight(400)


        self.listZoom = {1:1, 2:1.5, 3:2, 4:2.5}


        size = QSize(453, 255)




        smaller_pixmap = pixmap.scaled(self.listZoom[self.scaleFactor] * size, Qt.KeepAspectRatio, Qt.FastTransformation)

        self.lbImage.setPixmap(smaller_pixmap)

        #self.lbImage.resize(100, 100)
        #self.lbImage.setScaledContents(True)

        self.lbImage.setScaledContents(True)
        self.lbImage.show()


        # muestra siempre la primer tab
        self.tabwCedula.setCurrentIndex(0)

        # -- carga informacion de construcciones de PREDIO
        dataConstP = self.consumeWSConstr(self.cveCatastral)

        self.cargaConstrPred(dataConstP)

        self.cargada = True

        self.tabwCedula.blockSignals(True)
        self.tabwCedula.currentChanged.connect(self.event_cambioPestania)
        self.tabwCedula.blockSignals(False)

    # --- M E T O D O S ---

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

    # - carga la informacion de las construcciones
    def cargaConstrPred(self, dataConstP):
        
        try:
            if len(dataConstP) == 0:
                self.createAlert('Sin Resultados', titulo = 'cargaConstrPred', icono = QMessageBox().Warning)
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

        # autoguardado
        self.constrTemp()
        
        volumen = ''

        # se obtienen todos los volumenes de predios
        # en forma de una cadena (v1v2v3v4)
        count = self.cmbVolumenP.count()
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
            self.muestraComparativoFiscal()

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

    # 
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

    def event_spinBox(self, cadena):

        col = self.twIndivisos.currentColumn()
        row = self.twIndivisos.currentRow()

        # print(row, col, cadena)

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

    def event_zoomOutIma(self):
        
        print('--------------------------------------------------')
        print(self.scaleFactor)
        self.scaleFactor -= 1
        pixmap = self.lbImage.pixmap()

        print(self.listZoom[self.scaleFactor])

        size = self.lbImage.pixmap().size()
        size = QSize(453, 255)

        print(size)

        smaller_pixmap = pixmap.scaled(self.listZoom[self.scaleFactor] * size, Qt.KeepAspectRatio, Qt.FastTransformation)
        print(self.listZoom[self.scaleFactor] * size)

        self.lbImage.setPixmap(smaller_pixmap)

        #self.lbImage.resize(1000, 400)
        self.lbImage.setScaledContents(True)


        self.lbImage.show()

        self.btnZoomIn.setEnabled(self.listZoom[self.scaleFactor] < 2.5)
        self.btnZoomOut.setEnabled(self.listZoom[self.scaleFactor] > 1.0)
        

    def event_zoomInIma(self):

        print('--------------------------------------------------')
        print(self.scaleFactor)
        self.scaleFactor += 1 
                
        pixmap = self.lbImage.pixmap()

        print(self.listZoom[self.scaleFactor])

        size = self.lbImage.pixmap().size()
        size = QSize(453, 255)

        print(size)

        smaller_pixmap = pixmap.scaled(self.listZoom[self.scaleFactor] * size, Qt.KeepAspectRatio, Qt.FastTransformation)
        print(self.listZoom[self.scaleFactor] * size)

        self.lbImage.setPixmap(smaller_pixmap)

        #self.lbImage.resize(round(self.scaleFactor, 3) * size)

        #self.lbImage.resize(1000, 400)
        self.lbImage.setScaledContents(True)


        self.lbImage.show()

        #valueH = self.saImagenes.horizontalScrollBar().value()
        #valueV = self.saImagenes.verticalScrollBar().value()

        #print(valueH)
        #print(valueV)
        #print(int(1.1 * valueH + ((1.1 - 1) * self.saImagenes.horizontalScrollBar().pageStep()/2)))
        #print(int(1.1 * valueV + ((1.1 - 1) * self.saImagenes.verticalScrollBar().pageStep()/2)))

        #self.saImagenes.horizontalScrollBar().setValue(int(1.1 * valueH + ((1.1 - 1) * self.saImagenes.horizontalScrollBar().pageStep()/2)))
        #self.saImagenes.horizontalScrollBar().setValue(500)
        #self.saImagenes.verticalScrollBar().setValue(int(1.1 * valueV + ((1.1 - 1) * self.saImagenes.verticalScrollBar().pageStep()/2)))
        #self.saImagenes.verticalScrollBar().setValue(500)


        self.btnZoomIn.setEnabled(self.listZoom[self.scaleFactor] < 2.5)
        self.btnZoomOut.setEnabled(self.listZoom[self.scaleFactor] > 1.0)


    # --- CERRAR E V E N T O S   Widget ---

    # --- U T I L I D A D E S ---

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

