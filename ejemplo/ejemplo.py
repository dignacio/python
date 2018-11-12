# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ejemplo
                                 A QGIS plugin
 ejemplo
                              -------------------
        begin                : 2018-02-23
        git sha              : $Format:%H$
        copyright            : (C) 2018 by ejemplo
        email                : ejemplo
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
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAction


# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .ejemplo_dialog import ejemploDialog
import os.path
from qgis.core import *
import time
from .Worker import Worker
import os, json, requests, threading

from pprint import pprint
from requests_futures.sessions import FuturesSession

class ThreadingExample(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, interval=1):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval
        self.contador = 0

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution


    def run(self):
        """ Method that runs forever """
        while True:
            # Do something
            #print('Doing something imporant in the background')
            #print(self.interval)
            time.sleep(self.interval)

    def funcion(self, argumento):
        while True:
            self.contador += 1
            #print('hola ---------')

class ejemplo:
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
            'ejemplo_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.threadpool = QThreadPool()
        #print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        # Create the dialog (after translation) and keep reference
        self.dlg = ejemploDialog()
        self.counter = 0
        self.stop = True
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&ejemplo')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ejemplo')
        self.toolbar.setObjectName(u'ejemplo')


        
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()
        
        
        

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
        return QCoreApplication.translate('ejemplo', message)

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

        icon_path = ':/plugins/ejemplo/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'ejemplo'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&ejemplo'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def execute_this_fn(self):
        #print("Hello!")
        #self.l.setText('hola')
        #return 'hola'
        
        while self.stop:
            time.sleep(1)
            self.counter +=1

    def execute_this_fn__dos(self):
        #print("Hello!")
        #self.l.setText('hola')
        #return 'hola'
        
        self.stop = False

    def oh_no(self):
        # Pass the function to execute
        worker = Worker(self.execute_this_fn) # Any other args, kwargs are passed to the run function
        #print(worker)
        # Execute
        self.threadpool.start(worker)
        #print(self.counter)
        #ThreadingExample()

    def cambio(self):
        icon = QIcon()
        icon.addPixmap(QPixmap('C:/AplicacionQGIS/notify_off.png'))
        
        for action in self.iface.helpToolBar().actions():
            if not action.isSeparator():
                if(action.text() == 'btnPrueba'):
                    action.setIcon(icon)
                print('  action: %s (%s)' % (action.text(), action.isChecked()))

    def stop_event(self):

        worker = Worker(self.execute_this_fn__dos) # Any other args, kwargs are passed to the run function
        self.threadpool.start(worker)
        self.timer.stop()
        
        icon = QIcon()
        icon.addPixmap(QPixmap('C:/AplicacionQGIS/notify_on.png'))
        
        for action in self.iface.helpToolBar().actions():
            if not action.isSeparator():
                if(action.text() == 'btnPrueba'):
                    action.setIcon(icon)
                print('  action: %s (%s)' % (action.text(), action.isChecked()))



    def bg_cb(self, sess, resp):
        # parse the json storing the result on the response object
        resp.data = resp.json()

    def recurring_timer(self):
        #self.counter +=1
        #self.dlg.l.setText("Counter: %d" % self.counter)

        #if self.counter%2 == 0:
        print("Counter: %d" % self.counter)

        if not self.stop:
            if self.dlg.pushButton.icon():
                icon = QIcon()
                self.dlg.pushButton.setIcon(icon)

        if self.counter%10 == 0:
            icon = QIcon()
            icon.addPixmap(QPixmap('C:/AplicacionQGIS/notify_on.png'))
            
            for action in self.iface.helpToolBar().actions():
                if not action.isSeparator():
                    if(action.text() == 'btnPrueba'):
                        action.setIcon(icon)

        if self.counter%7 == 0:
            icon = QIcon()
            icon.addPixmap(QPixmap('C:/AplicacionQGIS/notify_off.png'))
            
            for action in self.iface.helpToolBar().actions():
                if not action.isSeparator():
                    if(action.text() == 'btnPrueba'):
                        action.setIcon(icon)
        #while self.counter < 30:
        #    print("Counter: %d" % self.counter)
        #    pass

    def run(self):

        # evento del boton
        self.dlg.pushButton_3.clicked.connect(self.cambio)
        self.dlg.pushButton_2.clicked.connect(self.oh_no)
        self.dlg.pushButton.clicked.connect(self.stop_event)



        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        
