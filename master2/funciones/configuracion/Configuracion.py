
class Configuracion():

    #Constructor
    def __init__(self):
        
        #Direccion IP del servidor
        self.servidorIP = 'http://192.168.0.40:8080/'
        #self.servidorIP = 'http://127.0.0.1:8080/'

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
        self.urlTipoVialidad = self.servidorIP + 'configuracion/api/cat-vialidads?page=0&size=1000'
        self.urlServCalle = self.servidorIP + 'busquedasimplewkn/api/cat-servicio/calle/'
        self.urlConsultaReferencia = self.servidorIP + 'busquedasimplewkn/api/busqueda/simple'

        #Urls para obtener campos dinamicos
        self.urlCamposCalles = self.servidorIP + 'busquedasimplewkn/api/thematics/lista/campos/sig:e_calle/true'
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
        self.urlGuardaVolumenP = self.servidorIP + 'featureswkn/api/cedula/construccion/'
        self.urlVerifSiTieneGeomConstP = self.servidorIP + 'busquedasimplewkn/api/construccion/geom/'
        self.urlGuardaCondominio = self.servidorIP + 'featureswkn/api/cedula/condominios/'
        self.urlIndivisos = self.servidorIP + 'busquedasimplewkn/api/cedula/condo/indivisos/'
        self.urlGuardaIndivisos = self.servidorIP + 'featureswkn/api/condominios/updateIndiviso'
        self.urlObtIdsImagenes = self.servidorIP + 'archivoswkn/api/archivo/getIdsArchivos/'
        self.urlImagenByIdAndCveCata = self.servidorIP + 'archivoswkn/api/archivo/getArchivo/'
        self.urlGetPadron = self.servidorIP + 'busquedasimplewkn/api/cedula/padron/'
        self.urlGetPropPredio = self.servidorIP + 'busquedasimplewkn/api/cedula/propietario/'
        #Urls para claves de manzana
        self.urlGetManzana = self.servidorIP + 'busquedasimplewkn/api/cedula/claves/mza/'
        #Url para copiar imagen 
        self.urlCopyIma = self.servidorIP +'archivoswkn/api/archivo/copiar'
        #Url para cortar imagen 
        self.urlCortaIma = self.servidorIP + 'archivoswkn/api/archivo/cortar'
        #Url para eliminar imagen
        self.urlEliminaIma = self.servidorIP + 'archivoswkn/api/archivo-resource/deleteArchivo'
        #Url subir imagen
        self.urlSubirIma = self.servidorIP + 'archivoswkn/api/archivo-resource/saveArchivo/'
        #Urls para asignacion de campo
        self.urlAsigCampoAgregar = self.servidorIP + 'busquedasimplewkn/api/asignacion/campo/asignar/'
        self.urlAsigCampoEliminar = self.servidorIP + 'busquedasimplewkn/api/asignacion/campo/eliminar/'
        self.urlAsigCampoConsultar = self.servidorIP + 'busquedasimplewkn/api/asignacion/campo/obtener/'
        self.urlAsigCampoTodos = self.servidorIP + 'busquedasimplewkn/api/asignacion/campo/todos'

        #Urls para asignacion de revision
        self.urlAsigRevAgregar = self.servidorIP + 'busquedasimplewkn/api/asignacion/revision/asignar/'
        self.urlAsigRevEliminar = self.servidorIP + 'busquedasimplewkn/api/asignacion/revision/eliminar/'
        self.urlAsigRevConsultar = self.servidorIP + 'busquedasimplewkn/api/asignacion/revision/obtener/'
        self.urlAsigRevTodos = self.servidorIP + 'busquedasimplewkn/api/asignacion/revision/todos'

        #Urls para asignacion de padron
        self.urlAsigPadAgregar = self.servidorIP + 'busquedasimplewkn/api/asignacion/padron/asignar/'
        self.urlAsigPadEliminar = self.servidorIP + 'busquedasimplewkn/api/asignacion/padron/eliminar/'
        self.urlAsigPadConsultar = self.servidorIP + 'busquedasimplewkn/api/asignacion/padron/obtener/'
        self.urlAsigPadTodos = self.servidorIP + 'busquedasimplewkn/api/asignacion/padron/todos'

        #urls para usuarios
        self.urlObtenerUsuarios = self.servidorIP + 'autentificacion/api/users'

        #Urls para asignacionrevision
        self.urlReviPredio = self.servidorIP + 'busquedasimplewkn/api/asignacion/revision/obtenerPredio/'
        self.urlReviConst = self.servidorIP + 'featureswkn/api/asignacion/revision/obtenerConstruccionesRelId/'
        self.urlReviCondominios = self.servidorIP + 'busquedasimplewkn/api/revision/combo/condo/'
        self.urlReviCondConsulta = self.servidorIP + 'featureswkn/api/asignacion/revision/obtenerCondominios/'
        self.urlObtenerIdPredio = self.servidorIP + 'busquedasimplewkn/api/asignacion/revision/obtenerIdPredio/'
        self.urlObtenerIdPredioEc = self.servidorIP + 'busquedasimplewkn/api/asignacion/revision/obtenerIdPredioEc/'
        self.urlObtenerCuentaPredial = self.servidorIP + 'busquedasimplewkn/api/asignacion/padron/obtenerCuentaPredial/'
        self.urlCvesUsuarioMan = self.servidorIP + 'busquedasimplewkn/api/asignacion/'

        self.urlActualizarPadron = self.servidorIP + 'busquedasimplewkn/api/asignacion/revision/actualizarPadron'
        self.urlConfirmarInicioR = self.servidorIP + 'busquedasimplewkn/api/asignacion/confirmarInicio/'
        self.urlConfirmarFinR = self.servidorIP + 'busquedasimplewkn/api/asignacion/confirmarFin/'