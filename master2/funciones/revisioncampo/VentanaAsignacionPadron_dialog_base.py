# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'VentanaAsignacionPadron_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VentanaAsignacionPadronDialogBase(object):
    def setupUi(self, VentanaAsignacionPadronDialogBase):
        VentanaAsignacionPadronDialogBase.setObjectName("VentanaAsignacionPadronDialogBase")
        VentanaAsignacionPadronDialogBase.resize(400, 300)
        self.button_box = QtWidgets.QDialogButtonBox(VentanaAsignacionPadronDialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")

        self.retranslateUi(VentanaAsignacionPadronDialogBase)
        self.button_box.accepted.connect(VentanaAsignacionPadronDialogBase.accept)
        self.button_box.rejected.connect(VentanaAsignacionPadronDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(VentanaAsignacionPadronDialogBase)

    def retranslateUi(self, VentanaAsignacionPadronDialogBase):
        _translate = QtCore.QCoreApplication.translate
        VentanaAsignacionPadronDialogBase.setWindowTitle(_translate("VentanaAsignacionPadronDialogBase", "VentanaAsignacionPadron"))

