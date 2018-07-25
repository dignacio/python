# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'VentanaDibujoV3_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VentanaDibujoV3DialogBase(object):
    def setupUi(self, VentanaDibujoV3DialogBase):
        VentanaDibujoV3DialogBase.setObjectName("VentanaDibujoV3DialogBase")
        VentanaDibujoV3DialogBase.resize(400, 300)
        self.button_box = QtWidgets.QDialogButtonBox(VentanaDibujoV3DialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")

        self.retranslateUi(VentanaDibujoV3DialogBase)
        self.button_box.accepted.connect(VentanaDibujoV3DialogBase.accept)
        self.button_box.rejected.connect(VentanaDibujoV3DialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(VentanaDibujoV3DialogBase)

    def retranslateUi(self, VentanaDibujoV3DialogBase):
        _translate = QtCore.QCoreApplication.translate
        VentanaDibujoV3DialogBase.setWindowTitle(_translate("VentanaDibujoV3DialogBase", "VentanaDibujoV3"))

