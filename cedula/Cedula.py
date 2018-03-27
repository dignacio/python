# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Cedula
                                 A QGIS plugin
 Cedula Catastral
                              -------------------
        begin                : 2018-03-20
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Worknest
        email                : dignacio.lopezo@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon, QCursor, QPixmap
from PyQt5.QtWidgets import QAction, QMessageBox

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .Cedula_dialog import CedulaDialog
from .Cedula_MainWindow import CedulaMainWindow
import os.path
from qgis.core import QgsMessageLog, QgsProject


class Cedula:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Cedula_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = CedulaDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Cedula')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Cedula')
        self.toolbar.setObjectName(u'Cedula')

        # evento boton 
        #self.dlg.pushButton.clicked.connect(self.abreVentana)
        #self.dlg.pushButton_2.clicked.connect(self.imprimeStatus)

        self.dlg.pushButton.clicked.connect(self.cambiaCursor)

        self.dlg.variable = {'uno': 1, 'dos': 2}
        self.dlg.lista = {}
        self.contador = 0

        self.dlg.predio = None

        self.canvas = iface.mapCanvas()

        self.cursorRedondo = QCursor(QPixmap(["16 16 3 1",
                                "      c None",
                                ".     c #FF0000",
                                "+     c #FFFFFF",
                                "                ",
                                "       +.+      ",
                                "      ++.++     ",
                                "     +.....+    ",
                                "    +.     .+   ",
                                "   +.   .   .+  ",
                                "  +.    .    .+ ",
                                " ++.    .    .++",
                                " ... ...+... ...",
                                " ++.    .    .++",
                                "  +.    .    .+ ",
                                "   +.   .   .+  ",
                                "   ++.     .+   ",
                                "    ++.....+    ",
                                "      ++.++     ",
                                "       +.+      "]))


    def imprimeStatus(self):
        for key, value in self.dlg.lista.items():
            #print(key, value) windowTitle

            print(str(self.dlg.lista[key].isVisible()),str(self.dlg.lista[key].windowTitle()))


    def cambiaCursor(self):
        self.dlg.predio = QgsProject.instance().mapLayersByName('predios.geom')[0]
        print(self.canvas)
        self.iface.actionSelect().trigger()
        self.canvas.setCursor(self.cursorRedondo)
        self.dlg.predio.selectionChanged.connect(self.touchPredio)
        self.dlg.pushButton.setEnabled(False)

    def abreVentana(self):

        if len(self.dlg.lista) == 5:
            self.msg = QMessageBox()
            self.msg.setText("Ha completado el numero maximo de Cedulas abiertas")
            self.msg.setIcon(QMessageBox().Warning)
            self.msg.setWindowTitle("titulo")
            self.msg.show()
            result = self.msg.exec_()
            #self.contador -= 1
            return

        #self.window = None

        #self.window = CedulaMainWindow()
        #self.window.pushButton.clicked.connect(self.hasAlgo)
        #self.window.show()


        #self.window1 = CedulaMainWindow()
        #self.window1.pushButton.clicked.connect(self.hasAlgo)
        #self.window1.show()


        
        self.dlg.lista[str(self.contador)] = CedulaMainWindow(str(self.contador))
        #self.dlg.lista[str(self.contador)].pushButton.clicked.connect(self.hasAlgo)
        #self.dlg.lista[str(self.contador)].closeEvent(self,event)
        self.dlg.lista[str(self.contador)].setWindowTitle(str(self.contador))
        #self.dlg.lista[str(self.contador)].setAttribute(55, True)
        self.dlg.lista[str(self.contador)].show()

        self.contador += 1

        # print('imprime algo x2')
        # QgsMessageLog.logMessage("message", "name")
        # print('imprime algo x3')

    def hasAlgo(self):
        texto = "Sin descripcion enviada"
        #self.msg = QMessageBox()
        #self.msg.setText("mensaje")
        #self.msg.setIcon(QMessageBox().Critical)
        #self.msg.setWindowTitle("titulo")
        #self.msg.show()
        #result = self.msg.exec_()

        #QgsMessageLog.logMessage("message", "name")
        #print('entro')

        if len(texto) != 0:
            return

        if "0" in self.dlg.lista:
            #print(str(self.dlg.lista["0"].isActiveWindow()) + str(self.dlg.lista["0"].windowTitle()) + str(self.dlg.lista["0"].close()))
            print(self.dlg.lista["0"].key, self.dlg.lista["0"].value)
            #self.dlg.lista["0"].lineEdit.setText("texto")

        if "1" in self.dlg.lista:
            #print(str(self.dlg.lista["1"].isActiveWindow()) + str(self.dlg.lista["1"].windowTitle()) + str(self.dlg.lista["1"].close()))
            print(self.dlg.lista["1"].key, self.dlg.lista["1"].value)
            #self.dlg.lista["1"].lineEdit.setText("otro texto")

        if "2" in self.dlg.lista:
            #print(str(self.dlg.lista["2"].isActiveWindow()) + str(self.dlg.lista["2"].windowTitle()) + str(self.dlg.lista["2"].close()))
            print(self.dlg.lista["2"].key, self.dlg.lista["2"].value)
            #self.dlg.lista["2"].lineEdit.setText("otro texto del dos")

        if "3" in self.dlg.lista:
            #print(str(self.dlg.lista["3"].isActiveWindow()) + str(self.dlg.lista["3"].windowTitle()) + str(self.dlg.lista["3"].close()))
            print(self.dlg.lista["3"].key, self.dlg.lista["3"].value)
            #self.dlg.lista["3"].lineEdit.setText("otro texto del tres")

        if "4" in self.dlg.lista:
            #print(str(self.dlg.lista["4"].isActiveWindow()) + str(self.dlg.lista["4"].windowTitle()) + str(self.dlg.lista["4"].close()))
            print(self.dlg.lista["4"].key, self.dlg.lista["4"].value)
            #self.dlg.lista["4"].lineEdit.setText("otro texto del tres")

        if "5" in self.dlg.lista:
            #print(str(self.dlg.lista["5"].isActiveWindow()) + str(self.dlg.lista["5"].windowTitle()) + str(self.dlg.lista["5"].close()))
            print(self.dlg.lista["5"].key, self.dlg.lista["5"].value)
            #self.dlg.lista["5"].lineEdit.setText("otro texto del tres")


    # - EVENTOS -

    # PREDIOS.selectionChange()
    def touchPredio(self):
        campos = self.dlg.predio.fields()
        print('entrap')
        features = self.dlg.predio.selectedFeatures()

        for f in features:
            print(f["cve_cat"])


        print(self.dlg.predio.isSignalConnected())

        self.dlg.predio.selectionChanged.disconnect()

        print(self.dlg.predio.isSignalConnected())

        self.dlg.pushButton.setEnabled(True)
    

    # CONDOMINIOS_VERTICALES.selectionChange()
    def touchCondV(self):
        print('entrav')
        features = self.condV.selectedFeatures()

        for f in features:
            print(f.id())

    # CLAVES_CONDOMINIOS_VERTICALES.selectionChange()
    def touchCvesCondV(self):
        print('entracvev')
        features = self.cveCondV.selectedFeatures()

        for f in features:
            print(f.id())

    # CONDOMINIOS_HORIZONTALES.selectionChange()
    def touchCondH(self):
        print('entrah')
        features = self.condH.selectedFeatures()

        for f in features:
            print(f.id())


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Cedula', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Cedula/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Cedula Catastral'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        # disconnects
        self.dlg.closingPlugin.disconnect(self.onClosePlugin)
        print('cerramos el plugin')

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Cedula'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):

        self.dlg.pushButton.setEnabled(True)
        #self.dlg.closingPlugin.connect(self.onClosePlugin)
        
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
        # Do something useful here - delete the line containing pass and
        # substitute with your code.
        # pass
            print("CERRAR")
        # OBTENER CAPAS A USAR
        # predio
            #self.predio.selectionChanged.disconnect(self.touchPredio)
        




            

