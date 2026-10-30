import json
import os
import sys

import pytest

# Agrega la carpeta del proyecto para poder importar el sistema
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sistema_solicitudes import GestorSolicitudes, SolicitudNueva


# ---------- Preparación común ----------

@pytest.fixture
def gestor(tmp_path, monkeypatch):
    # Ejecuta cada prueba en una carpeta temporal con un archivo JSON limpio
    monkeypatch.chdir(tmp_path)
    return GestorSolicitudes()


def registrar(gestor, legajo="10234", nombre="Ana Perez", email="ana.perez@mail.com",
              tipo="CERTIFICADO", prioridad="ALTA", descripcion="Certificado de alumno regular"):
    # Centraliza la llamada al registro para que un cambio de firma se ajuste en un solo lugar
    return gestor.registrar_solicitud(SolicitudNueva(legajo, nombre, email, tipo, prioridad, descripcion))


def leer_datos():
    # Lee el archivo JSON tal como lo guardó el sistema
    with open("solicitudes.json", "r", encoding="utf-8") as archivo:
        return json.load(archivo)


# ---------- Registrar solicitud ----------

def test_registrar_solicitud_valida(gestor, capsys):
    # Arrange: se usa una solicitud con datos válidos
    # Act
    registrar(gestor)
    # Assert
    datos = leer_datos()
    assert len(datos["solicitudes"]) == 1
    assert datos["solicitudes"][0]["estado"] == "PENDIENTE"
    assert datos["solicitudes"][0]["responsable"] is None
    assert "Solicitud registrada con id 1" in capsys.readouterr().out


def test_registrar_incorpora_al_estudiante_una_sola_vez(gestor):
    # Arrange y Act: el mismo estudiante registra dos solicitudes
    registrar(gestor)
    registrar(gestor, tipo="CONSTANCIA", descripcion="Constancia de examen")
    # Assert
    datos = leer_datos()
    assert len(datos["solicitudes"]) == 2
    assert len(datos["estudiantes"]) == 1


def test_plazo_segun_prioridad(gestor):
    # Act: se registra una solicitud por cada prioridad
    registrar(gestor, prioridad="ALTA")
    registrar(gestor, prioridad="MEDIA")
    registrar(gestor, prioridad="BAJA")
    # Assert
    plazos = [s["plazo"] for s in leer_datos()["solicitudes"]]
    assert plazos == [2, 5, 10]


def test_registrar_con_legajo_invalido_no_guarda(gestor, capsys):
    # Act: el legajo tiene menos de cinco dígitos
    registrar(gestor, legajo="123")
    # Assert
    assert len(leer_datos()["solicitudes"]) == 0
    assert "Error: legajo invalido" in capsys.readouterr().out


def test_registrar_con_email_invalido_no_guarda(gestor, capsys):
    # Act: el email no tiene arroba
    registrar(gestor, email="ana.mail.com")
    # Assert
    assert len(leer_datos()["solicitudes"]) == 0
    assert "Error: email invalido" in capsys.readouterr().out


def test_registrar_con_tipo_invalido_no_guarda(gestor, capsys):
    # Act: el tipo no pertenece a los tipos permitidos
    registrar(gestor, tipo="BECA")
    # Assert
    assert len(leer_datos()["solicitudes"]) == 0
    assert "Error: tipo invalido" in capsys.readouterr().out


# ---------- Asignar responsable ----------

def test_asignar_responsable_valido(gestor, capsys):
    # Arrange
    registrar(gestor)
    # Act
    gestor.asignar_responsable(1, 2)
    # Assert
    assert leer_datos()["solicitudes"][0]["responsable"] == 2
    assert "Responsable Martin Ruiz asignado a la solicitud 1" in capsys.readouterr().out


def test_asignar_responsable_inexistente(gestor, capsys):
    # Arrange
    registrar(gestor)
    # Act: el responsable 99 no existe
    gestor.asignar_responsable(1, 99)
    # Assert
    assert leer_datos()["solicitudes"][0]["responsable"] is None
    assert "Error: el responsable no existe" in capsys.readouterr().out


def test_asignar_responsable_a_solicitud_inexistente(gestor, capsys):
    # Act: no hay ninguna solicitud registrada
    gestor.asignar_responsable(5, 1)
    # Assert
    assert "Error: la solicitud no existe" in capsys.readouterr().out


# ---------- Cambiar estado ----------

def test_flujo_completo_de_estados(gestor):
    # Arrange
    registrar(gestor)
    gestor.asignar_responsable(1, 1)
    # Act
    gestor.cambiar_estado(1, "EN_PROCESO")
    gestor.cambiar_estado(1, "RESUELTA")
    # Assert
    assert leer_datos()["solicitudes"][0]["estado"] == "RESUELTA"


def test_no_pasa_a_en_proceso_sin_responsable(gestor, capsys):
    # Arrange
    registrar(gestor)
    # Act
    gestor.cambiar_estado(1, "EN_PROCESO")
    # Assert
    assert leer_datos()["solicitudes"][0]["estado"] == "PENDIENTE"
    assert "Error: la solicitud no tiene responsable" in capsys.readouterr().out


def test_pendiente_puede_rechazarse(gestor):
    # Arrange
    registrar(gestor)
    # Act
    gestor.cambiar_estado(1, "RECHAZADA")
    # Assert
    assert leer_datos()["solicitudes"][0]["estado"] == "RECHAZADA"


def test_transicion_no_permitida(gestor, capsys):
    # Arrange
    registrar(gestor)
    # Act: una solicitud pendiente no puede pasar directo a resuelta
    gestor.cambiar_estado(1, "RESUELTA")
    # Assert
    assert leer_datos()["solicitudes"][0]["estado"] == "PENDIENTE"
    assert "Error: transicion no permitida" in capsys.readouterr().out


def test_solicitud_cerrada_no_admite_cambios(gestor, capsys):
    # Arrange: la solicitud queda rechazada
    registrar(gestor)
    gestor.cambiar_estado(1, "RECHAZADA")
    # Act
    gestor.cambiar_estado(1, "EN_PROCESO")
    gestor.asignar_responsable(1, 1)
    # Assert
    solicitud = leer_datos()["solicitudes"][0]
    assert solicitud["estado"] == "RECHAZADA"
    assert solicitud["responsable"] is None
    assert capsys.readouterr().out.count("Error: la solicitud ya esta cerrada") == 2


# ---------- Buscar / filtrar ----------

def test_buscar_por_estado(gestor):
    # Arrange: una solicitud pendiente y otra rechazada
    registrar(gestor)
    registrar(gestor, legajo="10567", nombre="Juan Lopez", email="juan.lopez@mail.com")
    gestor.cambiar_estado(2, "RECHAZADA")
    # Act
    resultado = gestor.buscar("estado", "PENDIENTE")
    # Assert
    assert len(resultado) == 1
    assert resultado[0]["legajo"] == "10234"


def test_buscar_por_legajo(gestor):
    # Arrange
    registrar(gestor)
    registrar(gestor, legajo="10567", nombre="Juan Lopez", email="juan.lopez@mail.com")
    # Act
    resultado = gestor.buscar("legajo", "10567")
    # Assert
    assert len(resultado) == 1
    assert resultado[0]["legajo"] == "10567"


def test_buscar_sin_resultados(gestor, capsys):
    # Arrange
    registrar(gestor)
    # Act
    resultado = gestor.buscar("tipo", "RECLAMO")
    # Assert
    assert len(resultado) == 0
    assert "No se encontraron solicitudes" in capsys.readouterr().out


def test_buscar_con_legajo_invalido(gestor, capsys):
    # Act
    gestor.buscar("legajo", "12")
    # Assert
    assert "Error: legajo invalido" in capsys.readouterr().out


# ---------- Reporte ----------

def test_reporte_por_estado_prioridad_y_responsable(gestor, capsys):
    # Arrange: dos solicitudes, una asignada y en proceso
    registrar(gestor, prioridad="ALTA")
    registrar(gestor, legajo="10567", nombre="Juan Lopez", email="juan.lopez@mail.com", prioridad="MEDIA")
    gestor.asignar_responsable(1, 2)
    gestor.cambiar_estado(1, "EN_PROCESO")
    capsys.readouterr()
    # Act
    gestor.reporte()
    # Assert
    salida = capsys.readouterr().out
    assert "Total: 2" in salida
    assert "Pendientes: 1 | En proceso: 1 | Resueltas: 0 | Rechazadas: 0" in salida
    assert "Prioridad alta: 1 | media: 1 | baja: 0" in salida
    assert "Martin Ruiz (SECRETARIA ACADEMICA): 1 solicitudes asignadas" in salida


# ---------- Persistencia ----------

def test_responsables_precargados(gestor):
    # Assert: al iniciar por primera vez se crean tres responsables
    assert len(leer_datos()["responsables"]) == 3


def test_datos_se_conservan_al_reiniciar(gestor):
    # Arrange
    registrar(gestor)
    # Act: se crea un nuevo gestor, como si se reiniciara la aplicación
    otro_gestor = GestorSolicitudes()
    resultado = otro_gestor.buscar("legajo", "10234")
    # Assert
    assert len(resultado) == 1
