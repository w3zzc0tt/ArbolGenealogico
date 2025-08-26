# utils/validators.py - VERSIÓN CORREGIDA
import re
import datetime
from typing import Tuple, Optional

# Mapeo de provincias a dígitos de cédula
PROVINCIAS_DIGITOS = {
    "San José": "1",
    "Alajuela": "2",
    "Cartago": "3",
    "Heredia": "4",
    "Guanacaste": "5",
    "Puntarenas": "6",
    "Limón": "7"
}

def validar_cedula(cedula: str, provincia: str) -> Tuple[bool, Optional[str]]:
    """Valida el formato completo de una cédula costarricense"""
    if not cedula:
        return False, "La cédula no puede estar vacía"
    
    # Verificar que sea numérica
    if not cedula.isdigit():
        return False, "La cédula debe contener solo números"
    
    # Verificar longitud
    if not (9 <= len(cedula) <= 12):
        return False, "La cédula debe tener entre 9 y 12 dígitos"
    
    # Verificar que el primer dígito coincida con la provincia
    if provincia in PROVINCIAS_DIGITOS:
        digito_esperado = PROVINCIAS_DIGITOS[provincia]
        if cedula[0] != digito_esperado:
            provincia_correcta = next((prov for prov, dig in PROVINCIAS_DIGITOS.items() 
                                    if dig == cedula[0]), None)
            if provincia_correcta:
                return False, f"Error de provincia: La cédula {cedula} corresponde a {provincia_correcta}, no a {provincia}"
            else:
                return False, f"El primer dígito de la cédula ({cedula[0]}) no corresponde a ninguna provincia válida"
    
    return True, None

def validar_fecha(fecha_str: str, tipo: str = "nacimiento") -> Tuple[bool, Optional[str]]:
    """Valida que la fecha esté en el formato correcto y rango permitido"""
    if not fecha_str:
        if tipo == "nacimiento":
            return False, "La fecha de nacimiento es obligatoria"
        return True, None  # Fecha de fallecimiento puede ser opcional
    
    # Verificar formato básico
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", fecha_str):
        return False, f"Formato de fecha {tipo} inválido. Use YYYY-MM-DD"
    
    try:
        fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d")
    except ValueError:
        return False, f"Formato de fecha {tipo} inválido. Use YYYY-MM-DD"
    
    # RANGO CORREGIDO: 1810-01-01 a fecha actual + 1 año
    min_fecha = datetime.datetime(1810, 1, 1)
    max_fecha = datetime.datetime.now() + datetime.timedelta(days=365)
    
    if fecha < min_fecha:
        return False, f"La fecha de {tipo} no puede ser anterior a 1810-01-01"
    if fecha > max_fecha:
        return False, f"La fecha de {tipo} no puede ser posterior a {max_fecha.strftime('%Y-%m-%d')}"
    
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
        
        # Verificar que la persona no tenga más de 120 años
        edad = fecha_fall.year - fecha_nac.year - ((fecha_fall.month, fecha_fall.day) < (fecha_nac.month, fecha_nac.day))
        if edad > 120:
            return False, "Edad imposible: La persona no puede tener más de 120 años"
            
        return True, None
    except ValueError:
        return False, "Formato de fechas inválido"

def validar_genero(genero: str) -> Tuple[bool, Optional[str]]:
    """CORREGIDO: Ahora acepta tanto M/F como Masculino/Femenino"""
    generos_validos = ["M", "F", "Masculino", "Femenino"]
    if genero not in generos_validos:
        return False, "Debe seleccionar un género válido (Masculino/Femenino)"
    return True, None

def validar_provincia(provincia: str) -> Tuple[bool, Optional[str]]:
    """Valida que la provincia sea válida"""
    provincias_validas = list(PROVINCIAS_DIGITOS.keys())
    if provincia not in provincias_validas:
        return False, f"Provincia inválida. Debe ser una de: {', '.join(provincias_validas)}"
    return True, None

def validar_estado_civil(estado_civil: str) -> Tuple[bool, Optional[str]]:
    """Valida que el estado civil sea válido"""
    estados_validos = ["Casado/a", "Divorciado/a", "Soltero/a", "Viudo/a", "Unión Libre"]
    if estado_civil not in estados_validos:
        return False, f"Estado civil inválido. Debe ser uno de: {', '.join(estados_validos)}"
    return True, None

def validar_nombre(nombre: str, tipo: str = "nombre") -> Tuple[bool, Optional[str]]:
    """Valida que el nombre/apellido sea válido"""
    if not nombre:
        return False, f"El {tipo} no puede estar vacío"
    
    if len(nombre) < 2:
        return False, f"El {tipo} debe tener al menos 2 caracteres"
    
    # Permitir solo letras, espacios y guiones (sin números)
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-]+$", nombre):
        return False, f"El {tipo} solo puede contener letras, espacios y guiones (sin números)"
    
    # Verificar que no tenga espacios consecutivos
    if "  " in nombre:
        return False, f"El {tipo} no puede contener espacios consecutivos"
    
    # Verificar que no comience o termine con espacio o guion
    if nombre[0] in " -" or nombre[-1] in " -":
        return False, f"El {tipo} no puede comenzar ni terminar con espacio o guion"
    
    return True, None

def validar_persona_completa(cedula: str, nombre: str, apellido: str, 
                           fecha_nac: str, genero: str, provincia: str, 
                           estado_civil: str, fecha_fall: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """Valida todos los datos de una persona"""
    # Validar cédula (ahora con provincia)
    valido, error = validar_cedula(cedula, provincia)
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