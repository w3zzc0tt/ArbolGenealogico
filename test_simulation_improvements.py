#!/usr/bin/env python3
"""
Script de prueba para verificar las mejoras en la simulación
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.family import Family
from models.person import Person
from models.simulation_config import SimulationConfig
from services.simulacion_service import SimulacionService
from services.relacion_service import RelacionService

def crear_familia_prueba():
    """Crea una familia de prueba con algunos miembros solteros"""
    family = Family("test_family", "Familia de Prueba")
    family.current_year = 2025
    
    # Crear algunas personas solteras de diferentes edades
    personas = [
        Person("123456789", "Carlos", "Mendez", "1990-01-01", "M", "San José", marital_status="Soltero/a"),
        Person("987654321", "Ana", "Torres", "1992-01-01", "F", "Alajuela", marital_status="Soltero/a"),
        Person("456789123", "Luis", "García", "1985-01-01", "M", "Cartago", marital_status="Soltero/a"),
        Person("789123456", "María", "López", "1995-01-01", "F", "Heredia", marital_status="Soltero/a"),
    ]
    
    for person in personas:
        person.virtual_age = family.current_year - int(person.birth_date.split('-')[0])
        person.interests = ["Trabajo", "Familia", "Deportes", "Lectura"]
        person.emotional_health = 75
        family.add_or_update_member(person)
    
    return family

def test_generacion_parejas_externas():
    """Prueba la generación de parejas externas"""
    print("=== PRUEBA: Generación de Parejas Externas ===")
    family = crear_familia_prueba()
    
    print(f"Miembros iniciales: {len(family.members)}")
    for member in family.members:
        print(f"  - {member.first_name} {member.last_name}, {member.virtual_age} años, {member.gender}")
    
    # Intentar encontrar parejas para todos los solteros
    solteros = [p for p in family.members if p.marital_status == "Soltero/a"]
    
    for person in solteros:
        print(f"\nBuscando pareja para {person.first_name}...")
        success = SimulacionService.intentar_encontrar_pareja(person, family)
        
        if success and person.spouse:
            print(f"  ✅ {person.first_name} encontró pareja: {person.spouse.first_name} {person.spouse.last_name}")
            print(f"     Compatibilidad: {SimulacionService.calcular_compatibilidad_total(person, person.spouse)['total']:.1f}%")
            print(f"     Intereses comunes: {set(person.interests) & set(person.spouse.interests)}")
        else:
            print(f"  ❌ {person.first_name} no encontró pareja")
    
    print(f"\nMiembros finales: {len(family.members)}")
    for member in family.members:
        estado = f"Casado/a con {member.spouse.first_name}" if member.spouse else "Soltero/a"
        print(f"  - {member.first_name} {member.last_name}, {member.virtual_age} años, {estado}")

def test_nacimientos_con_apellidos():
    """Prueba los nacimientos con lógica correcta de apellidos"""
    print("\n\n=== PRUEBA: Nacimientos con Apellidos Correctos ===")
    family = crear_familia_prueba()
    
    # Crear una pareja
    padre = family.get_member_by_cedula("123456789")  # Carlos Mendez
    madre = family.get_member_by_cedula("987654321")   # Ana Torres
    
    # Registrar como pareja
    success, message = RelacionService.registrar_pareja(family, padre.cedula, madre.cedula, es_simulacion=True)
    print(f"Pareja registrada: {success} - {message}")
    
    if success:
        print(f"Padre: {padre.first_name} {padre.last_name}")
        print(f"Madre: {madre.first_name} {madre.last_name}")
        
        # Simular nacimientos
        for i in range(3):
            success, message = SimulacionService.simular_nacimiento_mejorado(madre, padre, family)
            if success:
                print(f"  ✅ {message}")
                # Encontrar el bebé recién nacido (último agregado)
                baby = family.members[-1]
                print(f"     Apellido completo: {baby.last_name}")
                print(f"     Edad virtual: {baby.virtual_age}")
                print(f"     Intereses: {baby.interests}")
            else:
                print(f"  ❌ Error en nacimiento: {message}")

def test_poblacion_externa():
    """Prueba la generación de población externa"""
    print("\n\n=== PRUEBA: Generación de Población Externa ===")
    family = crear_familia_prueba()
    
    print(f"Miembros antes: {len(family.members)}")
    
    # Generar población externa
    nuevas_personas = SimulacionService.generar_poblacion_externa(family, 8)
    
    print(f"Miembros después: {len(family.members)}")
    print(f"Personas generadas: {len(nuevas_personas)}")
    
    print("\nNuevas personas generadas:")
    for person in nuevas_personas:
        print(f"  - {person.first_name} {person.last_name}, {person.virtual_age} años, {person.gender}")
        print(f"    Provincia: {person.province}, Intereses: {len(person.interests)}")

def test_ciclo_completo():
    """Prueba un ciclo completo de simulación"""
    print("\n\n=== PRUEBA: Ciclo Completo de Simulación ===")
    family = crear_familia_prueba()
    
    # Generar algo de población externa primero
    SimulacionService.generar_poblacion_externa(family, 6)
    
    config = SimulationConfig()
    config.find_partner_probability = 0.8  # Alta probabilidad para pruebas
    config.birth_probability = 0.6
    
    print(f"Iniciando simulación con {len(family.members)} miembros")
    
    # Ejecutar varios ciclos
    for ciclo in range(3):
        print(f"\n--- Ciclo {ciclo + 1} ---")
        eventos = SimulacionService.ejecutar_ciclo_completo(family, config)
        
        for evento in eventos:
            print(f"  {evento}")
        
        # Estadísticas del ciclo
        vivos = len(family.get_living_members())
        casados = len([p for p in family.get_living_members() if p.spouse])
        print(f"  Estado: {vivos} vivos, {casados} casados")

if __name__ == "__main__":
    print("Iniciando pruebas de mejoras de simulación...\n")
    
    try:
        test_generacion_parejas_externas()
        test_nacimientos_con_apellidos()
        test_poblacion_externa()
        test_ciclo_completo()
        
        print("\n\n🎉 ¡Todas las pruebas completadas exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
