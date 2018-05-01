# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ActualizacionCatastral
                                 A QGIS plugin
 ActualizacionCatastral
                              -------------------
        begin                : 2018-02-20
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Worknest
        email                : worknest.contacto@gmail.com
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

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QAction, QMessageBox
from PyQt5 import QtWidgets
# Initialize Qt resources from file resources.py
from .resources import *
from qgis.core import *
from qgis.utils import iface
from qgis.gui import QgsLayerTreeView
from .auntenticacion import Autenticacion
from osgeo import ogr, osr
import os, json, requests

# Import the code for the DockWidget
from .ActualizacionCatastral_dockwidget import ActualizacionCatastralDockWidget
import os.path



class ActualizacionCatastral:
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

        #Objeto de autenticacion
        self.autenticacion = Autenticacion()

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ActualizacionCatastral_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.root = QgsProject.instance().layerTreeRoot()
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&ActualizacionCatastral')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ActualizacionCatastral')
        self.toolbar.setObjectName(u'ActualizacionCatastral')

        #print "** INITIALIZING ActualizacionCatastral"

        self.pluginIsActive = False
        self.dockwidget = ActualizacionCatastralDockWidget()

        # eventos botones
        self.dockwidget.botonActualizar.clicked.connect(self.actualizarCapa)
        self.dockwidget.botonCambiar.clicked.connect(self.guardarValor)

        # usoLogin - usada para acceso al Qgis mediante aplicacion de logueo
        # False
        QSettings().setValue("usoLogin", "False")


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
        return QCoreApplication.translate('ActualizacionCatastral', message)


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

        icon_path = ':/plugins/ActualizacionCatastral/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Act. Catastral'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def actualizarCapa(self):
        autenticado = self.validarAuth()
        if autenticado:

            # layer = QgsLayerTreeView().selectedLayers()
            # E R R O R la siguiente linea causa problemas en qgis
            # self.capas = QgsLayerTreeView().selectedLayers()
            
            self.capa = iface.activeLayer()

            if (self.capa == None):
                mensaje = "Seleccione una capa"
                self.createAlert(mensaje, QMessageBox().Critical, 'Edicion de atributos')
                self.dockwidget.fieldCapa.setText("")
                self.dockwidget.tableWidgetAtributosEdit.clearContents()
                self.dockwidget.tableWidgetAtributosEdit.setRowCount(0)
                for row in range(0, self.dockwidget.tableWidgetAtributosEdit.rowCount()):
                            
                    self.dockwidget.tableWidgetAtributosEdit.removeRow(row)

            else:
                self.capaActual = self.capa
                self.features = list(self.capaActual.selectedFeatures())

                if(len(self.features) != 1):
                    mensaje = "Debes tener seleccionada exactamente un elemento de la capa"
                    self.createAlert(mensaje, QMessageBox().Critical, 'Edicion de atributos')
                    self.dockwidget.fieldCapa.setText("")
                    self.dockwidget.tableWidgetAtributosEdit.clearContents()
                    self.dockwidget.tableWidgetAtributosEdit.setRowCount(0)
                    for row in range(0, self.dockwidget.tableWidgetAtributosEdit.rowCount()):
                            
                        self.dockwidget.tableWidgetAtributosEdit.removeRow(row)
                else:
                    if self.capaActual.name() in self.capasReferencia.values():
                        mensaje = "No puedes editar las capas de Referencia"
                        self.createAlert(mensaje, QMessageBox.Critical, 'Capas de referencia')

                        #Codifo para limpiar y remover la tabla para editar atributos
                        self.dockwidget.tableWidgetAtributosEdit.clearContents()
                        self.dockwidget.tableWidgetAtributosEdit.setRowCount(0)
                        for row in range(0, self.dockwidget.tableWidgetAtributosEdit.rowCount()):
                            
                            self.dockwidget.tableWidgetAtributosEdit.removeRow(row)  

                    else:
                        self.dockwidget.fieldCapa.setText(self.capaActual.name())
                        campos = self.capaActual.fields()   
                        nombres = [campo.name() for campo in campos]
                        
                    
                        self.dockwidget.tableWidgetAtributosEdit.clearContents()
                        self.dockwidget.tableWidgetAtributosEdit.setRowCount(0)
                        for row in range(0, self.dockwidget.tableWidgetAtributosEdit.rowCount()):
                            
                            self.dockwidget.tableWidgetAtributosEdit.removeRow(row)        
                            
                       

                        valores = self.capaActual.selectedFeatures()
                        
                        for x in range(0, len(nombres)):
                            
                            self.dockwidget.tableWidgetAtributosEdit.insertRow(x)
                            item = QtWidgets.QTableWidgetItem(nombres[x])
                            self.dockwidget.tableWidgetAtributosEdit.setItem(x, 0 , item)#self.capaActual.getFeatures().attributes()[x])
                            item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                            self.dockwidget.tableWidgetAtributosEdit.setItem(x, 1 , QtWidgets.QTableWidgetItem(str(valores[0].attributes()[x])))
                            

    def guardarValor(self):
        autenticado = self.validarAuth()
        if autenticado:
            
                if  self.dockwidget.tableWidgetAtributosEdit.rowCount() > 0:
                    
                    #Obtenemos las propiedades de la capa
                    self.capa = iface.activeLayer()
                    self.capaActual = self.capa
                    self.features = self.capaActual.selectedFeatures()[0]
                    


                    #Activamos el modo de edicion
                    self.capaActual.startEditing()
                    
                    for x in range(0, len(self.features.attributes())):
                        self.features[x] = self.dockwidget.tableWidgetAtributosEdit.item(x, 1).text()
                        

                    self.capaActual.updateFeature(self.features)
                    self.capaActual.commitChanges()
                    self.createAlert('Se guardo correctamente', QMessageBox.Information, 'Edicion de atributos')
                    self.actualizarCapa()
                else:
                    self.createAlert("Necesitas seleccionar una capa", QMessageBox.Warning, 'Edicion de atributos')
                

        elif autenticado == False:
            self.createAlert("Tu inicio de sesion expiro", QMessageBox.Warning, 'Sesion expiro edicion de atributos')

        print('se presiono el boton de guarda valor')

    #Metodo que solicita todos los sectores
    def getAllSectores(self):
        try:
            response = requests.get('http://192.168.0.30:91/api/busqueda/sectores/')
        except requests.exceptions.RequestException:
            raise RuntimeError('Error de servidor')
        
        self.dockwidget.comboBox.addItems(response.json())

    #Funcion que obtiene todas las Manzanas de acuerdo a un sector
    def getAllManzanasBySector(self):
        self.dockwidget.comboBoxManzanas.clear()
        sector = self.dockwidget.comboBox.currentText()
        try:
            response = requests.get('http://192.168.0.30:91/api/busqueda/manzanas/'+sector)
        except requests.exceptions.RequestException:
            self.createAlert('Error de servidor', QMessageBox.Critical, 'Consulta de servicio Manzanas')
            return

        self.dockwidget.comboBoxManzanas.addItems(response.json())

    #Funcion que introduce todas las capas de referencia en su respectivo combo
    def getAllCapas(self):
        self.dockwidget.comboBoxCapas.clear()
        #Get key from value capas.keys()[capas.values().index([value])]
        self.dockwidget.comboBoxCapas.addItems(self.capasReferencia.values())

    #Validar Sectores y Manzanas en ComboBox
    def validateSectoresAndManzanas(self):
        if (self.dockwidget.comboBoxManzanas.count() > 0 and self.dockwidget.comboBox.count() > 0):
            return True
        else:
            return False

    # R E M O V E R   G E O M E T R I A S
    #Funcion que elimina las Features de la capa de Manzana
    def removeFeaturesManzana(self):
        #Obtenemos el layer de predios
        mem_layer = QgsProject.instance().mapLayersByName('manzana')

        if len(mem_layer) != 1:
            raise AttributeError
        mem_layer = mem_layer[0]
        
        #Obtenemos los fields antes de eliminar las features
        inFields = mem_layer.dataProvider().fields()
        #Habilitamos opcion de editado
        mem_layer.startEditing()
        #Iteramos para eliminar Features
        for f in mem_layer.getFeatures():
            mem_layer.deleteFeature(f.id())
        
        #Reasignamos los fields al VectorLayer
        mem_layer.dataProvider().addAttributes(inFields.toList())
        #Guardamos los cambios
        mem_layer.commitChanges()

    #Funcion que elimina las Features de La capa de predios
    def removeFeaturesPredios(self):
        
        #Obtenemos el layer de predios
        mem_layer = QgsProject.instance().mapLayersByName('predios')
        
        if len(mem_layer) != 1:
            raise AttributeError
        mem_layer = mem_layer[0]
        
        #Obtenemos los fields antes de eliminar las features
        inFields = mem_layer.dataProvider().fields()
        #Habilitamos opcion de editado
        mem_layer.startEditing()
        #Iteramos para eliminar Features
        for f in mem_layer.getFeatures():
            mem_layer.deleteFeature(f.id())
        
        #Reasignamos los fields al VectorLayer
        mem_layer.dataProvider().addAttributes(inFields.toList())
        #Guardamos los cambios
        mem_layer.commitChanges()

    #Funcion que elimina las Features de las construcciones
    def removeFeaturesConstrucciones(self):
        #Obtenemos el layer de predios
        mem_layer = QgsProject.instance().mapLayersByName('construcciones')

        if len(mem_layer) != 1:
            raise AttributeError
        mem_layer = mem_layer[0]
        
        #Obtenemos los fields antes de eliminar las features
        inFields = mem_layer.dataProvider().fields()
        #Habilitamos opcion de editado
        mem_layer.startEditing()
        #Iteramos para eliminar Features
        for f in mem_layer.getFeatures():
            mem_layer.deleteFeature(f.id())
        
        #Reasignamos los fields al VectorLayer
        mem_layer.dataProvider().addAttributes(inFields.toList())
        #Guardamos los cambios
        mem_layer.commitChanges()

    #Funcion que elimina las Features de las volumenes construcciones
    def removeFeaturesVolumenConstrucciones(self):
        #Obtenemos el layer de predios
        mem_layer = QgsProject.instance().mapLayersByName('volumenes')

        if len(mem_layer) != 1:
            raise AttributeError
        mem_layer = mem_layer[0]
        
        # se ejecuta solamente cuando existe el layer
        if mem_layer != None:
            #Obtenemos los fields antes de eliminar las features
            inFields = mem_layer.dataProvider().fields()
            #Habilitamos opcion de editado
            mem_layer.startEditing()
            #Iteramos para eliminar Features
            for f in mem_layer.getFeatures():
                mem_layer.deleteFeature(f.id())
        
            #Reasignamos los fields al VectorLayer
            mem_layer.dataProvider().addAttributes(inFields.toList())
            #Guardamos los cambios
            mem_layer.commitChanges()

    #Funcion que elimin las Features de Construcciones especiales
    def removeFeaturesEspConstrucciones(self):
        #Obtenemos el layer de predios
        mem_layer = QgsProject.instance().mapLayersByName('constEsp')

        if len(mem_layer) != 1:
            raise AttributeError
        mem_layer = mem_layer[0]
        
        if mem_layer != None:
            #Obtenemos los fields antes de eliminar las features
            inFields = mem_layer.dataProvider().fields()
            #Habilitamos opcion de editado
            mem_layer.startEditing()
            #Iteramos para eliminar Features
            for f in mem_layer.getFeatures():
                mem_layer.deleteFeature(f.id())
            
            #Reasignamos los fields al VectorLayer
            mem_layer.dataProvider().addAttributes(inFields.toList())
            #Guardamos los cambios
            mem_layer.commitChanges()

    # P I N T A R   G E O M E T R I A S
    #Metodo que pinta la manzana en QGIS a traves de las propiedades de ObtenerManzana
    def pintarManzana(self):
        #A partir de la cadema creamos un objeto JSON con el metodo obtener manzana
        data = self.obtenerManzana()
        type(data)
        #Declaramos el sistema de referencia de corndanas
        srid = 32614
        inSpatialRef = osr.SpatialReference()
        inSpatialRef.ImportFromEPSG(int(srid))
        outSpatialRef = osr.SpatialReference()
        outSpatialRef.ImportFromEPSG(int(srid))
        coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
        if not bool(data):
            raise Exception('Error')

        #Obtenemos todos los atributos del JSON
        if data['features'] == []:
            return
        keys = list(data['features'][0]['properties'].keys())
        properties = []
        geoms = []
        for feature in data['features']:
            geom = feature['geometry']
            property = feature['properties']
            geom = json.dumps(geom)
            geometry = ogr.CreateGeometryFromJson(geom)
            geometry.Transform(coordTrans)
            geoms.append(geometry.ExportToWkt())
            l = []
            for i in range(0, len(keys)):
                l.append(property[keys[i]])
            properties.append(l)

        mem_layer = QgsProject.instance().mapLayersByName('manzana')

        if len(mem_layer) != 1:
            raise AttributeError
        mem_layer = mem_layer[0]

        prov = mem_layer.dataProvider()
        feats = [ QgsFeature() for i in range(len(geoms)) ]

        for i, feat in enumerate(feats):
            feat.setAttributes(properties[i])
            feat.setGeometry(QgsGeometry.fromWkt(geoms[i]))

        prov.addFeatures(feats)
        
        settings = QgsPalLayerSettings()
        settings.fieldName = 'clave'
        settings.centroidWhole = True

        textFormat = QgsTextFormat()
        textFormat.setColor(QColor(255,0,0))
        textFormat.setSize(8)
        textFormat.setNamedStyle('Bold')

        settings.setFormat(textFormat)

        labeling = QgsVectorLayerSimpleLabeling(settings)
        mem_layer.setLabeling(labeling)
        mem_layer.setLabelsEnabled(True)

        mem_layer.triggerRepaint()

        mem_layer.commitChanges()
        mem_layer.triggerRepaint()

    #Funcion que pinta los predios a traves de las propiedades del predio de acuerdo a la manzana
    def pintarPredios(self):
        data = self.obtenerPredios()
        type(data)
        srid = 32614
        inSpatialRef = osr.SpatialReference()
        inSpatialRef.ImportFromEPSG(int(srid))
        outSpatialRef = osr.SpatialReference()
        outSpatialRef.ImportFromEPSG(int(srid))
        coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
        if not bool(data):
            raise Exception('Error')

        if data['features'] == []:
            return
        keys = list(data['features'][0]['properties'].keys())
        properties = []
        geoms = []
        for feature in data['features']:
            geom = feature['geometry']
            property = feature['properties']
            geom = json.dumps(geom)
            geometry = ogr.CreateGeometryFromJson(geom)
            geometry.Transform(coordTrans)
            geoms.append(geometry.ExportToWkt())
            l = []
            for i in range(0, len(keys)):
                l.append(property[keys[i]])
            properties.append(l)

        
        
        mem_layer = QgsProject.instance().mapLayersByName('predios')

        if len(mem_layer) != 1:
            raise AttributeError
        mem_layer = mem_layer[0]

        prov = mem_layer.dataProvider()

        feats = [ QgsFeature() for i in range(len(geoms)) ]
        for i, feat in enumerate(feats):
            feat.setAttributes(properties[i])
            feat.setGeometry(QgsGeometry.fromWkt(geoms[i]))

        prov.addFeatures(feats)

        settings = QgsPalLayerSettings()
        settings.fieldName = 'clave'
        settings.centroidWhole = True

        textFormat = QgsTextFormat()
        textFormat.setColor(QColor(0,255,0))
        textFormat.setSize(8)
        textFormat.setNamedStyle('Bold')

        settings.setFormat(textFormat)

        labeling = QgsVectorLayerSimpleLabeling(settings)
        mem_layer.setLabeling(labeling)
        mem_layer.setLabelsEnabled(True)

        mem_layer.triggerRepaint()

        mem_layer.commitChanges()
        mem_layer.triggerRepaint()

    #Funcion que pinta las construcciones
    def pintarConstrucciones(self):
        data = self.obtenerConstrucciones()
        
        srid = 32614
        inSpatialRef = osr.SpatialReference()
        inSpatialRef.ImportFromEPSG(int(srid))
        outSpatialRef = osr.SpatialReference()
        outSpatialRef.ImportFromEPSG(int(srid))
        coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
        if not bool(data):
            raise Exception('Error')

        if data['features'] == []:
            return
        keys = list(data['features'][0]['properties'].keys())
        properties = []
        geoms = []
        for feature in data['features']:
            geom = feature['geometry']

            if geom == None:
                continue

            property = feature['properties']
            geom = json.dumps(geom)
            geometry = ogr.CreateGeometryFromJson(geom)
            geometry.Transform(coordTrans)
            geoms.append(geometry.ExportToWkt())
            l = []
            for i in range(0, len(keys)):
                l.append(property[keys[i]])
            properties.append(l)

        print('entra2')
        mem_layer = QgsProject.instance().mapLayersByName('construcciones')

        if len(mem_layer) != 1:
            raise AttributeError
        mem_layer = mem_layer[0]

        prov = mem_layer.dataProvider()
        feats = [ QgsFeature() for i in range(len(geoms)) ]

        for i, feat in enumerate(feats):
            feat.setAttributes(properties[i])
            feat.setGeometry(QgsGeometry.fromWkt(geoms[i]))
        print('entra3')

        prov.addFeatures(feats)

        settings = QgsPalLayerSettings()
        settings.fieldName = 'clave'
        settings.centroidWhole = True

        textFormat = QgsTextFormat()
        textFormat.setColor(QColor(0,0,0))
        textFormat.setSize(8)
        textFormat.setNamedStyle('Bold')

        settings.setFormat(textFormat)

        labeling = QgsVectorLayerSimpleLabeling(settings)
        mem_layer.setLabeling(labeling)
        mem_layer.setLabelsEnabled(True)

        mem_layer.triggerRepaint()

        mem_layer.commitChanges()
        mem_layer.triggerRepaint()

    #Funcion que pinta las construcciones especiales a partir de un ID de Manzana
    def pintarEspConstrucciones(self):
        mem_layer = QgsProject.instance().mapLayersByName('constEsp')

        if len(mem_layer) != 1:
            raise AttributeError
        mem_layer = mem_layer[0]

        if mem_layer == None:
            return
        data = self.obtenerEspConstrucciones()
        type(data)
        srid = 32614
        inSpatialRef = osr.SpatialReference()
        inSpatialRef.ImportFromEPSG(int(srid))
        outSpatialRef = osr.SpatialReference()
        outSpatialRef.ImportFromEPSG(int(srid))
        coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
        if not bool(data):
            raise Exception('Error')

        if data['features'] == []:
            return
        keys = list(data['features'][0]['properties'].keys())
        properties = []
        geoms = []
        for feature in data['features']:
            geom = feature['geometry']
            property = feature['properties']
            geom = json.dumps(geom)
            geometry = ogr.CreateGeometryFromJson(geom)
            geometry.Transform(coordTrans)
            geoms.append(geometry.ExportToWkt())
            l = []
            for i in range(0, len(keys)):
                l.append(property[keys[i]])
            properties.append(l)

        prov = mem_layer.dataProvider()
        feats = [ QgsFeature() for i in range(len(geoms)) ]
        for i, feat in enumerate(feats):
            feat.setAttributes(properties[i])
            feat.setGeometry(QgsGeometry.fromWkt(geoms[i]))

        prov.addFeatures(feats)
        settings = QgsPalLayerSettings()
        settings.fieldName = 'clave'
        settings.centroidWhole = True

        textFormat = QgsTextFormat()
        textFormat.setColor(QColor(0,255,255))
        textFormat.setSize(8)
        textFormat.setNamedStyle('Bold')

        settings.setFormat(textFormat)

        labeling = QgsVectorLayerSimpleLabeling(settings)
        mem_layer.setLabeling(labeling)
        mem_layer.setLabelsEnabled(True)

        mem_layer.triggerRepaint()

        mem_layer.commitChanges()
        mem_layer.triggerRepaint()


    #Funcion que pinta los vol de construcciones
    def pintarVolumenConstrucciones(self):
        
        mem_layer = QgsProject.instance().mapLayersByName('volumenes')

        if len(mem_layer) != 1:
            raise AttributeError
        mem_layer = mem_layer[0]

        if mem_layer == None:
            return

        data = self.obtenerVolConstrucciones()
        type(data)
        srid = 32614
        inSpatialRef = osr.SpatialReference()
        inSpatialRef.ImportFromEPSG(int(srid))
        outSpatialRef = osr.SpatialReference()
        outSpatialRef.ImportFromEPSG(int(srid))
        coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
        if not bool(data):
            raise Exception('Error')

        if data['features'] == []:
            return
        keys = list(data['features'][0]['properties'].keys())
        properties = []
        geoms = []
        for feature in data['features']:
            geom = feature['geometry']
            property = feature['properties']
            geom = json.dumps(geom)
            geometry = ogr.CreateGeometryFromJson(geom)
            geometry.Transform(coordTrans)
            geoms.append(geometry.ExportToWkt())
            l = []
            for i in range(0, len(keys)):
                l.append(property[keys[i]])
            properties.append(l)

 
        prov = mem_layer.dataProvider()
        feats = [ QgsFeature() for i in range(len(geoms)) ]
        for i, feat in enumerate(feats):
            feat.setAttributes(properties[i])
            feat.setGeometry(QgsGeometry.fromWkt(geoms[i]))

        prov.addFeatures(feats)
        settings = QgsPalLayerSettings()
        settings.fieldName = 'clave'
        settings.centroidWhole = True

        textFormat = QgsTextFormat()
        textFormat.setColor(QColor(0,0,255))
        textFormat.setSize(8)
        textFormat.setNamedStyle('Bold')

        settings.setFormat(textFormat)

        labeling = QgsVectorLayerSimpleLabeling(settings)
        mem_layer.setLabeling(labeling)
        mem_layer.setLabelsEnabled(True)

        mem_layer.triggerRepaint()

        mem_layer.commitChanges()
        mem_layer.triggerRepaint()

    #Funcion que pinta todas las capas de referencia
    def pintarCapasReferencia(self, uriFigura, value, posicion):
        
        consulta = self.root.findGroup('referencia')

        if consulta == None:
            raise AttributeError('Capas no detectadas')
            return None
        
        #Nombre de la capa de acuerdo al valor del ComboBox de capas a cargar
        nameCapa = value

        egName = list(self.capasReferencia.keys())[list(self.capasReferencia.values()).index(value)]
        #Obtenemos los datos
        data = self.obtenerCapasDeReferencia(egName)
        type(data)
        srid = 32614
        inSpatialRef = osr.SpatialReference()
        inSpatialRef.ImportFromEPSG(int(srid))
        outSpatialRef = osr.SpatialReference()
        outSpatialRef.ImportFromEPSG(int(srid))
        coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
        if not bool(data):
            raise Exception('Error')

        keys = list(data['features'][0]['properties'].keys())
        properties = []
        geoms = []
        for feature in data['features']:
            geom = feature['geometry']
            property = feature['properties']
            geom = json.dumps(geom)
            geometry = ogr.CreateGeometryFromJson(geom)
            geometry.Transform(coordTrans)
            geoms.append(geometry.ExportToWkt())
            l = []
            for i in range(0, len(keys)):
                l.append(property[keys[i]])
            properties.append(l)

        fields = ""
        for k in keys:
            fields = fields + "&field=" + k + ":string(15)"

        uri = str(uriFigura)+"?crs=epsg:" + str(srid) + fields + "&index=yes"
        mem_layer = QgsVectorLayer(uri, nameCapa, 'memory')
        mem_layer.setReadOnly(True)
        prov = mem_layer.dataProvider()
        feats = [ QgsFeature() for i in range(len(geoms)) ]
        for i, feat in enumerate(feats):
            feat.setAttributes(properties[i])
            feat.setGeometry(QgsGeometry.fromWkt(geoms[i]))

        prov.addFeatures(feats)
        settings = QgsPalLayerSettings()
        settings.fieldName = 'clave'
        settings.centroidWhole = True

        textFormat = QgsTextFormat()
        textFormat.setColor(QColor(0,0,0))
        textFormat.setSize(8)
        textFormat.setNamedStyle('Bold')

        settings.setFormat(textFormat)

        labeling = QgsVectorLayerSimpleLabeling(settings)
        mem_layer.setLabeling(labeling)
        mem_layer.setLabelsEnabled(True)

        QgsProject.instance().addMapLayers([mem_layer], False)


        mzaNL = QgsLayerTreeLayer(mem_layer)
        
        consulta.insertChildNode(0, mzaNL)

    # O B T E N E R   G E O M E T R I A S
    #Metodo que obtiene las propiedades de la manzana
    def obtenerManzana(self):
        #url del servicio
        url='http://192.168.0.30:91/api/busqueda/secmza/'
        #Obtenemos el sector del combo
        sec = self.dockwidget.comboBox.currentText()#'004'
        #Obtenemos el numero de manzana a traves del combo
        mza = self.dockwidget.comboBoxManzanas.currentText()#'048'
        #Cabecera de la peticion
        headers = {
                'Content-Type': 'application/json'
                }
        
        #Objeto JSON necesario para el servicio
        payload = {"nombre": "eg_manzana", "epsg": 32614,"bbox": False,"pin": "false","geomWKT": None, "epsgGeomWKT": None,"incluirGeom": True,"pagina": 2,"itemsPagina": 2,"properties": {}}
        #Concersion del objeto a JSON
        payload = json.dumps(payload)
        #Mandamos la peticon al servicio
        try:
            response = requests.post(url + sec + '/' + mza, headers = headers, data = payload)
        except requests.exceptions.RequestException:
             raise RuntimeError('Error de servidor')
             return
        
        data = ""
        #Verificamos el estado de la peticion
        if response.status_code == 200:
            data = response.content
        else:
            #En caso de que no sea un 200 mandamos una excepcion
            raise Exception('Error en peticion:\n' + response.text)
        #Retornamos la manzana

        return json.loads(data)#Para obtener el id ['features'][0]['id']

    #Funcion que obtiene todos los prredios a partir de un indice de manzana
    def obtenerPredios(self):
        url='http://192.168.0.30:91/api/busqueda/predios/'
        idMza = self.obtenerManzana()['features'][0]['id']
        headers = {
                'Content-Type': 'application/json'
                }
        payload = {"nombre": "eg_predio", "epsg": 32614,"bbox": False,"pin": "false","geomWKT": None, "epsgGeomWKT": None,"incluirGeom": True,"pagina": 2,"itemsPagina": 2,"properties": {}}

        payload = json.dumps(payload)
        try:

            response = requests.post(url + str(idMza), headers = headers, data = payload)
        except requests.exceptions.RequestException:
             raise RuntimeError('Error de servidor')
             return
        data = ""
        if response.status_code == 200:
            data = response.content
        else:
            raise Exception('Error en peticion:\n' + response.text)

        return json.loads(data)

    #Funcion que obtiene las construcciones a partir de un ID de Manzana
    def obtenerConstrucciones(self):
        url='http://192.168.0.30:91/api/busqueda/construcciones/'
        idMza = self.obtenerManzana()['features'][0]['id']
        headers = {
            'Content-Type': 'application/json'
            }
        payload = {"nombre": "eg_constr", "epsg": 32614,"bbox": False,"pin": "false","geomWKT": None, "epsgGeomWKT": None,"incluirGeom": True,"pagina": 2,"itemsPagina": 2,"properties": {}}

        payload = json.dumps(payload)
        try:
            response = requests.post(url + str(idMza), headers = headers, data = payload)
        except requests.exceptions.RequestException:
             raise RuntimeError('Error de servidor')
             return
        data = ""
        if response.status_code == 200:
            data = response.content
        else:
            raise Exception('Error en peticion:\n' + response.text)

        return json.loads(data)
        
    #Funcion que obtiene los volumenes de las construcciones    
    def obtenerVolConstrucciones(self):
        url='http://192.168.0.30:91/api/busqueda/constr/volum/'
        idMza = self.obtenerManzana()['features'][0]['id']
        headers = {
                'Content-Type': 'application/json'
                }
        payload = {"nombre": "eg_vol", "epsg": 32614,"bbox": False,"pin": "false","geomWKT": None, "epsgGeomWKT": None,"incluirGeom": True,"pagina": 2,"itemsPagina": 2,"properties": {}}

        payload = json.dumps(payload)
        try:
            response = requests.post(url + str(idMza), headers = headers, data = payload)
        except requests.exceptions.RequestException:
             raise RuntimeError('Error de servidor')
             return

        data = ""
        if response.status_code == 200:
            data = response.content
        else:
            raise Exception('Error en peticion:\n' + response.text)

        return json.loads(data)
    
    #Funcion que consume el servicio de Obtener construcciones especiales a partir de un ID de manzana
    def obtenerEspConstrucciones(self):
        url='http://192.168.0.30:91/api/busqueda/constr/esp/'
        idMza = self.obtenerManzana()['features'][0]['id']
        headers = {
                'Content-Type': 'application/json'
                }
        payload = {"nombre": "eg_constresp", "epsg": 32614,"bbox": False,"pin": "false","geomWKT": None, "epsgGeomWKT": None,"incluirGeom": True,"pagina": 2,"itemsPagina": 2,"properties": {}}

        payload = json.dumps(payload)
        try:
            response = requests.post(url + str(idMza), headers = headers, data = payload)
        except requests.exceptions.RequestException:
             raise RuntimeError('Error de servidor')
             return
        data = ""
        if response.status_code == 200:
            data = response.content
        else:
            raise Exception('Error en peticion:\n' + response.text)

        return json.loads(data)

    #Funcion para obtener Capa de referencia de acuerdo a un EgName
    def obtenerCapasDeReferencia(self, egName):
        url='http://192.168.0.30:91/api/busqueda/simple'
        payload = {"nombre": egName, "epsg": 32614,"bbox": False,"pin": False,"geomWKT": None, "epsgGeomWKT": None,"incluirGeom": True,"pagina": None,"itemsPagina": None,"properties": {}}
        payload = json.dumps(payload)
        headers = {
                'Content-Type': 'application/json'
                }
        try:
            response = requests.post(url, headers = headers, data = payload)
        except requests.exceptions.RequestException:
             raise RuntimeError('Error de servidor')
             return 
        if response.status_code == 200:
                data = response.content
        else:
            raise Exception('Error en peticion:\n' + response.text)
        
        return json.loads(data)

    #Funcion para obtener Capa de referencia de acuerdo a un EgName
    def obtenerCapasDeReferencia(self, egName):
        url='http://192.168.0.30:91/api/busqueda/simple'
        payload = {"nombre": egName, "epsg": 32614,"bbox": False,"pin": False,"geomWKT": None, "epsgGeomWKT": None,"incluirGeom": True,"pagina": None,"itemsPagina": None,"properties": {}}
        payload = json.dumps(payload)
        headers = {
                'Content-Type': 'application/json'
                }
        try:
            response = requests.post(url, headers = headers, data = payload)
        except requests.exceptions.RequestException:
             raise RuntimeError('Error de servidor')
             return 
        if response.status_code == 200:
                data = response.content
        else:
            raise Exception('Error en peticion:\n' + response.text)
        
        return json.loads(data)

    # zoom a una capa
    def zoomManzana(self):
    
        # self.canvas = QgsMapCanvas()

        mem_layer = QgsProject.instance().mapLayersByName('manzana')

        if len(mem_layer) != 1:
            raise AttributeError
     
        mem_layer = mem_layer[0]

        if mem_layer == None:
            return

        features = list(mem_layer.getFeatures())
        f = features[0]
        bbox = f.geometry().boundingBox()
        iface.mapCanvas().setExtent(bbox)
        iface.mapCanvas().refresh()

    #Funcion para pintar los predios, manzanas, construcciones, VolConstrucciones, EspConstrucciones
    def pintarCapas(self):
        try:
            #Exception en caso de no hayar token
            autenticado = self.validarAuth()
            if autenticado:
                if self.validateSectoresAndManzanas():
                    #Borramos las features 
                    self.removeFeaturesManzana()
                    self.removeFeaturesPredios()
                    self.removeFeaturesConstrucciones()
                    self.removeFeaturesVolumenConstrucciones()
                    self.removeFeaturesEspConstrucciones()
                        
                    #Repinstamos en la capa
                    self.pintarManzana()
                    self.pintarPredios()
                    print('entra1')
                    self.pintarConstrucciones()
                    print('entra2')
                    self.pintarVolumenConstrucciones()
                    self.pintarEspConstrucciones()
                    
                    #hacer zoom hacia la manzana
                    self.zoomManzana()
            
                else:#En caso de que no se pueda pintar capas mandar mensaje
                    self.createAlert('No existen manzanas', QMessageBox.Critical, 'Capas de consulta')
            elif autenticado == False:
                self.createAlert("Tu inicio de sesion expiro", QMessageBox.Warning, 'Capas de consulta')
        except RuntimeError:
            self.createAlert('Error de servidor: ' + e , QMessageBox.Critical, 'Capas de consulta')
        except AttributeError:
            self.createAlert('Capas No detectadas', QMessageBox.Critical, 'Capas de consulta')
    
                #Funcion que valida que el usuario no haya pintado ya la capa que selecciono
    def pintarCapaReferenciaConValidacion(self):
        try:
            #Verificamos auth
            autenticado = self.validarAuth()
            if autenticado:
                nameCapa = self.dockwidget.comboBoxCapas.currentText()
                #Obtenemos el layer de predios
                print(nameCapa)
                mem_layer = QgsProject.instance().mapLayersByName(nameCapa)

                #Para pintar las Calles como LineString  
                if mem_layer == []:
                    if nameCapa == "Calles":
                        figura = 'LineString'
                        posicion = QgsPalLayerSettings.Line
                    else:
                        figura = 'Polygon'
                        posicion = QgsPalLayerSettings.OrderedPositionsAroundPoint
                    self.pintarCapasReferencia(figura, nameCapa, posicion)
            
            elif autenticado == False:
                self.createAlert("Tu inicio de sesion expiro", QMessageBox.Warning, 'Capas de referencia')
        except RuntimeError:
            self.createAlert('Error de servidor', QMessageBox.Critical, 'Capas de referencia')
        except AttributeError:
            self.createAlert('Capas No detectadas', QMessageBox.Critical, 'Capas de referencia')
             

    #Metodo que crea un elemento QMessageBox
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

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING ActualizacionCatastral"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD ActualizacionCatastral"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&ActualizacionCatastral'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #Funcion que valida la existencia del toekn y de su veracidad
    def validarAuth(self):
         #Exception en caso de no hayar token
        try:
            login = self.autenticacion.autentication()
            if login:
                return True
            else:
                return False                
                
        except ValueError:
            self.createAlert("Inicie sesion", QMessageBox.Critical, 'Sistema cartografico')
            return None

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            autenticado = self.validarAuth()
            if autenticado:
                self.pluginIsActive = True

                #print "** STARTING ActualizacionCatastral"

                # dockwidget may not exist if:
                #    first run of plugin
                #    removed on close (see self.onClosePlugin method)
                if self.dockwidget == None:
                    # Create the dockwidget (after translation) and keep reference
                    self.dockwidget = ActualizacionCatastralDockWidget()

                # carga lista de capas por referencia
                self.capasReferencia = {'eg_sector':'Sectores', 'eg_colonia':'Colonias', 'eg_localidad':'Localidad', 'eg_region':'Region', 'eg_seccion':'Seccion', 'eg_estado':'Estado', 'eg_areavalor':'Area valor', 'eg_calle':'Calles', 'eg_predio':'Predios', 'eg_manzana':'Manzana', 'eg_sector':'Sector'}

                # connect to provide cleanup on closing of dockwidget
                self.dockwidget.closingPlugin.connect(self.onClosePlugin)

                try:

                    #Solicitud de todos los sectores
                    self.getAllSectores()
                    #Obtenemos las manzanas del prier sector
                    self.getAllManzanasBySector()
                    #Obtenemos las capas
                    self.getAllCapas()
                    
                    #Evento de cambio de sectores en el ComboBox
                    self.dockwidget.comboBox.currentIndexChanged.connect(self.getAllManzanasBySector)
                    #Agregado de evento pintar capas
                    self.dockwidget.pushButtonPintar.clicked.connect(self.pintarCapas)
                    #Agregado de evento pintar capa de referencia
                    self.dockwidget.pushButtonCargarCapa.clicked.connect(self.pintarCapaReferenciaConValidacion)

                    # show the dockwidget
                    # TODO: fix to allow choice of dock location
                    self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
                    self.dockwidget.show()
                except RuntimeError:
                    self.pluginIsActive = False
                    self.createAlert('Error de servidor', QMessageBox.Critical, 'Consulta de Capas')

