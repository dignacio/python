# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'actualizacioncatastralv2_dockwidget_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_actualizacioncatastralv2DockWidgetBase(object):
    def setupUi(self, actualizacioncatastralv2DockWidgetBase):
        actualizacioncatastralv2DockWidgetBase.setObjectName("actualizacioncatastralv2DockWidgetBase")
        actualizacioncatastralv2DockWidgetBase.resize(362, 315)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.dockWidgetContents)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.comboLocalidad = QtWidgets.QComboBox(self.tab)
        self.comboLocalidad.setGeometry(QtCore.QRect(110, 20, 191, 21))
        self.comboLocalidad.setObjectName("comboLocalidad")
        self.comboSector = QtWidgets.QComboBox(self.tab)
        self.comboSector.setGeometry(QtCore.QRect(110, 60, 191, 21))
        self.comboSector.setObjectName("comboSector")
        self.comboManzana = QtWidgets.QComboBox(self.tab)
        self.comboManzana.setGeometry(QtCore.QRect(110, 100, 191, 21))
        self.comboManzana.setObjectName("comboManzana")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(33, 20, 61, 21))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(30, 60, 61, 21))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setGeometry(QtCore.QRect(30, 100, 61, 21))
        self.label_3.setObjectName("label_3")
        self.botonCargar = QtWidgets.QPushButton(self.tab)
        self.botonCargar.setGeometry(QtCore.QRect(120, 160, 85, 26))
        self.botonCargar.setObjectName("botonCargar")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        actualizacioncatastralv2DockWidgetBase.setWidget(self.dockWidgetContents)

        self.retranslateUi(actualizacioncatastralv2DockWidgetBase)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(actualizacioncatastralv2DockWidgetBase)

    def retranslateUi(self, actualizacioncatastralv2DockWidgetBase):
        _translate = QtCore.QCoreApplication.translate
        actualizacioncatastralv2DockWidgetBase.setWindowTitle(_translate("actualizacioncatastralv2DockWidgetBase", "actualizacioncatastralv2"))
        self.label.setText(_translate("actualizacioncatastralv2DockWidgetBase", "<html><head/><body><p align=\"right\"><span style=\" font-size:10pt;\">Localidad</span></p></body></html>"))
        self.label_2.setText(_translate("actualizacioncatastralv2DockWidgetBase", "<html><head/><body><p align=\"right\"><span style=\" font-size:10pt;\">Sector</span></p></body></html>"))
        self.label_3.setText(_translate("actualizacioncatastralv2DockWidgetBase", "<html><head/><body><p align=\"right\"><span style=\" font-size:10pt;\">Manzana</span></p></body></html>"))
        self.botonCargar.setText(_translate("actualizacioncatastralv2DockWidgetBase", "Cargar"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("actualizacioncatastralv2DockWidgetBase", "Tab 1"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("actualizacioncatastralv2DockWidgetBase", "Tab 2"))

