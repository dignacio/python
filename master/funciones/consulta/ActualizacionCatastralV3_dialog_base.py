# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ActualizacionCatastralV3_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ActualizacionCatastralV3DialogBase(object):
    def setupUi(self, ActualizacionCatastralV3DialogBase):
        ActualizacionCatastralV3DialogBase.setObjectName("ActualizacionCatastralV3DialogBase")
        ActualizacionCatastralV3DialogBase.resize(537, 612)
        ActualizacionCatastralV3DialogBase.setStyleSheet("background : rgb(250,238,224);")
        self.tabWidget = QtWidgets.QTabWidget(ActualizacionCatastralV3DialogBase)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 521, 591))
        self.tabWidget.setStyleSheet("\n"
"    background : rgb(255,255,255)\n"
"")
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(20, 10, 361, 21))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.comboLocalidad = QtWidgets.QComboBox(self.tab)
        self.comboLocalidad.setGeometry(QtCore.QRect(20, 60, 121, 22))
        self.comboLocalidad.setStyleSheet("QComboBox QAbstractItemView::item { min-height: 25; font-family: \"Century Gothic\";}\n"
"QListView{color: black ; font-size: 16px; outline:none; font-weight:bold; font-family: \"Century Gothic\";}\n"
"QListView::item:selected { color: white; background-color:  rgb(250,238,224); font-family: \"Century Gothic\";}\n"
"QComboBox{\n"
"background : rgb(250,238,224);\n"
"}")
        self.comboLocalidad.setObjectName("comboLocalidad")
        self.comboSector = QtWidgets.QComboBox(self.tab)
        self.comboSector.setGeometry(QtCore.QRect(190, 60, 131, 22))
        self.comboSector.setStyleSheet("QComboBox QAbstractItemView::item { min-height: 25; font-family: \"Century Gothic\";}\n"
"QListView{color: black ; font-size: 16px; outline:none; font-weight:bold; font-family: \"Century Gothic\";}\n"
"QListView::item:selected { color: white; background-color:  rgb(250,238,224); font-family: \"Century Gothic\";}\n"
"QComboBox{\n"
"background : rgb(250,238,224);\n"
"}")
        self.comboSector.setObjectName("comboSector")
        self.comboManzana = QtWidgets.QComboBox(self.tab)
        self.comboManzana.setGeometry(QtCore.QRect(370, 60, 121, 22))
        self.comboManzana.setStyleSheet("QComboBox QAbstractItemView::item { min-height: 25; font-family: \"Century Gothic\";}\n"
"QListView{color: black ; font-size: 16px; outline:none; font-weight:bold; font-family: \"Century Gothic\";}\n"
"QListView::item:selected { color: white; background-color:  rgb(250,238,224); font-family: \"Century Gothic\";}\n"
"QComboBox{\n"
"background : rgb(250,238,224);\n"
"}")
        self.comboManzana.setObjectName("comboManzana")
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(20, 40, 121, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setGeometry(QtCore.QRect(193, 40, 131, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.tab)
        self.label_4.setGeometry(QtCore.QRect(370, 40, 121, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.botonCargar = QtWidgets.QPushButton(self.tab)
        self.botonCargar.setGeometry(QtCore.QRect(200, 100, 111, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.botonCargar.setFont(font)
        self.botonCargar.setStyleSheet("background : rgb(174, 116, 0);\n"
"color : rgb(255, 255, 255);\n"
"border-radius : 4px;")
        self.botonCargar.setObjectName("botonCargar")
        self.label_5 = QtWidgets.QLabel(self.tab)
        self.label_5.setGeometry(QtCore.QRect(20, 380, 151, 16))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.widget = QtWidgets.QWidget(self.tab)
        self.widget.setGeometry(QtCore.QRect(10, 160, 241, 201))
        self.widget.setStyleSheet("QWidget{\n"
"background : rgb(250,238,224);\n"
"}")
        self.widget.setObjectName("widget")
        self.label_6 = QtWidgets.QLabel(self.widget)
        self.label_6.setGeometry(QtCore.QRect(20, 10, 71, 16))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.labelTituloEditar = QtWidgets.QLabel(self.widget)
        self.labelTituloEditar.setGeometry(QtCore.QRect(20, 40, 101, 16))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(8)
        self.labelTituloEditar.setFont(font)
        self.labelTituloEditar.setObjectName("labelTituloEditar")
        self.labelCapaEdicion = QtWidgets.QLabel(self.widget)
        self.labelCapaEdicion.setGeometry(QtCore.QRect(133, 40, 81, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        self.labelCapaEdicion.setFont(font)
        self.labelCapaEdicion.setObjectName("labelCapaEdicion")
        self.botonEditar = QtWidgets.QPushButton(self.widget)
        self.botonEditar.setGeometry(QtCore.QRect(70, 160, 101, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.botonEditar.setFont(font)
        self.botonEditar.setStyleSheet("background : rgb(174, 116, 0);\n"
"color : rgb(255, 255, 255);\n"
"border-radius : 4px;")
        self.botonEditar.setObjectName("botonEditar")
        self.tablaEdicion = QtWidgets.QTableWidget(self.widget)
        self.tablaEdicion.setGeometry(QtCore.QRect(10, 60, 221, 91))
        self.tablaEdicion.setStyleSheet("QHeaderView::section\n"
"{\n"
"background-color: rgb(238,225,200);\n"
"color : rgb(52, 42, 24 );\n"
"text-align: right;\n"
"font-size:12px;\n"
"height:24px\n"
"}")
        self.tablaEdicion.setObjectName("tablaEdicion")
        self.tablaEdicion.setColumnCount(2)
        self.tablaEdicion.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tablaEdicion.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tablaEdicion.setHorizontalHeaderItem(1, item)
        self.widget_2 = QtWidgets.QWidget(self.tab)
        self.widget_2.setGeometry(QtCore.QRect(280, 160, 221, 181))
        self.widget_2.setStyleSheet("QWidget{\n"
"background : rgb(250,238,224);\n"
"}")
        self.widget_2.setObjectName("widget_2")
        self.label_9 = QtWidgets.QLabel(self.widget_2)
        self.label_9.setGeometry(QtCore.QRect(23, 10, 191, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.comboCapaReferencia = QtWidgets.QComboBox(self.widget_2)
        self.comboCapaReferencia.setGeometry(QtCore.QRect(20, 40, 181, 22))
        self.comboCapaReferencia.setStyleSheet("QComboBox QAbstractItemView::item { min-height: 25; font-family: \"Century Gothic\";}\n"
"QListView{color: black ; font-size: 16px; outline:none; font-weight:bold; font-family: \"Century Gothic\";}\n"
"QListView::item:selected { color: white; background-color:  rgb(250,238,224); font-family: \"Century Gothic\";}\n"
"QComboBox{\n"
"background : rgb(255,255,255);\n"
"}")
        self.comboCapaReferencia.setObjectName("comboCapaReferencia")
        self.checkTodasGeom = QtWidgets.QCheckBox(self.widget_2)
        self.checkTodasGeom.setGeometry(QtCore.QRect(25, 80, 181, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        self.checkTodasGeom.setFont(font)
        self.checkTodasGeom.setObjectName("checkTodasGeom")
        self.botonCargarReferencia = QtWidgets.QPushButton(self.widget_2)
        self.botonCargarReferencia.setGeometry(QtCore.QRect(60, 120, 101, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.botonCargarReferencia.setFont(font)
        self.botonCargarReferencia.setStyleSheet("background : rgb(174, 116, 0);\n"
"color : rgb(255, 255, 255);\n"
"border-radius : 4px;")
        self.botonCargarReferencia.setObjectName("botonCargarReferencia")
        self.btnAbrirCedula = QtWidgets.QPushButton(self.tab)
        self.btnAbrirCedula.setGeometry(QtCore.QRect(130, 440, 101, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.btnAbrirCedula.setFont(font)
        self.btnAbrirCedula.setStyleSheet("background : rgb(174, 116, 0);\n"
"color : rgb(255, 255, 255);\n"
"border-radius : 4px;")
        self.btnAbrirCedula.setObjectName("btnAbrirCedula")
        self.btnCancelAperCedula = QtWidgets.QPushButton(self.tab)
        self.btnCancelAperCedula.setGeometry(QtCore.QRect(290, 440, 101, 41))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.btnCancelAperCedula.setFont(font)
        self.btnCancelAperCedula.setStyleSheet("background : rgb(174, 116, 0);\n"
"color : rgb(255, 255, 255);\n"
"border-radius : 4px;")
        self.btnCancelAperCedula.setObjectName("btnCancelAperCedula")
        self.lbEstatusCedula = QtWidgets.QLabel(self.tab)
        self.lbEstatusCedula.setGeometry(QtCore.QRect(130, 410, 101, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        self.lbEstatusCedula.setFont(font)
        self.lbEstatusCedula.setObjectName("lbEstatusCedula")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.label_10 = QtWidgets.QLabel(self.tab_2)
        self.label_10.setGeometry(QtCore.QRect(20, 10, 301, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.label_11 = QtWidgets.QLabel(self.tab_2)
        self.label_11.setGeometry(QtCore.QRect(50, 50, 161, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.comboCapasEdicion = QtWidgets.QComboBox(self.tab_2)
        self.comboCapasEdicion.setGeometry(QtCore.QRect(50, 80, 161, 22))
        self.comboCapasEdicion.setStyleSheet("QComboBox QAbstractItemView::item { min-height: 25; font-family: \"Century Gothic\";}\n"
"QListView{color: black ; font-size: 16px; outline:none; font-weight:bold; font-family: \"Century Gothic\";}\n"
"QListView::item:selected { color: white; background-color:  rgb(250,238,224); font-family: \"Century Gothic\";}\n"
"QComboBox{\n"
"background : rgb(250,238,224);\n"
"}")
        self.comboCapasEdicion.setObjectName("comboCapasEdicion")
        self.botonActivarEdicion = QtWidgets.QPushButton(self.tab_2)
        self.botonActivarEdicion.setGeometry(QtCore.QRect(200, 120, 131, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.botonActivarEdicion.setFont(font)
        self.botonActivarEdicion.setStyleSheet("background : rgb(174, 116, 0);\n"
"color : rgb(255, 255, 255);\n"
"border-radius : 4px;")
        self.botonActivarEdicion.setObjectName("botonActivarEdicion")
        self.tablaServiciosCalles = QtWidgets.QTableWidget(self.tab_2)
        self.tablaServiciosCalles.setGeometry(QtCore.QRect(140, 380, 256, 131))
        self.tablaServiciosCalles.setObjectName("tablaServiciosCalles")
        self.tablaServiciosCalles.setColumnCount(0)
        self.tablaServiciosCalles.setRowCount(0)
        self.tablaEdicionRef = QtWidgets.QTableWidget(self.tab_2)
        self.tablaEdicionRef.setGeometry(QtCore.QRect(140, 160, 256, 131))
        self.tablaEdicionRef.setObjectName("tablaEdicionRef")
        self.tablaEdicionRef.setColumnCount(2)
        self.tablaEdicionRef.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tablaEdicionRef.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tablaEdicionRef.setHorizontalHeaderItem(1, item)
        self.botonActualizarRef = QtWidgets.QPushButton(self.tab_2)
        self.botonActualizarRef.setGeometry(QtCore.QRect(120, 300, 131, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.botonActualizarRef.setFont(font)
        self.botonActualizarRef.setStyleSheet("background : rgb(174, 116, 0);\n"
"color : rgb(255, 255, 255);\n"
"border-radius : 4px;")
        self.botonActualizarRef.setObjectName("botonActualizarRef")
        self.botonCancelarReferencia = QtWidgets.QPushButton(self.tab_2)
        self.botonCancelarReferencia.setGeometry(QtCore.QRect(290, 300, 121, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.botonCancelarReferencia.setFont(font)
        self.botonCancelarReferencia.setStyleSheet("background : rgb(174, 116, 0);\n"
"color : rgb(255, 255, 255);\n"
"border-radius : 4px;")
        self.botonCancelarReferencia.setObjectName("botonCancelarReferencia")
        self.botonActualizarServiciosCalles = QtWidgets.QPushButton(self.tab_2)
        self.botonActualizarServiciosCalles.setGeometry(QtCore.QRect(200, 520, 141, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.botonActualizarServiciosCalles.setFont(font)
        self.botonActualizarServiciosCalles.setStyleSheet("background : rgb(174, 116, 0);\n"
"color : rgb(255, 255, 255);\n"
"border-radius : 4px;")
        self.botonActualizarServiciosCalles.setObjectName("botonActualizarServiciosCalles")
        self.label_12 = QtWidgets.QLabel(self.tab_2)
        self.label_12.setGeometry(QtCore.QRect(30, 350, 181, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(12)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.labelCapaEdicionRef = QtWidgets.QLabel(self.tab_2)
        self.labelCapaEdicionRef.setGeometry(QtCore.QRect(300, 50, 161, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        self.labelCapaEdicionRef.setFont(font)
        self.labelCapaEdicionRef.setObjectName("labelCapaEdicionRef")
        self.labelStatusEdicionRef = QtWidgets.QLabel(self.tab_2)
        self.labelStatusEdicionRef.setGeometry(QtCore.QRect(300, 70, 161, 20))
        font = QtGui.QFont()
        font.setFamily("Century Gothic")
        font.setPointSize(10)
        self.labelStatusEdicionRef.setFont(font)
        self.labelStatusEdicionRef.setObjectName("labelStatusEdicionRef")
        self.tabWidget.addTab(self.tab_2, "")

        self.retranslateUi(ActualizacionCatastralV3DialogBase)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(ActualizacionCatastralV3DialogBase)

    def retranslateUi(self, ActualizacionCatastralV3DialogBase):
        _translate = QtCore.QCoreApplication.translate
        ActualizacionCatastralV3DialogBase.setWindowTitle(_translate("ActualizacionCatastralV3DialogBase", "ActualizacionCatastralV3"))
        self.label.setText(_translate("ActualizacionCatastralV3DialogBase", "Actualizacion Cartografica de Manzana"))
        self.label_2.setText(_translate("ActualizacionCatastralV3DialogBase", "<html><head/><body><p align=\"center\">Localidad</p></body></html>"))
        self.label_3.setText(_translate("ActualizacionCatastralV3DialogBase", "<html><head/><body><p align=\"center\">Sector</p></body></html>"))
        self.label_4.setText(_translate("ActualizacionCatastralV3DialogBase", "<html><head/><body><p align=\"center\">Manzana</p></body></html>"))
        self.botonCargar.setText(_translate("ActualizacionCatastralV3DialogBase", "Cargar \n"
"Manzana"))
        self.label_5.setText(_translate("ActualizacionCatastralV3DialogBase", "Cedula Catastral"))
        self.label_6.setText(_translate("ActualizacionCatastralV3DialogBase", "Edicion"))
        self.labelTituloEditar.setText(_translate("ActualizacionCatastralV3DialogBase", "Capa en Edicion"))
        self.labelCapaEdicion.setText(_translate("ActualizacionCatastralV3DialogBase", "TextLabel"))
        self.botonEditar.setText(_translate("ActualizacionCatastralV3DialogBase", "Actualizar"))
        item = self.tablaEdicion.horizontalHeaderItem(0)
        item.setText(_translate("ActualizacionCatastralV3DialogBase", "Atributo"))
        item = self.tablaEdicion.horizontalHeaderItem(1)
        item.setText(_translate("ActualizacionCatastralV3DialogBase", "Valor"))
        self.label_9.setText(_translate("ActualizacionCatastralV3DialogBase", "Capas de referencia"))
        self.checkTodasGeom.setText(_translate("ActualizacionCatastralV3DialogBase", "Incluir todas las geometrias"))
        self.botonCargarReferencia.setText(_translate("ActualizacionCatastralV3DialogBase", "Cargar capa\n"
"de Referencia"))
        self.btnAbrirCedula.setText(_translate("ActualizacionCatastralV3DialogBase", "Abrir Cedula"))
        self.btnCancelAperCedula.setText(_translate("ActualizacionCatastralV3DialogBase", "Cancelar"))
        self.lbEstatusCedula.setText(_translate("ActualizacionCatastralV3DialogBase", "<html><head/><body><p align=\"center\">Localidad</p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("ActualizacionCatastralV3DialogBase", "Actualizacion Cartografica de Manzana"))
        self.label_10.setText(_translate("ActualizacionCatastralV3DialogBase", "<html><head/><body><p align=\"center\"><span style=\" font-weight:600;\">Edicion de Capas de Referencia</span></p></body></html>"))
        self.label_11.setText(_translate("ActualizacionCatastralV3DialogBase", "<html><head/><body><p align=\"center\">Capa a Cargar</p></body></html>"))
        self.botonActivarEdicion.setText(_translate("ActualizacionCatastralV3DialogBase", "Activar Edicion de \n"
"Referencia"))
        item = self.tablaEdicionRef.horizontalHeaderItem(0)
        item.setText(_translate("ActualizacionCatastralV3DialogBase", "Atributo"))
        item = self.tablaEdicionRef.horizontalHeaderItem(1)
        item.setText(_translate("ActualizacionCatastralV3DialogBase", "Valor"))
        self.botonActualizarRef.setText(_translate("ActualizacionCatastralV3DialogBase", "Actualizar Datos"))
        self.botonCancelarReferencia.setText(_translate("ActualizacionCatastralV3DialogBase", "Cancelar Cambios"))
        self.botonActualizarServiciosCalles.setText(_translate("ActualizacionCatastralV3DialogBase", "Actualizar Servicios"))
        self.label_12.setText(_translate("ActualizacionCatastralV3DialogBase", "<html><head/><body><p align=\"center\"><span style=\" font-weight:600;\">Servicios de Calles</span></p></body></html>"))
        self.labelCapaEdicionRef.setText(_translate("ActualizacionCatastralV3DialogBase", "<html><head/><body><p align=\"center\">Capa a Cargar</p></body></html>"))
        self.labelStatusEdicionRef.setText(_translate("ActualizacionCatastralV3DialogBase", "<html><head/><body><p align=\"center\">Capa a Cargar</p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("ActualizacionCatastralV3DialogBase", "Capas de Referencia"))

