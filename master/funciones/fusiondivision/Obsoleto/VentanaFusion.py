
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, QSize
from PyQt5.QtGui import QIcon, QColor, QCursor, QPixmap, QStandardItemModel
from PyQt5.QtWidgets import QAction, QWidget,QVBoxLayout, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem
from PyQt5 import QtWidgets
from PyQt5 import QtCore

# Initialize Qt resources from file resources.py
from qgis.core import *
from qgis.utils import iface, loadPlugin, startPlugin, reloadPlugin
from qgis.gui import QgsLayerTreeView, QgsMapToolEmitPoint, QgsMapTool, QgsRubberBand, QgsVertexMarker

# Import the code for the DockWidget
import os.path
import os, json, requests, sys
from osgeo import ogr, osr


class VentanaFusion(QWidget): 

    def __init__(self, pluginFD): 
        QWidget.__init__(self)
 
        self.contenedor = QVBoxLayout()
        self.setLayout(self.contenedor)
        self.tabComp = QTableWidget()
        self.tabComp.setColumnCount(9)
        self.btnConfirmar = QPushButton()
        self.btnCancelar = QPushButton()
        self.btnConfirmar.setText('Confirmar fusion')
        self.btnCancelar.setText('Cancelar')
        self.pluginFD = pluginFD
        self.contenedor.addWidget(self.tabComp)
        self.contenedor.addWidget(self.btnConfirmar)
        self.contenedor.addWidget(self.btnCancelar)

        self.btnConfirmar.clicked.connect(self.confirmarFusion)
        self.btnCancelar.clicked.connect(self.cancelarFusion)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        header = self.tabComp.horizontalHeader()
        self.predios = [None, None]

        self.resize(700,220)
        self.setMinimumSize(QSize(700, 220))
        self.setMaximumSize(QSize(701, 221))


        self.listaCampos = ['cve_cat', 'clave', 'cve_cat_ant', 'cve_tipo_pred', 'num_ext', 'fondo', 'frente', 'sup_terr', 'uso_predio']
        self.listaEtiquetas = ['Clave Catastral', 'Clave', 'Cve. Cat. Anterior', 'Clave Tipo Predio', 'Numero Exterior', 'Fondo', 'Frente', 'Superficie de terreno', 'Uso de predio']

        for x in range(0, len(self.listaEtiquetas)):
            header.setSectionResizeMode(x, QtWidgets.QHeaderView.ResizeToContents)
            self.tabComp.setHorizontalHeaderItem(x, QTableWidgetItem(self.listaEtiquetas[x]))

        estilo = """
QWidget{
background : rgb(250,238,224)
}
QPushButton{
background : rgb(174, 116, 0);
color : rgb(255, 255, 255);
border-radius : 4px;
}
QPushButton::hover{
background : rgb(104, 69, 13);
color : rgb(255, 255, 255);
border-radius : 2px;
}
QTableWidget{
background : rgb(255,255,255);
}
"""

        self.setStyleSheet(estilo)

#--------------------------------------------------------

    def cancelarFusion(self):
        self.close()
        self.pluginFD.dlg.btnCargarPredio.setEnabled(True)

#------------------------------------------------------

    def closeEvent(self, evnt):
        self.pluginFD.dlg.btnCargarPredio.setEnabled(True)

#----------------------------------------------------------------------

    def confirmarFusion(self):
        numQueda = sorted(set(index.row() for index in self.tabComp.selectedIndexes()))

        if numQueda == None:
            self.pluginFD.UTI.mostrarAlerta('Debes seleccionar un reglon de la tabla', QMessageBox().Critical, 'Error de seleccion')
            return

        if len(numQueda) != 1:
            self.pluginFD.UTI.mostrarAlerta('Debes seleccionar solo un reglon de la tabla', QMessageBox().Critical, 'Error de seleccion')
            return

        numQueda = numQueda[0]
        self.pluginFD.fusionarPredios(numQueda)
        self.close()
#--------------------------------------------------------------------------

    def llenarTablaComp(self, predio1, predio2):
        self.vaciarTabla()
        self.tabComp.insertRow(0)
        self.tabComp.insertRow(1)
        self.predios[0] = predio1
        self.predios[1] = predio2

        for x in range(0, len(self.listaCampos)):

            item1 = QtWidgets.QTableWidgetItem(str(predio1[self.listaCampos[x]]))
            item2 = QtWidgets.QTableWidgetItem(str(predio2[self.listaCampos[x]]))

            self.tabComp.setItem(0, x , item1)
            self.tabComp.setItem(1, x , item2)

            item1.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            item2.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )


#------------------------------------------------------
    def vaciarTabla(self): #Vaciar tabla

        self.tabComp.clearContents()
        self.tabComp.setRowCount(0)

        for row in range(0, self.tabComp.rowCount()):        
            self.tabComp.removeRow(row) 