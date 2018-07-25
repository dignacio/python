# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TopologiaQG3
                                 A QGIS plugin
 TopologiaQG3
                              -------------------
        begin                : 2018-02-22
        git sha              : $Format:%H$
        copyright            : (C) 2018 by TopologiaQG3
        email                : TopologiaQG3
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
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from PyQt5 import QtWidgets
# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
from .TopologiaQG3_dockwidget import TopologiaQG3DockWidget
import os.path

from qgis.core import QgsProject
from .reglasQG3 import Reglas
from qgis.utils import iface
from PyQt5.QtWidgets import QAction, QMessageBox, QTableWidgetItem

class TopologiaQG3:
    """QGIS Plugin Implementation."""

    def __init__(self, iface, ACA):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        self.CFG = None
        self.UTI = None
        self.DFS = None
        self.DBJ = None
        self.ELM = None
        self.DFS = None
        self.ACA = ACA

        #print "** INITIALIZING TopologiaQG3"

        self.pluginIsActive = False
        self.dockwidget = None

        self.dockwidget = TopologiaQG3DockWidget()

        self.reglas = Reglas(self.ACA)

        header = self.dockwidget.tablaReglas.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)

        self.dockwidget.botonValidar.clicked.connect(self.validarTopologiaManual)
        self.dockwidget.botonValidarRef.clicked.connect(self.validarTopologiaManualRef)

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING TopologiaQG3"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING TopologiaQG3"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = TopologiaQG3DockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

            listaR = QSettings().value("reglasTopologicas")

            if len(listaR) > 0:
                self.llenarTablaReglas()

            self.modoDesarrollo = True

            #if self.modoDesarrollo:
            #    self.validarTopologiaManual()
            


    def validarTopologiaManual(self):
 
        self.todoEnOrden = True
        QSettings().setValue("posibleGuardar", "False")

        self.dockwidget.tablaErrores.clearContents()
        self.dockwidget.tablaErrores.setRowCount(0)
        for row in range(0, self.dockwidget.tablaErrores.rowCount()):
            self.dockwidget.tablaErrores.removeRow(row)

        root = QgsProject.instance().layerTreeRoot()

        group = root.findGroup('ERRORES DE TOPOLOGIA')
        if not group is None:
            for child in group.children():
                dump = child.dump()
                id = dump.split("=")[-1].strip()
                QgsProject.instance().removeMapLayer(id)
            root.removeChildNode(group)

        for layer in iface.mapCanvas().layers():
            layer.triggerRepaint()

        root.insertGroup(0, 'ERRORES DE TOPOLOGIA')

        self.obtenerXCapas()

        self.validarPoligonosInvalidos(self.xManzana)
        self.validarPoligonosInvalidos(self.xHoriGeom)
        self.validarPoligonosInvalidos(self.xConst)
        self.validarPoligonosInvalidos(self.xHoriGeom)
        self.validarPoligonosInvalidos(self.xVert)
        
        if self.todoEnOrden:
            self.reglasManuales()

            if self.todoEnOrden: #Topologia en orden
                self.UTI.mostrarAlerta("La topologia es correcta", QMessageBox().Information, "Comprobador de topologia")
                QSettings().setValue("posibleGuardar", "True")
                root = QgsProject.instance().layerTreeRoot()
                #Si todo esta bien, borramos el grupo de errores
                group = root.findGroup('ERRORES DE TOPOLOGIA')
                if not group is None:
                    for child in group.children():
                        dump = child.dump()
                        id = dump.split("=")[-1].strip()
                        QgsProject.instance().removeMapLayer(id)
                    root.removeChildNode(group)

                if self.CMS.dlg.isVisible():
                   # self.UTI.mostrarAlerta("Ahora puedes integrar", QMessageBox().Information, "Comprobador de topologia")
                    self.preguntarGuardarInte()
                else:
                    self.preguntarGuardar()
                    


            else: #Cuando hay errrpres
                self.UTI.mostrarAlerta("Se han detectado errores de topologia", QMessageBox().Critical, "Comprobador de topologia")
        else:
            self.UTI.mostrarAlerta("El comprobador de topologia no puede proceder hasta que se corrijan las geometrias invalidas", QMessageBox().Critical, "Comprobador de topologia")


#############################################################################################################

    def preguntarGuardar(self):
        mensaje = "La topologia es correcta, deseas guardar los cambios de las capas de consulta?"
        respuesta = QMessageBox.question(iface.mainWindow(), "Guardar Cambios", mensaje, QMessageBox.Yes, QMessageBox.No)

        if respuesta == QMessageBox.Yes:
            self.UTI.guardarCambios()

################################################################################################################
    
    def preguntarGuardarRef(self):
        mensaje = "La topologia es correcta, deseas guardar los cambios de la capa de referencia?"
        respuesta = QMessageBox.question(iface.mainWindow(), "Guardar Cambios", mensaje, QMessageBox.Yes, QMessageBox.No)

        if respuesta == QMessageBox.Yes:
            self.ACA.guardarCapaReferencia()

####################################################################################################################

    def preguntarGuardarInte(self):
        mensaje = "La topologia es correcta, deseas integrar la carta a la base de datos?"
        respuesta = QMessageBox.question(iface.mainWindow(), "Integrar carta", mensaje, QMessageBox.Yes, QMessageBox.No)

        if respuesta == QMessageBox.Yes:
            self.CMS.integrar()

#################################################################################################################
    def validarTopologiaManualRef(self):
    
        if self.ACA.capaEnEdicion != '':

            self.todoEnOrdenRef = True
            QSettings().setValue("posibleGuardarRef", "False")

            self.dockwidget.tablaErrores.clearContents()
            self.dockwidget.tablaErrores.setRowCount(0)
            for row in range(0, self.dockwidget.tablaErrores.rowCount()):
                self.dockwidget.tablaErrores.removeRow(row)

            root = QgsProject.instance().layerTreeRoot()

            group = root.findGroup('ERRORES DE TOPOLOGIA')
            if not group is None:
                for child in group.children():
                    dump = child.dump()
                    id = dump.split("=")[-1].strip()
                    QgsProject.instance().removeMapLayer(id)
                root.removeChildNode(group)

            for layer in iface.mapCanvas().layers():
                layer.triggerRepaint()

            root.insertGroup(0, 'ERRORES DE TOPOLOGIA')

            if self.siendoEditada('Estado'):
                
                self.validarPoligonosInvalidosRef('Estado')

            elif self.siendoEditada('Region Catastral'):
                
                self.validarPoligonosInvalidosRef('Region Catastral')
                self.validarPoligonosInvalidosRef('Estado')

            elif self.siendoEditada('Municipios'):
                self.validarPoligonosInvalidosRef('Municipios')
                self.validarPoligonosInvalidosRef('Region Catastral')

            elif self.siendoEditada('Secciones'):
                self.validarPoligonosInvalidosRef('Secciones')
                self.validarPoligonosInvalidosRef('Municipios')

            elif self.siendoEditada('Localidades'):
                self.validarPoligonosInvalidosRef('Localidades')
                self.validarPoligonosInvalidosRef('Secciones')

            elif self.siendoEditada('Sectores'):
                self.validarPoligonosInvalidosRef('Sectores')
                self.validarPoligonosInvalidosRef('Localidades')

            elif self.siendoEditada('Calles'):
                self.validarPoligonosInvalidosRef('Calles')

            elif self.siendoEditada('Colonias'):
                self.validarPoligonosInvalidosRef('Colonias')

            elif self.siendoEditada('Codigo Postal'):
                self.validarPoligonosInvalidosRef('Codigo Postal')

            elif self.siendoEditada('Zona Uno'):
                self.validarPoligonosInvalidosRef('Zona Uno')

            elif self.siendoEditada('Zona Dos'):
                self.validarPoligonosInvalidosRef('Zona Dos')

            elif self.siendoEditada('Area de Valor'):
                self.validarPoligonosInvalidosRef('Area de Valor')

            if self.todoEnOrdenRef:
                self.reglasManualesRef()

                if(self.todoEnOrdenRef): #Topologia en orden
                    self.UTI.mostrarAlerta("La topologia es correcta", QMessageBox().Information, "Comprobador de topologia")
                    QSettings().setValue("posibleGuardarRef", "True")
                    root = QgsProject.instance().layerTreeRoot()
                    #Si todo esta bien, borramos el grupo de errores
                    group = root.findGroup('ERRORES DE TOPOLOGIA')
                    if not group is None:
                        for child in group.children():
                            dump = child.dump()
                            id = dump.split("=")[-1].strip()
                            QgsProject.instance().removeMapLayer(id)
                        root.removeChildNode(group)
                    self.preguntarGuardarRef()
                else: #Cuando hay errrpres
                    self.UTI.mostrarAlerta("Se han detectado errores de topologia", QMessageBox().Critical, "Comprobador de topologia")
            else:
                self.UTI.mostrarAlerta("El comprobador de topologia no puede proceder hasta que se corrijan las geometrias invalidas", QMessageBox().Critical, "Comprobador de topologia")

        else:
            self.UTI.mostrarAlerta("Debes tener en edicion una capa de referencia para validar la topologia de referencia", QMessageBox().Critical, "Comprobador de topologia")


#############################################################################################################


    def validarTopologiaJson(self):

        
        self.todoEnOrden = True
        self.poligonosValidos = True
        QSettings().setValue("posibleGuardar", "True")

        self.dockwidget.tablaErrores.clearContents()
        self.dockwidget.tablaErrores.setRowCount(0)
        for row in range(0, self.dockwidget.tablaErrores.rowCount()):
            self.dockwidget.tablaErrores.removeRow(row)

        root = QgsProject.instance().layerTreeRoot()

        for layer in iface.mapCanvas().layers():
            layer.triggerRepaint()


        group = root.findGroup('ERRORES DE TOPOLOGIA')
        if not group is None:
            for child in group.children():
                dump = child.dump()
                id = dump.split("=")[-1].strip()
                QgsProject.instance().removeMapLayer(id)
            root.removeChildNode(group)

        root.insertGroup(0, 'ERRORES DE TOPOLOGIA')

        todasCapas = iface.mapCanvas().layers()
        for capa in todasCapas:
            if capa.isEditable():
                self.validarPoligonosInvalidos(capa.name())
        
        if self.poligonosValidos:
            listaDeReglas = QSettings().value("reglasTopologicas")

            for regla in listaDeReglas: #Obtenemos los parametros de las reglas y ejecutamos
                nombreRegla = regla[0]
                capa1 = regla[1]
                capa2 = regla[2]

                if nombreRegla == "invalidos":
                    self.validarPoligonosInvalidos(capa1)
                elif nombreRegla == "intersecciones":
                    self.validarIntersecciones(capa1, capa2)
                elif nombreRegla == "cobertura":
                    self.validarCobertura(capa1, capa2)
                elif nombreRegla == "inclusion":
                    self.validarInclusion(capa1, capa2)
                elif nombreRegla == "anillos":
                    self.validarAnillos(capa1)
                elif nombreRegla == "multipartes":
                    self.validarMultipartes(capa1)
                elif nombreRegla == "duplicados":
                    self.validarDuplicados(capa1)
                elif nombreRegla == "overlaps":
                    self.validarOverlapLineas(capa1)
                elif nombreRegla == "noCompartido":
                    self.validarCompartido(capa1, capa2)
                elif nombreRegla == "tocar":
                    self.validarTocar(capa1, capa2)

            if(self.todoEnOrden): #Topologia en orden
                self.UTI.mostrarAlerta("La topologia es correcta", QMessageBox().Information, "Comprobador de topologia")
                QSettings().setValue("posibleGuardar", "True")
                root = QgsProject.instance().layerTreeRoot()
                #Si todo esta bien, borramos el grupo de errores
                group = root.findGroup('ERRORES DE TOPOLOGIA')
                if not group is None:
                    for child in group.children():
                        dump = child.dump()
                        id = dump.split("=")[-1].strip()
                        QgsProject.instance().removeMapLayer(id)
                    root.removeChildNode(group)
            else: #Cuando hay errrpres
                self.UTI.mostrarAlerta("Se han detectado errores de topologia", QMessageBox().Critical, "Comprobador de topologia")



#############################################################################################################

    def validarIntersecciones(self, nombreCapa1, nombreCapa2):
        
        self.reglas.validarIntersecciones(nombreCapa1, nombreCapa2)
        self.llenaTablaErrores()

###############################################################################################################

    def validarCobertura(self, nombreBase, nombreCobertura):
        
        self.reglas.validarCobertura(nombreBase, nombreCobertura)
        self.llenaTablaErrores()

###############################################################################################################

    def validarInclusion(self, nombreObjetos, nombreContenedor):
        
        self.reglas.validarInclusion(nombreObjetos, nombreContenedor)
        self.llenaTablaErrores()

###################################################################################################################

    def validarPoligonosInvalidos(self, nombreCapa):
        
        self.reglas.validarPoligonosInvalidos(nombreCapa)
        self.llenaTablaErrores()

#####################################################################################################################

    def validarAnillos(self, nombreCapa):
        
        self.reglas.validarAnillos(nombreCapa)
        self.llenaTablaErrores()

######################################################################################################################

    def validarMultipartes(self, nombreCapa):
        
        self.reglas.validarMultipartes(nombreCapa)
        self.llenaTablaErrores()

#########################################################################################################################

    def validarDuplicados(self, nombreCapa):
        
        self.reglas.validarDuplicados(nombreCapa)
        self.llenaTablaErrores()

###########################################################################################################################

    def validarOverlapLineas(self, nombreCapa):
        
        self.reglas.validarOverlapLineas(nombreCapa)
        self.llenaTablaErrores()

############################################################################################################################

    def validarCompartido(self, nombreObj, nombreBase):
        
        self.reglas.validarCompartido(nombreObj, nombreBase)
        self.llenaTablaErrores()
##############################################################################################################################

    def validarTocar(self, nombreObj, nombreBase):
        
        self.reglas.validarTocar(nombreObj, nombreBase)
        self.llenaTablaErrores()

###############################################################################################################################

    def validarPuntoEnPoligono(self, nombrePunto, nombrePoligono):
        self.reglas.validarPuntoEnPoligono(nombrePunto, nombrePoligono)
        self.llenaTablaErrores()

###############################################################################################################################

    def validarToqueCompartido(self, nombreObj, nombreBase):
            self.reglas.validarToqueCompartido(nombreObj, nombreBase)
            self.llenaTablaErrores()

###############################################################################################################################

    def validarPoligonosDuplicados(self, nombreCapa):
        
        self.reglas.validarPoligonosDuplicados(nombreCapa)
        self.llenaTablaErrores()

#############################################################################################################################

    def validarSoloUnPunto(self, nombrePunto, nombrePoligono):
        self.reglas.validarSoloUnPunto(nombrePunto, nombrePoligono)
        self.llenaTablaErrores()

################################################################################################################################

    def validarAlMenosUnPunto(self, nombrePunto, nombrePoligono):
        self.reglas.validarAlMenosUnPunto(nombrePunto, nombrePoligono)
        self.llenaTablaErrores()

####################################################################################################################################

    def llenaTablaErrores(self):
        header = self.dockwidget.tablaErrores.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        if self.reglas.cuentaError > 0:
            self.todoEnOrden = False
            self.todoEnOrdenRef = False
            self.dockwidget.tablaErrores.insertRow(self.dockwidget.tablaErrores.rowCount())
            item = QTableWidgetItem(self.reglas.stringError)
            self.dockwidget.tablaErrores.setItem(self.dockwidget.tablaErrores.rowCount()-1, 0 , item)
        
###############################################################################################################################

    def validarInclusionRef(self, nombreObjetos, nombreContenedor):
    
        self.reglas.validarInclusionRef(nombreObjetos, nombreContenedor)
        self.llenaTablaErrores()

##########################################################################

    def validarPoligonosInvalidosRef(self, nombreCapa):
        
        self.reglas.validarPoligonosInvalidosRef(nombreCapa)
        self.llenaTablaErrores()

####################################################################################

    def validarCamposRef(self, nombreCapa):
        
        self.reglas.validarCamposRef(nombreCapa)
        self.llenaTablaErrores()

####################################################################################

    def validarInterseccionesRef(self, nombreCapa1, nombreCapa2):
        
        self.reglas.validarInterseccionesRef(nombreCapa1, nombreCapa2)
        self.llenaTablaErrores()

################################################################################################

    def validarInscritasEnPrediosIrregulares(self):
        
        self.reglas.validarInscritasEnPrediosIrregulares()
        self.llenaTablaErrores()

##############################################################################################


    def validarAreasInscritasCuadraditas(self):
        
        self.reglas.validarAreasInscritasCuadraditas()
        self.llenaTablaErrores()

##############################################################################################

    def validarCantidadAreasInscritas(self):
        
        self.reglas.validarCantidadAreasInscritas()
        self.llenaTablaErrores()

###############################################################################################

    def validarLongitudCampo(self, capa, campo, longitud):
        
        self.reglas.validarLongitudCampo(capa, campo, longitud)
        self.llenaTablaErrores()

####################################################################################

    def validarCampoNoNulo(self, capa, campo):
        
        self.reglas.validarCampoNoNulo(capa, campo)
        self.llenaTablaErrores()

###################################################################################

    def validarCampoNoNuloDoble(self, capa, campo1, campo2):
        
        self.reglas.validarCampoNoNuloDoble(capa, campo1, campo2)
        self.llenaTablaErrores()

##########################################################################################

    def validarCamposDuplicados(self, capaContenedor, capaObjeto, campo):
        
        self.reglas.validarCamposDuplicados(capaContenedor, capaObjeto, campo)
        self.llenaTablaErrores()


##############################################################################################


    def llenarTablaReglas(self):

        listaDeReglas = QSettings().value("reglasTopologicas") #Obtenemos la lista de reglas
        

        self.dockwidget.tablaReglas.clearContents() #Borramos el contenido de la tabla de relgas
        self.dockwidget.tablaReglas.setRowCount(0) 
        for row in range(0, self.dockwidget.tablaReglas.rowCount()): #Borrams todos los renglones de la tabla
            self.dockwidget.tablaReglas.removeRow(row) 

        for regla in listaDeReglas: #Obtenemos los parametros de las reglas y ejecutamos
            nombreRegla = regla[0] #Obtenemos el identificador de la regla
            capa1 = regla[1] #Obtenemos el nombre de la primera capa involucrada
            capa2 = regla[2] #Obtenemos el nombre de la segunda capa involucrada

            reglaRow = "" #Este string contiene lo que vamos a meter en la tabla de reglas

            # Checamos el nombre de la regla para ver que string vamos a agregar a la tabla
            if nombreRegla == "invalidos": 
                reglaRow = "No se permiten poligonos invalidos en la capa " + capa1
            elif nombreRegla == "intersecciones":
                reglaRow = "Las geometrias de la capa " + capa1 + " no deben solaparse con las geometrias de la capa " + capa2
            elif nombreRegla == "cobertura":
                reglaRow = "Las geometrias de la capa " + capa1 + " deben estar totalmente cubiertas por geometrias de la capa " + capa2
            elif nombreRegla == "inclusion":
                reglaRow = "Las geometrias de la capa " + capa1 + " deben estar totalmente incluidas en geometrias de la capa " + capa2
            elif nombreRegla == "multigeometrias":
                reglaRow = "No se permiten multigeometrias (anillos) en la capa " + capa1
            elif nombreRegla == "multipartes":
                reglaRow = "No se permiten geometrias multiparte en la capa " + capa1
            elif nombreRegla == "duplicados":
                reglaRow = "No se permiten geometrias duplicadas en la capa " + capa1
            elif nombreRegla == "overlaps":
                reglaRow = "Las lineas de la capa " + capa1 + " no deben solaparse consigo mismas"
            elif nombreRegla == "noCompartido":
                reglaRow = "Las geometrias de la capa " + capa1 + " no deben estar incluidas en mas de una geometria de la capa " + capa2
            elif nombreRegla == "tocar":
                reglaRow = "Las geometrias de la capa " + capa1 + " deben tocar exactamente a una geometria de la capa " +  capa2

            self.dockwidget.tablaReglas.insertRow( self.dockwidget.tablaReglas.rowCount())
            item = QTableWidgetItem(reglaRow)
            self.dockwidget.tablaReglas.setItem(self.dockwidget.tablaReglas.rowCount()-1, 0 , item)

######################################################################################################################

    def reglasManuales(self):
        
        self.obtenerXCapas()
        
        self.validarIntersecciones(self.xPredGeom, self.xPredGeom)
        self.validarIntersecciones(self.xManzana, self.xManzana)
        self.validarIntersecciones(self.xHoriGeom, self.xHoriGeom)
        self.validarIntersecciones(self.xHoriGeom, self.xVert)
        
        self.validarCobertura(self.xManzana, self.xPredGeom)
        
        self.validarInclusion(self.xPredGeom, self.xManzana)
        
        self.validarAnillos(self.xPredGeom)
        self.validarAnillos(self.xManzana)
        self.validarAnillos(self.xVert)
        self.validarAnillos(self.xHoriGeom)
    
        self.validarMultipartes(self.xManzana)
        self.validarMultipartes(self.xPredGeom)
        self.validarMultipartes(self.xConst)
        self.validarMultipartes(self.xHoriGeom)
        self.validarMultipartes(self.xVert)
        
        self.validarDuplicados(self.xCvesVert)
        self.validarDuplicados(self.xPredNum)
        self.validarDuplicados(self.xVert)
        
        self.validarToqueCompartido(self.xConst, self.xPredGeom)
        
        self.validarPuntoEnPoligono(self.xCvesVert, self.xVert)
        self.validarPuntoEnPoligono(self.xPredNum, self.xPredGeom)
        self.validarPuntoEnPoligono(self.xHoriNum, self.xHoriGeom)

        self.validarSoloUnPunto(self.xPredNum, self.xPredGeom)
        self.validarSoloUnPunto(self.xHoriNum, self.xHoriGeom)

        self.validarAlMenosUnPunto(self.xCvesVert, self.xVert)

        self.validarPoligonosDuplicados(self.xConst)
        
        self.validarInscritasEnPrediosIrregulares()
        self.validarAreasInscritasCuadraditas()
        self.validarCantidadAreasInscritas()
        
        self.validarLongitudCampo(self.xManzana, 'clave', 3)
        self.validarLongitudCampo(self.xPredGeom, 'clave', 5)
        self.validarLongitudCampo(self.xHoriGeom, 'clave', 6)
        self.validarLongitudCampo(self.xVert, 'clave', 2)
        self.validarLongitudCampo(self.xCvesVert, 'clave', 4)

        self.validarCampoNoNulo(self.xManzana, 'clave')
        self.validarCampoNoNulo(self.xPredGeom, 'clave')
        self.validarCampoNoNulo(self.xPredNum, 'numExt')
        self.validarCampoNoNulo(self.xConst, 'nom_volumen')
        self.validarCampoNoNuloDoble(self.xConst, 'num_niveles', 'cve_const_esp')
        self.validarCampoNoNulo(self.xHoriGeom, 'clave')
        self.validarCampoNoNulo(self.xHoriNum, 'num_ofi')
        self.validarCampoNoNulo(self.xVert, 'clave')
        self.validarCampoNoNulo(self.xCvesVert, 'clave')

        self.validarCamposDuplicados(self.xManzana, self.xPredGeom, 'clave')
        self.validarCamposDuplicados(self.xPredGeom, self.xConst, 'nom_volumen')

        self.printearErrores()

#############################################################################################################

    def reglasManualesRef(self):
        
        
        if self.siendoEditada('Sectores'):
            self.validarInclusionRef('Sectores', 'Localidades')
        elif self.siendoEditada('Localidades'):
            self.validarInclusionRef('Localidades', 'Secciones')
        elif self.siendoEditada('Secciones'):
            self.validarInclusionRef('Secciones', 'Municipios')
        elif self.siendoEditada('Municipios'):
            self.validarInclusionRef('Municipios', 'Region Catastral')
        elif self.siendoEditada('Region Catastral'):
            self.validarInclusionRef('Region Catastral', 'Estado')
        
        capaTraducida = self.ACA.traducirIdCapa(self.ACA.capaEnEdicion)
        #print('capatraducida: ', capaTraducida.name())
        self.validarCamposRef(capaTraducida)
        self.validarInterseccionesRef(capaTraducida, capaTraducida)

        #else:
        #    QSettings().setValue('posibleGuardarRef', 'True')
        #    self.UTI.mostrarAlerta("No tienes cargada ninguna capa de referencia", QMessageBox().Information, "Comprobador de topologia")

################################################################################################

    def siendoEditada(self, nombreCapa):
        #print('nombreCapa', self.ACA.obtenerIdCapa(nombreCapa))
        #print('refedicion', QSettings().value("capaRefEdicion"))
        return self.ACA.obtenerIdCapa(nombreCapa) == QSettings().value("capaRefEdicion")


###########################################################################

    def obtenerXCapas(self):
        xMan = QSettings().value('xManzana')
        xPredG = QSettings().value('xPredGeom')
        xPredN = QSettings().value('xPredNum')
        xCon = QSettings().value('xConst')
        xHoriG = QSettings().value('xHoriGeom')
        xHoriN = QSettings().value('xHoriNum')
        xVe = QSettings().value('xVert')
        xCv = QSettings().value('xCvesVert')

        self.xManzana = QgsProject.instance().mapLayer(xMan)
        self.xPredGeom = QgsProject.instance().mapLayer(xPredG)
        self.xPredNum = QgsProject.instance().mapLayer(xPredN)
        self.xConst = QgsProject.instance().mapLayer(xCon)
        self.xHoriGeom = QgsProject.instance().mapLayer(xHoriG)
        self.xHoriNum = QgsProject.instance().mapLayer(xHoriN)
        self.xVert = QgsProject.instance().mapLayer(xVe)
        self.xCvesVert = QgsProject.instance().mapLayer(xCv)

##################################################################################################

    def printearErrores(self):

        manzanasTotales = self.xManzana.featureCount()
        prediosTotales = self.xPredGeom.featureCount()
        constTotales = self.xConst.featureCount()

        manzanasMalas = len(self.reglas.manzanasMalas)
        prediosMalos = len(self.reglas.prediosMalos)
        construMalas = len(self.reglas.constMalas)

        manzanasBuenas = manzanasTotales - manzanasMalas
        prediosBuenos = prediosTotales - prediosMalos
        constBuenas = constTotales - construMalas

        self.dockwidget.tablaComp.clearContents()
        self.dockwidget.tablaComp.setRowCount(0)
            
        for row in range(0, self.dockwidget.tablaComp.rowCount()):        
            self.dockwidget.tablaComp.removeRow(row) 

        
        #Manzana
        self.dockwidget.tablaComp.insertRow(0)
        item = QtWidgets.QTableWidgetItem(str('Manzanas'))
        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.dockwidget.tablaComp.setItem(0, 0 , item)

        item = QtWidgets.QTableWidgetItem(str(manzanasTotales))
        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.dockwidget.tablaComp.setItem(0, 1 , item)

        item = QtWidgets.QTableWidgetItem(str(manzanasBuenas))
        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.dockwidget.tablaComp.setItem(0, 2 , item)

        item = QtWidgets.QTableWidgetItem(str(manzanasMalas))
        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.dockwidget.tablaComp.setItem(0, 3 , item)
        #Predios
        self.dockwidget.tablaComp.insertRow(1)
        item = QtWidgets.QTableWidgetItem(str('Predios'))
        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.dockwidget.tablaComp.setItem(1, 0 , item)

        item = QtWidgets.QTableWidgetItem(str(prediosTotales))
        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.dockwidget.tablaComp.setItem(1, 1 , item)

        item = QtWidgets.QTableWidgetItem(str(prediosBuenos))
        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.dockwidget.tablaComp.setItem(1, 2 , item)

        item = QtWidgets.QTableWidgetItem(str(prediosMalos))
        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.dockwidget.tablaComp.setItem(1, 3 , item)
        #Construcciones
        self.dockwidget.tablaComp.insertRow(2)
        item = QtWidgets.QTableWidgetItem(str('Construcciones'))
        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.dockwidget.tablaComp.setItem(2, 0 , item)

        item = QtWidgets.QTableWidgetItem(str(constTotales))
        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.dockwidget.tablaComp.setItem(2, 1 , item)

        item = QtWidgets.QTableWidgetItem(str(constBuenas))
        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.dockwidget.tablaComp.setItem(2, 2 , item)

        item = QtWidgets.QTableWidgetItem(str(construMalas))
        item.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
        self.dockwidget.tablaComp.setItem(2, 3 , item)


        #print('----TOTALES----')
        #print('Manzanas totales', manzanasTotales)
        #print('predios totales', prediosTotales)
        #rint('constru totales', constTotales)
        #print('----BUENOS----')
        #print('Manzanas buenos', manzanasBuenas)
        #print('predios buenos', prediosBuenos)
        #print('constru buenos', constBuenas)
        #print('----MALOS----')
        #print('Manzanas malas', manzanasMalas)
        #print('predios malas', prediosMalos)
        #print('constru malas', construMalas)

        self.reglas.manzanasMalas = []
        self.reglas.prediosMalos = []
        self.reglas.constMalas = []