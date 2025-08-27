# gui/simulation_panel.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import time
from models.simulation_config import SimulationConfig
from services.simulacion_service import SimulacionService
from utils.graph_visualizer import FamilyGraphVisualizer
from utils.timeline_visualizer import TimelineVisualizer

class SimulationPanel:
    def __init__(self, parent, family):
        self.parent = parent
        self.family = family
        self.simulated_family = None
        self.running = False
        self.config = SimulationConfig()
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
        
        # Configurar velocidad
        speed = float(self.speed_var.get().replace('x', ''))
        self.config.real_time_per_year = max(1, 10 / speed)  # Ajustar tiempo real por año
        
        self.running = True
        self.btn_start.configure(state="disabled")
        self.btn_pause.configure(state="normal")
        self.btn_stop.configure(state="normal")
        
        # Iniciar hilo de simulación
        thread = threading.Thread(target=self.run_simulation, daemon=True)
        thread.start()
    
    def run_simulation(self):
        """Ciclo de simulación mejorado - CORREGIDO"""
        last_birthday = time.time()
        last_events = time.time()
        
        while self.running:
            current_time = time.time()
            
            # Cumpleaños cada 10 segundos
            if current_time - last_birthday >= 10:
                try:
                    birthday_events = SimulacionService.ejecutar_ciclo_cumpleanos(self.simulated_family)
                    for evento in birthday_events:
                        self.event_text.insert("end", f"{evento}\n")
                        self.event_text.see("end")
                except Exception as e:
                    self.event_text.insert("end", f"Error en cumpleaños: {e}\n")
                last_birthday = current_time
            
            # Otros eventos cada 5 segundos
            if current_time - last_events >= 5:
                try:
                    eventos = SimulacionService.ejecutar_ciclo_completo(  # ← CAMBIAR MÉTODO
                        self.simulated_family, 
                        self.config
                    )
                    
                    for evento in eventos:
                        self.event_text.insert("end", f"{evento}\n")
                        self.event_text.see("end")
                except Exception as e:
                    self.event_text.insert("end", f"Error en simulación: {e}\n")
                    
                last_events = current_time
            
            # Actualizar estadísticas
            try:
                self.update_stats_display()
            except:
                pass
            
            # Redibujar árbol
            try:
                self.draw_tree()
            except Exception as e:
                print(f"Error dibujando árbol: {e}")
            
            # Esperar intervalo mínimo
            time.sleep(0.5)
    
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
                label="🔍 Ver relaciones",
                command=lambda: self.mostrar_relaciones(person)
            )
            menu.tk_popup(event.x_root, event.y_root)
            menu.grab_release()

        # ✅ Asignar el nuevo método con el orden correcto
        visualizer._show_menu = custom_show_menu
        
        visualizer.draw_family_tree(self.simulated_family, self.tree_canvas)
    
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
        # Implementar selección de persona
        # Por simplicidad, mostrar de la primera persona
        if self.simulated_family and self.simulated_family.members:
            person = self.simulated_family.members[0]
            TimelineVisualizer.create_timeline_window(person)

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
            stats = {
                'total_people': len(self.simulated_family.members),
                'alive_count': len(self.simulated_family.get_living_members()),
                'deceased_count': len(self.simulated_family.get_deceased_members()),
                'married_count': len([p for p in self.simulated_family.members if p.has_partner()]),
                'children_count': len([p for p in self.simulated_family.members 
                                    if p.alive and p.calculate_age() < 18]),
                'current_year': getattr(self.simulated_family, 'current_year', 2024)
            }
            
            for key, value in stats.items():
                if key in self.stats_labels:
                    label_text = self.stats_labels[key].cget('text').split(':')[0]
                    self.stats_labels[key].configure(text=f"{label_text}: {value}")
        except Exception as e:
            print(f"Error actualizando estadísticas: {e}")