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
        self.ego_cedula = None  # Para futuras mejoras

    def build_family_graph(self, family) -> nx.DiGraph:
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
            # Relaciones padre-hijo (flechas hacia abajo)
            if person.father and person.father.cedula in [p.cedula for p in family.members]:
                self.G.add_edge(person.father.cedula, person.cedula, relationship="parent")
            if person.mother and person.mother.cedula in [p.cedula for p in family.members]:
                self.G.add_edge(person.mother.cedula, person.cedula, relationship="parent")

            # Relación de pareja (bidireccional, sin flechas)
            if person.spouse and person.spouse.cedula in [p.cedula for p in family.members]:
                self.G.add_edge(person.cedula, person.spouse.cedula, relationship="spouse")
                self.G.add_edge(person.spouse.cedula, person.cedula, relationship="spouse")

            # Relación de hermanos (opcional, línea punteada)
            for sibling in person.siblings:
                if sibling.cedula in [p.cedula for p in family.members]:
                    # Evitar duplicados
                    if not self.G.has_edge(person.cedula, sibling.cedula):
                        self.G.add_edge(person.cedula, sibling.cedula, relationship="sibling")

        return self.G

    def calculate_hierarchical_layout(self, family) -> Dict[str, Tuple[float, float]]:
        """Calcula posiciones jerárquicas centradas y dentro del canvas"""
        pos = {}
        levels = self._assign_levels(family)

        if not levels:
            return {}

        # Ajustar niveles para que el mínimo sea 0
        min_level = min(levels.values())
        adjusted_levels = {cedula: level - min_level for cedula, level in levels.items()}
        max_level = max(adjusted_levels.values()) if adjusted_levels else 0

        canvas_width = 1200
        canvas_height = 800
        margin_top = 100
        margin_bottom = 150
        available_height = canvas_height - margin_top - margin_bottom

        if max_level == 0:
            level_height = available_height
        else:
            level_height = available_height / max_level if max_level > 0 else available_height

        # Distribuir nodos por niveles
        level_nodes = {}
        for cedula, level in adjusted_levels.items():
            level_nodes.setdefault(level, []).append(cedula)

        # Posicionar nodos
        for level, cedulas in level_nodes.items():
            y = margin_top + (level * level_height)
            x_spacing = canvas_width / (len(cedulas) + 1)
            for i, cedula in enumerate(cedulas):
                x = (i + 1) * x_spacing
                pos[cedula] = (x, y)

        return pos

    def _assign_levels(self, family) -> Dict[str, int]:
        """Asigna niveles jerárquicos a cada persona"""
        levels = {}
        visited = set()

        def dfs(person, level):
            if person.cedula in visited:
                return
            visited.add(person.cedula)
            levels[person.cedula] = level

            # Padres van un nivel arriba
            if person.father and person.father.cedula in [p.cedula for p in family.members]:
                dfs(person.father, level - 1)
            if person.mother and person.mother.cedula in [p.cedula for p in family.members]:
                dfs(person.mother, level - 1)

            # Hijos van un nivel abajo
            for child in person.children:
                if child.cedula in [p.cedula for p in family.members]:
                    dfs(child, level + 1)

        try:
            # Empezar desde raíces (personas sin padres)
            roots = [p for p in family.members if not p.father and not p.mother]
            if not roots and family.members:
                dfs(family.members[0], 0)
            else:
                for root in roots:
                    dfs(root, 0)

            # Asegurar que todos tengan nivel
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
            # Verificar si el canvas aún existe
            if not canvas.winfo_exists():
                return
                
            # Limpiar canvas solo si existe
            canvas.delete("all")
            
            if not family.members:
                if canvas.winfo_exists():
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
            
            # Verificar si el canvas sigue existiendo después de construir el grafo
            if not canvas.winfo_exists():
                return

            # Dibujar conexiones primero (líneas)
            for edge in self.G.edges():
                try:
                    source, target = edge
                    if source in pos and target in pos:
                        x1, y1 = pos[source]
                        x2, y2 = pos[target]
                        
                        edge_data = self.G[source][target]
                        if edge_data.get('relationship') == 'parent':
                            # Dibuja línea verde para padre/madre
                            canvas.create_line(x1, y1, x2, y2, fill="#4CAF50", width=2, arrow=tk.LAST)
                        elif edge_data.get('relationship') == 'spouse':
                            # Dibuja línea roja para pareja
                            canvas.create_line(x1, y1, x2, y2, fill="#FF6B6B", width=2, dash=(4, 2))
                        elif edge_data.get('relationship') == 'sibling':
                            # Dibuja línea azul para hermanos
                            canvas.create_line(x1, y1, x2, y2, fill="#2ECC71", width=1, dash=(4, 2))
                except Exception as e:
                    continue

            # Dibujar nodos (personas)
            for cedula, (x, y) in pos.items():
                try:
                    # Verificar que el canvas aún exista antes de dibujar
                    if not canvas.winfo_exists():
                        return
                        
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
                                  lambda e, p=person: self._show_menu(e, p))

                except Exception as e:
                    print(f"Error dibujando nodo {cedula}: {e}")
                    continue

        except Exception as e:
            # Manejar errores sin intentar dibujar en un canvas inexistente
            print(f"Error crítico al dibujar árbol: {e}")
            try:
                if canvas.winfo_exists():
                    canvas.create_text(
                        600, 400,
                        text=f"Error al dibujar árbol: {str(e)}",
                        font=("Arial", 12),
                        fill="red"
                    )
            except:
                # Si no podemos dibujar en el canvas, solo imprimimos el error
                print(f"Error crítico al dibujar árbol: {e}")

    def _show_menu(self, event, person):
        """Placeholder - será reemplazado en app.py"""
        print(f"Menú para {person.first_name} - Implementado en app.py")


# Función de utilidad
def get_family_graph(family):
    visualizer = FamilyGraphVisualizer()
    return visualizer.build_family_graph(family)