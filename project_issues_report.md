# Informe de Problemas, Errores y Defectos del Proyecto

## 1. Confusión entre `calculate_age` y `calculate_virtual_age`
- **Descripción**: El método `calculate_age` calcula la edad real basada en la fecha de nacimiento, mientras que `calculate_virtual_age` devuelve el atributo `virtual_age`. En el constructor, `virtual_age` se inicializa con el valor devuelto por `calculate_age()`. Además, en `main.py` y `gui/app.py` se menciona que se debe usar `calculate_virtual_age()` en lugar de `calculate_age()`, lo que sugiere que hay un uso incorrecto en alguna parte del código.
- **Impacto**: Puede causar inconsistencias en la simulación si se usan los métodos incorrectamente.

## 2. Inicialización de `virtual_age`
- **Descripción**: En el constructor, `self.virtual_age = self.calculate_age()` inicializa la edad virtual con la edad real. Esto podría no ser lo deseado si se quiere simular una edad diferente.
- **Impacto**: La simulación no reflejará correctamente la edad virtual de la persona.

## 3. Uso inconsistente de `calculate_age` vs `calculate_virtual_age`
- **Descripción**: Algunos métodos como `get_family_tree` y `get_statistics` usan `calculate_age()` para mostrar la edad real, mientras que otros como `can_have_children` usan `calculate_virtual_age()`. Es importante mantener la consistencia en todo el código.
- **Impacto**: Puede causar confusión sobre qué edad se está mostrando o usando en cada parte de la aplicación.

## 4. Lógica de estado civil en `update_relationships`
- **Descripción**: El método `update_relationships` actualiza el estado civil basado en si la persona está viva y si su pareja está viva. Sin embargo, hay un error lógico: si una persona tiene una pareja, su estado civil debería ser "Casado/a" independientemente de si su pareja está viva o no. El estado de "Viudo/a" debería aplicarse solo si la pareja ha fallecido.
- **Impacto**: El estado civil de las personas puede no reflejar correctamente su situación real.

## 5. Validación de integridad
- **Descripción**: El método `validate_integrity` valida la integridad de las relaciones familiares. Es una buena práctica, pero hay que asegurarse de que se llame en los momentos adecuados.
- **Impacto**: Si no se llama regularmente, pueden acumularse errores en las relaciones familiares.

## 6. Serialización de relaciones
- **Descripción**: Los métodos `to_dict` y `from_dict` se usan para serializar y deserializar la persona. Es importante asegurarse de que todos los atributos se manejen correctamente, especialmente las relaciones que son referencias a otras personas.
- **Impacto**: Si no se manejan correctamente, se pueden perder relaciones al guardar y cargar datos.

## 7. Manejo de Importaciones
- **Descripción**: La importación de `FamilyGraphVisualizer` se maneja con un bloque `try-except`, lo que significa que si no se puede importar, se establece `HAS_VISUALIZER` en `False`, pero no se maneja adecuadamente el caso en que se necesita el visualizador.
- **Impacto**: Puede causar errores en tiempo de ejecución si se intenta usar el visualizador sin verificar si está disponible.

## 8. Validación de Género
- **Descripción**: En el método `abrir_formulario_relacion`, hay validaciones de género que podrían ser más robustas.
- **Impacto**: No se manejan otros posibles valores o errores de entrada.

## 9. Errores de Sintaxis
- **Descripción**: Hay un error de sintaxis en la línea que pregunta al usuario si desea eliminar a una persona en el método `eliminar_persona`.
- **Impacto**: Causará un error de sintaxis y evitará que la aplicación funcione correctamente.

## 10. Manejo de Errores
- **Descripción**: El método `draw_tree` tiene un bloque `try-except` que captura excepciones, pero no proporciona información detallada sobre el error.
- **Impacto**: Dificulta la depuración.

## 11. Uso de `messagebox`
- **Descripción**: Se utilizan cuadros de mensaje para mostrar errores o información, pero no hay un manejo adicional para continuar el flujo de la aplicación.
- **Impacto**: Puede causar confusión al usuario.

## 12. Dependencias Faltantes
- **Descripción**: El archivo `main.py` menciona que `customtkinter` debe ser instalado, pero no hay un manejo adecuado para verificar si todas las dependencias necesarias están instaladas.
- **Impacto**: Puede causar fallos en la ejecución si faltan dependencias.

## 13. Estructura del Proyecto
- **Descripción**: El código asume que la estructura del proyecto es correcta, pero no hay validaciones para verificar que todos los archivos necesarios estén presentes.
