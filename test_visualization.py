import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.family_management_app import Person, Family
from utils.graph_visualizer import FamilyGraphVisualizer

def create_test_family():
    """Crea una familia de prueba para probar la visualización"""
    family = Family(1, "Familia de Prueba")
    
    # Crear personas
    abuelo = Person("123456789", "Juan", "Pérez", "1950-01-01", "Masculino", "San José")
    abuela = Person("987654321", "María", "González", "1952-03-15", "Femenino", "Alajuela")
    padre = Person("456789123", "Carlos", "Pérez", "1975-06-20", "Masculino", "San José")
    madre = Person("789123456", "Ana", "López", "1978-09-10", "Femenino", "Heredia")
    hijo = Person("321654987", "Pedro", "Pérez", "2000-12-25", "Masculino", "San José")
    hija = Person("654987321", "Laura", "Pérez", "2003-08-14", "Femenino", "San José")
    
    # Establecer relaciones
    padre.father = abuelo
    padre.mother = abuela
    abuelo.children.append(padre)
    abuela.children.append(padre)
    
    madre.spouse = padre
    padre.spouse = madre
    
    hijo.father = padre
    hijo.mother = madre
    padre.children.append(hijo)
    madre.children.append(hijo)
    
    hija.father = padre
    hija.mother = madre
    padre.children.append(hija)
    madre.children.append(hija)
    
    # Agregar todos los miembros a la familia
    family.members = [abuelo, abuela, padre, madre, hijo, hija]
    
    return family

def test_visualization():
    """Prueba la visualización del árbol genealógico"""
    print("Creando familia de prueba...")
    family = create_test_family()
    
    print("Creando visualizador...")
    visualizer = FamilyGraphVisualizer()
    
    print("Construyendo grafo familiar...")
    graph = visualizer.build_family_graph(family)
    
    print(f"Nodos en el grafo: {len(graph.nodes())}")
    print(f"Aristas en el grafo: {len(graph.edges())}")
    
    print("Nodos:")
    for node in graph.nodes(data=True):
        print(f"  {node[0]}: {node[1]}")
    
    print("Aristas:")
    for edge in graph.edges(data=True):
        print(f"  {edge[0]} -> {edge[1]}: {edge[2]}")
    
    print("Calculando layout jerárquico...")
    pos = visualizer.calculate_hierarchical_layout(family)
    print("Posiciones calculadas:")
    for cedula, (x, y) in pos.items():
        person = next(p for p in family.members if p.cedula == cedula)
        print(f"  {person.first_name} {person.last_name}: ({x:.1f}, {y:.1f})")
    
    print("¡Prueba completada exitosamente!")

if __name__ == "__main__":
    test_visualization()
