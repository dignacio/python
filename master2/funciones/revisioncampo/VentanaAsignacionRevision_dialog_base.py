# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'VentanaAsignacionRevision_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VentanaAsignacionRevisionDialogBase(object):
    def setupUi(self, VentanaAsignacionRevisionDialogBase):
        VentanaAsignacionRevisionDialogBase.setObjectName("VentanaAsignacionRevisionDialogBase")
        VentanaAsignacionRevisionDialogBase.resize(400, 300)
        self.button_box = QtWidgets.QDialogButtonBox(VentanaAsignacionRevisionDialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")

        self.retranslateUi(VentanaAsignacionRevisionDialogBase)
        self.button_box.accepted.connect(VentanaAsignacionRevisionDialogBase.accept)
        self.button_box.rejected.connect(VentanaAsignacionRevisionDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(VentanaAsignacionRevisionDialogBase)

    def retranslateUi(self, VentanaAsignacionRevisionDialogBase):
        _translate = QtCore.QCoreApplication.translate
        VentanaAsignacionRevisionDialogBase.setWindowTitle(_translate("VentanaAsignacionRevisionDialogBase", "VentanaAsignacionRevision"))

