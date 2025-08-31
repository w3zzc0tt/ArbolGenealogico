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
            # Relaciones padre-hijo (SOLO una dirección: padre → hijo)
            if person.father and person.father.cedula in [p.cedula for p in family.members]:
                self.G.add_edge(person.father.cedula, person.cedula, relationship="parent")
            if person.mother and person.mother.cedula in [p.cedula for p in family.members]:
                self.G.add_edge(person.mother.cedula, person.cedula, relationship="parent")

            # Relación de pareja (bidireccional, pero solo agregar una vez)
            if person.spouse and person.spouse.cedula in [p.cedula for p in family.members]:
                # Solo agregar si no existe ya (evita duplicados)
                if not self.G.has_edge(person.cedula, person.spouse.cedula) and not self.G.has_edge(person.spouse.cedula, person.cedula):
                    self.G.add_edge(person.cedula, person.spouse.cedula, relationship="spouse")

            # Relación de hermanos (solo agregar una vez entre cada par)
            for sibling in person.siblings:
                if sibling.cedula in [p.cedula for p in family.members]:
                    # Evitar duplicados comparando cédulas alfabéticamente
                    if person.cedula < sibling.cedula:  # Solo agregar una vez por par
                        self.G.add_edge(person.cedula, sibling.cedula, relationship="sibling")

        return self.G

    def calculate_hierarchical_layout(self, family) -> Dict[str, Tuple[float, float]]:
        """Calcula posiciones jerárquicas mejoradas con posicionamiento optimizado de cónyuges"""
        pos = {}
        levels = self._assign_levels(family)
        
        # Debug: Verificar niveles asignados
        print("\n📊 DEPURACIÓN DE NIVELES:")
        for person in family.members:
            parent_info = f"Padre: {person.father.get_full_name() if person.father else 'N/A'}, Madre: {person.mother.get_full_name() if person.mother else 'N/A'}"
            children_info = f"Hijos: {[c.get_full_name() for c in person.children] if person.children else 'N/A'}"
            print(f"  🟦 {person.get_full_name()} (ID: {person.cedula}) - Nivel: {levels.get(person.cedula, 'SIN_NIVEL')} | {parent_info} | {children_info}")
        print("📊 FIN DEPURACIÓN DE NIVELES\n")

        if not levels:
            return {}

        # Ajustar niveles para que el mínimo sea 0
        min_level = min(levels.values())
        adjusted_levels = {cedula: level - min_level for cedula, level in levels.items()}
        max_level = max(adjusted_levels.values()) if adjusted_levels else 0

        # Dimensiones del canvas con espacio para la leyenda
        canvas_width = 1200
        canvas_height = 800
        
        # Reservar espacio para la leyenda (220px desde la derecha)
        usable_width = canvas_width - 250  # Dejar 250px para la leyenda
        margin_left = 50
        margin_top = 80
        margin_bottom = 100
        
        available_height = canvas_height - margin_top - margin_bottom
        available_width = usable_width - margin_left

        # Calcular altura entre niveles (más espacio para tarjetas)
        if max_level == 0:
            level_height = available_height / 2
        else:
            level_height = max(120, available_height / max_level) if max_level > 0 else available_height

        # Agrupar personas por unidades familiares (parejas + solteros)
        family_units = self._create_family_units(family, adjusted_levels)

        # Implementar layout balanceado como en la imagen objetivo
        pos = self._calculate_balanced_layout(family_units, margin_left, margin_top, 
                                            available_width, available_height, level_height)

        return pos

    def _create_family_units(self, family, levels) -> List[Dict]:
        """Crea unidades familiares (parejas y solteros) organizadas por nivel"""
        family_units = []
        processed_persons = set()
        
        # Agrupar por niveles
        level_groups = {}
        for person in family.members:
            level = levels.get(person.cedula, 0)
            level_groups.setdefault(level, []).append(person)
        
        for level, persons in level_groups.items():
            level_units = []
            
            for person in persons:
                if person.cedula in processed_persons:
                    continue
                    
                # Verificar si tiene cónyuge en el mismo nivel (INDEPENDIENTE del estado de vida)
                if (person.spouse and 
                    person.spouse.cedula in [p.cedula for p in family.members] and
                    levels.get(person.spouse.cedula, 0) == level and
                    person.spouse.cedula not in processed_persons):
                    
                    # Crear unidad de pareja (vivos o fallecidos, siguen siendo pareja)
                    unit = {
                        'type': 'couple',
                        'level': level,
                        'members': [person.cedula, person.spouse.cedula],
                        'left_cedula': min(person.cedula, person.spouse.cedula),
                        'right_cedula': max(person.cedula, person.spouse.cedula),
                        'width': 280,  # Más espacio para dos tarjetas lado a lado como en imagen
                        'both_alive': person.alive and person.spouse.alive,
                        'both_dead': not person.alive and not person.spouse.alive,
                        'mixed_status': person.alive != person.spouse.alive
                    }
                    level_units.append(unit)
                    processed_persons.add(person.cedula)
                    processed_persons.add(person.spouse.cedula)
                    
                else:
                    # Crear unidad individual
                    unit = {
                        'type': 'single',
                        'level': level,
                        'members': [person.cedula],
                        'width': 160,  # Espacio para una tarjeta como en imagen
                        'alive': person.alive
                    }
                    level_units.append(unit)
                    processed_persons.add(person.cedula)
            
            family_units.extend(level_units)
        
        return family_units

    def _calculate_balanced_layout(self, family_units, margin_left, margin_top, 
                                 available_width, available_height, level_height):
        """Calcula un layout balanceado y centrado como en la imagen objetivo"""
        pos = {}
        
        # Organizar unidades por nivel
        units_by_level = {}
        for unit in family_units:
            level = unit['level']
            units_by_level.setdefault(level, []).append(unit)
        
        # Para cada nivel, calcular posiciones centradas
        for level, level_units in units_by_level.items():
            if not level_units:
                continue
                
            y = margin_top + (level * level_height)
            
            # Calcular ancho total necesario para este nivel
            total_width = 0
            for unit in level_units:
                if unit['type'] == 'couple':
                    total_width += 280  # Ancho para pareja
                else:
                    total_width += 160  # Ancho para soltero
            
            # Espaciado entre unidades
            num_gaps = max(0, len(level_units) - 1)
            gap_width = 60  # Espacio entre unidades
            total_width_with_gaps = total_width + (num_gaps * gap_width)
            
            # Centrar todo el nivel en el ancho disponible
            start_x = margin_left + (available_width - total_width_with_gaps) / 2
            
            # Posicionar cada unidad
            current_x = start_x
            
            for unit in level_units:
                if unit['type'] == 'couple':
                    left_cedula = unit.get('left_cedula') or unit['members'][0]
                    right_cedula = unit.get('right_cedula') or unit['members'][1]
                    
                    # Centrar la pareja en su espacio asignado
                    couple_center = current_x + 140  # Centro del espacio de pareja
                    couple_spacing = 150
                    
                    pos[left_cedula] = (couple_center - couple_spacing / 2, y)
                    pos[right_cedula] = (couple_center + couple_spacing / 2, y)
                    
                    current_x += 280 + gap_width  # Avanzar al siguiente espacio
                
                else:
                    person_cedula = unit['members'][0]
                    person_center = current_x + 80  # Centro del espacio individual
                    pos[person_cedula] = (person_center, y)
                    
                    current_x += 160 + gap_width  # Avanzar al siguiente espacio
        
        return pos

    def _compute_unit_x_positions(self, family_units: List[Dict]) -> Dict[Tuple[str,...], float]:
        """Calcula una posición X para cada unidad familiar (clave: tuple(members))
        usando un algoritmo bottom-up que intenta centrar padres sobre sus hijos.
        """
        # Organizar unidades por nivel
        units_by_level = {}
        for unit in family_units:
            units_by_level.setdefault(unit['level'], []).append(unit)

        # Mapa clave->unit for easy lookup
        unit_key_map = {tuple(u['members']): u for u in family_units}

        # Construir relación unit -> children_units (niveles inferiores)
        children_map = {tuple(u['members']): set() for u in family_units}

        # Para cada unidad, buscar unidades en el siguiente nivel que contengan hijos de sus miembros
        for unit in family_units:
            unit_key = tuple(unit['members'])
            for other in family_units:
                # other es potencial unidad hija si alguno de sus miembros es hijo de alguien en unit
                if other['level'] == unit['level'] + 1:
                    # comprobar relaciones por cédula: si alguno de other.members tiene padre/madre en unit.members
                    # Dado que no tenemos referencia directa a objetos aquí, asumimos que la organización de niveles
                    # sitúa a hijos en el siguiente nivel y que la relación estará reflejada por proximidad.
                    # Como heurística, si hay intersección de cedulas (rare), lo vinculamos; de lo contrario, usamos
                    # proximidad temporal (no ideal). Para robustez, vinculamos si alguna cedula coincide en nombres de miembros.
                    # Simplicidad: si el first member of other shares last name with any in unit, consider child.
                    # (Mejoras futuras: pasar objetos en lugar de cedulas)
                    try:
                        # crude heuristic: if any string fragment matches
                        if any(m in other['members'] for m in unit['members']):
                            children_map[unit_key].add(tuple(other['members']))
                    except Exception:
                        continue

        # Lista de niveles ordenada de abajo hacia arriba
        levels_sorted = sorted(units_by_level.keys(), reverse=True)

        x_positions = {}
        next_x = 0
        x_spacing = 200  # Más espacio entre unidades para tarjetas

        # Asignar X para niveles más profundos (hojas)
        if levels_sorted:
            deepest = levels_sorted[0]
            for unit in units_by_level.get(deepest, []):
                key = tuple(unit['members'])
                x_positions[key] = next_x
                next_x += x_spacing

        # Subir niveles y centrar unidades sobre sus hijos cuando sea posible
        for level in levels_sorted[1:]:
            level_units = units_by_level.get(level, [])
            for unit in level_units:
                key = tuple(unit['members'])
                children = children_map.get(key, set())
                if children:
                    # Centrar sobre las posiciones de las unidades hijas
                    child_xs = [x_positions[c] for c in children if c in x_positions]
                    if child_xs:
                        x_positions[key] = sum(child_xs) / len(child_xs)
                        continue

                # Si no tiene hijos posicionados, asignar siguiente X disponible
                if key not in x_positions:
                    x_positions[key] = next_x
                    next_x += x_spacing

        # Convertir a coordenadas centradas (mantener valores numéricos)
        return x_positions

    def _assign_levels(self, family) -> Dict[str, int]:
        """Asigna niveles jerárquicos a cada persona"""
        levels = {}
        visited = set()

        def dfs(person, level):
            if person.cedula in visited:
                return
            visited.add(person.cedula)
            levels[person.cedula] = level

            # Si tiene cónyuge, asignar el mismo nivel PRIMERO
            if person.spouse and person.spouse.cedula in [p.cedula for p in family.members]:
                if person.spouse.cedula not in visited:
                    visited.add(person.spouse.cedula)
                    levels[person.spouse.cedula] = level

            # Padres van un nivel arriba
            if person.father and person.father.cedula in [p.cedula for p in family.members]:
                dfs(person.father, level - 1)
            if person.mother and person.mother.cedula in [p.cedula for p in family.members]:
                dfs(person.mother, level - 1)

            # Hijos van un nivel abajo - CORREGIR: usar parents para la verificación
            for child in person.children:
                if child.cedula in [p.cedula for p in family.members]:
                    # Asegurar que el hijo esté correctamente conectado
                    if child.father == person or child.mother == person:
                        dfs(child, level + 1)

            # Si tiene cónyuge, procesar también sus relaciones familiares
            if person.spouse and person.spouse.cedula in [p.cedula for p in family.members]:
                spouse = person.spouse
                # Padres del cónyuge van un nivel arriba
                if spouse.father and spouse.father.cedula in [p.cedula for p in family.members]:
                    dfs(spouse.father, level - 1)
                if spouse.mother and spouse.mother.cedula in [p.cedula for p in family.members]:
                    dfs(spouse.mother, level - 1)
                
                # Hijos del cónyuge van un nivel abajo
                for child in spouse.children:
                    if child.cedula in [p.cedula for p in family.members]:
                        # Asegurar que el hijo esté correctamente conectado
                        if child.father == spouse or child.mother == spouse:
                            dfs(child, level + 1)

        try:
            # Empezar desde raíces (personas sin padres)
            roots = [p for p in family.members if not p.father and not p.mother]
            if not roots and family.members:
                dfs(family.members[0], 0)
            else:
                for root in roots:
                    dfs(root, 0)

            # Verificación adicional para hijos que puedan haber quedado sin nivel
            for person in family.members:
                if person.cedula not in levels:
                    # Si la persona no tiene nivel pero tiene padres en la familia, asignar nivel
                    parent_level = None
                    if person.father and person.father.cedula in levels:
                        parent_level = levels[person.father.cedula]
                    elif person.mother and person.mother.cedula in levels:
                        parent_level = levels[person.mother.cedula]
                    
                    if parent_level is not None:
                        levels[person.cedula] = parent_level + 1
                        print(f"⚠️ Asignando nivel tardío a {person.get_full_name()}: {parent_level + 1}")
                    else:
                        # Si no tiene padres en la familia, asignar nivel 0
                        levels[person.cedula] = 0
                        print(f"⚠️ Asignando nivel por defecto a {person.get_full_name()}: 0")

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

            # NUEVA LÓGICA: Dibujar conexiones familiares inteligentes
            self._draw_family_connections(canvas, family, pos)

            # Dibujar nodos (personas) como tarjetas estilo imagen
            for cedula, (x, y) in pos.items():
                try:
                    # Verificar que el canvas aún exista antes de dibujar
                    if not canvas.winfo_exists():
                        return
                        
                    person = next((p for p in family.members if p.cedula == cedula), None)
                    if not person:
                        continue

                    # Dimensiones de la tarjeta
                    card_width = 130
                    card_height = 85
                    
                    # Colores según género y estado
                    if person.gender == "M":
                        border_color = "#2196F3"  # Azul para hombres
                        header_color = "#E3F2FD"
                    else:
                        border_color = "#E91E63"  # Rosa para mujeres
                        header_color = "#FCE4EC"
                    
                    card_color = "#FFFFFF" if person.alive else "#F5F5F5"

                    # Coordenadas de la tarjeta
                    card_x1, card_y1 = x - card_width//2, y - card_height//2
                    card_x2, card_y2 = x + card_width//2, y + card_height//2
                    
                    # Dibujar tarjeta principal
                    card_id = canvas.create_rectangle(card_x1, card_y1, card_x2, card_y2,
                                                    fill=card_color, outline=border_color, width=2)

                    # Header de la tarjeta (franja superior)
                    header_height = 25
                    canvas.create_rectangle(card_x1, card_y1, card_x2, card_y1 + header_height,
                                          fill=header_color, outline="", width=0)

                    # Ícono de género en header
                    icon_x = card_x1 + 12
                    icon_y = card_y1 + 12
                    gender_icon = "👨" if person.gender == "M" else "👩"
                    canvas.create_text(icon_x, icon_y, text=gender_icon, 
                                     font=("Arial", 12), anchor="center")

                    # Botón de opciones en header (esquina derecha)
                    options_x = card_x2 - 12
                    options_y = card_y1 + 12
                    canvas.create_text(options_x, options_y, text="⋮", 
                                     font=("Arial", 12, "bold"), fill="#666666", anchor="center")

                    # Nombre completo (línea principal)
                    name_y = card_y1 + 40
                    full_name = f"{person.first_name}"
                    surname = person.last_name
                    canvas.create_text(x, name_y, text=full_name, 
                                     font=("Arial", 10, "bold"), fill="#333333", anchor="center")
                    canvas.create_text(x, name_y + 15, text=surname, 
                                     font=("Arial", 9), fill="#666666", anchor="center")

                    # Información de edad/estado en la parte inferior
                    info_y = card_y2 - 12
                    if person.alive:
                        age = person.calculate_virtual_age()
                        status_text = f"{age} años • Vivo"
                        status_color = "#4CAF50"
                    else:
                        # Manejar fechas que pueden ser datetime o string
                        if hasattr(person.death_date, 'strftime'):
                            death_year = person.death_date.strftime("%Y")
                        elif person.death_date:
                            death_year = str(person.death_date).split('-')[0]
                        else:
                            death_year = "????"
                            
                        if hasattr(person.birth_date, 'strftime'):
                            birth_year = person.birth_date.strftime("%Y")
                        elif person.birth_date:
                            birth_year = str(person.birth_date).split('-')[0]
                        else:
                            birth_year = "????"
                            
                        status_text = f"{birth_year}-{death_year} • Fallecido"
                        status_color = "#F44336"
                    
                    canvas.create_text(x, info_y, text=status_text, 
                                     font=("Arial", 7), fill=status_color, anchor="center")

                    # Hacer la tarjeta clickeable para menú contextual
                    canvas.tag_bind(card_id, "<Button-1>", 
                                  lambda e, p=person: self._show_menu(e, p))

                except Exception as e:
                    print(f"Error dibujando tarjeta {cedula}: {e}")
                    continue

            # Agregar leyenda de colores de relaciones
            self._draw_relationship_legend(canvas)

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

    def _draw_relationship_legend(self, canvas):
        """Dibuja una leyenda explicando los colores como en la imagen"""
        try:
            if not canvas.winfo_exists():
                return
            
            # Posición de la leyenda (esquina superior derecha)
            canvas_width = canvas.winfo_width() if canvas.winfo_width() > 1 else 1200
            legend_x = canvas_width - 200
            legend_y = 20
            
            # Fondo de la leyenda
            legend_bg = canvas.create_rectangle(
                legend_x - 10, legend_y - 10,
                legend_x + 180, legend_y + 160,
                fill="#FFFFFF", outline="#CCCCCC", width=2
            )
            
            # Título de la leyenda
            canvas.create_text(
                legend_x + 75, legend_y + 10,
                text="🗂️ Leyenda",
                font=("Arial", 11, "bold"),
                fill="#333333",
                anchor="center"
            )
            
            # Elementos de la leyenda como en la imagen
            legend_items = [
                ("👨 Hombre vivo", "#2196F3", "■"),
                ("👩 Mujer viva", "#E91E63", "■"),
                ("⚰️ Fallecido/a", "#9E9E9E", "■"),
                ("💕 Pareja", "#E91E63", "━"),
                ("→ Relación padre-hijo", "#1976D2", "→"),
                ("○ Tiene hijos", "#666666", "○"),
                ("🤝 Hermanos", "#4CAF50", "~")
            ]
            
            y_offset = 35
            for i, (label, color, symbol) in enumerate(legend_items):
                item_y = legend_y + y_offset + (i * 18)
                
                # Símbolo/icono
                canvas.create_text(
                    legend_x + 10, item_y,
                    text=symbol, font=("Arial", 10),
                    fill=color, anchor="w"
                )
                
                # Etiqueta
                canvas.create_text(
                    legend_x + 30, item_y,
                    text=label,
                    font=("Arial", 8),
                    fill="#333333",
                    anchor="w"
                )
                
        except Exception as e:
            print(f"Error dibujando leyenda: {e}")

    def _draw_family_connections(self, canvas, family, pos):
        """Dibuja conexiones familiares con algoritmo anti-colisiones avanzado"""
        try:
            # 1. Primero dibujar relaciones de pareja/cónyuge
            parejas_dibujadas = set()
            puntos_medios_parejas = {}
            rutas_ocupadas = []  # Para rastrear rutas ya dibujadas y evitar colisiones
            
            # Recopilar todas las parejas únicas
            parejas_unicas = set()
            for person in family.members:
                if person.spouse and person.cedula in pos and person.spouse.cedula in pos:
                    pareja_id = tuple(sorted([person.cedula, person.spouse.cedula]))
                    parejas_unicas.add(pareja_id)
            
            # Dibujar cada pareja única solo una vez
            for pareja_id in parejas_unicas:
                cedula1, cedula2 = pareja_id
                if cedula1 in pos and cedula2 in pos:
                    x1, y1 = pos[cedula1]
                    x2, y2 = pos[cedula2]
                    
                    # LÍNEAS MATRIMONIALES: Horizontales directas fucsia como en la imagen
                    canvas.create_line(x1, y1, x2, y2, 
                                     fill="#E91E63", width=4, smooth=True, capstyle="round")
                    
                    # Registrar ruta ocupada
                    rutas_ocupadas.append({
                        'type': 'matrimonial',
                        'y': y1,
                        'x_start': min(x1, x2),
                        'x_end': max(x1, x2)
                    })
                    
                    # Punto medio para conexiones padre-hijo
                    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                    puntos_medios_parejas[pareja_id] = (mid_x, mid_y)
                    
                    # Pequeño círculo en el punto medio (como en la imagen)
                    canvas.create_oval(mid_x-4, mid_y-4, mid_x+4, mid_y+4, 
                                     fill="#E91E63", outline="#FFFFFF", width=1)
                    parejas_dibujadas.add(pareja_id)

            # 2. CONEXIONES PADRE-HIJO con sistema de ramificación horizontal
            # Primero, agrupar todos los hijos por sus padres
            conexiones_por_padres = {}
            
            for person in family.members:
                if person.cedula in pos:
                    child_x, child_y = pos[person.cedula]
                    
                    # Si la persona tiene ambos padres
                    if (person.father and person.mother and 
                        person.father.cedula in pos and person.mother.cedula in pos):
                        
                        padre_cedula = person.father.cedula
                        madre_cedula = person.mother.cedula
                        pareja_id = tuple(sorted([padre_cedula, madre_cedula]))
                        
                        if pareja_id in puntos_medios_parejas:
                            # PADRES CASADOS: Agrupar hijos
                            if pareja_id not in conexiones_por_padres:
                                conexiones_por_padres[pareja_id] = {
                                    'parent_pos': puntos_medios_parejas[pareja_id],
                                    'hijos': [],
                                    'tipo': 'casados'
                                }
                            conexiones_por_padres[pareja_id]['hijos'].append((person.cedula, child_x, child_y))
                        
                        else:
                            # PADRES NO CASADOS: Crear punto medio virtual
                            padre_x, padre_y = pos[padre_cedula]
                            madre_x, madre_y = pos[madre_cedula]
                            parent_mid_x, parent_mid_y = (padre_x + madre_x) / 2, (padre_y + madre_y) / 2
                            
                            if pareja_id not in conexiones_por_padres:
                                # Línea entre padres no casados
                                canvas.create_line(padre_x, padre_y, madre_x, madre_y,
                                                 fill="#FF9800", width=3, dash=(10, 5), capstyle="round")
                                
                                conexiones_por_padres[pareja_id] = {
                                    'parent_pos': (parent_mid_x, parent_mid_y),
                                    'hijos': [],
                                    'tipo': 'no_casados'
                                }
                            conexiones_por_padres[pareja_id]['hijos'].append((person.cedula, child_x, child_y))
                    
                    # PADRE SOLTERO
                    elif person.father and person.father.cedula in pos:
                        padre_x, padre_y = pos[person.father.cedula]
                        padre_id = f"solo_{person.father.cedula}"
                        
                        if padre_id not in conexiones_por_padres:
                            conexiones_por_padres[padre_id] = {
                                'parent_pos': (padre_x, padre_y),
                                'hijos': [],
                                'tipo': 'padre_solo'
                            }
                        conexiones_por_padres[padre_id]['hijos'].append((person.cedula, child_x, child_y))
                    
                    # MADRE SOLTERA
                    elif person.mother and person.mother.cedula in pos:
                        madre_x, madre_y = pos[person.mother.cedula]
                        madre_id = f"solo_{person.mother.cedula}"
                        
                        if madre_id not in conexiones_por_padres:
                            conexiones_por_padres[madre_id] = {
                                'parent_pos': (madre_x, madre_y),
                                'hijos': [],
                                'tipo': 'madre_sola'
                            }
                        conexiones_por_padres[madre_id]['hijos'].append((person.cedula, child_x, child_y))

            # Ahora dibujar las conexiones con ramificación horizontal
            for parent_key, info in conexiones_por_padres.items():
                parent_x, parent_y = info['parent_pos']
                hijos = info['hijos']
                
                if len(hijos) == 1:
                    # Un solo hijo: línea directa
                    cedula, child_x, child_y = hijos[0]
                    canvas.create_line(parent_x, parent_y, child_x, child_y,
                                     fill="#1976D2", width=4, capstyle="round", 
                                     arrow=tk.LAST, arrowshape=(16, 20, 8))
                
                elif len(hijos) > 1:
                    # Múltiples hijos: sistema de ramificación horizontal
                    
                    # Calcular la altura de la línea horizontal (a mitad de camino)
                    min_child_y = min(child_y for _, _, child_y in hijos)
                    horizontal_y = parent_y + (min_child_y - parent_y) * 0.6
                    
                    # Calcular el rango horizontal de los hijos
                    children_x = [child_x for _, child_x, _ in hijos]
                    min_child_x = min(children_x)
                    max_child_x = max(children_x)
                    
                    # 1. Línea vertical desde el padre hasta la altura horizontal
                    canvas.create_line(parent_x, parent_y, parent_x, horizontal_y,
                                     fill="#1976D2", width=4, capstyle="round")
                    
                    # 2. Línea horizontal que abarca todos los hijos
                    canvas.create_line(min_child_x, horizontal_y, max_child_x, horizontal_y,
                                     fill="#1976D2", width=4, capstyle="round")
                    
                    # 3. Líneas verticales individuales a cada hijo
                    for cedula, child_x, child_y in hijos:
                        canvas.create_line(child_x, horizontal_y, child_x, child_y,
                                         fill="#1976D2", width=4, capstyle="round",
                                         arrow=tk.LAST, arrowshape=(16, 20, 8))
                    
                    # 4. Registrar las rutas ocupadas para evitar colisiones futuras
                    rutas_ocupadas.append({
                        'type': 'padre-hijo-horizontal',
                        'horizontal_y': horizontal_y,
                        'x_start': min_child_x,
                        'x_end': max_child_x
                    })

            # 3. RELACIONES DE HERMANOS (solo si no interfieren)
            hermanos_unicos = set()
            for person in family.members:
                if person.siblings and person.cedula in pos:
                    for sibling in person.siblings:
                        if sibling.cedula in pos:
                            hermano_id = tuple(sorted([person.cedula, sibling.cedula]))
                            hermanos_unicos.add(hermano_id)
            
            # Dibujar hermanos con rutas que eviten todas las líneas existentes
            for hermano_id in hermanos_unicos:
                cedula1, cedula2 = hermano_id
                if cedula1 in pos and cedula2 in pos:
                    x1, y1 = pos[cedula1]
                    x2, y2 = pos[cedula2]
                    
                    # Solo dibujar si están en el mismo nivel
                    if abs(y1 - y2) < 30:
                        # Buscar altura libre arriba del nivel
                        curve_y = self._encontrar_altura_libre_para_hermanos(
                            min(x1, x2), max(x1, x2), y1, rutas_ocupadas
                        )
                        
                        if curve_y:  # Solo dibujar si encontramos espacio libre
                            mid_x = (x1 + x2) / 2
                            canvas.create_line(x1, y1, mid_x, curve_y, x2, y2,
                                             fill="#4CAF50", width=3, dash=(8, 4), smooth=True, 
                                             capstyle="round", joinstyle="round")
                                             
        except Exception as e:
            print(f"Error dibujando conexiones familiares: {e}")

    def _calcular_ruta_sin_colisiones(self, start_x, start_y, end_x, end_y, rutas_ocupadas):
        """Calcula la mejor ruta en L evitando colisiones con rutas existentes"""
        # Distancia base para el punto de inflexión
        base_offset = abs(end_y - start_y) * 0.6
        
        # Probar diferentes alturas para el segmento horizontal
        for offset_multiplier in [0.6, 0.4, 0.8, 0.3, 0.9]:
            test_y = start_y + (end_y - start_y) * offset_multiplier
            
            # Verificar si esta altura está libre de colisiones
            if self._ruta_libre_de_colisiones(start_x, test_y, end_x, test_y, rutas_ocupadas):
                return {
                    'start': (start_x, start_y),
                    'bend1': (start_x, test_y),
                    'bend2': (end_x, test_y),
                    'end': (end_x, end_y)
                }
        
        # Si no encuentra espacio, usar ruta básica con offset mínimo
        fallback_y = start_y + (end_y - start_y) * 0.5
        return {
            'start': (start_x, start_y),
            'bend1': (start_x, fallback_y),
            'bend2': (end_x, fallback_y),
            'end': (end_x, end_y)
        }
    
    def _ruta_libre_de_colisiones(self, x1, y, x2, y2, rutas_ocupadas):
        """Verifica si una ruta horizontal está libre de colisiones"""
        min_x, max_x = min(x1, x2), max(x1, x2)
        
        for ruta in rutas_ocupadas:
            if ruta['type'] == 'matrimonial':
                # Verificar colisión con líneas matrimoniales horizontales
                if (abs(ruta['y'] - y) < 20 and  # Misma altura aproximada
                    not (max_x < ruta['x_start'] or min_x > ruta['x_end'])):  # Se superponen horizontalmente
                    return False
            
            elif ruta['type'] == 'padre-hijo':
                # Verificar colisión con segmentos horizontales de otras rutas padre-hijo
                if 'horizontal_y' in ruta:
                    if (abs(ruta['horizontal_y'] - y) < 20 and
                        not (max_x < ruta['x_start'] or min_x > ruta['x_end'])):
                        return False
        
        return True
    
    def _dibujar_ruta_en_l(self, canvas, ruta, color, width, arrow=False):
        """Dibuja una ruta en L con los puntos especificados y mejor apariencia"""
        start = ruta['start']
        bend1 = ruta['bend1']
        bend2 = ruta['bend2']
        end = ruta['end']
        
        # Segmento vertical inicial con bordes redondeados
        canvas.create_line(start[0], start[1], bend1[0], bend1[1],
                         fill=color, width=width, capstyle="round", joinstyle="round")
        
        # Segmento horizontal con suavizado
        canvas.create_line(bend1[0], bend1[1], bend2[0], bend2[1],
                         fill=color, width=width, smooth=True, capstyle="round", joinstyle="round")
        
        # Segmento vertical final
        if arrow:
            canvas.create_line(bend2[0], bend2[1], end[0], end[1],
                             fill=color, width=width, arrow=tk.LAST,
                             arrowshape=(16, 20, 8), capstyle="round")
        else:
            canvas.create_line(bend2[0], bend2[1], end[0], end[1],
                             fill=color, width=width, capstyle="round", joinstyle="round")
    
    def _registrar_ruta_ocupada(self, rutas_ocupadas, ruta, tipo):
        """Registra una ruta como ocupada para evitar futuras colisiones"""
        rutas_ocupadas.append({
            'type': tipo,
            'horizontal_y': ruta['bend1'][1],  # Altura del segmento horizontal
            'x_start': min(ruta['bend1'][0], ruta['bend2'][0]),
            'x_end': max(ruta['bend1'][0], ruta['bend2'][0])
        })
    
    def _encontrar_altura_libre_para_hermanos(self, x_start, x_end, base_y, rutas_ocupadas):
        """Encuentra una altura libre arriba del nivel para líneas de hermanos"""
        for offset in [-30, -50, -70, -90]:  # Probar diferentes alturas arriba
            test_y = base_y + offset
            
            # Verificar que no colisione con rutas existentes
            libre = True
            for ruta in rutas_ocupadas:
                if 'horizontal_y' in ruta:
                    if (abs(ruta['horizontal_y'] - test_y) < 15 and
                        not (x_end < ruta['x_start'] or x_start > ruta['x_end'])):
                        libre = False
                        break
            
            if libre:
                return test_y
        
        return None  # No se encontró espacio libre

    def _show_menu(self, event, person):
        """Placeholder - será reemplazado en app.py"""
        print(f"Menú para {person.first_name} - Implementado en app.py")

    def _toggle_expand(self, person):
        """Maneja expand/collapse de una persona (placeholder para futuro)"""
        print(f"Toggle expand para {person.first_name} - Funcionalidad futura")


# Función de utilidad
def get_family_graph(family):
    visualizer = FamilyGraphVisualizer()
    return visualizer.build_family_graph(family)