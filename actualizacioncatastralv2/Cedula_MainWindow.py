import os

from PyQt5 import uic
from PyQt5 import QtWidgets

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMessageBox


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'mainWindow.ui'))

class CedulaMainWindow(QtWidgets.QMainWindow, FORM_CLASS):
    def __init__(self, numero = "0", parent=None):
        """Constructor."""
        super(CedulaMainWindow, self).__init__(parent, \
            flags=Qt.WindowMinimizeButtonHint|Qt.WindowMaximizeButtonHint|Qt.WindowCloseButtonHint)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        # print(numero)
        self.cveCatastral = numero
        self.setupUi(self)

    def closeEvent(self,event):
        reply = QMessageBox.question(self,'Message',"Are you sure to quit? - " + self.windowTitle(), QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


    def showEvent(self, event):
        # -- Eventos
        self.pushButton.clicked.connect(self.hasAlgo)

        # -- Titulo
        self.setWindowTitle(self.descomponeCveCata(self.cveCatastral))

        # -- carga informacion
        self.lbCveCata.setText(self.descomponeCveCata(self.cveCatastral))
        self.muestraClaveGlobal(self.cveCatastral)


        

    # -- Metodos --

    def descomponeCveCata(self, cveCata):

        clave = cveCata[0:2] + '-'
        clave += cveCata[2:5] + '-'
        clave += cveCata[5:8] + '-'
        clave += cveCata[8:10] + '-'
        clave += cveCata[10:14] + '-'
        clave += cveCata[14:17] + '-'
        clave += cveCata[17:20] + '-'
        clave += cveCata[20:25]

        return clave

    def muestraClaveGlobal(self, cveCata):

        self.lbEdo.setText(cveCata[0:2])
        self.lbRegCat.setText(cveCata[2:5])
        self.lbMpio.setText(cveCata[5:8])
        self.lbSecc.setText(cveCata[8:10])
        self.lbLoc.setText(cveCata[10:14])
        self.lbSec.setText(cveCata[14:17])
        self.lbMza.setText(cveCata[17:20])
        self.lbPredio.setText(cveCata[20:25])

    def hasAlgo(self):

        # clave = "-";

        # for llave, valor in self.lista.items():
        #    if valor.isActiveWindow():
        #        clave = llave

        self.createAlert('Clave: ' + self.cveCatastral, QMessageBox.Information, 'Cedula Catastral')
        #self.createAlert('Clave: ' + clave, QMessageBox.Information, 'Cedula Catastral')

    # -- Metodos CIERRA --
    

    def createAlert(self, mensaje, icono, titulo):
        #Create QMessageBox
        self.msg = QMessageBox()
        #Add message
        self.msg.setText(mensaje)
        #Add icon of critical error
        self.msg.setIcon(icono)
        #Add tittle
        self.msg.setWindowTitle(titulo)
        #Show of message dialog
        self.msg.show()
         # Run the dialog event loop
        result = self.msg.exec_()