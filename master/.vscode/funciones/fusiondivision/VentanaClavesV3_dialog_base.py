# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'VentanaClavesV3_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VentanaClavesV3DialogBase(object):
    def setupUi(self, VentanaClavesV3DialogBase):
        VentanaClavesV3DialogBase.setObjectName("VentanaClavesV3DialogBase")
        VentanaClavesV3DialogBase.resize(400, 300)
        self.button_box = QtWidgets.QDialogButtonBox(VentanaClavesV3DialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")

        self.retranslateUi(VentanaClavesV3DialogBase)
        self.button_box.accepted.connect(VentanaClavesV3DialogBase.accept)
        self.button_box.rejected.connect(VentanaClavesV3DialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(VentanaClavesV3DialogBase)

    def retranslateUi(self, VentanaClavesV3DialogBase):
        _translate = QtCore.QCoreApplication.translate
        VentanaClavesV3DialogBase.setWindowTitle(_translate("VentanaClavesV3DialogBase", "VentanaClavesV3"))

