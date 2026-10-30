import json
from abc import ABC, abstractmethod


class RepositorioSolicitudes(ABC):
    # Define las operaciones de persistencia que necesita el gestor

    @abstractmethod
    def cargar(self):
        pass

    @abstractmethod
    def guardar(self, datos):
        pass


class RepositorioJSON(RepositorioSolicitudes):
    # Guarda y recupera los datos del sistema en un archivo JSON

    def __init__(self, ruta):
        self.ruta = ruta

    def cargar(self):
        # Devuelve los datos del archivo o None si todavia no existe
        try:
            with open(self.ruta, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            raise ValueError("Error: el archivo de datos esta dañado y no se modificara")

    def guardar(self, datos):
        # Escribe los datos completos en el archivo
        with open(self.ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)
