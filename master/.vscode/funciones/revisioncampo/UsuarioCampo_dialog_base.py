# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UsuarioCampo_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_UsuarioCampoDialogBase(object):
    def setupUi(self, UsuarioCampoDialogBase):
        UsuarioCampoDialogBase.setObjectName("UsuarioCampoDialogBase")
        UsuarioCampoDialogBase.resize(400, 300)
        self.button_box = QtWidgets.QDialogButtonBox(UsuarioCampoDialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")

        self.retranslateUi(UsuarioCampoDialogBase)
        self.button_box.accepted.connect(UsuarioCampoDialogBase.accept)
        self.button_box.rejected.connect(UsuarioCampoDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(UsuarioCampoDialogBase)

    def retranslateUi(self, UsuarioCampoDialogBase):
        _translate = QtCore.QCoreApplication.translate
        UsuarioCampoDialogBase.setWindowTitle(_translate("UsuarioCampoDialogBase", "UsuarioCampo"))

