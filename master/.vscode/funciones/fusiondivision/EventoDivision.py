
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, QSize
from PyQt5.QtGui import QIcon, QColor, QCursor, QPixmap
from PyQt5.QtWidgets import QAction, QWidget,QVBoxLayout, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem
from PyQt5 import QtWidgets
from PyQt5 import QtCore
# Initialize Qt resources from file resources.py
from qgis.core import *
from qgis.utils import iface, loadPlugin, startPlugin, reloadPlugin
from qgis.gui import QgsLayerTreeView, QgsMapToolEmitPoint, QgsMapTool, QgsRubberBand, QgsVertexMarker

import os.path
import os, json, requests, sys
from osgeo import ogr, osr
from random import randint

class EventoDivision(QgsMapTool):   
    def __init__(self, canvas, pluginM):
        QgsMapTool.__init__(self, canvas)
        #Asignacion inicial
        self.canvas = canvas
        self.pluginM = pluginM
        self.modoDividir = False
        self.modoEliminar = False
        self.modoEditar = False
        self.moviendoVertice = False

        self.relaciones = {}
        self.punteroRelaciones = 0

        self.relaciones[self.punteroRelaciones] = RelacionRubberGeom(self.crearNuevoRubberLinea(), None)
        
        self.rubberPunto = QgsRubberBand(self.canvas, QgsWkbTypes.PointGeometry)
        self.rubberPunto.setFillColor(QColor(0,0,0,0))
        self.rubberPunto.setStrokeColor(QColor(255,0,0,255))
        self.rubberPunto.setWidth(6)

        self.primerClick = False
        self.snapper = self.canvas.snappingUtils()
        self.listaPuntosLineaTemp = []
        self.cuentaClickLinea = 0
        self.relacionEnEdicion = -1
        

#--------------------------------------------------------------------------------------------

    def canvasPressEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        startingPoint = QtCore.QPoint(x,y)
        trans = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        posTemp = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        if self.modoDividir: # ----- Modo Dividir ---- #
            if event.buttons() == Qt.LeftButton: 
                
                self.puntoLineaTemp = self.toMapCoordinates(event.pos())
                geoTemp = QgsPoint(trans.x(),trans.y())
                self.cuentaClickLinea += 1

                puntoSnap = self.snapCompleto(startingPoint)
                if puntoSnap != None: #Cuando tenemos snap ------------#
                    
                    self.listaPuntosLineaTemp.append(puntoSnap)
                    self.isEmittingPoint = True
                    marcador = self.crearNuevoMarcaVert()
                    self.relaciones[self.punteroRelaciones].marcadores.append(marcador)
                    marcador.setCenter(puntoSnap)
                else: #Cuando no tenemos snap ------------- #

                    self.listaPuntosLineaTemp.append(self.puntoLineaTemp)
                    self.isEmittingPoint = True
                    marcador = self.crearNuevoMarcaVert()
                    self.relaciones[self.punteroRelaciones].marcadores.append(marcador)
                    marcador.setCenter(self.puntoLineaTemp)

                if not self.primerClick:
                    self.primerClick = True

            if event.buttons() == Qt.RightButton: #Click derecho
                self.primerClick = False

                if self.cuentaClickLinea >= 2: #Cuando son mas de dos puntos
                    
                    self.isEmittingPoint = False
                    self.cuentaClickLinea = 0
                    self.primerClick = False

                    self.relaciones[self.punteroRelaciones].rubber.reset(QgsWkbTypes.LineGeometry) #Vaciamos el rubber

                    rango = len(self.listaPuntosLineaTemp) - 1 #Agregamos todos los puntos al rubber excepto el ultimo
                    for x in range(0, rango):
                        punto = self.listaPuntosLineaTemp[x]
                        self.relaciones[self.punteroRelaciones].rubber.addPoint(punto, True)
                    
                    geometriaR = QgsGeometry( self.relaciones[self.punteroRelaciones].rubber.asGeometry()) #Ponemos la geometria en la relacion
                    self.relaciones[self.punteroRelaciones].geom = geometriaR
                    
                    vertices = self.obtenerVertices(geometriaR) #Obtenemos los vertices de la geometria
                    
                    self.relaciones[self.punteroRelaciones].rubber.reset(QgsWkbTypes.LineGeometry) #Vaciamos el rubber

                    for vertice in vertices: #Ponemos los vertices en el rubber
                        self.relaciones[self.punteroRelaciones].rubber.addPoint(QgsPointXY(vertice.x(), vertice.y()), True)
                        

                    self.relaciones[self.punteroRelaciones].rubber.show()
                    self.listaPuntosLineaTemp = []
                    
                    self.punteroRelaciones += 1 #Agregamos otro Rubber
                    self.relaciones[self.punteroRelaciones] = RelacionRubberGeom(self.crearNuevoRubberLinea(), None)

                else:
                    self.relaciones[self.punteroRelaciones].rubber.reset(QgsWkbTypes.LineGeometry)
                    self.listaPuntosLineaTemp = []
                    self.relaciones[self.punteroRelaciones].geom = None


        elif self.modoEliminar: #-------Modo Elimina-------------#
            if event.buttons() == Qt.LeftButton: 
                geomClick = QgsGeometry(QgsGeometry.fromPointXY(posTemp))
                bufferClick = geomClick.buffer(0.25, 1)
                
                relacion = self.obtenerRelacionCercana(bufferClick)
                if relacion != None:
                    relacion.rubber.reset(QgsWkbTypes.LineGeometry)
                    relacion.geom = None
                    relacion.vaciarMarcadores()

        elif self.modoEditar: #--------------Modo Editar---------#
            geomClick = QgsGeometry(QgsGeometry.fromPointXY(posTemp))
            bufferClick = geomClick.buffer(0.25, 1)
            relacion = self.obtenerRelacionCercana(bufferClick)

            if event.buttons() == Qt.LeftButton: #---------Click Izquierdo ------#
                
                if not self.moviendoVertice: #Cuando NO estamos moviendo un vertice y buscamos mover uno
                    
                    if relacion != None:

                        relacion.rubber.setStrokeColor(QColor(255,170,0,255))
                        iface.mapCanvas().refresh()
                        vertices = self.obtenerVertices(relacion.geom)
                        verticeSeleccionado = None
                        for vertice in vertices: #Aqui buscamos el vertice cercano al click
                            puntoXY = QgsPointXY(vertice.x(), vertice.y())
                            geomVertice = QgsGeometry(QgsGeometry.fromPointXY(puntoXY)).buffer(2.25, 1)
                            if geomVertice.intersects(bufferClick):
                                verticeSeleccionado = vertice
                                break

                        if verticeSeleccionado != None: #aqui tenemos ya un vertice jalando para arrastrase
                            self.listaPuntosLineaTemp = []
                            self.indiceSeleccionado = vertices.index(vertice)
                            self.moviendoVertice = True
                            for vertice in vertices:
                                puntoXY = QgsPointXY(vertice.x(), vertice.y())
                                self.listaPuntosLineaTemp.append(puntoXY)
                                
                            print(self.indiceSeleccionado)
                else: #Cuando estamos moviendo un vertice y queremos soltarlo
                    self.moviendoVertice = False
                    rel = self.relaciones[self.relacionEnEdicion]
                    rel.geom = rel.rubber.asGeometry()
                    rel.rubber.setStrokeColor(QColor(0,62,240,255))
                    self.punteroRelaciones = len(self.relaciones)
                    self.relaciones[self.punteroRelaciones] = RelacionRubberGeom(self.crearNuevoRubberLinea(), None)
                    self.listaPuntosLineaTemp = []
                    self.pluginM.VentanaAreas.close()
                    iface.mapCanvas().refresh()

            elif event.buttons() == Qt.RightButton: #--------Click Derecho -----# Para agregar vertices personales
                
                if relacion != None:
                    inter = bufferClick.intersection(relacion.geom.buffer(0.000004, 1)) #Checamos la interseccion con la linea a editar
                    c = inter.centroid().asPoint() #Obtenemos el centroide, aqui se pintara el vertice

                    vertices1 = self.obtenerVertices(relacion.geom) #Obtenemos todos los vertices acutales

                    rango = len(vertices1)

                    posiblesX = []
                    for x in range(0, rango-1): #Recorremos todos los vertices
                        v1 = vertices1[x] #Punto izqueirdo
                        v2 = vertices1[x+1] #punto derecho
                        par = (v1, v2)
                        
                        if v1.x() <= v2.x(): #Cuando el primer punto esta a la izquierda
                            if c.x() >= v1.x() and c.x() <= v2.x():
                                posiblesX.append(par)
                        else: #Cuando el primer punto esta a la derecha
                            if c.x() <= v1.x() and c.x() >= v2.x():
                                posiblesX.append(par)

                    
                    for pa in posiblesX: #Checamos todos los posibles que se encuentren en el eje X
                        v1 = pa[0]
                        v2 = pa[1]
                        if v1.y() <= v2.y(): #Cuando el primer punto esta abajo
                            if c.y() >= v1.y() and c.y() <= v2.y():
                                salidaY = pa
                                break
                        else: #Cuando esta arriba
                            if c.y() <= v1.y() and c.y() >= v2.y():
                                salidaY = pa
                                break

                    indiceI = vertices1.index(salidaY[0])
                    indiceD = vertices1.index(salidaY[1])

                    vertices2 = []
                    relacion.vaciarMarcadores()
                    for x in range(0, rango): #Generamos lista d epuntos que incluyan el nuevo
                        if x == indiceD:

                            vertices2.append(c)
                            nuevo = self.crearNuevoMarcaVert()
                            centroM = QgsPointXY(c.x(),c.y())
                            nuevo.setCenter(centroM)
                            relacion.marcadores.append(nuevo)
                            
                            vertices2.append(vertices1[x])
                            nuevo = self.crearNuevoMarcaVert()
                            centroM = QgsPointXY(vertices1[x].x(),vertices1[x].y())
                            nuevo.setCenter(centroM)
                            relacion.marcadores.append(nuevo)

                        else: 
                            vertices2.append(vertices1[x])
                            nuevo = self.crearNuevoMarcaVert()
                            centroM = QgsPointXY(vertices1[x].x(),vertices1[x].y())
                            nuevo.setCenter(centroM)
                            relacion.marcadores.append(nuevo)

                    relacion.rubber.reset(QgsWkbTypes.LineGeometry)

                    for punto in vertices2: #Regeneramos el rubber
                        puntoXY = QgsPointXY(punto.x(),punto.y())
                        relacion.rubber.addPoint(puntoXY, True)

                    relacion.geom = relacion.rubber.asGeometry()

#-----------------------------------------------------------------------


    def canvasMoveEvent(self, event):

        x = event.pos().x()
        y = event.pos().y()
        startingPoint = QtCore.QPoint(x,y)
        posTemp = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        
        if self.modoDividir:
            self.relaciones[self.punteroRelaciones].rubber.reset(QgsWkbTypes.LineGeometry)
            self.rubberPunto.reset(QgsWkbTypes.PointGeometry)
            puntoSnap = self.snapCompleto(startingPoint)

            if puntoSnap != None:

                puntoSnapXY = QgsPointXY(puntoSnap.x(),puntoSnap.y())
                self.rubberPunto.addPoint(puntoSnapXY, True)
                self.rubberPunto.show()

            if self.primerClick:
                if (len(self.listaPuntosLineaTemp) > 1):

                    if puntoSnap != None:
                        self.listaPuntosLineaTemp[-1] = puntoSnapXY
                    else:
                        self.listaPuntosLineaTemp[-1] = posTemp

                    for punto in self.listaPuntosLineaTemp[:-1]:
                        self.relaciones[self.punteroRelaciones].rubber.addPoint(punto, False)
                    self.relaciones[self.punteroRelaciones].rubber.addPoint(self.listaPuntosLineaTemp[-1], True)
                    self.relaciones[self.punteroRelaciones].rubber.show()
                else:
                    if puntoSnap != None:
                        self.listaPuntosLineaTemp.append(puntoSnapXY)
                    else:
                        self.listaPuntosLineaTemp.append(posTemp)
                    self.relaciones[self.punteroRelaciones].rubber.addPoint(self.listaPuntosLineaTemp[0], True)
                    self.relaciones[self.punteroRelaciones].rubber.show()
        
        elif self.modoEditar: #-modo editar

            if self.moviendoVertice: #Arrastrando un vertice

                self.rubberPunto.reset(QgsWkbTypes.PointGeometry)
                puntoSnap = self.snapCompleto(startingPoint)

                if puntoSnap != None:

                    puntoSnapXY = QgsPointXY(puntoSnap.x(),puntoSnap.y())
                    self.rubberPunto.addPoint(puntoSnapXY, True)
                    self.rubberPunto.show()
                    self.listaPuntosLineaTemp[self.indiceSeleccionado] = puntoSnapXY
                    self.relaciones[self.relacionEnEdicion].marcadores[self.indiceSeleccionado].setCenter(puntoSnapXY)

                else:
                    self.listaPuntosLineaTemp[self.indiceSeleccionado] = posTemp
                    self.relaciones[self.relacionEnEdicion].marcadores[self.indiceSeleccionado].setCenter(posTemp)
                
                self.relaciones[self.relacionEnEdicion].rubber.reset(QgsWkbTypes.LineGeometry)
                
                for punto in self.listaPuntosLineaTemp:
                    self.relaciones[self.relacionEnEdicion].rubber.addPoint(punto, True)
                
                
                self.relaciones[self.relacionEnEdicion].rubber.show()

    
#-------------------------------------------------------------------------------------#

    def snapVertice(self, startingPoint, nombreCapa):

        layer = QgsProject.instance().mapLayer(self.pluginM.ACA.obtenerIdCapa(nombreCapa))
        
        self.snapper.setCurrentLayer(layer)
        snapMatch = self.snapper.snapToCurrentLayer(startingPoint, QgsPointLocator.Vertex)

        if snapMatch.hasVertex():
            return snapMatch.point()

#------------------------------------------------------------------------------------#

    def snapArista(self, startingPoint, nombreCapa):

        layer = QgsProject.instance().mapLayer(self.pluginM.ACA.obtenerIdCapa(nombreCapa))
        
        self.snapper.setCurrentLayer(layer)
        snapMatch = self.snapper.snapToCurrentLayer(startingPoint, QgsPointLocator.Edge)

        if snapMatch.hasEdge():
            return snapMatch.point()

#-----------------------------------------------------------------------------------

    def snapCompleto(self, startingPoint):
        snap = self.snapVertice(startingPoint, 'predios.geom') #----vertices -----#
        if snap != None:
            return snap
        else:
            snap = self.snapVertice(startingPoint, 'construcciones')
            if snap != None:
                return snap
            else:
                snap = self.snapVertice(startingPoint, 'horizontales.geom')
                if snap != None:
                    return snap
                else:
                    snap = self.snapVertice(startingPoint, 'verticales') #-----Hasta aqui son vertices -----#
                    if snap != None:
                        return snap
                    else:
                        snap = self.snapArista(startingPoint, 'predios.geom')
                        if snap != None:
                            return snap
                        else:
                            snap = self.snapArista(startingPoint, 'construcciones')
                            if snap != None:
                                return snap
                            else:
                                snap = self.snapArista(startingPoint, 'horizontales.geom')
                                if snap != None:
                                    return snap
                                else:
                                    snap = self.snapArista(startingPoint, 'verticales') #-------- hasta aqui aristas-----------#
                                    if snap != None:
                                        return snap
                                    else:
                                        return None

#----------------------------------------------------------------------------------------------

    def crearNuevoRubberLinea(self):
        nuevoRubber = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
        nuevoRubber.setFillColor(QColor(0,0,0,0))
        nuevoRubber.setStrokeColor(QColor(0,62,240,255))
        nuevoRubber.setWidth(2)
        #penStyle = Qt.PenStyle()
        nuevoRubber.setLineStyle(Qt.PenStyle(3))
        return nuevoRubber

#------------------------------------------------------------------------------------------

    def crearNuevoRubberPoly(self):
        nuevoRubber = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        
        r = randint(0, 255)
        g = randint(0, 255)
        b = randint(0, 255)
        
        color = QColor(r,g,b,36)
        colorAg = QColor(r,g,b,87)
        self.pluginM.listaColores.append(colorAg)
        nuevoRubber.setFillColor(color)
        nuevoRubber.setStrokeColor(QColor(r,g,b,255))
        nuevoRubber.setWidth(2)
        return nuevoRubber

#-------------------------------------------------------------------------------------

    def recargarRelaciones(self):
        self.relaciones = {}
        self.punteroRelaciones = 0

        self.relaciones[self.punteroRelaciones] = RelacionRubberGeom(self.crearNuevoRubberLinea(), None)

#-----------------------------------------------------------------------------------------

    def prueba(self, e):
        print(e)

#----------------------------------------------------------------------------------

    def obtenerRelacionCercana(self, punto):
        rango = len(self.relaciones) - 1
        for i in range(0, rango):
            relacion = self.relaciones[i]
            geom = relacion.geom
            if geom != None:
                if geom.buffer(0.000004,1).intersects(punto):
                    self.relacionEnEdicion = i
                    return relacion
                    

#-----------------------------------------------------------------------------------

    def obtenerVertices(self, geom):
        n  = 0
        ver = geom.vertexAt(0)
        vertices=[]

        while(ver != QgsPoint(0,0)):
            n +=1
            vertices.append(ver)
            ver=geom.vertexAt(n)

        return vertices

    def crearNuevoMarcaVert(self):
        marcador = QgsVertexMarker(iface.mapCanvas())
        marcador.setColor(QColor(0,255,0))
        marcador.setIconSize(5)
        marcador.setIconType(QgsVertexMarker.ICON_BOX)
        marcador.setPenWidth(3)

        return marcador


class RelacionRubberGeom():
    def __init__(self, rubber, geom):
        self.rubber = rubber
        self.geom = geom
        self.marcadores = []

    def vaciarMarcadores(self):
        for marcador in self.marcadores:
            marcador.setColor(QColor(255,255,255,0))
        self.marcadores = []

