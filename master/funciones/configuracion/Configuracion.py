
class Configuracion():

    #Constructor
    def __init__(self):
        
        #Direccion IP del servidor
        self.servidorIP = 'http://192.168.0.40:8080/'
        
        #Combos de localidades, sectores y manzanas
        self.urlLocalidades = self.servidorIP + 'busquedasimplewkn/api/combo/001/localidades/'
        self.urlSectores = self.servidorIP +  'busquedasimplewkn/api/combo/localidades/'
        self.urlManzanas = self.servidorIP +  'busquedasimplewkn/api/combo/sector/'

        #Urls para capas de consulta
        self.urlConsultaManzana = self.servidorIP + 'busquedasimplewkn/api/manzana/'
        self.urlConsultaPrediosGeom = self.servidorIP + 'busquedasimplewkn/api/manzana/predios/'
        self.urlConsultaPrediosNum = self.servidorIP + 'busquedasimplewkn/api/busqueda/manzana/predios/'
        self.urlConsultaConstrucciones = self.servidorIP + 'busquedasimplewkn/api/manzana/construcciones/'
        self.urlConsultaHorizontalesGeom = self.servidorIP + 'busquedasimplewkn/api/manzana/deptoh/'
        self.urlConsultaHorizontalesNum = self.servidorIP + 'busquedasimplewkn/api/busqueda/manzana/cond-horizontales/'
        self.urlConsultaVerticales = self.servidorIP + 'busquedasimplewkn/api/manzana/deptov/'
        self.urlConsultaClavesV = self.servidorIP + 'busquedasimplewkn/api/manzana/deptovcve/'
       
       #Urls para llenar table items
        self.urlTipoConstEsp = self.servidorIP + 'busquedasimplewkn/api/cat/const/esp/'
        self.urlTipoConst = self.servidorIP + 'configuracion/api/cat-tipo-construccions/?page=0&size=1000'
        self.urlValoresTerrenos = self.servidorIP + 'configuracion/api/cat-valores-terrenos?page=0&size=1000'
        self.urlTipoAsentamiento = self.servidorIP + 'configuracion/api/cat-tipo-asentamiento-humanos?page=0&size=1000'
        self.urlTipoVialidad = self.servidorIP + 'configuracion/api/cat-tipo-asentamiento-humanos?page=0&size=1000'
        self.urlServCalle = self.servidorIP + 'busquedasimplewkn/api/cat-servicio/calle/'
        self.urlConsultaReferencia = self.servidorIP + 'busquedasimplewkn/api/busqueda/simple'
        
        #Urls para obtener campos dinamicos
        self.urlCamposCalles = self.servidorIP + 'busquedasimplewkn/api/thematics/lista/campos/sig:e_calle'
        self.urlCamposCapas = self.servidorIP + 'busquedasimplewkn/api/thematics/lista/campos/'

        #Urls para autenticacion
        self.urlAutenticacion= self.servidorIP + 'auth/login'
        
        #Guardado
        self.urlGuardadoRef = 'http://192.168.0.40:6543/api/etables/'
        self.urlGuardadoCon = self.servidorIP + 'featureswkn/api/manzana/'

        #SRID
        self.urlMunicipio = self.servidorIP + 'busquedasimplewkn/api/cat/municipio/'
        
        #Cargar capas con web service
        self.urlCargarCapa = 'http://192.168.0.50:8080/configuracion/api/adm-capas/getAllCapasConfiguration'

        #Urls para cedula
        self.urlCedPredio = self.servidorIP + 'busquedasimplewkn/api/cedula/predio/'
        self.urlCedConstr = self.servidorIP + 'featureswkn/api/construccion/getAllByCve/'
        self.urlCedCatalogos = self.servidorIP + 'configuracion/api/cat/getAllCatalogosEpredio'
        self.urlCedCatTipoUsoSuelo = self.servidorIP + 'configuracion/api/cat-tipo-uso-suelos?page=0&size=1000'
        self.urlCedCatUsoSueloByTipoUso = self.servidorIP + 'featureswkn/api/cat-tipo-uso-suelo/getCatUsoSueloByCve/'
        self.urlCedUsoConstr = self.servidorIP + 'configuracion/api/cat-uso-construccions?page=0&size=1000'
        self.urlCedDestino = self.servidorIP + 'configuracion/api/cat-destinos?page=0&size=1000'
        self.urlCedEdoConstr = self.servidorIP + 'configuracion/api/cat-estado-construccions?page=0&size=1000'
        self.urlCedCatFactorByTipoFactor = self.servidorIP + 'featureswkn/api/cat-factor/getAllFactorByIdTipoFactor/'
        self.urlCedCategoriasByIdUsoConst = self.servidorIP + 'featureswkn/api/cat-vuc/getCategoriasByIdConstruccion/'
        self.urlCedUsoEspecifByIdUsoConst = self.servidorIP + 'featureswkn/api/cat-uso-especifico/getCatUsoEspecificoByIdUsoConstruccion/'
        self.urlCedRCaracCategoria = self.servidorIP + 'featureswkn/api/cat-vuc/getRCaractCara/'
        self.urlCedCondominios = self.servidorIP + 'busquedasimplewkn/api/cedula/combo/condo/'
        self.urlCedCondByCveCatTipoPred = self.servidorIP + 'featureswkn/api/condominios/getByCveCatAndType/'
        self.urlCedServiciosCuenta = self.servidorIP + 'busquedasimplewkn/api/cat-servicio/cuenta/'
        self.urlCedCatVuc = self.servidorIP + 'featureswkn/api/cat-vuc/getCatVucFronCatCategoriCatUsoConstAndVigencia/'
        self.urlGuardaPredio = self.servidorIP + 'featureswkn/api/cedula/predio/update'
        self.urlGuardaServiciosP = self.servidorIP + 'featureswkn/api/cedula/servicioCuenta/'