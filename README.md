# Sistema de Gestión de Solicitudes Académicas

Trabajo Práctico Integrador — Metodología de Sistemas II
Tecnicatura Universitaria en Programación (UTN)

## Descripción
Sistema de consola que permite registrar solicitudes de estudiantes (certificados, equivalencias, reclamos y constancias), clasificarlas por tipo, prioridad y estado, asignarles un responsable de área, buscarlas y generar un reporte básico. Los datos se guardan en un archivo JSON.

El repositorio documenta la evolución del sistema desde una versión inicial con problemas de calidad interna hasta una versión refactorizada que conserva el comportamiento externo.

## Funcionalidades
- Registrar solicitud.
- Cambiar estado: PENDIENTE → EN_PROCESO o RECHAZADA; EN_PROCESO → RESUELTA o RECHAZADA. Para pasar a EN_PROCESO debe tener responsable.
- Asignar responsable de área.
- Buscar solicitudes por estado, prioridad, tipo o legajo.
- Reporte por estado, prioridad y responsable.

## Tecnologías
- Python 3.10 o superior.
- Persistencia en archivo JSON.
- pytest para las pruebas automatizadas.
- Git y GitHub.

## Instalación y uso
```
git clone https://github.com/pao41/tpi-gestion-solicitudes.git
cd tpi-gestion-solicitudes
python sistema_solicitudes.py
```
Al ejecutarse por primera vez se crea `solicitudes.json` con tres responsables precargados. Todos los datos son sintéticos.

## Pruebas
```
pip install pytest
python -m pytest tests -v
```

## Estructura
| Archivo / carpeta | Contenido |
|---|---|
| `sistema_solicitudes.py` | Constantes, clase SolicitudNueva, GestorSolicitudes (reglas del negocio) y MenuConsola (interacción por consola). |
| `repositorio.py` | Interfaz RepositorioSolicitudes y clase RepositorioJSON (persistencia). |
| `tests/` | 21 pruebas automatizadas. |
| `docs/` | Diagnóstico, verificación de pruebas y code review. |

## Tags
| Tag | Hito |
|---|---|
| `estado-inicial` | Versión base del sistema. |
| `etapa-diagnostico` | Diagnóstico de deuda técnica y code smells. |
| `etapa-refactoring` | Refactorings R1 a R6 aplicados. |
| `etapa-pruebas` | Verificación del comportamiento antes y después. |
| `etapa-docs` | Code review y documentación. |
| `estado-refactorizado` | Estado final del código. |
