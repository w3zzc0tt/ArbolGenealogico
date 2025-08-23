import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from typing import Dict, List, Tuple
import math

class FamilyGraphVisualizer:
    def __init__(self):
        self.G = nx.DiGraph()
        
    def set_ego_node(self, cedula: str):
        """Set the cedula of the Ego node."""
        self.ego_cedula = cedula

    def build_family_graph(self, family) -> nx.DiGraph:
        """Construye el grafo familiar a partir de los miembros"""
        self.G.clear()
        self.ego_cedula = None  # Initialize ego_cedula
        
        """Construye el grafo familiar a partir de los miembros"""
        self.G.clear()
        
        # Agregar todos los miembros como nodos
        for person in family.members:
            self.G.add_node(
                person.cedula,
                label=f"{person.first_name} {person.last_name}",
                alive=person.alive,
                gender=person.gender,
                marital_status=person.marital_status
            )
        
        # Agregar relaciones familiares
        for person in family.members:
            # Relaciones padre-hijo
            if person.father and person.father.cedula in [p.cedula for p in family.members]:
                self.G.add_edge(person.father.cedula, person.cedula, relationship="parent")
            if person.mother and person.mother.cedula in [p.cedula for p in family.members]:
                self.G.add_edge(person.mother.cedula, person.cedula, relationship="parent")
            
            # Relación de pareja
            if person.spouse and person.spouse.cedula in [p.cedula for p in family.members]:
                self.G.add_edge(person.cedula, person.spouse.cedula, relationship="spouse")
                self.G.add_edge(person.spouse.cedula, person.cedula, relationship="spouse")
        
        return self.G
    
    def calculate_hierarchical_layout(self, family) -> Dict[str, Tuple[float, float]]:
        """Calcula posiciones jerárquicas para la visualización"""
        pos = {}
        levels = self._assign_levels(family)
        
        canvas_width = 1200
        canvas_height = 800
        level_height = canvas_height / (max(levels.values()) + 2 if levels else 1)
        
        # Distribuir nodos por niveles
        level_nodes = {}
        for cedula, level in levels.items():
            if level not in level_nodes:
                level_nodes[level] = []
            level_nodes[level].append(cedula)
        
        ego_cedula = "YOUR_EGO_CEDULA"  # Replace with the actual cedula of the Ego
        ego_index = None
        for level, nodes in level_nodes.items():
            level_width = canvas_width / (len(nodes) + 1)
            for i, cedula in enumerate(nodes):
                x = (i + 1) * level_width
                y = canvas_height - (level * level_height)
                pos[cedula] = (x, y)
        
        return pos
    
    def _assign_levels(self, family) -> Dict[str, int]:
        """Asigna niveles jerárquicos a cada persona con manejo robusto"""
        levels = {}
        visited = set()
        
        def dfs(person, level):
            if person.cedula in visited:
                return
            visited.add(person.cedula)
            levels[person.cedula] = level
            
            try:
                # Padres van un nivel arriba
                if person.father and person.father.cedula in [p.cedula for p in family.members]:
                    dfs(person.father, level - 1)
                if person.mother and person.mother.cedula in [p.cedula for p in family.members]:
                    dfs(person.mother, level - 1)
                
                # Hijos van un nivel abajo
                for child in person.children:
                    if child.cedula in [p.cedula for p in family.members]:
                        dfs(child, level + 1)
            except Exception as e:
                print(f"Error en DFS para persona {person.cedula}: {e}")
        
        try:
            # Empezar desde todas las personas sin padres (raíces del árbol)
            roots = [p for p in family.members if not p.father and not p.mother]
            if not roots and family.members:
                # Si no hay raíces claras, usar la primera persona como nivel 0
                dfs(family.members[0], 0)
            else:
                for root in roots:
                    dfs(root, 0)
            
            # Asegurar que todos los miembros tengan un nivel
            for person in family.members:
                if person.cedula not in levels:
                    levels[person.cedula] = 0
                    
        except Exception as e:
            print(f"Error en asignación de niveles: {e}")
            # Asignar niveles secuenciales como fallback
            for i, person in enumerate(family.members):
                levels[person.cedula] = i
        
        return levels
    
    def draw_family_tree(self, family, canvas: tk.Canvas):
        """Dibuja el árbol familiar en el canvas de tkinter con manejo robusto de errores"""
        try:
            canvas.delete("all")
            
            if not family.members:
                canvas.create_text(
                    600, 400,
                    text="No hay personas en el árbol",
                    font=("Arial", 16),
                    fill="white"
                )
                return
            
            # Construir grafo y calcular layout
            self.build_family_graph(family)
            pos = self.calculate_hierarchical_layout(family)
            
            # Dibujar conexiones primero (líneas)
            for edge in self.G.edges():
                try:
                    source, target = edge
                    if source in pos and target in pos:
                        x1, y1 = pos[source]
                        x2, y2 = pos[target]
                        
                        # Color y estilo según el tipo de relación
                        edge_data = self.G[source][target]
                        if edge_data.get('relationship') == 'parent':
                            color = "#4CAF50"  # Verde para relaciones padre-hijo
                            arrow = tk.LAST
                            canvas.create_line(x1, y1, x2, y2, fill=color, width=2, arrow=arrow)
                        else:  # spouse
                            color = "#FF6B6B"  # Rojo para relaciones de pareja
                            # Dibujar línea doble para parejas
                            canvas.create_line(x1, y1, x2, y2, fill=color, width=2, dash=(4, 2))
                except Exception as e:
                    print(f"Error dibujando conexión {edge}: {e}")
                    continue
            
            # Dibujar nodos (personas)
            for cedula, (x, y) in pos.items():
                try:
                    person = next((p for p in family.members if p.cedula == cedula), None)
                    if not person:
                        continue
                        
                    # Color según estado de vida
                    color = "#3b8ed0" if person.alive else "#d35f5f"
                    status_color = "lightgreen" if person.alive else "red"
                    
                    # Dibujar círculo del nodo
                    radius = 30
                    node_id = canvas.create_oval(x-radius, y-radius, x+radius, y+radius, 
                                              fill=color, outline="#1f7dbf", width=2)
                    
                    # Información de la persona
                    name_text = f"{person.first_name}\n{person.last_name}"
                    canvas.create_text(x, y-15, text=name_text, font=("Arial", 8, "bold"), 
                                     fill="white", anchor="center")
                    
                    # Cédula y estado
                    info_text = f"{person.cedula}\n{'Vivo' if person.alive else 'Fallecido'}"
                    canvas.create_text(x, y+15, text=info_text, font=("Arial", 7), 
                                     fill=status_color, anchor="center")
                    
                    # Botón de menú contextual
                    menu_btn = canvas.create_oval(x-8, y+radius+5, x+8, y+radius+20, 
                                                fill="#1db954", outline="white", width=1)
                    canvas.tag_bind(menu_btn, "<Button-1>", 
                                  lambda e, p=person: self._show_menu(p, e))
                    
                except Exception as e:
                    print(f"Error dibujando nodo {cedula}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error crítico al dibujar árbol: {e}")
            canvas.create_text(
                600, 400,
                text=f"Error al dibujar árbol: {str(e)}",
                font=("Arial", 12),
                fill="red"
            )
    
    def _show_menu(self, person, event):
        """Muestra el menú contextual (será sobreescrito por la clase principal)"""
        pass

# Función de utilidad para obtener el grafo familiar
def get_family_graph(family):
    visualizer = FamilyGraphVisualizer()
    return visualizer.build_family_graph(family)
