# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AsignacionPadron_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AsignacionPadronDialogBase(object):
    def setupUi(self, AsignacionPadronDialogBase):
        AsignacionPadronDialogBase.setObjectName("AsignacionPadronDialogBase")
        AsignacionPadronDialogBase.resize(400, 300)
        self.button_box = QtWidgets.QDialogButtonBox(AsignacionPadronDialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")

        self.retranslateUi(AsignacionPadronDialogBase)
        self.button_box.accepted.connect(AsignacionPadronDialogBase.accept)
        self.button_box.rejected.connect(AsignacionPadronDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(AsignacionPadronDialogBase)

    def retranslateUi(self, AsignacionPadronDialogBase):
        _translate = QtCore.QCoreApplication.translate
        AsignacionPadronDialogBase.setWindowTitle(_translate("AsignacionPadronDialogBase", "AsignacionPadron"))

