# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DibujoV3_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DibujoV3DialogBase(object):
    def setupUi(self, DibujoV3DialogBase):
        DibujoV3DialogBase.setObjectName("DibujoV3DialogBase")
        DibujoV3DialogBase.resize(400, 300)
        self.button_box = QtWidgets.QDialogButtonBox(DibujoV3DialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")

        self.retranslateUi(DibujoV3DialogBase)
        self.button_box.accepted.connect(DibujoV3DialogBase.accept)
        self.button_box.rejected.connect(DibujoV3DialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(DibujoV3DialogBase)

    def retranslateUi(self, DibujoV3DialogBase):
        _translate = QtCore.QCoreApplication.translate
        DibujoV3DialogBase.setWindowTitle(_translate("DibujoV3DialogBase", "DibujoV3"))

