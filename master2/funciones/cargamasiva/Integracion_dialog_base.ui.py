# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Integracion_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_IntegracionDialogBase(object):
    def setupUi(self, IntegracionDialogBase):
        IntegracionDialogBase.setObjectName("IntegracionDialogBase")
        IntegracionDialogBase.resize(400, 300)
        self.button_box = QtWidgets.QDialogButtonBox(IntegracionDialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")

        self.retranslateUi(IntegracionDialogBase)
        self.button_box.accepted.connect(IntegracionDialogBase.accept)
        self.button_box.rejected.connect(IntegracionDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(IntegracionDialogBase)

    def retranslateUi(self, IntegracionDialogBase):
        _translate = QtCore.QCoreApplication.translate
        IntegracionDialogBase.setWindowTitle(_translate("IntegracionDialogBase", "Integracion"))

