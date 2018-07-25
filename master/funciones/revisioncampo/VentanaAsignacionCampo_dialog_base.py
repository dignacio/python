# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'VentanaAsignacionCampo_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VentanaAsignacionCampoDialogBase(object):
    def setupUi(self, VentanaAsignacionCampoDialogBase):
        VentanaAsignacionCampoDialogBase.setObjectName("VentanaAsignacionCampoDialogBase")
        VentanaAsignacionCampoDialogBase.resize(365, 427)
        self.lblUsuario = QtWidgets.QLabel(VentanaAsignacionCampoDialogBase)
        self.lblUsuario.setGeometry(QtCore.QRect(10, 20, 101, 16))
        self.lblUsuario.setObjectName("lblUsuario")
        self.tablaMazPred = QtWidgets.QTableWidget(VentanaAsignacionCampoDialogBase)
        self.tablaMazPred.setGeometry(QtCore.QRect(70, 50, 221, 311))
        self.tablaMazPred.setObjectName("tablaMazPred")
        self.tablaMazPred.setColumnCount(2)
        self.tablaMazPred.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tablaMazPred.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tablaMazPred.setHorizontalHeaderItem(1, item)
        self.btnLiberar = QtWidgets.QPushButton(VentanaAsignacionCampoDialogBase)
        self.btnLiberar.setGeometry(QtCore.QRect(120, 380, 131, 26))
        self.btnLiberar.setObjectName("btnLiberar")
        self.fldUsuario = QtWidgets.QLineEdit(VentanaAsignacionCampoDialogBase)
        self.fldUsuario.setGeometry(QtCore.QRect(130, 20, 211, 20))
        self.fldUsuario.setObjectName("fldUsuario")

        self.retranslateUi(VentanaAsignacionCampoDialogBase)
        QtCore.QMetaObject.connectSlotsByName(VentanaAsignacionCampoDialogBase)

    def retranslateUi(self, VentanaAsignacionCampoDialogBase):
        _translate = QtCore.QCoreApplication.translate
        VentanaAsignacionCampoDialogBase.setWindowTitle(_translate("VentanaAsignacionCampoDialogBase", "VentanaAsignacionCampo"))
        self.lblUsuario.setText(_translate("VentanaAsignacionCampoDialogBase", "<html><head/><body><p align=\"right\">USUARIO:</p></body></html>"))
        item = self.tablaMazPred.horizontalHeaderItem(0)
        item.setText(_translate("VentanaAsignacionCampoDialogBase", "Manzana"))
        item = self.tablaMazPred.horizontalHeaderItem(1)
        item.setText(_translate("VentanaAsignacionCampoDialogBase", "Predio"))
        self.btnLiberar.setText(_translate("VentanaAsignacionCampoDialogBase", "Liberar"))

