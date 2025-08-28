# services/utils_service.py
from typing import Tuple
from models.family import Family
from models.person import Person

def verificar_requisitos_union(person1: Person, person2: Person, family: Family) -> Tuple[bool, str]:
    """
    Verifica todos los requisitos para una unión de pareja
    
    Returns:
        Tuple[bool, str]: (Es compatible, Mensaje de resultado)
    """
    # ✅ IMPORTACIÓN LOCAL CORREGIDA
    from services.simulacion_service import SimulacionService
    
    # 1. Verificar edad mínima (18 años)
    if person1.calculate_virtual_age() < 18:
        return False, f"{person1.first_name} debe ser mayor de 18 años ({person1.calculate_virtual_age()} años)"
    if person2.calculate_virtual_age() < 18:
        return False, f"{person2.first_name} debe ser mayor de 18 años ({person2.calculate_virtual_age()} años)"
    
    # 2. Verificar estado civil (no pueden estar unidos a otra persona)
    if person1.has_partner():
        return False, f"{person1.first_name} ya está en una relación"
    if person2.has_partner():
        return False, f"{person2.first_name} ya está en una relación"
    
    # 3. Verificar diferencia de edad (máximo 15 años)
    age_diff = abs(person1.calculate_virtual_age() - person2.calculate_virtual_age())
    if age_diff > 15:
        return False, f"Diferencia de edad excesiva ({age_diff} años). Máximo permitido: 15 años"
    
    # 4. Verificar compatibilidad genética
    if not SimulacionService.es_compatible_geneticamente(person1, person2):
        return False, "Incompatibilidad genética detectada. No se recomienda la unión por riesgos en descendencia"
    
    # 5. Verificar compatibilidad emocional (intereses en común)
    common_interests = set(person1.interests) & set(person2.interests)
    if len(common_interests) < 2:
        return False, f"Se requieren al menos 2 intereses en común. Tienen {len(common_interests)} interés(es) compartido(s)"
    
    # 6. Verificar índice de compatibilidad
    compatibility = SimulacionService.calcular_compatibilidad_total(person1, person2)
    if not compatibility['compatible']:
        return False, f"Índice de compatibilidad insuficiente ({compatibility['total']:.1f}%). Mínimo requerido: 70%"
    
    return True, f"✅ {person1.first_name} y {person2.first_name} cumplen con todos los requisitos para formar pareja"

def calcular_compatibilidad_total(person1: Person, person2: Person) -> dict:
    """
    Sistema completo de compatibilidad con 4 factores principales
    
    Returns:
        dict: Resultados de la compatibilidad
    """
    # ✅ IMPORTACIÓN LOCAL CORREGIDA
    from services.simulacion_service import SimulacionService
    
    return SimulacionService.calcular_compatibilidad_total(person1, person2)