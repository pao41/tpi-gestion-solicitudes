# Code review

Revisión técnica del repositorio sobre la versión refactorizada (tag `etapa-refactoring`), comparada con la versión inicial (tag `estado-inicial`).

## 1. Checklist técnico

| Categoría | Criterio | Versión inicial | Versión refactorizada | Justificación |
|---|---|---|---|---|
| Lógica y funcionalidad | ¿El código hace lo que debe hacer? | Sí | Sí | Las 21 pruebas se aprueban en ambas versiones. |
| Lógica y funcionalidad | ¿Cubre casos de borde? | Parcial | Sí | Se verifican datos inválidos, transiciones no permitidas, solicitudes cerradas y archivo dañado. |
| Legibilidad | ¿Los nombres son descriptivos? | No | Sí | Se reemplazaron variables de una o dos letras (R6). |
| Legibilidad | ¿El código resulta legible para otro desarrollador? | No | Sí | Métodos cortos con un comentario que indica su propósito. |
| Diseño y arquitectura | ¿Las funciones poseen una única responsabilidad? | No | Sí | registrar_solicitud() se dividió en métodos con una única tarea (R1). |
| Diseño y arquitectura | ¿Existe duplicación innecesaria? | Sí | No | Se centralizaron la búsqueda por id, la validación del legajo y el guardado (R1, R3). |
| Diseño y arquitectura | ¿El código es fácilmente extensible? | No | Sí | Estados y transiciones definidos como constantes (R5). |
| Diseño y arquitectura | ¿Existe acoplamiento innecesario? | Alto | Bajo | El gestor depende de la abstracción RepositorioSolicitudes (R3). |
| Diseño y arquitectura | ¿La cohesión es adecuada? | Baja | Alta | Tres clases con responsabilidades separadas: menú, gestor y repositorio (R3, R4). |
| Diseño y arquitectura | ¿Se respetan los principios SOLID? | No | Sí | SRP, OCP, ISP, LSP y DIP aplicados (etapa 4). |
| Diseño y arquitectura | ¿Hay manejo correcto de errores? | No | Parcial | Se eliminaron los except vacíos y sin tipo; los códigos de error (S9) quedan como mejora pendiente. |
| Seguridad | ¿Hay datos sensibles expuestos? | No | No | Se utilizan datos sintéticos; no hay credenciales en el código. |
| Rendimiento | ¿Hay bucles innecesarios? | Sí | No | Se eliminaron los recorridos repetidos de búsqueda; los recorridos restantes son adecuados para el volumen de datos. |

## 2. Observaciones y feedback

| N.º | Observación | Feedback | Estado |
|---|---|---|---|
| O1 | Las comparaciones con None usan `==` en cambiar_estado() y asignar_responsable(). | La guía de estilo de Python recomienda `is None`, que es la forma correcta de comparar con None y la que detecta el linter. Se propone reemplazar `== None` por `is None`. | Corregida |
| O2 | Los métodos registrar_solicitud(), cambiar_estado(), asignar_responsable(), buscar() y reporte() no tienen comentario, a diferencia del resto. | Agregar un comentario de una línea con el propósito de cada método mantiene la documentación uniforme y facilita la lectura. | Corregida |
| O3 | Los métodos del gestor siguen devolviendo -1, False o None ante un error e imprimen los mensajes (S9). | Se reconoce que el comportamiento es correcto y está cubierto por las pruebas. Como mejora, se propone reemplazar los códigos de error por excepciones y mostrar los mensajes desde MenuConsola. | Pendiente |
| O4 | La separación en capas y el uso de la interfaz RepositorioSolicitudes. | Aspecto positivo: permite cambiar el almacenamiento sin modificar el gestor y facilita las pruebas. | Sin cambios |

## 3. Correcciones realizadas

- Commit `refactor: comparaciones con None y comentarios segun code review`: resuelve O1 y O2.
- Verificación: 21 pruebas aprobadas después de la corrección.

## 4. Criterios de aceptación técnica (TAC)

| Criterio | Cumple | Evidencia |
|---|---|---|
| El código se ejecuta y pasa todas las pruebas | Sí | 21 pruebas aprobadas (docs/verificacion.md). |
| No rompe funcionalidades existentes | Sí | Mismos resultados que sobre estado-inicial. |
| Respeta principios de diseño (SOLID) | Sí | Etapa 4 del informe. |
| Cumple los estándares de código (nombres, estilo) | Sí | Nombres descriptivos y comparaciones con None corregidas. |
| Manejo correcto de errores | Parcial | Sin except vacíos; S9 queda como mejora pendiente. |
| No genera deuda técnica innecesaria | Sí | Los smells del diagnóstico se resolvieron, excepto S9. |
| Documentación | Sí | README.md y carpeta docs. |
| Atomicidad | Sí | Un commit por refactoring, integrados mediante Pull Requests revisados. |
