# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TopologiaQG3_dockwidget_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TopologiaQG3DockWidgetBase(object):
    def setupUi(self, TopologiaQG3DockWidgetBase):
        TopologiaQG3DockWidgetBase.setObjectName("TopologiaQG3DockWidgetBase")
        TopologiaQG3DockWidgetBase.resize(427, 445)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName("gridLayout")
        self.labelErrores = QtWidgets.QLabel(self.dockWidgetContents)
        self.labelErrores.setObjectName("labelErrores")
        self.gridLayout.addWidget(self.labelErrores, 2, 0, 1, 1)
        self.tablaReglas = QtWidgets.QTableWidget(self.dockWidgetContents)
        self.tablaReglas.setObjectName("tablaReglas")
        self.tablaReglas.setColumnCount(1)
        self.tablaReglas.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tablaReglas.setHorizontalHeaderItem(0, item)
        self.gridLayout.addWidget(self.tablaReglas, 1, 0, 1, 1)
        self.tablaErrores = QtWidgets.QTableWidget(self.dockWidgetContents)
        self.tablaErrores.setObjectName("tablaErrores")
        self.tablaErrores.setColumnCount(1)
        self.tablaErrores.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tablaErrores.setHorizontalHeaderItem(0, item)
        self.gridLayout.addWidget(self.tablaErrores, 3, 0, 1, 1)
        self.labelReglas = QtWidgets.QLabel(self.dockWidgetContents)
        self.labelReglas.setObjectName("labelReglas")
        self.gridLayout.addWidget(self.labelReglas, 0, 0, 1, 1)
        self.botonValidar = QtWidgets.QPushButton(self.dockWidgetContents)
        self.botonValidar.setObjectName("botonValidar")
        self.gridLayout.addWidget(self.botonValidar, 4, 0, 1, 1)
        TopologiaQG3DockWidgetBase.setWidget(self.dockWidgetContents)

        self.retranslateUi(TopologiaQG3DockWidgetBase)
        QtCore.QMetaObject.connectSlotsByName(TopologiaQG3DockWidgetBase)

    def retranslateUi(self, TopologiaQG3DockWidgetBase):
        _translate = QtCore.QCoreApplication.translate
        TopologiaQG3DockWidgetBase.setWindowTitle(_translate("TopologiaQG3DockWidgetBase", "TopologiaQG3"))
        self.labelErrores.setText(_translate("TopologiaQG3DockWidgetBase", "<html><head/><body><p align=\"center\">ERRORES DE TOPOLOGIA DETECTADOS</p></body></html>"))
        item = self.tablaReglas.horizontalHeaderItem(0)
        item.setText(_translate("TopologiaQG3DockWidgetBase", "Regla"))
        item = self.tablaErrores.horizontalHeaderItem(0)
        item.setText(_translate("TopologiaQG3DockWidgetBase", "Error"))
        self.labelReglas.setText(_translate("TopologiaQG3DockWidgetBase", "<html><head/><body><p align=\"center\">REGLAS DE TOPOLOGIA</p></body></html>"))
        self.botonValidar.setText(_translate("TopologiaQG3DockWidgetBase", "Validar Topologia"))

