from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, QSize
from PyQt5.QtGui import QIcon, QColor, QCursor, QPixmap
from PyQt5.QtWidgets import QAction, QWidget,QVBoxLayout, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QTextEdit, QLineEdit
from PyQt5 import QtWidgets
from PyQt5 import QtCore

from qgis.core import *
from qgis.utils import iface, loadPlugin, startPlugin, reloadPlugin
from qgis.gui import QgsLayerTreeView, QgsMapToolEmitPoint, QgsMapTool, QgsRubberBand, QgsVertexMarker

import os.path
import os, json, requests, sys
from osgeo import ogr, osr


class VentanaAreas(QWidget): 

    def __init__(self, pluginDFS): 
        QWidget.__init__(self)
 
        self.contenedor = QVBoxLayout()
        self.setLayout(self.contenedor)
        self.tablaAreas = QTableWidget()
        self.tablaAreas.setColumnCount(1)
        self.pluginDFS = pluginDFS
        self.contenedor.addWidget(self.tablaAreas)
        
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

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

#----------------------------------------------------------------

    def mostrarAreas(self):
        self.limpiarTabla()

        rango = len(self.pluginDFS.geomsAreas) -1

        for x in range(0, rango):

            self.tablaAreas.insertRow(x)
            area = "%.2f" % self.pluginDFS.geomsAreas[x].area()

            string = str(area) + ' m2'
            item = QtWidgets.QTableWidgetItem(string)
            self.tablaAreas.setItem(x, 0 , item)#self.capaActual.getFeatures().attributes()[x])
            item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            color = self.pluginDFS.listaColores[x]
            self.tablaAreas.item(x, 0).setBackground(color)

        header = self.tablaAreas.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.tablaAreas.setHorizontalHeaderItem(0, QTableWidgetItem('Area (Metros cuadrados)'))
        self.show()

#--------------------------------------------------------

    def limpiarTabla(self):
        self.tablaAreas.clearContents()
        self.tablaAreas.setRowCount(0)

        for row in range(0, self.tablaAreas.rowCount()):        
            self.tablaAreas.removeRow(row) 

#---------------------------------------------------

    def closeEvent(self, evnt):
        self.pluginDFS.quitarAreas()

       
#########################################################################
