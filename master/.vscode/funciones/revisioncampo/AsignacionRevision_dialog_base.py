# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AsignacionRevision_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VentanaAsignacionRevisionDialogBase(object):
    def setupUi(self, VentanaAsignacionRevisionDialogBase):
        VentanaAsignacionRevisionDialogBase.setObjectName("VentanaAsignacionRevisionDialogBase")
        VentanaAsignacionRevisionDialogBase.resize(561, 534)
        self.btnLiberarAsig = QtWidgets.QPushButton(VentanaAsignacionRevisionDialogBase)
        self.btnLiberarAsig.setGeometry(QtCore.QRect(400, 490, 121, 26))
        self.btnLiberarAsig.setObjectName("btnLiberarAsig")
        self.btnMenos = QtWidgets.QPushButton(VentanaAsignacionRevisionDialogBase)
        self.btnMenos.setGeometry(QtCore.QRect(250, 270, 61, 26))
        self.btnMenos.setObjectName("btnMenos")
        self.chkTodoMazPred = QtWidgets.QCheckBox(VentanaAsignacionRevisionDialogBase)
        self.chkTodoMazPred.setGeometry(QtCore.QRect(330, 90, 211, 20))
        self.chkTodoMazPred.setObjectName("chkTodoMazPred")
        self.tablaMazPred = QtWidgets.QTableWidget(VentanaAsignacionRevisionDialogBase)
        self.tablaMazPred.setGeometry(QtCore.QRect(320, 120, 221, 311))
        self.tablaMazPred.setObjectName("tablaMazPred")
        self.tablaMazPred.setColumnCount(2)
        self.tablaMazPred.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tablaMazPred.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tablaMazPred.setHorizontalHeaderItem(1, item)
        self.tablaClaves = QtWidgets.QTableWidget(VentanaAsignacionRevisionDialogBase)
        self.tablaClaves.setGeometry(QtCore.QRect(20, 120, 221, 311))
        self.tablaClaves.setObjectName("tablaClaves")
        self.tablaClaves.setColumnCount(1)
        self.tablaClaves.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tablaClaves.setHorizontalHeaderItem(0, item)
        self.cmbUsuario = QtWidgets.QComboBox(VentanaAsignacionRevisionDialogBase)
        self.cmbUsuario.setGeometry(QtCore.QRect(30, 490, 201, 22))
        self.cmbUsuario.setObjectName("cmbUsuario")
        self.btnAsignar = QtWidgets.QPushButton(VentanaAsignacionRevisionDialogBase)
        self.btnAsignar.setGeometry(QtCore.QRect(270, 490, 121, 26))
        self.btnAsignar.setObjectName("btnAsignar")
        self.chkTodoClaves = QtWidgets.QCheckBox(VentanaAsignacionRevisionDialogBase)
        self.chkTodoClaves.setGeometry(QtCore.QRect(30, 90, 211, 20))
        self.chkTodoClaves.setObjectName("chkTodoClaves")
        self.btnMas = QtWidgets.QPushButton(VentanaAsignacionRevisionDialogBase)
        self.btnMas.setGeometry(QtCore.QRect(250, 230, 61, 26))
        self.btnMas.setObjectName("btnMas")
        self.lblUsuario_2 = QtWidgets.QLabel(VentanaAsignacionRevisionDialogBase)
        self.lblUsuario_2.setGeometry(QtCore.QRect(30, 460, 191, 20))
        self.lblUsuario_2.setObjectName("lblUsuario_2")
        self.lblLocalidad_2 = QtWidgets.QLabel(VentanaAsignacionRevisionDialogBase)
        self.lblLocalidad_2.setGeometry(QtCore.QRect(30, 20, 141, 20))
        self.lblLocalidad_2.setObjectName("lblLocalidad_2")
        self.cmbLocalidad = QtWidgets.QComboBox(VentanaAsignacionRevisionDialogBase)
        self.cmbLocalidad.setGeometry(QtCore.QRect(30, 40, 141, 22))
        self.cmbLocalidad.setObjectName("cmbLocalidad")

        self.retranslateUi(VentanaAsignacionRevisionDialogBase)
        QtCore.QMetaObject.connectSlotsByName(VentanaAsignacionRevisionDialogBase)

    def retranslateUi(self, VentanaAsignacionRevisionDialogBase):
        _translate = QtCore.QCoreApplication.translate
        VentanaAsignacionRevisionDialogBase.setWindowTitle(_translate("VentanaAsignacionRevisionDialogBase", "VentanaAsignacionRevision"))
        self.btnLiberarAsig.setText(_translate("VentanaAsignacionRevisionDialogBase", "Liberar asignaciones"))
        self.btnMenos.setText(_translate("VentanaAsignacionRevisionDialogBase", "-"))
        self.chkTodoMazPred.setText(_translate("VentanaAsignacionRevisionDialogBase", "Seleccionar Todo"))
        item = self.tablaMazPred.horizontalHeaderItem(0)
        item.setText(_translate("VentanaAsignacionRevisionDialogBase", "Manzana"))
        item = self.tablaMazPred.horizontalHeaderItem(1)
        item.setText(_translate("VentanaAsignacionRevisionDialogBase", "Predio"))
        item = self.tablaClaves.horizontalHeaderItem(0)
        item.setText(_translate("VentanaAsignacionRevisionDialogBase", "Claves catastrales"))
        self.btnAsignar.setText(_translate("VentanaAsignacionRevisionDialogBase", "Asignar"))
        self.chkTodoClaves.setText(_translate("VentanaAsignacionRevisionDialogBase", "Seleccionar Todo"))
        self.btnMas.setText(_translate("VentanaAsignacionRevisionDialogBase", "+"))
        self.lblUsuario_2.setText(_translate("VentanaAsignacionRevisionDialogBase", "<html><head/><body><p align=\"center\">USUARIO</p></body></html>"))
        self.lblLocalidad_2.setText(_translate("VentanaAsignacionRevisionDialogBase", "<html><head/><body><p align=\"center\">MANZANA</p></body></html>"))

