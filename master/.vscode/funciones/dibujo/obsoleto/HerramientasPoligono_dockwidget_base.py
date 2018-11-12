# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'HerramientasPoligono_dockwidget_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_HerramientasPoligonoDockWidgetBase(object):
    def setupUi(self, HerramientasPoligonoDockWidgetBase):
        HerramientasPoligonoDockWidgetBase.setObjectName("HerramientasPoligonoDockWidgetBase")
        HerramientasPoligonoDockWidgetBase.resize(232, 141)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.dockWidgetContents)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        HerramientasPoligonoDockWidgetBase.setWidget(self.dockWidgetContents)

        self.retranslateUi(HerramientasPoligonoDockWidgetBase)
        QtCore.QMetaObject.connectSlotsByName(HerramientasPoligonoDockWidgetBase)

    def retranslateUi(self, HerramientasPoligonoDockWidgetBase):
        _translate = QtCore.QCoreApplication.translate
        HerramientasPoligonoDockWidgetBase.setWindowTitle(_translate("HerramientasPoligonoDockWidgetBase", "HerramientasPoligono"))
        self.label.setText(_translate("HerramientasPoligonoDockWidgetBase", "Replace this QLabel\n"
"with the desired\n"
"plugin content."))

