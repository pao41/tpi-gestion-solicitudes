# Verificación del comportamiento

Pruebas automatizadas: `tests/test_solicitudes.py` (pytest, patrón AAA).
Comando de ejecución: `python -m pytest tests -v`

## Resultado antes y después del refactoring

| Versión | Tag | Pruebas ejecutadas | Aprobadas | Fallidas |
|---|---|---|---|---|
| Versión inicial | `estado-inicial` | 21 | 21 | 0 |
| Versión refactorizada | `etapa-refactoring` | 21 | 21 | 0 |

## Casos cubiertos

| Operación | Cantidad de casos |
|---|---|
| Registrar solicitud | 6 |
| Asignar responsable | 3 |
| Cambiar estado | 5 |
| Buscar / filtrar | 4 |
| Reporte | 1 |
| Persistencia | 2 |
| **Total** | **21** |

## Ajustes realizados en las pruebas

Los casos de prueba y sus resultados esperados no se modificaron. Solo se ajustó la preparación:

- **R2 (Introduce Parameter Object):** la función auxiliar `registrar()` construye un objeto `SolicitudNueva`.
- **R3 (Move Method):** el gestor se crea con `RepositorioJSON("solicitudes.json")`.

## Verificación por refactoring

| Refactoring | Pruebas aprobadas |
|---|---|
| R1 Extract Method | 21 / 21 |
| R2 Introduce Parameter Object | 21 / 21 |
| R3 Move Method (persistencia) | 21 / 21 |
| R4 Move Method (menú) | 21 / 21 |
| R5 Constantes y tabla de transiciones | 21 / 21 |
| R6 Mejores nombres | 21 / 21 |
