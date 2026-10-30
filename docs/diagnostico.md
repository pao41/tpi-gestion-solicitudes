# Diagnóstico de deuda técnica y code smells

Versión analizada: tag `estado-inicial` — archivo `sistema_solicitudes.py`.

## Criterio de prioridad
- **Alta:** genera riesgo de errores o pérdida de datos, o condiciona el resto de las mejoras.
- **Media:** dificulta el mantenimiento y la extensión del sistema.
- **Baja:** afecta la legibilidad sin riesgo funcional directo.

## Code smells identificados

| N° | Smell | Ubicación | Prioridad |
|---|---|---|---|
| S1 | Clase Gigante (Large Class) | Clase `GestorSolicitudes` (completa) | Alta |
| S2 | Método Largo (Long Method) | `registrar_solicitud()`, `reporte()` y `menu()` | Media |
| S3 | Demasiados Parámetros (Long Parameter List) | Firma de `registrar_solicitud()` | Media |
| S4 | Código Duplicado (Duplicated Code) | `registrar_solicitud()`, `cambiar_estado()` y `asignar_responsable()` | Alta |
| S5 | Obsesión por Primitivos (Primitive Obsession) | `registrar_solicitud()` y `cambiar_estado()` | Media |
| S6 | Strings hardcodeados | `registrar_solicitud()`, `cambiar_estado()`, `asignar_responsable()`, `reporte()`, `cargar()` y `guardar()` | Baja |
| S7 | Uso excesivo de if-else | `cambiar_estado()`, `buscar()`, `reporte()` y `menu()` | Alta |
| S8 | Nombres poco descriptivos | Todo el archivo, en especial `reporte()` | Baja |
| S9 | Retorno de códigos de error | `registrar_solicitud()`, `cambiar_estado()`, `asignar_responsable()` y `buscar()` | Media |
| S10 | Catch vacío (silencio de errores) | `cargar()` y `menu()` | Alta |
| S11 | Alto acoplamiento con persistencia y consola | `registrar_solicitud()`, `cambiar_estado()`, `asignar_responsable()`, `buscar()` y `menu()` | Alta |

## Orden de corrección propuesto
1. Prioridad alta: S10, S4, S11, S1, S7.
2. Prioridad media: S2, S3, S5, S9.
3. Prioridad baja: S6, S8.
