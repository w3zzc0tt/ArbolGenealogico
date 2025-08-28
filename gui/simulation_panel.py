# gui/simulation_panel.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import time
import logging  # ✅ CORRECCIÓN CLAVE: Falta importar logging
from models.simulation_config import SimulationConfig
from services.simulacion_service import SimulacionService
from utils.graph_visualizer import FamilyGraphVisualizer  # ✅ CORRECCIÓN: Cambiado a gui.graph_visualizer
from utils.timeline_visualizer import TimelineVisualizer  # ✅ CORRECCIÓN: Cambiado a gui.timeline_visualizer
from gui.forms import RelationshipForm, PersonForm  # ✅ CORRECCIÓN: Importar formularios necesarios
from services.utils_service import calcular_compatibilidad_total  # ✅ IMPORTACIÓN CORREGIDA

class SimulationPanel:
    def __init__(self, parent, family, config: SimulationConfig = None):
        self.parent = parent
        self.family = family
        self.simulated_family = None
        self.running = False
        self.config = config or SimulationConfig()
        self.selected_person = None
        self.setup_ui()
    
    def setup_ui(self):
        self.frame = ctk.CTkFrame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel de control
        control_frame = ctk.CTkFrame(self.frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Botones de control - ✅ DEFINIR button_frame AQUÍ
        self.button_frame = ctk.CTkFrame(control_frame)  # ✅ AÑADIDO self.
        self.button_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        self.btn_start = ctk.CTkButton(
            self.button_frame,  # ✅ USAR self.button_frame
            text="▶️ Iniciar Simulación",
            command=self.iniciar_simulacion,
            fg_color="#1db954"
        )
        self.btn_start.pack(side=tk.LEFT, padx=5)
        
        self.btn_pause = ctk.CTkButton(
            self.button_frame,  # ✅ USAR self.button_frame
            text="⏸️ Pausar",
            command=self.pausar_simulacion,
            fg_color="#3498db",
            state="disabled"
        )
        self.btn_pause.pack(side=tk.LEFT, padx=5)
        
        self.btn_stop = ctk.CTkButton(
            self.button_frame,  # ✅ USAR self.button_frame
            text="⏹️ Detener",
            command=self.detener_simulacion,
            fg_color="#e74c3c",
            state="disabled"
        )
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        # Configuración de velocidad
        speed_frame = ctk.CTkFrame(control_frame)
        speed_frame.pack(side=tk.RIGHT, padx=5, pady=5)
        
        ctk.CTkLabel(speed_frame, text="Velocidad:").pack(side=tk.LEFT, padx=5)
        
        self.speed_var = ctk.StringVar(value="1x")
        speed_options = ctk.CTkComboBox(
            speed_frame,
            values=["0.5x", "1x", "2x", "5x", "10x"],
            variable=self.speed_var,
            width=80,
            state="readonly"
        )
        speed_options.pack(side=tk.LEFT, padx=5)
        speed_options.set("1x")
        
        # Canvas para el árbol
        self.tree_canvas = tk.Canvas(self.frame, bg="#2a2a2a", highlightthickness=0)
        self.tree_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Área de eventos
        event_frame = ctk.CTkFrame(self.frame)
        event_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ctk.CTkLabel(event_frame, text="Eventos recientes:").pack(anchor="w", padx=5, pady=2)
        
        self.event_text = ctk.CTkTextbox(event_frame, height=100)
        self.event_text.pack(fill=tk.X, padx=5, pady=2)

        self.agregar_boton_timeline()
        self.setup_stats_panel()
    
    def iniciar_simulacion(self):
        # Crear copia del árbol para simulación
        from copy import deepcopy
        self.simulated_family = deepcopy(self.family)
        self.simulated_family.current_year = self.family.current_year
        
        # ✅ CORRECCIÓN CLAVE: Configurar velocidad correctamente
        speed = float(self.speed_var.get().replace('x', ''))
        self.config.events_interval = 1 / speed  # Ajustar intervalo de eventos
        
        self.running = True
        self.btn_start.configure(state="disabled")
        self.btn_pause.configure(state="normal")
        self.btn_stop.configure(state="normal")
        
        # Iniciar hilo de simulación
        thread = threading.Thread(target=self.run_simulation, daemon=True)
        thread.start()
    
    def run_simulation(self):
        """Ciclo de simulación mejorado - CORREGIDO"""
        last_event = time.time()
        while self.running:
            current_time = time.time()
            
            # Procesar todos los eventos en un solo ciclo cada 10 segundos
            if current_time - last_event >= 10:
                try:
                    # Ejecutar ciclo completo de simulación
                    eventos = SimulacionService.ejecutar_ciclo_completo(
                        self.simulated_family,
                        self.config
                    )
                    
                    # Mostrar eventos
                    for evento in eventos:
                        self.event_text.insert("end", f"{evento}\n")
                        self.event_text.see("end")
                        
                    last_event = current_time
                    
                    # Actualizar estadísticas
                    self.update_stats_display()
                    
                    # Redibujar árbol
                    self.draw_tree()
                    
                except Exception as e:
                    self.event_text.insert("end", f"Error en simulación: {str(e)}\n")
                    logging.error(f"Error en simulación: {str(e)}", exc_info=True)  # ✅ Mejor logging
            
            # Esperar un poco para no saturar la CPU
            time.sleep(0.1)
    
    def pausar_simulacion(self):
        self.running = False
        self.btn_start.configure(state="normal")
        self.btn_pause.configure(state="disabled")
        self.btn_stop.configure(state="normal")
    
    def detener_simulacion(self):
        self.running = False
        self.simulated_family = None
        self.event_text.delete("1.0", "end")
        self.tree_canvas.delete("all")
        self.btn_start.configure(state="normal")
        self.btn_pause.configure(state="disabled")
        self.btn_stop.configure(state="disabled")
        self.update_stats_display()
    
    def draw_tree(self):
        if not self.simulated_family or not self.simulated_family.members:
            return
        
        self.tree_canvas.delete("all")
        
        # Usar el visualizador para dibujar el árbol
        visualizer = FamilyGraphVisualizer()
        
        # ✅ CORRECCIÓN CLAVE: Nueva definición con orden correcto
        def custom_show_menu(event, person):
            menu = tk.Menu(self.parent, tearoff=0)
            menu.add_command(
                label="➕ Agregar Padre",
                command=lambda: self.abrir_formulario_relacion(person, "padre")
            )
            menu.add_command(
                label="➕ Agregar Madre",
                command=lambda: self.abrir_formulario_relacion(person, "madre")
            )
            menu.add_command(
                label="💍 Agregar Cónyuge",
                command=lambda: self.abrir_formulario_relacion(person, "conyuge")
            )
            menu.add_command(
                label="👶 Agregar Hijo",
                command=lambda: self.abrir_formulario_relacion(person, "hijo")
            )
            menu.add_command(
                label="🧍 Agregar Hermano",
                command=lambda: self.abrir_formulario_relacion(person, "hermano")
            )
            menu.add_separator()
            menu.add_command(
                label="📊 Ver Estadísticas",
                command=lambda: self.mostrar_estadisticas_persona(person)
            )
            menu.add_command(
                label="🔍 Ver Relaciones",
                command=lambda: self.mostrar_relaciones(person)
            )
            menu.add_command(
                label="⏰ Ver Línea de Tiempo",
                command=lambda: TimelineVisualizer.create_timeline_window(person)
            )
            menu.add_separator()
            menu.add_command(
                label="✏️ Editar Persona",
                command=lambda: self.abrir_formulario_edicion(person)
            )
            menu.add_command(
                label="🗑️ Eliminar Persona",
                command=lambda: self.eliminar_persona(person)
            )
            menu.tk_popup(event.x_root, event.y_root)
            menu.grab_release()

        # ✅ Asignar el nuevo método con el orden correcto
        visualizer._show_menu = custom_show_menu
        
        # ✅ CORRECCIÓN: Método correcto para dibujar el árbol
        visualizer.draw_tree(self.simulated_family, self.tree_canvas)
    
    def agregar_boton_timeline(self):
        """Agrega botón para ver línea de tiempo"""
        timeline_btn = ctk.CTkButton(
            self.button_frame,
            text="⏰ Línea de Tiempo",
            command=self.mostrar_timeline_seleccionada,
            fg_color="#9b59b6"
        )
        timeline_btn.pack(side=tk.LEFT, padx=5)

    def mostrar_timeline_seleccionada(self):
        """Muestra línea de tiempo de persona seleccionada"""
        if not self.simulated_family or not self.simulated_family.members:
            messagebox.showinfo("Información", "No hay personas en la familia para mostrar")
            return
            
        # Crear ventana de selección
        select_window = ctk.CTkToplevel(self.parent)
        select_window.title("Seleccionar Persona")
        select_window.geometry("400x300")
        
        # Frame para lista de personas
        list_frame = ctk.CTkFrame(select_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ctk.CTkScrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Lista de personas
        person_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 12))
        person_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar.configure(command=person_list.yview)
        
        # Agregar personas a la lista
        for person in self.simulated_family.members:
            status = "Vivo" if person.alive else "Fallecido"
            person_list.insert(tk.END, f"{person.first_name} {person.last_name} ({status})")
        
        # Botón de selección
        def on_select():
            selection = person_list.curselection()
            if selection:
                index = selection[0]
                person = self.simulated_family.members[index]
                TimelineVisualizer.create_timeline_window(person)
                select_window.destroy()
        
        select_btn = ctk.CTkButton(
            select_window, 
            text="Ver Línea de Tiempo", 
            command=on_select,
            fg_color="#1db954"
        )
        select_btn.pack(pady=10)
    
    def setup_stats_panel(self):
        """Panel de estadísticas en tiempo real"""
        stats_frame = ctk.CTkFrame(self.frame)
        stats_frame.pack(fill="x", padx=5, pady=5)
        
        # Labels de estadísticas
        self.stats_labels = {}
        stats = [
            ("👥 Total", "total_people"),
            ("💚 Vivos", "alive_count"),
            ("💔 Fallecidos", "deceased_count"),
            ("💍 Casados", "married_count"),
            ("👶 Menores", "children_count"),
            ("🔥 Año", "current_year")
        ]
        
        for i, (label, key) in enumerate(stats):
            stat_label = ctk.CTkLabel(stats_frame, text=f"{label}: 0")
            stat_label.grid(row=0, column=i, padx=10, pady=5)
            self.stats_labels[key] = stat_label
    
    def update_stats_display(self):
        """Actualiza estadísticas en pantalla - CORREGIDO"""
        if not self.simulated_family or not hasattr(self, 'stats_labels'):
            return
        
        try:
            # ✅ CORRECCIÓN: Usar métodos correctos y calculate_virtual_age
            stats = {
                'total_people': len(self.simulated_family.members),
                'alive_count': sum(1 for p in self.simulated_family.members if p.alive),
                'deceased_count': sum(1 for p in self.simulated_family.members if not p.alive),
                'married_count': sum(1 for p in self.simulated_family.members if p.has_partner()),
                'children_count': sum(1 for p in self.simulated_family.members 
                                    if p.alive and p.calculate_virtual_age() < 18),
                'current_year': getattr(self.simulated_family, 'current_year', 2024)
            }
            
            for key, value in stats.items():
                if key in self.stats_labels:
                    label_text = self.stats_labels[key].cget('text').split(':')[0]
                    self.stats_labels[key].configure(text=f"{label_text}: {value}")
        except Exception as e:
            logging.error(f"Error actualizando estadísticas: {e}", exc_info=True)
    
    # ✅ NUEVOS MÉTODOS AGREGADOS
    def abrir_formulario_relacion(self, person, relation_type):
        """Abre el formulario para agregar una relación"""
        RelationshipForm(self.parent, self.simulated_family, person, relation_type)
    
    def mostrar_relaciones(self, person):
        """Muestra todas las relaciones de una persona"""
        if not self.simulated_family:
            return
            
        relations = []
        
        # Padre/Madre
        if person.father:
            relations.append(f"Padre: {person.father.first_name} {person.father.last_name}")
        if person.mother:
            relations.append(f"Madre: {person.mother.first_name} {person.mother.last_name}")
        
        # Hijo/Hija
        if person.children:
            children = ", ".join([f"{c.first_name}" for c in person.children])
            relations.append(f"Hijos: {children}")
        
        # Hermanos
        if person.siblings:
            siblings = ", ".join([f"{s.first_name}" for s in person.siblings])
            relations.append(f"Hermanos: {siblings}")
        
        # Pareja
        if person.spouse:
            relations.append(f"Pareja: {person.spouse.first_name} {person.spouse.last_name} ({person.marital_status})")
        
        # Si no hay relaciones
        if not relations:
            relations.append("No hay relaciones registradas")
        
        # Mostrar en popup
        relations_window = ctk.CTkToplevel(self.parent)
        relations_window.title(f"Relaciones de {person.first_name}")
        relations_window.geometry("400x300")
        
        # Configuración crítica para ventanas modales
        relations_window.transient(self.parent)
        relations_window.grab_set()
        relations_window.focus_force()
        
        # Crear texto con scroll
        text_frame = ctk.CTkFrame(relations_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ctk.CTkScrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(text_frame, yscrollcommand=scrollbar.set, 
                             bg="#2a2a2a", fg="white", font=("Arial", 12))
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.configure(command=text_widget.yview)
        
        # Insertar relaciones
        for relation in relations:
            text_widget.insert(tk.END, f"• {relation}\n\n")
        
        text_widget.config(state="disabled")
        
        # Botón para cerrar
        ctk.CTkButton(relations_window,
                     text="Cerrar",
                     command=relations_window.destroy,
                     fg_color="#e74c3c").pack(pady=10)
        
        # Esperar a que la ventana se cierre
        self.parent.wait_window(relations_window)
    
    def mostrar_estadisticas_persona(self, person):
        """Muestra estadísticas detalladas de una persona"""
        stats = person.get_statistics()
        
        # Crear ventana de estadísticas
        stats_window = ctk.CTkToplevel(self.parent)
        stats_window.title(f"Estadísticas - {person.first_name} {person.last_name}")
        stats_window.geometry("400x450")
        
        # Título
        ctk.CTkLabel(stats_window, text=f"Estadísticas - {person.first_name} {person.last_name}", 
                    font=("Arial", 16, "bold")).pack(pady=10)
        
        # Mostrar estadísticas
        stats_frame = ctk.CTkFrame(stats_window)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for key, value in stats.items():
            if isinstance(value, float):
                value = f"{value:.2f}"
            ctk.CTkLabel(stats_frame, text=f"{key}:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
            ctk.CTkLabel(stats_frame, text=str(value), font=("Arial", 12)).pack(anchor="w", padx=20, pady=(0, 10))
        
        # ✅ Añadir sección de compatibilidad
        ctk.CTkLabel(stats_frame, text="\nCompatibilidad:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        
        # Buscar pareja para mostrar compatibilidad
        if person.spouse:
            compatibility = calcular_compatibilidad_total(person, person.spouse)
            
            ctk.CTkLabel(stats_frame, text=f"Con {person.spouse.first_name}:", font=("Arial", 11)).pack(anchor="w", padx=10)
            ctk.CTkLabel(stats_frame, text=f"Total: {compatibility['total']:.1f}%", font=("Arial", 11)).pack(anchor="w", padx=20)
            ctk.CTkLabel(stats_frame, text=f"Recomendación: {compatibility['recommendation']}", 
                        font=("Arial", 11), wraplength=350).pack(anchor="w", padx=20)
            
            # Mostrar desglose
            ctk.CTkLabel(stats_frame, text="Desglose:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(5, 0))
            for category, score in compatibility['breakdown'].items():
                ctk.CTkLabel(stats_frame, text=f"- {category.capitalize()}: {score}", 
                            font=("Arial", 10)).pack(anchor="w", padx=30)
            
            # Mostrar intereses en común
            if 'common_interests' in compatibility and compatibility['common_interests']:
                ctk.CTkLabel(stats_frame, text="Intereses en común:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(5, 0))
                for interest in compatibility['common_interests']:
                    ctk.CTkLabel(stats_frame, text=f"- {interest}", 
                                font=("Arial", 10)).pack(anchor="w", padx=30)
        
        # Botón de cierre
        ctk.CTkButton(stats_window, text="Cerrar", command=stats_window.destroy, 
                     fg_color="#3498db").pack(pady=10)
    
    def abrir_formulario_edicion(self, person):
        """Abre el formulario para editar una persona"""
        def on_save(data):
            # Actualizar los datos de la persona
            person.cedula = data["cedula"]
            person.first_name = data["first_name"]
            person.last_name = data["last_name"]
            person.birth_date = data["birth_date"]
            person.gender = data["gender"]  # Ya está en formato M/F
            person.province = data["province"]
            person.marital_status = data["marital_status"]
            person.death_date = data["death_date"]
            
            # Actualizar estado de vida
            person.alive = person.death_date is None
            
            # Actualizar árbol
            self.draw_tree()
            # Actualizar estadísticas
            self.update_stats_display()
        
        PersonForm(
            self.parent, 
            self.simulated_family,
            title=f"Editar {person.first_name}",
            on_save=on_save,
            data={
                "cedula": person.cedula,
                "first_name": person.first_name,
                "last_name": person.last_name,
                "birth_date": person.birth_date,
                "gender": "Masculino" if person.gender == "M" else "Femenino",
                "province": person.province,
                "marital_status": person.marital_status,
                "death_date": person.death_date,
            }
        )
    
    def eliminar_persona(self, person):
        """Elimina una persona de la familia"""
        from services.persona_service import PersonaService
        
        confirm = messagebox.askyesno("Confirmar eliminación", 
                                    f"¿Está seguro de eliminar a {person.first_name} {person.last_name}?")
        if confirm:
            exito, mensaje = PersonaService.eliminar_persona(self.simulated_family, person.cedula)
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                # Actualizar árbol
                self.draw_tree()
                # Actualizar estadísticas
                self.update_stats_display()
            else:
                messagebox.showerror("Error", mensaje)