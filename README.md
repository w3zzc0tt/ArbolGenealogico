# 🌳 Árbol Genealógico - Proyecto Completo

## 📋 Descripción del Proyecto

Aplicación de escritorio desarrollada en Python para la gestión y visualización de árboles genealógicos familiares, con capacidades de simulación temporal y análisis de relaciones.

## ✨ Características Principales

### 🏠 **Gestión Familiar**
- ✅ Creación y edición de personas con datos completos
- ✅ Gestión de relaciones familiares (matrimonios, hijos, divorcios)
- ✅ Validación de datos y coherencia temporal
- ✅ **Límite generacional**: Restringido a 5 generaciones (Bisabuelos → Nietos)

### 🎯 **Sistema de Consultas**
- ✅ 8 tipos de consultas genealógicas especializadas
- ✅ Análisis de relaciones entre personas
- ✅ Búsquedas específicas (primos, antepasados, descendientes)
- ✅ Estadísticas familiares avanzadas

### 🔮 **Simulación Temporal**
- ✅ Motor de simulación de eventos familiares
- ✅ Generación automática de nacimientos, matrimonios y defunciones
- ✅ **Timeline visual** integrado en el panel de simulación
- ✅ Respeta límites generacionales durante la simulación

### 📊 **Visualización**
- ✅ Grafo interactivo del árbol familiar con NetworkX
- ✅ Timeline temporal de eventos familiares
- ✅ Historial de acciones con navegación temporal

### 💾 **Persistencia**
- ✅ Guardado automático en formato JSON
- ✅ Sistema de backups automáticos
- ✅ Exportación e importación de datos familiares

## 🏗️ Arquitectura del Proyecto

```
ArbolGenealogico/
├── 📄 main.py                    # Punto de entrada principal
├── 📄 requirements.txt           # Dependencias del proyecto
├── 🔧 test_*.py                 # Scripts de testing
│
├── 📁 gui/                      # Interfaz gráfica
│   ├── app.py                   # Aplicación principal
│   ├── forms.py                 # Formularios de entrada
│   ├── consultas_panel.py       # Panel de consultas rediseñado
│   ├── family_manager_panel.py  # Gestión familiar
│   ├── simulation_panel.py      # Simulación con timeline
│   └── history_panel.py         # Historial de acciones
│
├── 📁 models/                   # Modelos de datos
│   ├── person.py               # Modelo de persona
│   ├── family.py               # Modelo de familia
│   ├── family_manager.py       # Gestor principal
│   └── simulation_config.py    # Configuración de simulación
│
├── 📁 services/                 # Lógica de negocio
│   ├── simulacion_service.py   # 🔥 Motor de simulación con límites
│   ├── persistence_service.py  # Persistencia de datos
│   ├── persona_service.py      # Servicios de personas
│   ├── relacion_service.py     # Servicios de relaciones
│   └── utils_service.py        # Utilidades diversas
│
├── 📁 utils/                    # Utilidades
│   ├── graph_visualizer.py     # Visualización de grafos
│   ├── timeline_visualizer.py  # 🔥 Timeline temporal (movido aquí)
│   ├── gedcom_parser.py        # Parser GEDCOM
│   └── validators.py           # Validadores de datos
│
├── 📁 data/                     # Datos persistentes
│   ├── families.json           # Datos familiares principales
│   ├── manager_state.json      # Estado del gestor
│   └── backups/                # Copias de seguridad automáticas
│
└── 📁 simulations/             # Archivos de simulación
    ├── current.ged             # Simulación actual
    └── ejemplo.ged             # Ejemplo de datos
```

## 🎯 Funcionalidades Implementadas

### ✅ **Completadas y Validadas**

#### 1. **Límite Generacional (Reciente)**
- **Implementación**: Función `_verificar_limite_generacional()` en `SimulacionService`
- **Validación Manual**: Función `_verificar_limite_generacional_manual()` en formularios
- **Alcance**: 5 generaciones máximo (Bisabuelos → Nietos)
- **Estado**: ✅ **Validado con testing completo**

#### 2. **Timeline Visual Reubicado**
- **Origen**: Movido desde `history_panel.py` 
- **Destino**: `simulation_panel.py` con integración completa
- **Funcionalidad**: Visualización temporal de eventos durante simulación
- **Estado**: ✅ **Implementado y funcional**

#### 3. **Panel de Consultas Rediseñado**
- **Problema Original**: Botón "Ejecutar Consulta" no visible
- **Solución**: Rediseño completo del layout y organización
- **Características**: 8 consultas categorizadas + ejecución múltiple
- **Estado**: ✅ **Rediseño completo documentado**

#### 4. **Sistema de Fechas Realistas**
- **Problema Original**: Fechas fijas 1-1 poco realistas
- **Solución**: Generación aleatoria de días y meses
- **Alcance**: Nacimientos, matrimonios y defunciones
- **Estado**: ✅ **Implementado en simulación**

## 🔧 Dependencias

```bash
pip install -r requirements.txt
```

**Librerías principales:**
- `customtkinter` >= 5.2.0 - Interfaz gráfica moderna
- `networkx` >= 3.0 - Análisis y visualización de grafos
- `matplotlib` >= 3.7.0 - Gráficos y visualizaciones
- `Pillow` >= 10.0.0 - Procesamiento de imágenes
- `python-dateutil` >= 2.8.0 - Manejo avanzado de fechas

## 🚀 Ejecución

```bash
# Desde el directorio del proyecto
python main.py
```

## 🧪 Testing

### **Validación de Límites Generacionales**
```bash
python test_correct_limit.py      # Test completo de 5 generaciones
python test_generational_limit.py # Test básico de límites
```

### **Resultados de Testing Recientes**
```
✅ CORRECTO: Se prohibió correctamente la generación de bisnietos
✅ CORRECTO: Se permitió que los hijos (nivel 3) tengan descendencia
```

## 📈 Estado del Proyecto

### 🎯 **Completitud: 100%**

| Componente | Estado | Descripción |
|------------|--------|-------------|
| 🏠 **Gestión Familiar** | ✅ **Completo** | CRUD completo con validaciones |
| 🔮 **Simulación** | ✅ **Completo** | Motor con límites generacionales |
| 📊 **Visualización** | ✅ **Completo** | Grafos + Timeline integrado |
| 🎯 **Consultas** | ✅ **Completo** | 8 consultas + panel rediseñado |
| 💾 **Persistencia** | ✅ **Completo** | JSON + Backups automáticos |
| 🧪 **Testing** | ✅ **Completo** | Validación exhaustiva de límites |

### 🔄 **Últimas Actualizaciones**
- **2025-08-31**: ✅ Límite generacional implementado y validado
- **2025-08-31**: ✅ Timeline reubicado a simulación  
- **2025-08-31**: ✅ Fechas de nacimiento realistas
- **2025-08-31**: ✅ Panel de consultas rediseñado

## 🎖️ **Proyecto Completo y Funcional**

La aplicación está **100% funcional** con todas las características solicitadas implementadas y validadas. El sistema respeta los límites generacionales, ofrece simulación temporal realista, y proporciona una interfaz intuitiva para la gestión genealógica familiar.

---
*Última actualización: 31 de Agosto, 2025*
