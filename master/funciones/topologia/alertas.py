
from PyQt5.QtWidgets import QAction, QMessageBox

class Alerta:

        def createAlert(self, mensaje, icono, titulo):
                #Create QMessageBox
                msg = QMessageBox()
                #Add message
                msg.setText(mensaje)
                #Add icon of critical error
                msg.setIcon(icono)
                #Add tittle
                msg.setWindowTitle(titulo)
                #Show of message dialog
                msg.show()
                # Run the dialog event loop
                result = msg.exec_()