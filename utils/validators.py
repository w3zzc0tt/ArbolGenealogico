import re
import datetime
from typing import Tuple, Optional

def validar_cedula(cedula: str) -> Tuple[bool, Optional[str]]:
    """Valida el formato de una cédula"""
    if not cedula:
        return False, "La cédula no puede estar vacía"
    
    if not re.match(r"^\d{9,12}$", cedula):
        return False, "La cédula debe ser numérica y tener entre 9 y 12 dígitos"
    
    return True, None

def validar_fecha(fecha_str: str, tipo: str = "nacimiento") -> Tuple[bool, Optional[str]]:
    """Valida que la fecha esté en el formato correcto y rango permitido"""
    if not fecha_str:
        if tipo == "nacimiento":
            return False, "La fecha de nacimiento es obligatoria"
        return True, None  # Fecha de fallecimiento puede ser opcional
    
    try:
        fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d")
    except ValueError:
        return False, f"Formato de fecha {tipo} inválido (debe ser YYYY-MM-DD)"
    
    # Rango permitido: 1820-01-01 a 2025-01-01
    min_fecha = datetime.datetime(1820, 1, 1)
    max_fecha = datetime.datetime(2025, 1, 1)
    
    if not (min_fecha <= fecha <= max_fecha):
        return False, f"La fecha de {tipo} debe estar entre 1820-01-01 y 2025-01-01"
    
    return True, None

def validar_fechas_coherentes(nacimiento: str, fallecimiento: Optional[str]) -> Tuple[bool, Optional[str]]:
    """Valida que las fechas sean coherentes (fallecimiento después de nacimiento)"""
    if not fallecimiento:
        return True, None
    
    try:
        fecha_nac = datetime.datetime.strptime(nacimiento, "%Y-%m-%d")
        fecha_fall = datetime.datetime.strptime(fallecimiento, "%Y-%m-%d")
        
        if fecha_fall <= fecha_nac:
            return False, "La fecha de fallecimiento debe ser posterior a la de nacimiento"
        
        return True, None
        
    except ValueError:
        return False, "Formato de fechas inválido"

def validar_genero(genero: str) -> Tuple[bool, Optional[str]]:
    """Valida que el género sea M o F"""
    if genero not in ["M", "F"]:
        return False, "El género debe ser 'M' (masculino) o 'F' (femenino)"
    return True, None

def validar_provincia(provincia: str) -> Tuple[bool, Optional[str]]:
    """Valida que la provincia sea válida"""
    provincias_validas = ["Alajuela", "Heredia", "San José", "Limón", "Puntarenas", "Guanacaste", "Cartago"]
    
    if provincia not in provincias_validas:
        return False, f"Provincia inválida. Debe ser una de: {', '.join(provincias_validas)}"
    return True, None

def validar_estado_civil(estado_civil: str) -> Tuple[bool, Optional[str]]:
    """Valida que el estado civil sea válido"""
    estados_validos = ["Casado/a", "Divorciado/a", "Soltero/a", "Viudo/a"]
    
    if estado_civil not in estados_validos:
        return False, f"Estado civil inválido. Debe ser uno de: {', '.join(estados_validos)}"
    return True, None

def validar_nombre(nombre: str, tipo: str = "nombre") -> Tuple[bool, Optional[str]]:
    """Valida que el nombre/apellido sea válido"""
    if not nombre:
        return False, f"El {tipo} no puede estar vacío"
    
    if len(nombre) < 2:
        return False, f"El {tipo} debe tener al menos 2 caracteres"
    
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-]+$", nombre):
        return False, f"El {tipo} solo puede contener letras, espacios y guiones"
    
    return True, None

def validar_persona_completa(cedula: str, nombre: str, apellido: str, 
                           fecha_nac: str, genero: str, provincia: str, 
                           estado_civil: str, fecha_fall: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """Valida todos los datos de una persona"""
    
    # Validar cédula
    valido, error = validar_cedula(cedula)
    if not valido:
        return False, error
    
    # Validar nombre
    valido, error = validar_nombre(nombre, "nombre")
    if not valido:
        return False, error
    
    # Validar apellido
    valido, error = validar_nombre(apellido, "apellido")
    if not valido:
        return False, error
    
    # Validar fecha de nacimiento
    valido, error = validar_fecha(fecha_nac, "nacimiento")
    if not valido:
        return False, error
    
    # Validar fecha de fallecimiento (si existe)
    if fecha_fall:
        valido, error = validar_fecha(fecha_fall, "fallecimiento")
        if not valido:
            return False, error
        
        # Validar coherencia entre fechas
        valido, error = validar_fechas_coherentes(fecha_nac, fecha_fall)
        if not valido:
            return False, error
    
    # Validar género
    valido, error = validar_genero(genero)
    if not valido:
        return False, error
    
    # Validar provincia
    valido, error = validar_provincia(provincia)
    if not valido:
        return False, error
    
    # Validar estado civil
    valido, error = validar_estado_civil(estado_civil)
    if not valido:
        return False, error
    
    return True, None
   ### Paso 5: Refactorizar el servicio de simulación