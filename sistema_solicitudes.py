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
        self.d = self.repositorio.cargar()
        if self.d is None:
            self.d = {"estudiantes": [], "responsables": [], "solicitudes": []}
        # Carga responsables iniciales si no hay ninguno
        if len(self.d["responsables"]) == 0:
            self.d["responsables"] = [
                {"id": 1, "nombre": "Laura Gomez", "area": "BEDELIA"},
                {"id": 2, "nombre": "Martin Ruiz", "area": "SECRETARIA ACADEMICA"},
                {"id": 3, "nombre": "Carla Diaz", "area": "ALUMNADO"},
            ]
            self.guardar()

    def guardar(self):
        # Delega el guardado de los datos en el repositorio
        self.repositorio.guardar(self.d)

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
        for e in self.d["estudiantes"]:
            if e["legajo"] == solicitud.legajo:
                return e
        est = {"legajo": solicitud.legajo, "nombre": solicitud.nombre, "email": solicitud.email}
        self.d["estudiantes"].append(est)
        return est

    def generar_id(self):
        # Calcula el siguiente id disponible
        n = 1
        for s in self.d["solicitudes"]:
            if s["id"] >= n:
                n = s["id"] + 1
        return n

    def calcular_plazo(self, prioridad):
        # Devuelve los dias de plazo segun la prioridad
        return PLAZOS[prioridad]

    def buscar_solicitud(self, id):
        # Devuelve la solicitud con el id indicado o None si no existe
        for x in self.d["solicitudes"]:
            if x["id"] == id:
                return x
        return None

    def registrar_solicitud(self, solicitud):
        if not self.validar_estudiante(solicitud):
            return -1
        if not self.validar_solicitud(solicitud):
            return -1
        self.buscar_o_crear_estudiante(solicitud)
        n = self.generar_id()
        s = {
            "id": n,
            "legajo": solicitud.legajo,
            "tipo": solicitud.tipo,
            "prioridad": solicitud.prioridad,
            "descripcion": solicitud.descripcion,
            "estado": ESTADO_INICIAL,
            "responsable": None,
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "plazo": self.calcular_plazo(solicitud.prioridad),
        }
        self.d["solicitudes"].append(s)
        self.guardar()
        print("Solicitud registrada con id", n)
        return n

    def cambiar_estado(self, id, nuevo):
        s = self.buscar_solicitud(id)
        if s == None:
            print("Error: la solicitud no existe")
            return False
        # Controla las transiciones permitidas segun la tabla de transiciones
        if s["estado"] in ESTADOS_CERRADOS:
            print("Error: la solicitud ya esta cerrada")
            return False
        if nuevo not in TRANSICIONES[s["estado"]]:
            print("Error: transicion no permitida")
            return False
        if nuevo in ESTADOS_QUE_REQUIEREN_RESPONSABLE and s["responsable"] == None:
            print("Error: la solicitud no tiene responsable")
            return False
        s["estado"] = nuevo
        self.guardar()
        print("Estado actualizado a", nuevo)
        return True

    def asignar_responsable(self, id, id_resp):
        s = self.buscar_solicitud(id)
        if s == None:
            print("Error: la solicitud no existe")
            return False
        r = None
        for x in self.d["responsables"]:
            if x["id"] == id_resp:
                r = x
        if r == None:
            print("Error: el responsable no existe")
            return False
        if s["estado"] in ESTADOS_CERRADOS:
            print("Error: la solicitud ya esta cerrada")
            return False
        s["responsable"] = id_resp
        self.guardar()
        print("Responsable", r["nombre"], "asignado a la solicitud", id)
        return True

    def buscar(self, filtro, valor):
        l = []
        if filtro in FILTROS_SIMPLES:
            for x in self.d["solicitudes"]:
                if x[filtro] == valor:
                    l.append(x)
        elif filtro == "legajo":
            if not self.validar_legajo(valor):
                return None
            for x in self.d["solicitudes"]:
                if x["legajo"] == valor:
                    l.append(x)
        else:
            print("Error: filtro invalido")
            return None
        for x in l:
            print(x["id"], "-", x["tipo"], "-", x["prioridad"], "-", x["estado"], "-", x["legajo"])
        if len(l) == 0:
            print("No se encontraron solicitudes")
        return l

    def reporte(self):
        p = {}
        for e in ESTADOS:
            p[e] = 0
        a = {}
        for pr in PRIORIDADES:
            a[pr] = 0
        # Cuenta las solicitudes por estado y por prioridad
        for x in self.d["solicitudes"]:
            p[x["estado"]] = p[x["estado"]] + 1
            a[x["prioridad"]] = a[x["prioridad"]] + 1
        print("===== REPORTE DE SOLICITUDES =====")
        print("Total:", len(self.d["solicitudes"]))
        print("Pendientes:", p["PENDIENTE"], "| En proceso:", p["EN_PROCESO"],
              "| Resueltas:", p["RESUELTA"], "| Rechazadas:", p["RECHAZADA"])
        print("Prioridad alta:", a["ALTA"], "| media:", a["MEDIA"], "| baja:", a["BAJA"])
        for x in self.d["responsables"]:
            c = 0
            for y in self.d["solicitudes"]:
                if y["responsable"] == x["id"]:
                    c = c + 1
            print(x["nombre"], "(" + x["area"] + "):", c, "solicitudes asignadas")
        r = {"total": len(self.d["solicitudes"])}
        r.update(p)
        r.update(a)
        return r

    def obtener_responsables(self):
        # Devuelve la lista de responsables disponibles
        return self.d["responsables"]


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
        lg = input("Legajo: ")
        nm = input("Nombre: ")
        em = input("Email: ")
        tp = input("Tipo (CERTIFICADO/EQUIVALENCIA/RECLAMO/CONSTANCIA): ").upper()
        pr = input("Prioridad (ALTA/MEDIA/BAJA): ").upper()
        ds = input("Descripcion: ")
        self.gestor.registrar_solicitud(SolicitudNueva(lg, nm, em, tp, pr, ds))

    def opcion_cambiar_estado(self):
        # Pide la solicitud y el nuevo estado
        i = self.leer_numero("Id de la solicitud: ")
        nv = input("Nuevo estado (EN_PROCESO/RESUELTA/RECHAZADA): ").upper()
        self.gestor.cambiar_estado(i, nv)

    def opcion_asignar_responsable(self):
        # Muestra los responsables y asigna uno a la solicitud
        for x in self.gestor.obtener_responsables():
            print(x["id"], "-", x["nombre"], "-", x["area"])
        i = self.leer_numero("Id de la solicitud: ")
        j = self.leer_numero("Id del responsable: ")
        self.gestor.asignar_responsable(i, j)

    def opcion_buscar(self):
        # Pide el filtro y el valor de busqueda
        fl = input("Filtrar por (estado/prioridad/tipo/legajo): ").lower()
        vl = input("Valor: ").upper()
        self.gestor.buscar(fl, vl)

    def ejecutar(self):
        # Repite el menu hasta que el usuario elige salir
        op = ""
        while op != "0":
            self.mostrar_opciones()
            op = input("Opcion: ")
            if op == "1":
                self.opcion_registrar()
            elif op == "2":
                self.opcion_cambiar_estado()
            elif op == "3":
                self.opcion_asignar_responsable()
            elif op == "4":
                self.opcion_buscar()
            elif op == "5":
                self.gestor.reporte()
            elif op != "0":
                print("Opcion invalida")


if __name__ == "__main__":
    try:
        g = GestorSolicitudes(RepositorioJSON(ARCHIVO_DATOS))
    except ValueError as error:
        print(error)
    else:
        MenuConsola(g).ejecutar()
