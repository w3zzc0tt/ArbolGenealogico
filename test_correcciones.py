#!/usr/bin/env python3
"""
Script de prueba para verificar las correcciones de dibujo de nodos
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.person import Person
from models.family import Family
from utils.graph_visualizer import FamilyGraphVisualizer

def test_visualizador_corregido():
    """Prueba el visualizador con datos de prueba"""
    print("=== PRUEBA DEL VISUALIZADOR CORREGIDO ===")
    
    # Crear familia de prueba
    familia = Family(1, "Familia de Prueba")
    
    # Crear personas de prueba
    persona1 = Person(
        cedula="123456789",
        first_name="Juan",
        last_name="Pérez",
        birth_date="1980-01-01",
        gender="Masculino",
        province="San José"
    )
    
    persona2 = Person(
        cedula="987654321", 
        first_name="María",
        last_name="González",
        birth_date="1982-03-15",
        gender="Femenino",
        province="Alajuela"
    )
    
    # Agregar personas a la familia
    familia.members.append(persona1)
    familia.members.append(persona2)
    
    print(f"Familia creada con {len(familia.members)} miembros")
    
    # Probar el visualizador
    try:
        visualizador = FamilyGraphVisualizer()
        
        # Probar construcción del grafo
        grafo = visualizador.build_family_graph(familia)
        print(f"✓ Grafo construido: {len(grafo.nodes())} nodos, {len(grafo.edges())} aristas")
        
        # Probar cálculo de niveles
        niveles = visualizador._assign_levels(familia)
        print(f"✓ Niveles asignados: {niveles}")
        
        # Probar cálculo de layout
        posiciones = visualizador.calculate_hierarchical_layout(familia)
        print(f"✓ Posiciones calculadas: {len(posiciones)} posiciones")
        
        print("✓ Todas las pruebas del visualizador pasaron correctamente")
        return True
        
    except Exception as e:
        print(f"✗ Error en el visualizador: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agregar_persona_nueva():
    """Prueba agregar una nueva persona a una familia existente"""
    print("\n=== PRUEBA DE AGREGAR PERSONA NUEVA ===")
    
    familia = Family(1, "Familia Test")
    
    # Persona inicial
    persona_inicial = Person(
        cedula="111111111",
        first_name="Inicial",
        last_name="Test",
        birth_date="1970-01-01",
        gender="Masculino",
        province="Heredia"
    )
    familia.members.append(persona_inicial)
    
    print(f"Familia inicial: {len(familia.members)} miembros")
    
    # Agregar nueva persona
    nueva_persona = Person(
        cedula="222222222",
        first_name="Nueva",
        last_name="Persona", 
        birth_date="1990-05-20",
        gender="Femenino",
        province="Cartago"
    )
    familia.members.append(nueva_persona)
    
    print(f"Después de agregar: {len(familia.members)} miembros")
    
    # Verificar que el visualizador maneje correctamente la nueva persona
    try:
        visualizador = FamilyGraphVisualizer()
        niveles = visualizador._assign_levels(familia)
        
        print(f"Niveles después de agregar persona: {niveles}")
        
        # Verificar que ambas personas tengan niveles asignados
        if len(niveles) == 2:
            print("✓ Ambas personas tienen niveles asignados correctamente")
            return True
        else:
            print(f"✗ Error: Se esperaban 2 niveles, se obtuvieron {len(niveles)}")
            return False
            
    except Exception as e:
        print(f"✗ Error al procesar nueva persona: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando pruebas de las correcciones...\n")
    
    # Ejecutar pruebas
    prueba1_ok = test_visualizador_corregido()
    prueba2_ok = test_agregar_persona_nueva()
    
    print("\n" + "="*50)
    if prueba1_ok and prueba2_ok:
        print("✓ TODAS LAS PRUEBAS PASARON CORRECTAMENTE")
        print("Las correcciones parecen funcionar correctamente.")
    else:
        print("✗ ALGUNAS PRUEBAS FALLARON")
        print("Revise los mensajes de error para identificar problemas.")
    
    print("\nPara probar la interfaz gráfica completa, ejecute:")
    print("python gui/app.py")
