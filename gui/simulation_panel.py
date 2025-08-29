# gui/simulation_panel.py
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import logging
import threading
import datetime
import os
import random
from models.simulation_config import SimulationConfig
from services.simulacion_service import SimulacionService
from utils.graph_visualizer import FamilyGraphVisualizer
from utils.timeline_visualizer import TimelineVisualizer

# ✅ CORRECCIÓN: Asegurar que logging esté importado
logger = logging.getLogger(__name__)

# gui/simulation_panel.py
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import logging
import threading
import datetime
import os
import random
from models.simulation_config import SimulationConfig
from services.simulacion_service import SimulacionService
from utils.graph_visualizer import FamilyGraphVisualizer
from utils.timeline_visualizer import TimelineVisualizer

# ✅ CORRECCIÓN: Asegurar que logging esté importado
logger = logging.getLogger(__name__)

class SimulationPanel:
    def __init__(self, parent, family, config: SimulationConfig = None):
        self.parent = parent
        self.family = family
        self.config = config or SimulationConfig()
        self.simulated_family = None
        self.simulation_events = []
        self.running = False
        self.paused = False
        self.simulation_mode = "memory"  # "memory" o "file"
        
        # ✅ CORRECCIÓN: Inicializar referencias de UI como None
        self.btn_start = None
        self.btn_pause = None
        self.btn_stop = None
        self.btn_import_example = None
        self.event_listbox = None
        self.tree_canvas = None
        self.stats_frame = None
        self.mode_var = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario del panel de simulación"""
        try:
            # Frame principal
            main_frame = ctk.CTkFrame(self.parent)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Título
            title_label = ctk.CTkLabel(
                main_frame,
                text="🎮 Simulación Genealógica",
                font=("Arial", 20, "bold")
            )
            title_label.pack(pady=10)
            
            # Frame de control superior
            control_frame = ctk.CTkFrame(main_frame)
            control_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Botones de control
            self.button_frame = ctk.CTkFrame(control_frame)
            self.button_frame.pack(side=tk.LEFT, padx=5, pady=5)
            
            self.btn_start = ctk.CTkButton(
                self.button_frame,
                text="▶ Iniciar",
                command=self.iniciar_simulacion,
                fg_color="#1db954",
                width=100
            )
            self.btn_start.pack(side=tk.LEFT, padx=2)
            
            self.btn_pause = ctk.CTkButton(
                self.button_frame,
                text="⏸ Pausar",
                command=self.pausar_simulacion,
                fg_color="#f39c12",
                width=100,
                state="disabled"
            )
            self.btn_pause.pack(side=tk.LEFT, padx=2)
            
            self.btn_stop = ctk.CTkButton(
                self.button_frame,
                text="⏹ Detener",
                command=self.detener_simulacion,
                fg_color="#e74c3c",
                width=100,
                state="disabled"
            )
            self.btn_stop.pack(side=tk.LEFT, padx=2)
            
            # Frame para botón de ejemplo
            example_frame = ctk.CTkFrame(control_frame)
            example_frame.pack(side=tk.RIGHT, padx=5, pady=5)
            
            self.btn_import_example = ctk.CTkButton(
                example_frame,
                text="📂 Importar Ejemplo",
                command=self.importar_ejemplo,
                fg_color="#3498db",
                width=140
            )
            self.btn_import_example.pack(side=tk.LEFT, padx=2)
            
            # Frame para modo de simulación
            mode_frame = ctk.CTkFrame(control_frame)
            mode_frame.pack(side=tk.RIGHT, padx=5, pady=5)
            
            ctk.CTkLabel(mode_frame, text="Modo:").pack(side=tk.LEFT, padx=5)
            
            self.mode_var = ctk.StringVar(value="Memoria (Rápido)")
            mode_combo = ctk.CTkComboBox(
                mode_frame,
                values=["Memoria (Rápido)", "Archivo (Persistente)"],
                variable=self.mode_var,
                width=150,
                command=self.on_mode_change
            )
            mode_combo.pack(side=tk.LEFT, padx=5)
            
            # Frame principal dividido
            content_frame = ctk.CTkFrame(main_frame)
            content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # Panel izquierdo - Árbol genealógico con scroll y zoom
            left_panel = ctk.CTkFrame(content_frame)
            left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Frame de título y controles de zoom
            tree_header_frame = ctk.CTkFrame(left_panel)
            tree_header_frame.pack(fill=tk.X, padx=5, pady=5)
            
            ctk.CTkLabel(tree_header_frame, text="🌳 Árbol Genealógico Simulado", font=("Arial", 14, "bold")).pack(side=tk.LEFT, pady=5)
            
            # Controles de zoom
            zoom_frame = ctk.CTkFrame(tree_header_frame)
            zoom_frame.pack(side=tk.RIGHT, padx=5)
            
            self.zoom_level = 1.0
            self.min_zoom = 0.3
            self.max_zoom = 3.0
            
            ctk.CTkButton(
                zoom_frame,
                text="🔍-",
                command=self.zoom_out,
                width=30,
                height=25
            ).pack(side=tk.LEFT, padx=2)
            
            self.zoom_label = ctk.CTkLabel(zoom_frame, text="100%", width=50)
            self.zoom_label.pack(side=tk.LEFT, padx=2)
            
            ctk.CTkButton(
                zoom_frame,
                text="🔍+",
                command=self.zoom_in,
                width=30,
                height=25
            ).pack(side=tk.LEFT, padx=2)
            
            ctk.CTkButton(
                zoom_frame,
                text="⚡",
                command=self.reset_zoom,
                width=30,
                height=25
            ).pack(side=tk.LEFT, padx=2)
            
            ctk.CTkButton(
                zoom_frame,
                text="📐",
                command=self.fit_to_screen,
                width=30,
                height=25
            ).pack(side=tk.LEFT, padx=2)
            
            # Frame para canvas con scrollbars
            canvas_frame = ctk.CTkFrame(left_panel)
            canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Crear scrollbars
            h_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            
            v_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Canvas principal con scrollbars
            self.tree_canvas = tk.Canvas(
                canvas_frame,
                bg="#2a2a2a",
                highlightthickness=0,
                xscrollcommand=h_scrollbar.set,
                yscrollcommand=v_scrollbar.set,
                scrollregion=(0, 0, 2000, 2000)  # Región de scroll inicial grande
            )
            self.tree_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Configurar scrollbars
            h_scrollbar.config(command=self.tree_canvas.xview)
            v_scrollbar.config(command=self.tree_canvas.yview)
            
            # Bind eventos del mouse para scroll y zoom
            self.bind_mouse_events()
            
            # Panel derecho - Eventos y estadísticas
            right_panel = ctk.CTkFrame(content_frame)
            right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
            right_panel.configure(width=300)
            
            # Eventos de simulación
            events_frame = ctk.CTkFrame(right_panel)
            events_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            ctk.CTkLabel(events_frame, text="📋 Eventos de Simulación", font=("Arial", 12, "bold")).pack(pady=5)
            
            # Lista de eventos
            events_list_frame = ctk.CTkFrame(events_frame)
            events_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            self.event_listbox = tk.Listbox(
                events_list_frame,
                bg="#3b3b3b",
                fg="white",
                selectbackground="#1db954",
                font=("Consolas", 9),
                height=15
            )
            self.event_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Estadísticas
            self.stats_frame = ctk.CTkFrame(right_panel)
            self.stats_frame.pack(fill=tk.X, padx=5, pady=5)
            
            ctk.CTkLabel(self.stats_frame, text="📊 Estadísticas", font=("Arial", 12, "bold")).pack(pady=5)
            
            # Labels para estadísticas
            self.stats_labels = {}
            stats_info = [
                ("Año actual:", "year"),
                ("Miembros vivos:", "living"),
                ("Total miembros:", "total"),
                ("Parejas:", "couples"),
                ("Nacimientos:", "births"),
                ("Fallecimientos:", "deaths")
            ]
            
            for label_text, key in stats_info:
                frame = ctk.CTkFrame(self.stats_frame)
                frame.pack(fill=tk.X, padx=5, pady=2)
                
                ctk.CTkLabel(frame, text=label_text).pack(side=tk.LEFT, padx=5)
                label = ctk.CTkLabel(frame, text="0")
                label.pack(side=tk.RIGHT, padx=5)
                self.stats_labels[key] = label
            
            # ✅ CORRECCIÓN: Inicializar visualizador aquí
            self.visualizer = None
            
            logger.info("UI del panel de simulación configurada correctamente")
            
        except Exception as e:
            logger.error(f"Error configurando UI del panel de simulación: {e}", exc_info=True)
            raise
    
    def bind_mouse_events(self):
        """Configura eventos del mouse para el canvas"""
        try:
            # Scroll con rueda del mouse
            self.tree_canvas.bind("<MouseWheel>", self.on_mouse_wheel)
            self.tree_canvas.bind("<Button-4>", self.on_mouse_wheel)  # Linux
            self.tree_canvas.bind("<Button-5>", self.on_mouse_wheel)  # Linux
            
            # Zoom con Ctrl + rueda del mouse
            self.tree_canvas.bind("<Control-MouseWheel>", self.on_ctrl_mouse_wheel)
            
            # Arrastrar canvas
            self.tree_canvas.bind("<ButtonPress-1>", self.on_canvas_drag_start)
            self.tree_canvas.bind("<B1-Motion>", self.on_canvas_drag)
            
            # Focus para recibir eventos de teclado
            self.tree_canvas.focus_set()
            
        except Exception as e:
            logger.error(f"Error configurando eventos del mouse: {e}")
    
    def on_mouse_wheel(self, event):
        """Maneja el scroll vertical con la rueda del mouse"""
        try:
            if event.delta:
                delta = event.delta
            elif event.num == 4:
                delta = 120
            elif event.num == 5:
                delta = -120
            else:
                delta = 0
            
            self.tree_canvas.yview_scroll(int(-1 * (delta / 120)), "units")
        except Exception as e:
            logger.error(f"Error en scroll del mouse: {e}")
    
    def on_ctrl_mouse_wheel(self, event):
        """Maneja el zoom con Ctrl + rueda del mouse"""
        try:
            if event.delta > 0 or event.num == 4:
                self.zoom_in()
            elif event.delta < 0 or event.num == 5:
                self.zoom_out()
        except Exception as e:
            logger.error(f"Error en zoom del mouse: {e}")
    
    def on_canvas_drag_start(self, event):
        """Inicia el arrastre del canvas"""
        self.tree_canvas.scan_mark(event.x, event.y)
    
    def on_canvas_drag(self, event):
        """Arrastra el canvas"""
        self.tree_canvas.scan_dragto(event.x, event.y, gain=1)
    
    def zoom_in(self):
        """Aumenta el zoom"""
        try:
            if self.zoom_level < self.max_zoom:
                old_zoom = self.zoom_level
                self.zoom_level = min(self.max_zoom, self.zoom_level * 1.2)
                self.apply_zoom(old_zoom)
        except Exception as e:
            logger.error(f"Error en zoom in: {e}")
    
    def zoom_out(self):
        """Disminuye el zoom"""
        try:
            if self.zoom_level > self.min_zoom:
                old_zoom = self.zoom_level
                self.zoom_level = max(self.min_zoom, self.zoom_level / 1.2)
                self.apply_zoom(old_zoom)
        except Exception as e:
            logger.error(f"Error en zoom out: {e}")
    
    def reset_zoom(self):
        """Resetea el zoom al 100%"""
        try:
            old_zoom = self.zoom_level
            self.zoom_level = 1.0
            self.apply_zoom(old_zoom)
            
            # Centrar la vista
            self.tree_canvas.xview_moveto(0.3)
            self.tree_canvas.yview_moveto(0.1)
        except Exception as e:
            logger.error(f"Error en reset zoom: {e}")
    
    def fit_to_screen(self):
        """Ajusta el zoom para que todo el contenido sea visible"""
        try:
            # Actualizar canvas y obtener dimensiones
            self.tree_canvas.update_idletasks()
            bbox = self.tree_canvas.bbox("all")
            
            if not bbox:
                return
            
            # Obtener dimensiones del canvas visible
            canvas_width = self.tree_canvas.winfo_width()
            canvas_height = self.tree_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return
            
            # Calcular dimensiones del contenido
            content_width = bbox[2] - bbox[0]
            content_height = bbox[3] - bbox[1]
            
            # Calcular zoom necesario con margen
            margin_factor = 0.9  # 10% de margen
            zoom_x = (canvas_width * margin_factor) / content_width
            zoom_y = (canvas_height * margin_factor) / content_height
            
            # Usar el menor zoom para que todo encaje
            new_zoom = min(zoom_x, zoom_y)
            new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))
            
            # Aplicar nuevo zoom
            old_zoom = self.zoom_level
            self.zoom_level = new_zoom
            self.apply_zoom(old_zoom)
            
            # Centrar contenido
            self.tree_canvas.xview_moveto(0.1)
            self.tree_canvas.yview_moveto(0.1)
            
        except Exception as e:
            logger.error(f"Error en fit to screen: {e}")
    
    def apply_zoom(self, old_zoom):
        """Aplica el nivel de zoom actual al canvas"""
        try:
            # Actualizar etiqueta de zoom
            zoom_percent = int(self.zoom_level * 100)
            self.zoom_label.configure(text=f"{zoom_percent}%")
            
            # Escalar todo el contenido del canvas
            scale_factor = self.zoom_level / old_zoom
            self.tree_canvas.scale("all", 0, 0, scale_factor, scale_factor)
            
            # Actualizar región de scroll
            bbox = self.tree_canvas.bbox("all")
            if bbox:
                margin = 100
                scroll_region = (
                    bbox[0] - margin,
                    bbox[1] - margin,
                    bbox[2] + margin,
                    bbox[3] + margin
                )
                self.tree_canvas.configure(scrollregion=scroll_region)
            
        except Exception as e:
            logger.error(f"Error aplicando zoom: {e}")
    
    def on_mode_change(self, selection):
        """Cambia el modo de simulación"""
        self.simulation_mode = "memory" if "Memoria" in selection else "file"
        logger.info(f"Modo de simulación cambiado a: {self.simulation_mode}")
    
    def iniciar_simulacion(self):
        """Inicia la simulación según el modo seleccionado"""
        try:
            if self.simulation_mode == "memory":
                self.iniciar_simulacion_memoria()
            else:
                self.iniciar_simulacion_archivo()
        except Exception as e:
            logger.error(f"Error iniciando simulación: {e}", exc_info=True)
            messagebox.showerror("Error", f"Error al iniciar simulación: {str(e)}")
    
    def iniciar_simulacion_memoria(self):
        """Simulación en memoria - RÁPIDA"""
        try:
            import copy
            
            if not self.simulated_family:
                # Crear copia profunda de la familia
                self.simulated_family = copy.deepcopy(self.family)
                self.simulated_family.current_year = self.family.current_year or 2024
                
                # Limpiar eventos anteriores
                self.simulation_events.clear()
                if self.event_listbox:
                    self.event_listbox.delete(0, tk.END)
                
                self.add_simulation_event("🚀 Simulación iniciada en modo memoria")
            
            # Configurar controles
            if self.btn_start:
                self.btn_start.configure(state="disabled")
            if self.btn_pause:
                self.btn_pause.configure(state="normal")
            if self.btn_stop:
                self.btn_stop.configure(state="normal")
            
            self.running = True
            self.paused = False
            
            # Actualizar visualización inicial
            self.draw_tree()
            self.update_stats_display()
            
            # Iniciar hilo de simulación
            thread = threading.Thread(target=self.run_simulation, daemon=True)
            thread.start()
            
        except Exception as e:
            logger.error(f"Error en iniciar_simulacion_memoria: {e}", exc_info=True)
            raise
    
    def iniciar_simulacion_archivo(self):
        """Simulación basada en archivos - PERSISTENTE"""
        try:
            from utils.gedcom_parser import GedcomParser
            
            # 1. Exportar familia actual a GEDCOM temporal
            temp_file = "simulations/temp_family.ged"
            os.makedirs("simulations", exist_ok=True)
            
            success = self.family.export_to_gedcom(temp_file)
            if not success:
                messagebox.showerror("Error", "No se pudo exportar la familia")
                return
            
            # 2. Leer el GEDCOM como nueva familia
            with open(temp_file, 'r', encoding='utf-8') as file:
                gedcom_content = file.read()
            
            # Crear nueva familia para la simulación
            from models.family import Family
            self.simulated_family = Family(id="simulated_family", name="Familia Simulada")
            
            # Parsear el contenido GEDCOM
            self.simulated_family = GedcomParser.parse(self.simulated_family, gedcom_content)
            
            if not self.simulated_family:
                messagebox.showerror("Error", "No se pudo cargar la familia desde GEDCOM")
                return
            
            # 3. Configurar simulación
            self.simulated_family.current_year = self.family.current_year or 2024
            
            # 4. Guardar estado inicial
            self.save_simulation_state()
            
            self.add_simulation_event("🚀 Simulación iniciada en modo archivo")
            
        except Exception as e:
            logger.error(f"Error en iniciar_simulacion_archivo: {e}", exc_info=True)
            messagebox.showerror("Error", f"Error al iniciar simulación: {e}")
    
    def importar_ejemplo(self):
        """Importa la familia de ejemplo y inicia la simulación automáticamente"""
        try:
            from utils.gedcom_parser import GedcomParser
            
            # Ruta del archivo de ejemplo
            ejemplo_path = os.path.join("simulations", "ejemplo.ged")
            
            # Verificar que el archivo existe
            if not os.path.exists(ejemplo_path):
                messagebox.showerror(
                    "Error", 
                    f"No se encontró el archivo de ejemplo en: {ejemplo_path}\n"
                    "Asegúrate de que el archivo ejemplo.ged existe en la carpeta simulations/"
                )
                return
            
            # Confirmar importación
            response = messagebox.askyesno(
                "Importar Ejemplo",
                "¿Deseas cargar la familia de ejemplo?\n\n"
                "Esto reemplazará la familia actual en la simulación y comenzará "
                "una nueva simulación automáticamente.\n\n"
                "Familia de ejemplo: Familia Rodríguez-González\n"
                "• 9 miembros (3 generaciones)\n"
                "• Incluye abuelos, padres e hijos\n"
                "• Datos realistas para simulación"
            )
            
            if not response:
                return
            
            # Leer el archivo GEDCOM
            with open(ejemplo_path, 'r', encoding='utf-8') as file:
                gedcom_content = file.read()
            
            # Crear nueva familia para el ejemplo
            from models.family import Family
            ejemplo_family = Family(id="ejemplo_family", name="Familia Rodríguez-González")
            
            # Parsear el contenido GEDCOM
            ejemplo_family = GedcomParser.parse(ejemplo_family, gedcom_content)
            
            if not ejemplo_family or not ejemplo_family.members:
                messagebox.showerror("Error", "No se pudo cargar la familia de ejemplo")
                return
            
            # Importar la familia de ejemplo
            self.simulated_family = ejemplo_family
            self.simulated_family.current_year = 2024  # Año base
            
            # Limpiar eventos anteriores
            self.simulation_events.clear()
            if self.event_listbox:
                self.event_listbox.delete(0, tk.END)
            
            # Actualizar visualización
            self.draw_tree()
            self.update_stats_display()
            
            # Agregar evento de importación
            self.add_simulation_event("📂 Familia de ejemplo importada exitosamente")
            
            # Mostrar información de la familia importada
            living_members = len([p for p in self.simulated_family.members if p.alive])
            total_members = len(self.simulated_family.members)
            couples = len([p for p in self.simulated_family.members if p.has_partner()]) // 2
            
            info_event = f"👥 {living_members} miembros vivos de {total_members} totales, {couples} parejas"
            self.add_simulation_event(info_event)
            
            # Configurar modo de simulación a memoria para velocidad
            self.simulation_mode = "memory"
            if self.mode_var:
                self.mode_var.set("Memoria (Rápido)")
            
            # Mostrar confirmación
            messagebox.showinfo(
                "Ejemplo Cargado",
                f"¡Familia de ejemplo cargada exitosamente!\n\n"
                f"• {living_members} miembros vivos\n"
                f"• {total_members} miembros totales\n"
                f"• {couples} parejas\n\n"
                "Usa el botón 'Iniciar' para comenzar la simulación."
            )
            
        except Exception as e:
            logger.error(f"Error importando ejemplo: {e}", exc_info=True)
            messagebox.showerror("Error", f"Error al importar ejemplo: {str(e)}")
    
    def pausar_simulacion(self):
        """Pausa o reanuda la simulación"""
        if self.paused:
            self.paused = False
            if self.btn_pause:
                self.btn_pause.configure(text="⏸ Pausar")
            self.add_simulation_event("▶ Simulación reanudada")
        else:
            self.paused = True
            if self.btn_pause:
                self.btn_pause.configure(text="▶ Reanudar")
            self.add_simulation_event("⏸ Simulación pausada")
    
    def detener_simulacion(self):
        """Detiene la simulación"""
        self.running = False
        self.paused = False
        
        if self.btn_start:
            self.btn_start.configure(state="normal")
        if self.btn_pause:
            self.btn_pause.configure(state="disabled", text="⏸ Pausar")
        if self.btn_stop:
            self.btn_stop.configure(state="disabled")
        
        self.add_simulation_event("⏹ Simulación detenida")
    
    def run_simulation(self):
        """Ejecuta el bucle principal de simulación"""
        try:
            while self.running:
                if not self.paused and self.simulated_family:
                    # Ejecutar un ciclo de simulación
                    eventos = SimulacionService.ejecutar_ciclo_completo(self.simulated_family, self.config)
                    
                    # Agregar eventos a la lista
                    for evento in eventos:
                        self.add_simulation_event(evento)
                    
                    # Actualizar visualización
                    self.parent.after(0, self.draw_tree)
                    self.parent.after(0, self.update_stats_display)
                    
                    # Avanzar un año
                    self.simulated_family.current_year += 1
                    
                    # Dormir según la configuración
                    threading.Event().wait(self.config.events_interval)
                else:
                    # Si está pausado, dormir un poco
                    threading.Event().wait(0.1)
                    
        except Exception as e:
            logger.error(f"Error en simulación: {e}", exc_info=True)
            self.parent.after(0, lambda: self.add_simulation_event(f"❌ Error en simulación: {str(e)}"))
    
    def draw_tree(self):
        """Dibuja el árbol de la familia simulada con soporte para scroll y zoom"""
        try:
            if not self.simulated_family or not hasattr(self, 'tree_canvas'):
                return
            
            # Crear nuevo visualizador si no existe
            if not self.visualizer:
                self.visualizer = FamilyGraphVisualizer()
            
            # Limpiar canvas antes de dibujar
            self.tree_canvas.delete("all")
            
            # ✅ USAR EL MÉTODO CORRECTO con Canvas
            self.visualizer.draw_family_tree(self.simulated_family, self.tree_canvas)
            
            # Actualizar región de scroll después de dibujar
            self.update_scroll_region()
            
        except Exception as e:
            logger.error(f"Error al dibujar árbol en simulación: {e}", exc_info=True)
            # Mostrar error en el canvas
            if hasattr(self, 'tree_canvas'):
                self.tree_canvas.delete("all")
                self.tree_canvas.create_text(
                    600, 400,
                    text="Error al dibujar simulación",
                    font=("Arial", 12),
                    fill="red"
                )
    
    def update_scroll_region(self):
        """Actualiza la región de scroll basada en el contenido del canvas"""
        try:
            # Actualizar el canvas para asegurar que todos los elementos estén dibujados
            self.tree_canvas.update_idletasks()
            
            # Obtener las dimensiones del contenido
            bbox = self.tree_canvas.bbox("all")
            
            if bbox:
                margin = 100
                scroll_region = (
                    bbox[0] - margin,
                    bbox[1] - margin,
                    bbox[2] + margin,
                    bbox[3] + margin
                )
                self.tree_canvas.configure(scrollregion=scroll_region)
                
                # Si es la primera vez, centrar la vista
                if not hasattr(self, '_initial_view_set'):
                    self.tree_canvas.xview_moveto(0.2)
                    self.tree_canvas.yview_moveto(0.1)
                    self._initial_view_set = True
            else:
                # Si no hay contenido, usar una región por defecto
                self.tree_canvas.configure(scrollregion=(0, 0, 1500, 1500))
                
        except Exception as e:
            logger.error(f"Error actualizando región de scroll: {e}")

    def update_stats_display(self):
        """Actualiza las estadísticas mostradas"""
        try:
            if not self.simulated_family or not self.stats_labels:
                return
            
            living_members = len([p for p in self.simulated_family.members if p.alive])
            total_members = len(self.simulated_family.members)
            couples = len([p for p in self.simulated_family.members if p.has_partner()]) // 2
            
            # Contar nacimientos y fallecimientos (simplificado)
            births = len([p for p in self.simulated_family.members if p.calculate_virtual_age() < 1])
            deaths = len([p for p in self.simulated_family.members if not p.alive])
            
            # Actualizar labels
            stats = {
                "year": str(self.simulated_family.current_year),
                "living": str(living_members),
                "total": str(total_members),
                "couples": str(couples),
                "births": str(births),
                "deaths": str(deaths)
            }
            
            for key, value in stats.items():
                if key in self.stats_labels:
                    self.stats_labels[key].configure(text=value)
                    
        except Exception as e:
            logger.error(f"Error actualizando estadísticas: {e}", exc_info=True)
    
    def add_simulation_event(self, event_text: str):
        """Agrega un evento a la lista de eventos de simulación"""
        try:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            formatted_event = f"[{timestamp}] {event_text}"
            
            # Agregar a la lista interna
            self.simulation_events.append(formatted_event)
            
            # Agregar al listbox visual si existe
            if self.event_listbox:
                self.event_listbox.insert(tk.END, formatted_event)
                self.event_listbox.see(tk.END)
                
                # Limitar número de eventos mostrados
                if self.event_listbox.size() > 1000:
                    self.event_listbox.delete(0, 50)
                    
        except Exception as e:
            logger.error(f"Error agregando evento de simulación: {e}", exc_info=True)
    
    def save_simulation_state(self):
        """Guarda el estado actual de la simulación"""
        if self.simulation_mode == "file" and self.simulated_family:
            try:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"simulations/simulation_{timestamp}.ged"
                self.simulated_family.export_to_gedcom(filename)
                logger.info(f"Estado de simulación guardado en: {filename}")
            except Exception as e:
                logger.error(f"Error guardando estado de simulación: {e}")
    
    def load_simulation_state(self, filename):
        """Carga un estado de simulación guardado"""
        try:
            from utils.gedcom_parser import GedcomParser
            
            # Leer el archivo GEDCOM
            with open(filename, 'r', encoding='utf-8') as file:
                gedcom_content = file.read()
            
            # Crear nueva familia para cargar el estado
            from models.family import Family
            loaded_family = Family(id="loaded_family", name="Familia Cargada")
            
            # Parsear el contenido GEDCOM
            self.simulated_family = GedcomParser.parse(loaded_family, gedcom_content)
            
            if self.simulated_family:
                self.draw_tree()
                self.update_stats_display()
                logger.info(f"Estado de simulación cargado desde: {filename}")
        except Exception as e:
            logger.error(f"Error cargando estado de simulación: {e}")