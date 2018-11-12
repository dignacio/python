# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'IntermedioCedulaRevision_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_IntermedioCedulaRevisionDialogBase(object):
    def setupUi(self, IntermedioCedulaRevisionDialogBase):
        IntermedioCedulaRevisionDialogBase.setObjectName("IntermedioCedulaRevisionDialogBase")
        IntermedioCedulaRevisionDialogBase.resize(400, 300)
        self.button_box = QtWidgets.QDialogButtonBox(IntermedioCedulaRevisionDialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.button_box.setObjectName("button_box")

        self.retranslateUi(IntermedioCedulaRevisionDialogBase)
        self.button_box.accepted.connect(IntermedioCedulaRevisionDialogBase.accept)
        self.button_box.rejected.connect(IntermedioCedulaRevisionDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(IntermedioCedulaRevisionDialogBase)

    def retranslateUi(self, IntermedioCedulaRevisionDialogBase):
        _translate = QtCore.QCoreApplication.translate
        IntermedioCedulaRevisionDialogBase.setWindowTitle(_translate("IntermedioCedulaRevisionDialogBase", "IntermedioCedulaRevision"))

