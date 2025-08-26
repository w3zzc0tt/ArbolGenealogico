# gui/simulation_panel.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import time
from models.simulation_config import SimulationConfig
from services.simulacion_service import SimulacionService
from utils.graph_visualizer import FamilyGraphVisualizer

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
        
        # Botones de control
        button_frame = ctk.CTkFrame(control_frame)
        button_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        self.btn_start = ctk.CTkButton(
            button_frame,
            text="▶️ Iniciar Simulación",
            command=self.iniciar_simulacion,
            fg_color="#1db954"
        )
        self.btn_start.pack(side=tk.LEFT, padx=5)
        
        self.btn_pause = ctk.CTkButton(
            button_frame,
            text="⏸️ Pausar",
            command=self.pausar_simulacion,
            fg_color="#3498db",
            state="disabled"
        )
        self.btn_pause.pack(side=tk.LEFT, padx=5)
        
        self.btn_stop = ctk.CTkButton(
            button_frame,
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
        while self.running:
            # Ejecutar ciclo de simulación
            eventos = SimulacionService.ejecutar_ciclo_simulacion(
                self.simulated_family, 
                self.config
            )
            
            # Agregar eventos al historial
            for evento in eventos:
                self.event_text.insert("end", f"{evento}\n")
                self.event_text.see("end")
            
            # Redibujar árbol
            self.draw_tree()
            
            # Esperar tiempo real configurado
            time.sleep(self.config.real_time_per_year)
    
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