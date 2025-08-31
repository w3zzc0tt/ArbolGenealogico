#!/usr/bin/env python3
"""
Script de prueba para verificar el límite generacional
Crea una familia de 5 generaciones para probar las limitaciones
"""

from models.family import Family
from models.person import Person
from services.simulacion_service import SimulacionService
import datetime

def create_test_family_with_5_generations():
    """Crea una familia de prueba con 5 generaciones completas"""
    
    # Crear familia
    test_family = Family(
        id=999,
        name="Familia Prueba Generacional"
    )
    test_family.description = "Familia de prueba para verificar límites generacionales"
    
    # GENERACIÓN 0 - BISABUELOS (Nivel 0)
    bisabuelo = Person(
        cedula="100000001",
        first_name="Antonio",
        last_name="García López",
        birth_date="1900-01-01",
        gender="M",
        province="San José",
        marital_status="Casado/a"
    )
    
    bisabuela = Person(
        cedula="100000002", 
        first_name="Carmen",
        last_name="Morales Jiménez",
        birth_date="1905-01-01",
        gender="F",
        province="San José",
        marital_status="Casado/a"
    )
    
    # GENERACIÓN 1 - ABUELOS (Nivel 1)
    abuelo = Person(
        cedula="100000003",
        first_name="José",
        last_name="García Morales",
        birth_date="1925-01-01",
        gender="M",
        province="San José",
        marital_status="Casado/a"
    )
    
    abuela = Person(
        cedula="100000004",
        first_name="María",
        last_name="Fernández Castro",
        birth_date="1930-01-01",
        gender="F",
        province="San José",
        marital_status="Casado/a"
    )
    
    # GENERACIÓN 2 - PADRES (Nivel 2)
    padre = Person(
        cedula="100000005",
        first_name="Carlos",
        last_name="García Fernández",
        birth_date="1955-01-01",
        gender="M",
        province="San José",
        marital_status="Casado/a"
    )
    
    madre = Person(
        cedula="100000006",
        first_name="Ana",
        last_name="Rodríguez Vargas", 
        birth_date="1960-01-01",
        gender="F",
        province="San José",
        marital_status="Casado/a"
    )
    
    # GENERACIÓN 3 - HIJOS (Nivel 3)
    hijo = Person(
        cedula="100000007",
        first_name="Roberto",
        last_name="García Rodríguez",
        birth_date="1985-01-01",
        gender="M",
        province="San José",
        marital_status="Casado/a"
    )
    
    hija = Person(
        cedula="100000008",
        first_name="Laura",
        last_name="García Rodríguez",
        birth_date="1987-01-01",
        gender="F",
        province="San José",
        marital_status="Casado/a"
    )
    
    # Parejas para la generación 3
    yerno = Person(
        cedula="100000009",
        first_name="Miguel",
        last_name="Torres Silva",
        birth_date="1983-01-01",
        gender="M",
        province="San José",
        marital_status="Casado/a"
    )
    
    nuera = Person(
        cedula="100000010",
        first_name="Patricia",
        last_name="Mendez Santos",
        birth_date="1988-01-01",
        gender="F",
        province="San José",
        marital_status="Casado/a"
    )
    
    # GENERACIÓN 4 - NIETOS (Nivel 4) - ÚLTIMA GENERACIÓN PERMITIDA
    nieto1 = Person(
        cedula="100000011",
        first_name="Diego",
        last_name="García Mendez",
        birth_date="2010-01-01",
        gender="M",
        province="San José",
        marital_status="Soltero/a"
    )
    
    nieta1 = Person(
        cedula="100000012",
        first_name="Sofia",
        last_name="García Mendez",
        birth_date="2012-01-01",
        gender="F",
        province="San José",
        marital_status="Soltero/a"
    )
    
    nieto2 = Person(
        cedula="100000013",
        first_name="Andrés",
        last_name="Torres García",
        birth_date="2015-01-01",
        gender="M",
        province="San José",
        marital_status="Soltero/a"
    )
    
    # Agregar todos a la familia
    personas = [
        bisabuelo, bisabuela,  # Nivel 0
        abuelo, abuela,        # Nivel 1  
        padre, madre,          # Nivel 2
        hijo, hija, yerno, nuera,  # Nivel 3
        nieto1, nieta1, nieto2     # Nivel 4 - LÍMITE
    ]
    
    for persona in personas:
        persona.virtual_age = 2025 - int(persona.birth_date.split('-')[0])
        test_family.add_or_update_member(persona)
    
    # Establecer relaciones familiares
    # Matrimonios
    bisabuelo.spouse = bisabuela
    bisabuela.spouse = bisabuelo
    
    abuelo.spouse = abuela
    abuela.spouse = abuelo
    
    padre.spouse = madre
    madre.spouse = padre
    
    hijo.spouse = nuera
    nuera.spouse = hijo
    
    hija.spouse = yerno
    yerno.spouse = hija
    
    # Relaciones padre-hijo
    # Bisabuelos -> Abuelos
    abuelo.father = bisabuelo
    abuelo.mother = bisabuela
    bisabuelo.children = [abuelo]
    bisabuela.children = [abuelo]
    
    # Abuelos -> Padres
    padre.father = abuelo
    padre.mother = abuela
    abuelo.children = [padre]
    abuela.children = [padre]
    
    # Padres -> Hijos
    hijo.father = padre
    hijo.mother = madre
    hija.father = padre
    hija.mother = madre
    padre.children = [hijo, hija]
    madre.children = [hijo, hija]
    
    # Hijos -> Nietos (NIVEL 4 - LÍMITE)
    nieto1.father = hijo
    nieto1.mother = nuera
    nieta1.father = hijo
    nieta1.mother = nuera
    hijo.children = [nieto1, nieta1]
    nuera.children = [nieto1, nieta1]
    
    nieto2.father = yerno
    nieto2.mother = hija
    yerno.children = [nieto2]
    hija.children = [nieto2]
    
    return test_family

if __name__ == "__main__":
    # Crear familia de prueba
    family = create_test_family_with_5_generations()
    
    print("=== FAMILIA DE PRUEBA GENERACIONAL ===")
    print(f"Familia: {family.name}")
    print(f"Total miembros: {len(family.members)}")
    print()
    
    # Mostrar estructura generacional
    from utils.graph_visualizer import FamilyGraphVisualizer
    visualizer = FamilyGraphVisualizer()
    levels = visualizer._assign_levels(family)
    
    print("📊 ESTRUCTURA GENERACIONAL:")
    for level in range(5):
        personas_nivel = [p for p in family.members if levels.get(p.cedula) == level]
        if personas_nivel:
            generation_name = ["Bisabuelos", "Abuelos", "Padres", "Hijos", "Nietos"][level]
            print(f"  Nivel {level} ({generation_name}):")
            for persona in personas_nivel:
                print(f"    - {persona.get_full_name()} (ID: {persona.cedula})")
    
    print()
    print("🧪 AHORA PROBEMOS EL LÍMITE GENERACIONAL...")
    print("Intentando que los nietos (nivel 4) tengan hijos (sería nivel 5 - BISNIETOS)...")
    
    # Intentar generar un bisnieto (debería fallar)
    nieto_para_prueba = family.get_member_by_cedula("100000011")  # Diego
    nieta_para_prueba = family.get_member_by_cedula("100000012")  # Sofia
    
    if nieto_para_prueba and nieta_para_prueba:
        # Hacer que sean mayores para poder tener hijos
        nieto_para_prueba.birth_date = "1995-01-01"
        nieta_para_prueba.birth_date = "1997-01-01"
        nieto_para_prueba.virtual_age = 30
        nieta_para_prueba.virtual_age = 28
        nieto_para_prueba.marital_status = "Casado/a"
        nieta_para_prueba.marital_status = "Casado/a"
        nieto_para_prueba.spouse = nieta_para_prueba
        nieta_para_prueba.spouse = nieto_para_prueba
        
        print(f"Intentando nacimiento entre {nieto_para_prueba.get_full_name()} y {nieta_para_prueba.get_full_name()}")
        
        # Probar el límite generacional
        success, message = SimulacionService.simular_nacimiento_mejorado(
            nieta_para_prueba, nieto_para_prueba, family
        )
        
        print(f"Resultado: {'✅ ÉXITO' if success else '🚫 BLOQUEADO'}")
        print(f"Mensaje: {message}")
        
        if success:
            print("❌ ERROR: El límite generacional NO está funcionando!")
        else:
            print("✅ ÉXITO: El límite generacional está funcionando correctamente!")
    
    print()
    print("=== FIN DE LA PRUEBA ===")
