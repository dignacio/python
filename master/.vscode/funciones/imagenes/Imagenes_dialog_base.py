# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Imagenes_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ImagenesDialogBase(object):
    def setupUi(self, ImagenesDialogBase):
        ImagenesDialogBase.setObjectName("ImagenesDialogBase")
        ImagenesDialogBase.resize(400, 300)
        self.button_box = QtWidgets.QDialogButtonBox(ImagenesDialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")

        self.retranslateUi(ImagenesDialogBase)
        self.button_box.accepted.connect(ImagenesDialogBase.accept)
        self.button_box.rejected.connect(ImagenesDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(ImagenesDialogBase)

    def retranslateUi(self, ImagenesDialogBase):
        _translate = QtCore.QCoreApplication.translate
        ImagenesDialogBase.setWindowTitle(_translate("ImagenesDialogBase", "Imagenes"))

