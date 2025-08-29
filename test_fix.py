#!/usr/bin/env python3
# test_fix.py - Script para verificar que la corrección funciona

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.family import Family
from models.person import Person
from services.relacion_service import RelacionService

def test_pareja_sin_intereses():
    """Prueba que se pueda registrar una pareja sin intereses compartidos en modo manual"""
    
    # Crear familia
    family = Family(id="test_family", name="Familia de Prueba")
    
    # Crear dos personas sin intereses en común
    person1 = Person(
        cedula="123456789",
        first_name="Juan",
        last_name="Pérez",
        birth_date="1990-01-01",
        gender="Masculino",
        province="San José",
        marital_status="Soltero"
    )
    person1.virtual_age = 30
    person1.interests = ["Fútbol", "Música"]  # Solo 2 intereses
    
    person2 = Person(
        cedula="987654321",
        first_name="María",
        last_name="González",
        birth_date="1992-01-01",
        gender="Femenino",
        province="San José",
        marital_status="Soltera"
    )
    person2.virtual_age = 28
    person2.interests = ["Lectura", "Cocina"]  # Diferentes intereses, SIN INTERESES EN COMÚN
    
    # Agregar a la familia
    family.add_or_update_member(person1)
    family.add_or_update_member(person2)
    
    print("=== PRUEBA: Registrar pareja SIN intereses compartidos ===")
    print(f"Persona 1: {person1.first_name} - Intereses: {person1.interests}")
    print(f"Persona 2: {person2.first_name} - Intereses: {person2.interests}")
    print(f"Intereses en común: {set(person1.interests) & set(person2.interests)}")
    
    # Intentar registrar pareja en modo MANUAL (es_simulacion=False por defecto)
    print("\n--- Probando en modo MANUAL (construcción de árbol) ---")
    success, message = RelacionService.registrar_pareja(family, person1.cedula, person2.cedula)
    print(f"Resultado: {'✅ ÉXITO' if success else '❌ FALLO'}")
    print(f"Mensaje: {message}")
    
    if success:
        print(f"Estado civil de {person1.first_name}: {person1.marital_status}")
        print(f"Estado civil de {person2.first_name}: {person2.marital_status}")
        print(f"Cónyuge de {person1.first_name}: {person1.spouse.first_name if person1.spouse else 'Ninguno'}")
        print(f"Cónyuge de {person2.first_name}: {person2.spouse.first_name if person2.spouse else 'Ninguno'}")
    
    # Resetear para la segunda prueba
    person1.spouse = None
    person2.spouse = None
    person1.marital_status = "Soltero"
    person2.marital_status = "Soltera"
    
    # Intentar registrar pareja en modo SIMULACIÓN (es_simulacion=True)
    print("\n--- Probando en modo SIMULACIÓN ---")
    success_sim, message_sim = RelacionService.registrar_pareja(family, person1.cedula, person2.cedula, es_simulacion=True)
    print(f"Resultado: {'✅ ÉXITO' if success_sim else '❌ FALLO'}")
    print(f"Mensaje: {message_sim}")
    
    print("\n=== RESUMEN ===")
    print(f"Modo MANUAL: {'✅ PERMITE la unión' if success else '❌ RECHAZA la unión'}")
    print(f"Modo SIMULACIÓN: {'✅ PERMITE la unión' if success_sim else '❌ RECHAZA la unión'}")
    
    # Verificar que el comportamiento es el esperado
    if success and not success_sim:
        print("\n🎉 ¡CORRECCIÓN EXITOSA! El sistema ahora permite crear parejas manualmente sin intereses compartidos,")
        print("   pero sigue aplicando las validaciones estrictas en las simulaciones.")
        return True
    else:
        print("\n⚠️  Algo no funcionó como se esperaba.")
        return False

if __name__ == "__main__":
    test_pareja_sin_intereses()
