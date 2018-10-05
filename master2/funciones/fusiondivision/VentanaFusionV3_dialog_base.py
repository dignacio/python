# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'VentanaFusionV3_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VentanaFusionV3DialogBase(object):
    def setupUi(self, VentanaFusionV3DialogBase):
        VentanaFusionV3DialogBase.setObjectName("VentanaFusionV3DialogBase")
        VentanaFusionV3DialogBase.resize(400, 300)
        self.button_box = QtWidgets.QDialogButtonBox(VentanaFusionV3DialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")

        self.retranslateUi(VentanaFusionV3DialogBase)
        self.button_box.accepted.connect(VentanaFusionV3DialogBase.accept)
        self.button_box.rejected.connect(VentanaFusionV3DialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(VentanaFusionV3DialogBase)

    def retranslateUi(self, VentanaFusionV3DialogBase):
        _translate = QtCore.QCoreApplication.translate
        VentanaFusionV3DialogBase.setWindowTitle(_translate("VentanaFusionV3DialogBase", "VentanaFusionV3"))

