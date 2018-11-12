# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EliminarPoligonos_dockwidget_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_EliminarPoligonosDockWidgetBase(object):
    def setupUi(self, EliminarPoligonosDockWidgetBase):
        EliminarPoligonosDockWidgetBase.setObjectName("EliminarPoligonosDockWidgetBase")
        EliminarPoligonosDockWidgetBase.resize(232, 141)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.dockWidgetContents)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        EliminarPoligonosDockWidgetBase.setWidget(self.dockWidgetContents)

        self.retranslateUi(EliminarPoligonosDockWidgetBase)
        QtCore.QMetaObject.connectSlotsByName(EliminarPoligonosDockWidgetBase)

    def retranslateUi(self, EliminarPoligonosDockWidgetBase):
        _translate = QtCore.QCoreApplication.translate
        EliminarPoligonosDockWidgetBase.setWindowTitle(_translate("EliminarPoligonosDockWidgetBase", "EliminarPoligonos"))
        self.label.setText(_translate("EliminarPoligonosDockWidgetBase", "Replace this QLabel\n"
"with the desired\n"
"plugin content."))

