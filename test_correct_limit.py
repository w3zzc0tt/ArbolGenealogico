#!/usr/bin/env python3
# Test script para verificar el límite generacional correcto

from models.family import Family
from models.person import Person
from services.simulacion_service import SimulacionService
from utils.graph_visualizer import FamilyGraphVisualizer

def test_generational_limits():
    print("🧪 Probando límites generacionales correctos...")
    
    # Crear familia de prueba
    family = Family(1, "Familia de Prueba Completa")
    family.description = "Test de 5 generaciones"
    
    # Crear 5 generaciones completas
    print("\n📊 Creando estructura de 5 generaciones:")
    
    # NIVEL 0: Bisabuelos
    bisabuelo = Person("1000", "Juan", "Pérez López", "1920-05-15", "M", "San José", "Casado/a")
    bisabuela = Person("1001", "María", "García Morales", "1925-03-20", "F", "San José", "Casado/a")
    bisabuelo.alive = True
    bisabuela.alive = True
    bisabuelo.spouse = bisabuela
    bisabuela.spouse = bisabuelo
    family.add_or_update_member(bisabuelo)
    family.add_or_update_member(bisabuela)
    print("  ✅ Nivel 0: Bisabuelos creados")
    
    # NIVEL 1: Abuelos  
    abuelo = Person("2000", "Carlos", "Pérez García", "1945-08-10", "M", "San José", "Casado/a")
    abuela = Person("2001", "Ana", "Rodríguez Vega", "1948-12-05", "F", "Alajuela", "Casado/a")
    abuelo.alive = True
    abuela.alive = True
    abuelo.spouse = abuela
    abuela.spouse = abuelo
    # Establecer relaciones familiares
    abuelo.father = bisabuelo
    abuelo.mother = bisabuela
    bisabuelo.children.append(abuelo)
    bisabuela.children.append(abuelo)
    family.add_or_update_member(abuelo)
    family.add_or_update_member(abuela)
    print("  ✅ Nivel 1: Abuelos creados")
    
    # NIVEL 2: Padres
    padre = Person("3000", "Roberto", "Pérez Rodríguez", "1970-04-25", "M", "San José", "Casado/a")
    madre = Person("3001", "Laura", "Jiménez Castro", "1975-09-15", "F", "Cartago", "Casado/a")
    padre.alive = True
    madre.alive = True
    padre.spouse = madre
    madre.spouse = padre
    # Establecer relaciones familiares
    padre.father = abuelo
    padre.mother = abuela
    abuelo.children.append(padre)
    abuela.children.append(padre)
    family.add_or_update_member(padre)
    family.add_or_update_member(madre)
    print("  ✅ Nivel 2: Padres creados")
    
    # NIVEL 3: Hijos
    hijo = Person("4000", "Miguel", "Pérez Jiménez", "1995-06-30", "M", "San José", "Casado/a")
    nuera = Person("4001", "Sofía", "López Herrera", "1997-11-20", "F", "Heredia", "Casado/a")
    hijo.alive = True
    nuera.alive = True
    hijo.spouse = nuera
    nuera.spouse = hijo
    # Establecer relaciones familiares
    hijo.father = padre
    hijo.mother = madre
    padre.children.append(hijo)
    madre.children.append(hijo)
    family.add_or_update_member(hijo)
    family.add_or_update_member(nuera)
    print("  ✅ Nivel 3: Hijos creados")
    
    # NIVEL 4: Nietos (última generación permitida)
    nieto = Person("5000", "Diego", "Pérez López", "1998-02-14", "M", "San José", "Casado/a")  # 27 años
    nieta = Person("5001", "Valentina", "Pérez López", "2000-07-08", "F", "San José", "Soltero/a")  # 25 años
    nieto.alive = True
    nieta.alive = True
    # Establecer relaciones familiares
    nieto.father = hijo
    nieto.mother = nuera
    nieta.father = hijo
    nieta.mother = nuera
    hijo.children.append(nieto)
    hijo.children.append(nieta)
    nuera.children.append(nieto)
    nuera.children.append(nieta)
    family.add_or_update_member(nieto)
    family.add_or_update_member(nieta)
    print("  ✅ Nivel 4: Nietos creados")
    
    print(f"\n📈 Familia creada con {len(family.members)} miembros")
    
    # Verificar niveles
    visualizer = FamilyGraphVisualizer()
    levels = visualizer._assign_levels(family)
    
    print("\n📊 Verificación de niveles:")
    for person in family.members:
        level = levels.get(person.cedula, "SIN_NIVEL")
        print(f"  - {person.get_full_name()}: Nivel {level}")
    
    # Ahora hacer que el nieto (nivel 4) tenga edad reproductiva
    # nieto.birth_date = "1998-02-14"  # Ya está configurado arriba - 27 años
    nieta_pareja = Person("5002", "Camila", "Vargas Solano", "1999-05-10", "F", "San José", "Casado/a")  # 26 años
    nieta_pareja.alive = True
    nieto.spouse = nieta_pareja
    nieta_pareja.spouse = nieto
    family.add_or_update_member(nieta_pareja)
    
    print(f"\n🧪 PRUEBA 1: Intentar que nietos (nivel 4) tengan hijos...")
    print(f"Padres: {nieto.get_full_name()} (nivel {levels.get(nieto.cedula)}) y {nieta_pareja.get_full_name()}")
    
    # Intentar generar bisnieto (nivel 5 - DEBE SER PROHIBIDO)
    result = SimulacionService.simular_nacimiento_mejorado(nieta_pareja, nieto, family)
    
    print(f"Resultado: {result}")
    
    if not result[0]:
        print("✅ CORRECTO: Se prohibió correctamente la generación de bisnietos")
    else:
        print("❌ ERROR: Se permitió generar bisnietos cuando debería estar prohibido")
    
    # Ahora probar con los hijos (nivel 3) - DEBE SER PERMITIDO
    print(f"\n🧪 PRUEBA 2: Intentar que hijos (nivel 3) tengan hijos...")
    print(f"Padres: {hijo.get_full_name()} (nivel {levels.get(hijo.cedula)}) y {nuera.get_full_name()}")
    
    result2 = SimulacionService.simular_nacimiento_mejorado(nuera, hijo, family)
    
    print(f"Resultado: {result2}")
    
    if result2[0]:
        print("✅ CORRECTO: Se permitió que los hijos (nivel 3) tengan descendencia")
    else:
        print("❌ ERROR: Se prohibió incorrectamente que los hijos tengan descendencia")

if __name__ == "__main__":
    test_generational_limits()
