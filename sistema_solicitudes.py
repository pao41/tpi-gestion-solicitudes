import json
from datetime import datetime


class GestorSolicitudes:

    def __init__(self):
        self.d = {"estudiantes": [], "responsables": [], "solicitudes": []}
        self.cargar()
        # Carga responsables iniciales si el archivo esta vacio
        if len(self.d["responsables"]) == 0:
            self.d["responsables"] = [
                {"id": 1, "nombre": "Laura Gomez", "area": "BEDELIA"},
                {"id": 2, "nombre": "Martin Ruiz", "area": "SECRETARIA ACADEMICA"},
                {"id": 3, "nombre": "Carla Diaz", "area": "ALUMNADO"},
            ]
            self.guardar()

    def cargar(self):
        try:
            f = open("solicitudes.json", "r", encoding="utf-8")
            self.d = json.load(f)
            f.close()
        except:
            pass

    def guardar(self):
        f = open("solicitudes.json", "w", encoding="utf-8")
        json.dump(self.d, f, indent=4, ensure_ascii=False)
        f.close()

    def registrar_solicitud(self, legajo, nombre, email, tipo, prioridad, descripcion):
        # Valida los datos del estudiante
        if legajo == "" or len(legajo) != 5 or not legajo.isdigit():
            print("Error: legajo invalido")
            return -1
        if nombre == "":
            print("Error: nombre vacio")
            return -1
        if "@" not in email or "." not in email:
            print("Error: email invalido")
            return -1
        # Valida los datos de la solicitud
        if tipo != "CERTIFICADO" and tipo != "EQUIVALENCIA" and tipo != "RECLAMO" and tipo != "CONSTANCIA":
            print("Error: tipo invalido")
            return -1
        if prioridad != "ALTA" and prioridad != "MEDIA" and prioridad != "BAJA":
            print("Error: prioridad invalida")
            return -1
        if descripcion == "":
            print("Error: descripcion vacia")
            return -1
        # Busca el estudiante y lo agrega si no existe
        est = None
        for e in self.d["estudiantes"]:
            if e["legajo"] == legajo:
                est = e
        if est == None:
            est = {"legajo": legajo, "nombre": nombre, "email": email}
            self.d["estudiantes"].append(est)
        # Calcula el siguiente id
        n = 1
        for s in self.d["solicitudes"]:
            if s["id"] >= n:
                n = s["id"] + 1
        s = {
            "id": n,
            "legajo": legajo,
            "tipo": tipo,
            "prioridad": prioridad,
            "descripcion": descripcion,
            "estado": "PENDIENTE",
            "responsable": None,
            "fecha": datetime.now().strftime("%d/%m/%Y"),
        }
        # Asigna los dias de plazo segun la prioridad
        if prioridad == "ALTA":
            s["plazo"] = 2
        elif prioridad == "MEDIA":
            s["plazo"] = 5
        else:
            s["plazo"] = 10
        self.d["solicitudes"].append(s)
        f = open("solicitudes.json", "w", encoding="utf-8")
        json.dump(self.d, f, indent=4, ensure_ascii=False)
        f.close()
        print("Solicitud registrada con id", n)
        return n

    def cambiar_estado(self, id, nuevo):
        s = None
        for x in self.d["solicitudes"]:
            if x["id"] == id:
                s = x
        if s == None:
            print("Error: la solicitud no existe")
            return False
        # Controla las transiciones permitidas entre estados
        if s["estado"] == "PENDIENTE":
            if nuevo == "EN_PROCESO":
                if s["responsable"] == None:
                    print("Error: la solicitud no tiene responsable")
                    return False
                s["estado"] = nuevo
            elif nuevo == "RECHAZADA":
                s["estado"] = nuevo
            else:
                print("Error: transicion no permitida")
                return False
        elif s["estado"] == "EN_PROCESO":
            if nuevo == "RESUELTA" or nuevo == "RECHAZADA":
                s["estado"] = nuevo
            else:
                print("Error: transicion no permitida")
                return False
        elif s["estado"] == "RESUELTA" or s["estado"] == "RECHAZADA":
            print("Error: la solicitud ya esta cerrada")
            return False
        f = open("solicitudes.json", "w", encoding="utf-8")
        json.dump(self.d, f, indent=4, ensure_ascii=False)
        f.close()
        print("Estado actualizado a", nuevo)
        return True

    def asignar_responsable(self, id, id_resp):
        s = None
        for x in self.d["solicitudes"]:
            if x["id"] == id:
                s = x
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
        if s["estado"] == "RESUELTA" or s["estado"] == "RECHAZADA":
            print("Error: la solicitud ya esta cerrada")
            return False
        s["responsable"] = id_resp
        f = open("solicitudes.json", "w", encoding="utf-8")
        json.dump(self.d, f, indent=4, ensure_ascii=False)
        f.close()
        print("Responsable", r["nombre"], "asignado a la solicitud", id)
        return True

    def buscar(self, filtro, valor):
        l = []
        if filtro == "estado":
            for x in self.d["solicitudes"]:
                if x["estado"] == valor:
                    l.append(x)
        elif filtro == "prioridad":
            for x in self.d["solicitudes"]:
                if x["prioridad"] == valor:
                    l.append(x)
        elif filtro == "tipo":
            for x in self.d["solicitudes"]:
                if x["tipo"] == valor:
                    l.append(x)
        elif filtro == "legajo":
            # Valida el legajo antes de buscar
            if valor == "" or len(valor) != 5 or not valor.isdigit():
                print("Error: legajo invalido")
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
        p = 0
        e = 0
        r = 0
        rc = 0
        a = 0
        m = 0
        b = 0
        for x in self.d["solicitudes"]:
            if x["estado"] == "PENDIENTE":
                p = p + 1
            elif x["estado"] == "EN_PROCESO":
                e = e + 1
            elif x["estado"] == "RESUELTA":
                r = r + 1
            elif x["estado"] == "RECHAZADA":
                rc = rc + 1
            if x["prioridad"] == "ALTA":
                a = a + 1
            elif x["prioridad"] == "MEDIA":
                m = m + 1
            else:
                b = b + 1
        print("===== REPORTE DE SOLICITUDES =====")
        print("Total:", len(self.d["solicitudes"]))
        print("Pendientes:", p, "| En proceso:", e, "| Resueltas:", r, "| Rechazadas:", rc)
        print("Prioridad alta:", a, "| media:", m, "| baja:", b)
        for x in self.d["responsables"]:
            c = 0
            for y in self.d["solicitudes"]:
                if y["responsable"] == x["id"]:
                    c = c + 1
            print(x["nombre"], "(" + x["area"] + "):", c, "solicitudes asignadas")
        return {"total": len(self.d["solicitudes"]), "PENDIENTE": p, "EN_PROCESO": e,
                "RESUELTA": r, "RECHAZADA": rc, "ALTA": a, "MEDIA": m, "BAJA": b}

    def menu(self):
        op = ""
        while op != "0":
            print("\n--- SISTEMA DE GESTION DE SOLICITUDES ACADEMICAS ---")
            print("1. Registrar solicitud")
            print("2. Cambiar estado")
            print("3. Asignar responsable")
            print("4. Buscar solicitudes")
            print("5. Reporte")
            print("0. Salir")
            op = input("Opcion: ")
            if op == "1":
                lg = input("Legajo: ")
                nm = input("Nombre: ")
                em = input("Email: ")
                tp = input("Tipo (CERTIFICADO/EQUIVALENCIA/RECLAMO/CONSTANCIA): ").upper()
                pr = input("Prioridad (ALTA/MEDIA/BAJA): ").upper()
                ds = input("Descripcion: ")
                self.registrar_solicitud(lg, nm, em, tp, pr, ds)
            elif op == "2":
                try:
                    i = int(input("Id de la solicitud: "))
                except:
                    i = 0
                nv = input("Nuevo estado (EN_PROCESO/RESUELTA/RECHAZADA): ").upper()
                self.cambiar_estado(i, nv)
            elif op == "3":
                for x in self.d["responsables"]:
                    print(x["id"], "-", x["nombre"], "-", x["area"])
                try:
                    i = int(input("Id de la solicitud: "))
                    j = int(input("Id del responsable: "))
                except:
                    i = 0
                    j = 0
                self.asignar_responsable(i, j)
            elif op == "4":
                fl = input("Filtrar por (estado/prioridad/tipo/legajo): ").lower()
                vl = input("Valor: ").upper()
                self.buscar(fl, vl)
            elif op == "5":
                self.reporte()
            elif op != "0":
                print("Opcion invalida")


if __name__ == "__main__":
    g = GestorSolicitudes()
    g.menu()