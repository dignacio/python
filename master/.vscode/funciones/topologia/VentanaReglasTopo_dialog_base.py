# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'VentanaReglasTopo_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VentanaReglasTopoDialogBase(object):
    def setupUi(self, VentanaReglasTopoDialogBase):
        VentanaReglasTopoDialogBase.setObjectName("VentanaReglasTopoDialogBase")
        VentanaReglasTopoDialogBase.resize(400, 300)
        self.button_box = QtWidgets.QDialogButtonBox(VentanaReglasTopoDialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")

        self.retranslateUi(VentanaReglasTopoDialogBase)
        self.button_box.accepted.connect(VentanaReglasTopoDialogBase.accept)
        self.button_box.rejected.connect(VentanaReglasTopoDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(VentanaReglasTopoDialogBase)

    def retranslateUi(self, VentanaReglasTopoDialogBase):
        _translate = QtCore.QCoreApplication.translate
        VentanaReglasTopoDialogBase.setWindowTitle(_translate("VentanaReglasTopoDialogBase", "VentanaReglasTopo"))

