from dataclasses import dataclass
from datetime import datetime

from repositorio import RepositorioJSON

# Valores permitidos del sistema
TIPOS = ["CERTIFICADO", "EQUIVALENCIA", "RECLAMO", "CONSTANCIA"]
PRIORIDADES = ["ALTA", "MEDIA", "BAJA"]
ESTADOS = ["PENDIENTE", "EN_PROCESO", "RESUELTA", "RECHAZADA"]
ESTADO_INICIAL = "PENDIENTE"
ESTADOS_CERRADOS = ["RESUELTA", "RECHAZADA"]
ESTADOS_QUE_REQUIEREN_RESPONSABLE = ["EN_PROCESO"]
FILTROS_SIMPLES = ["estado", "prioridad", "tipo"]
ARCHIVO_DATOS = "solicitudes.json"

# Dias de plazo segun la prioridad
PLAZOS = {"ALTA": 2, "MEDIA": 5, "BAJA": 10}

# Estados a los que puede pasar cada estado
TRANSICIONES = {
    "PENDIENTE": ["EN_PROCESO", "RECHAZADA"],
    "EN_PROCESO": ["RESUELTA", "RECHAZADA"],
    "RESUELTA": [],
    "RECHAZADA": [],
}


@dataclass
class SolicitudNueva:
    # Agrupa los datos necesarios para registrar una solicitud
    legajo: str
    nombre: str
    email: str
    tipo: str
    prioridad: str
    descripcion: str


class GestorSolicitudes:

    def __init__(self, repositorio):
        # Recibe el repositorio que se encarga de guardar los datos
        self.repositorio = repositorio
        self.datos = self.repositorio.cargar()
        if self.datos is None:
            self.datos = {"estudiantes": [], "responsables": [], "solicitudes": []}
        # Carga responsables iniciales si no hay ninguno
        if len(self.datos["responsables"]) == 0:
            self.datos["responsables"] = [
                {"id": 1, "nombre": "Laura Gomez", "area": "BEDELIA"},
                {"id": 2, "nombre": "Martin Ruiz", "area": "SECRETARIA ACADEMICA"},
                {"id": 3, "nombre": "Carla Diaz", "area": "ALUMNADO"},
            ]
            self.guardar()

    def guardar(self):
        # Delega el guardado de los datos en el repositorio
        self.repositorio.guardar(self.datos)

    def validar_legajo(self, legajo):
        # Verifica que el legajo tenga cinco digitos
        if legajo == "" or len(legajo) != 5 or not legajo.isdigit():
            print("Error: legajo invalido")
            return False
        return True

    def validar_estudiante(self, solicitud):
        # Valida los datos del estudiante
        if not self.validar_legajo(solicitud.legajo):
            return False
        if solicitud.nombre == "":
            print("Error: nombre vacio")
            return False
        if "@" not in solicitud.email or "." not in solicitud.email:
            print("Error: email invalido")
            return False
        return True

    def validar_solicitud(self, solicitud):
        # Valida los datos de la solicitud
        if solicitud.tipo not in TIPOS:
            print("Error: tipo invalido")
            return False
        if solicitud.prioridad not in PRIORIDADES:
            print("Error: prioridad invalida")
            return False
        if solicitud.descripcion == "":
            print("Error: descripcion vacia")
            return False
        return True

    def buscar_o_crear_estudiante(self, solicitud):
        # Busca el estudiante por legajo y lo agrega si no existe
        for estudiante in self.datos["estudiantes"]:
            if estudiante["legajo"] == solicitud.legajo:
                return estudiante
        nuevo_estudiante = {"legajo": solicitud.legajo, "nombre": solicitud.nombre, "email": solicitud.email}
        self.datos["estudiantes"].append(nuevo_estudiante)
        return nuevo_estudiante

    def generar_id(self):
        # Calcula el siguiente id disponible
        siguiente_id = 1
        for solicitud in self.datos["solicitudes"]:
            if solicitud["id"] >= siguiente_id:
                siguiente_id = solicitud["id"] + 1
        return siguiente_id

    def calcular_plazo(self, prioridad):
        # Devuelve los dias de plazo segun la prioridad
        return PLAZOS[prioridad]

    def buscar_solicitud(self, id_solicitud):
        # Devuelve la solicitud con el id indicado o None si no existe
        for solicitud in self.datos["solicitudes"]:
            if solicitud["id"] == id_solicitud:
                return solicitud
        return None

    def buscar_responsable(self, id_responsable):
        # Devuelve el responsable con el id indicado o None si no existe
        for responsable in self.datos["responsables"]:
            if responsable["id"] == id_responsable:
                return responsable
        return None

    def registrar_solicitud(self, solicitud):
        # Valida los datos, registra la solicitud y la guarda
        if not self.validar_estudiante(solicitud):
            return -1
        if not self.validar_solicitud(solicitud):
            return -1
        self.buscar_o_crear_estudiante(solicitud)
        nuevo_id = self.generar_id()
        solicitud_registrada = {
            "id": nuevo_id,
            "legajo": solicitud.legajo,
            "tipo": solicitud.tipo,
            "prioridad": solicitud.prioridad,
            "descripcion": solicitud.descripcion,
            "estado": ESTADO_INICIAL,
            "responsable": None,
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "plazo": self.calcular_plazo(solicitud.prioridad),
        }
        self.datos["solicitudes"].append(solicitud_registrada)
        self.guardar()
        print("Solicitud registrada con id", nuevo_id)
        return nuevo_id

    def cambiar_estado(self, id_solicitud, nuevo_estado):
        # Cambia el estado de la solicitud si la transicion esta permitida
        solicitud = self.buscar_solicitud(id_solicitud)
        if solicitud is None:
            print("Error: la solicitud no existe")
            return False
        # Controla las transiciones permitidas segun la tabla de transiciones
        if solicitud["estado"] in ESTADOS_CERRADOS:
            print("Error: la solicitud ya esta cerrada")
            return False
        if nuevo_estado not in TRANSICIONES[solicitud["estado"]]:
            print("Error: transicion no permitida")
            return False
        if nuevo_estado in ESTADOS_QUE_REQUIEREN_RESPONSABLE and solicitud["responsable"] is None:
            print("Error: la solicitud no tiene responsable")
            return False
        solicitud["estado"] = nuevo_estado
        self.guardar()
        print("Estado actualizado a", nuevo_estado)
        return True

    def asignar_responsable(self, id_solicitud, id_responsable):
        # Asigna un responsable a una solicitud abierta
        solicitud = self.buscar_solicitud(id_solicitud)
        if solicitud is None:
            print("Error: la solicitud no existe")
            return False
        responsable = self.buscar_responsable(id_responsable)
        if responsable is None:
            print("Error: el responsable no existe")
            return False
        if solicitud["estado"] in ESTADOS_CERRADOS:
            print("Error: la solicitud ya esta cerrada")
            return False
        solicitud["responsable"] = id_responsable
        self.guardar()
        print("Responsable", responsable["nombre"], "asignado a la solicitud", id_solicitud)
        return True

    def buscar(self, filtro, valor):
        # Devuelve las solicitudes que coinciden con el filtro indicado
        resultado = []
        if filtro in FILTROS_SIMPLES:
            for solicitud in self.datos["solicitudes"]:
                if solicitud[filtro] == valor:
                    resultado.append(solicitud)
        elif filtro == "legajo":
            if not self.validar_legajo(valor):
                return None
            for solicitud in self.datos["solicitudes"]:
                if solicitud["legajo"] == valor:
                    resultado.append(solicitud)
        else:
            print("Error: filtro invalido")
            return None
        for solicitud in resultado:
            print(solicitud["id"], "-", solicitud["tipo"], "-", solicitud["prioridad"], "-",
                  solicitud["estado"], "-", solicitud["legajo"])
        if len(resultado) == 0:
            print("No se encontraron solicitudes")
        return resultado

    def reporte(self):
        # Muestra y devuelve la cantidad de solicitudes por estado, prioridad y responsable
        cantidad_por_estado = {}
        for estado in ESTADOS:
            cantidad_por_estado[estado] = 0
        cantidad_por_prioridad = {}
        for prioridad in PRIORIDADES:
            cantidad_por_prioridad[prioridad] = 0
        # Cuenta las solicitudes por estado y por prioridad
        for solicitud in self.datos["solicitudes"]:
            cantidad_por_estado[solicitud["estado"]] = cantidad_por_estado[solicitud["estado"]] + 1
            cantidad_por_prioridad[solicitud["prioridad"]] = cantidad_por_prioridad[solicitud["prioridad"]] + 1
        print("===== REPORTE DE SOLICITUDES =====")
        print("Total:", len(self.datos["solicitudes"]))
        print("Pendientes:", cantidad_por_estado["PENDIENTE"], "| En proceso:", cantidad_por_estado["EN_PROCESO"],
              "| Resueltas:", cantidad_por_estado["RESUELTA"], "| Rechazadas:", cantidad_por_estado["RECHAZADA"])
        print("Prioridad alta:", cantidad_por_prioridad["ALTA"], "| media:", cantidad_por_prioridad["MEDIA"],
              "| baja:", cantidad_por_prioridad["BAJA"])
        for responsable in self.datos["responsables"]:
            cantidad_asignadas = 0
            for solicitud in self.datos["solicitudes"]:
                if solicitud["responsable"] == responsable["id"]:
                    cantidad_asignadas = cantidad_asignadas + 1
            print(responsable["nombre"], "(" + responsable["area"] + "):", cantidad_asignadas, "solicitudes asignadas")
        resumen = {"total": len(self.datos["solicitudes"])}
        resumen.update(cantidad_por_estado)
        resumen.update(cantidad_por_prioridad)
        return resumen

    def obtener_responsables(self):
        # Devuelve la lista de responsables disponibles
        return self.datos["responsables"]


class MenuConsola:
    # Se encarga de la interaccion con el usuario por consola

    def __init__(self, gestor):
        self.gestor = gestor

    def mostrar_opciones(self):
        # Muestra las opciones del menu principal
        print("\n--- SISTEMA DE GESTION DE SOLICITUDES ACADEMICAS ---")
        print("1. Registrar solicitud")
        print("2. Cambiar estado")
        print("3. Asignar responsable")
        print("4. Buscar solicitudes")
        print("5. Reporte")
        print("0. Salir")

    def leer_numero(self, mensaje):
        # Lee un numero entero y devuelve 0 si el valor ingresado no es valido
        try:
            return int(input(mensaje))
        except ValueError:
            return 0

    def opcion_registrar(self):
        # Pide los datos y registra una nueva solicitud
        legajo = input("Legajo: ")
        nombre = input("Nombre: ")
        email = input("Email: ")
        tipo = input("Tipo (CERTIFICADO/EQUIVALENCIA/RECLAMO/CONSTANCIA): ").upper()
        prioridad = input("Prioridad (ALTA/MEDIA/BAJA): ").upper()
        descripcion = input("Descripcion: ")
        self.gestor.registrar_solicitud(SolicitudNueva(legajo, nombre, email, tipo, prioridad, descripcion))

    def opcion_cambiar_estado(self):
        # Pide la solicitud y el nuevo estado
        id_solicitud = self.leer_numero("Id de la solicitud: ")
        nuevo_estado = input("Nuevo estado (EN_PROCESO/RESUELTA/RECHAZADA): ").upper()
        self.gestor.cambiar_estado(id_solicitud, nuevo_estado)

    def opcion_asignar_responsable(self):
        # Muestra los responsables y asigna uno a la solicitud
        for responsable in self.gestor.obtener_responsables():
            print(responsable["id"], "-", responsable["nombre"], "-", responsable["area"])
        id_solicitud = self.leer_numero("Id de la solicitud: ")
        id_responsable = self.leer_numero("Id del responsable: ")
        self.gestor.asignar_responsable(id_solicitud, id_responsable)

    def opcion_buscar(self):
        # Pide el filtro y el valor de busqueda
        filtro = input("Filtrar por (estado/prioridad/tipo/legajo): ").lower()
        valor = input("Valor: ").upper()
        self.gestor.buscar(filtro, valor)

    def ejecutar(self):
        # Repite el menu hasta que el usuario elige salir
        opcion = ""
        while opcion != "0":
            self.mostrar_opciones()
            opcion = input("Opcion: ")
            if opcion == "1":
                self.opcion_registrar()
            elif opcion == "2":
                self.opcion_cambiar_estado()
            elif opcion == "3":
                self.opcion_asignar_responsable()
            elif opcion == "4":
                self.opcion_buscar()
            elif opcion == "5":
                self.gestor.reporte()
            elif opcion != "0":
                print("Opcion invalida")


if __name__ == "__main__":
    try:
        gestor = GestorSolicitudes(RepositorioJSON(ARCHIVO_DATOS))
    except ValueError as error:
        print(error)
    else:
        MenuConsola(gestor).ejecutar()
