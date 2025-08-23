# utils/graph_visualizer.py
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
        self.ego_cedula = None
        
        for person in family.members:
            self.G.add_node(
                person.cedula,
                label=f"{person.first_name} {person.last_name}",
                alive=person.alive,
                gender=person.gender,
                marital_status=person.marital_status
            )
        
        for person in family.members:
            if person.father and person.father.cedula in [p.cedula for p in family.members]:
                self.G.add_edge(person.father.cedula, person.cedula, relationship="parent")
            if person.mother and person.mother.cedula in [p.cedula for p in family.members]:
                self.G.add_edge(person.mother.cedula, person.cedula, relationship="parent")
            
            if person.spouse and person.spouse.cedula in [p.cedula for p in family.members]:
                self.G.add_edge(person.cedula, person.spouse.cedula, relationship="spouse")
                self.G.add_edge(person.spouse.cedula, person.cedula, relationship="spouse")
        
        return self.G
    
    def calculate_hierarchical_layout(self, family) -> Dict[str, Tuple[float, float]]:
        """Calcula posiciones jerárquicas centradas y dentro del canvas"""
        pos = {}
        levels = self._assign_levels(family)
        
        if not levels:
            return {}

        min_level = min(levels.values())
        adjusted_levels = {cedula: level - min_level for cedula, level in levels.items()}
        max_level = max(adjusted_levels.values()) if adjusted_levels else 0

        canvas_width = 1200
        canvas_height = 800
        margin_top = 100
        margin_bottom = 150
        available_height = canvas_height - margin_top - margin_bottom

        level_height = available_height / max_level if max_level > 0 else available_height

        level_nodes = {}
        for cedula, level in adjusted_levels.items():
            level_nodes.setdefault(level, []).append(cedula)

        for level, cedulas in level_nodes.items():
            y = margin_top + (level * level_height)
            x_spacing = canvas_width / (len(cedulas) + 1)
            for i, cedula in enumerate(cedulas):
                x = (i + 1) * x_spacing
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
                if person.father and person.father.cedula in [p.cedula for p in family.members]:
                    dfs(person.father, level - 1)
                if person.mother and person.mother.cedula in [p.cedula for p in family.members]:
                    dfs(person.mother, level - 1)
                
                for child in person.children:
                    if child.cedula in [p.cedula for p in family.members]:
                        dfs(child, level + 1)
            except Exception as e:
                print(f"Error en DFS para persona {person.cedula}: {e}")
        
        try:
            roots = [p for p in family.members if not p.father and not p.mother]
            if not roots and family.members:
                dfs(family.members[0], 0)
            else:
                for root in roots:
                    dfs(root, 0)
            
            for person in family.members:
                if person.cedula not in levels:
                    levels[person.cedula] = 0
                    
        except Exception as e:
            print(f"Error en asignación de niveles: {e}")
            for i, person in enumerate(family.members):
                levels[person.cedula] = i
        
        return levels
    
    def draw_family_tree(self, family, canvas: tk.Canvas):
        """Dibuja el árbol familiar en el canvas de tkinter"""
        try:
            canvas.delete("all")
            
            if not family.members:
                canvas.create_text(600, 400, text="No hay personas en el árbol", font=("Arial", 16), fill="white")
                return
            
            self.build_family_graph(family)
            pos = self.calculate_hierarchical_layout(family)
            
            # Dibujar conexiones
            for edge in self.G.edges():
                try:
                    source, target = edge
                    if source in pos and target in pos:
                        x1, y1 = pos[source]
                        x2, y2 = pos[target]
                        edge_data = self.G[source][target]
                        
                        if edge_data.get('relationship') == 'parent':
                            color = "#4CAF50"
                            arrow = tk.LAST
                            canvas.create_line(x1, y1, x2, y2, fill=color, width=2, arrow=arrow)
                        else:
                            color = "#FF6B6B"
                            canvas.create_line(x1, y1, x2, y2, fill=color, width=2, dash=(4, 2))
                except Exception as e:
                    continue
            
            # Dibujar nodos
            for cedula, (x, y) in pos.items():
                try:
                    person = next((p for p in family.members if p.cedula == cedula), None)
                    if not person:
                        continue
                        
                    color = "#3b8ed0" if person.alive else "#d35f5f"
                    status_color = "lightgreen" if person.alive else "red"
                    radius = 30
                    
                    canvas.create_oval(x-radius, y-radius, x+radius, y+radius, fill=color, outline="#1f7dbf", width=2)
                    canvas.create_text(x, y-15, text=f"{person.first_name}\n{person.last_name}", fill="white", font=("Arial", 8, "bold"), anchor="center")
                    canvas.create_text(x, y+15, text=f"{person.cedula}\n{'Vivo' if person.alive else 'Fallecido'}", fill=status_color, font=("Arial", 7), anchor="center")
                    
                    # Botón de menú contextual
                    menu_btn = canvas.create_oval(x-8, y+radius+5, x+8, y+radius+20, fill="#1db954", outline="white", width=1)
                    canvas.tag_bind(menu_btn, "<Button-1>", lambda e, p=person: self._show_menu(e, p))
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            canvas.create_text(600, 400, text=f"Error al dibujar árbol: {str(e)}", font=("Arial", 12), fill="red")

    # ✅ Este es el método original: solo recibe (person, event)
    def _show_menu(self, event, person):
        """Placeholder - será reemplazado en app.py con una versión que reciba app_instance"""
        print(f"Menú para {person.first_name} - Implementado en app.py")

# Función de utilidad
def get_family_graph(family):
    visualizer = FamilyGraphVisualizer()
    return visualizer.build_family_graph(family)