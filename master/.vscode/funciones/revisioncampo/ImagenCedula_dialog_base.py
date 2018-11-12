# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ImagenCedula_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ImagenCedulaDialogBase(object):
    def setupUi(self, ImagenCedulaDialogBase):
        ImagenCedulaDialogBase.setObjectName("ImagenCedulaDialogBase")
        ImagenCedulaDialogBase.resize(400, 300)
        self.button_box = QtWidgets.QDialogButtonBox(ImagenCedulaDialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")

        self.retranslateUi(ImagenCedulaDialogBase)
        self.button_box.accepted.connect(ImagenCedulaDialogBase.accept)
        self.button_box.rejected.connect(ImagenCedulaDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(ImagenCedulaDialogBase)

    def retranslateUi(self, ImagenCedulaDialogBase):
        _translate = QtCore.QCoreApplication.translate
        ImagenCedulaDialogBase.setWindowTitle(_translate("ImagenCedulaDialogBase", "ImagenCedula"))

