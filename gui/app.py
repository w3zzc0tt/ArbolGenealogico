# gui/app.py
import customtkinter as ctk
import tkinter as tk
import sys
import os
from tkinter import messagebox

# Añadir raíz del proyecto para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.family import Family
from models.person import Person
from models.family_manager import FamilyManager
from gui.forms import PersonForm
from gui.family_manager_panel import FamilyManagerPanel
from services.relacion_service import RelacionService
from services.persistence_service import PersistenceService
from gui.history_panel import HistoryPanel  # Importar el nuevo panel
from services.persona_service import PersonaService  # IMPORTAR EL SERVICIO DE PERSONAS

try:
    from utils.graph_visualizer import FamilyGraphVisualizer
    HAS_VISUALIZER = True
except ImportError:
    HAS_VISUALIZER = False
    print("Advertencia: No se pudo importar FamilyGraphVisualizer")


class GenealogyApp:
    def __init__(self, root):
        self.root = root  # Guardar la ventana principal
        self.root.title("🌳 Árbol Genealógico Familiar")
        self.root.geometry("1200x800")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Inicializar servicio de persistencia
        self.persistence_service = PersistenceService()
        
        # Intentar cargar datos guardados
        loaded_manager = self.persistence_service.load_family_manager()
        
        if loaded_manager:
            self.family_manager = loaded_manager
            print(f"✅ Datos cargados: {len(self.family_manager.families)} familias restauradas")
        else:
            # Inicializar nuevo gestor si no hay datos guardados
            self.family_manager = FamilyManager()
            # Crear una familia por defecto si no hay ninguna
            self.family_manager.create_family("Mi Primera Familia", "Familia de ejemplo inicial")
            print("📁 Nuevo gestor de familias creado")
        
        # Obtener la familia actual
        self.family = self.family_manager.get_current_family()
        
        # Configurar evento de cierre para guardar automáticamente
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Pestañas
        self.notebook = ctk.CTkTabview(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # NUEVA: Pestaña de Gestor de Familias (primera pestaña)
        self.family_manager_tab = self.notebook.add("👨‍👩‍👧‍👦 Gestor de Familias")
        self.tree_tab = self.notebook.add("🌳 Árbol Genealógico")
        self.history_tab = self.notebook.add("📚 Historial")
        self.simulation_tab = self.notebook.add("🎲 Simulación")
        self.consultas_tab = self.notebook.add("🔍 Consultas")

        # Configurar pestañas
        self.setup_family_manager_tab()
        self.setup_tree_tab()
        self.setup_history_tab()
        self.setup_simulation_tab()
        self.setup_consultas_tab()
    
    def setup_family_manager_tab(self):
        """Configura la pestaña del gestor de familias"""
        self.family_manager_panel = FamilyManagerPanel(
            self.family_manager_tab, 
            self.family_manager,
            on_family_change_callback=self.on_family_change,
            app_instance=self  # Pasar referencia de la aplicación
        )

    def setup_consultas_tab(self):
        from gui.consultas_panel import ConsultasPanel
        self.consultas_panel = ConsultasPanel(self.consultas_tab, self.family)

    def setup_simulation_tab(self):
        from gui.simulation_panel import SimulationPanel
        self.simulation_panel = SimulationPanel(self.simulation_tab, self.family)

    def setup_tree_tab(self):
        frame = ctk.CTkFrame(self.tree_tab)
        frame.pack(fill=tk.BOTH, expand=True)

        # Canvas para el árbol
        self.tree_canvas = tk.Canvas(frame, bg="#2a2a2a", highlightthickness=0)
        self.tree_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configurar botón del Ego inicial
        self.update_ego_button()
        
        self.draw_tree()

    def open_person_form_for_ego(self):
        def on_save(data):
            person = Person(
                cedula=data["cedula"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                birth_date=data["birth_date"],
                gender=data["gender"],
                province=data["province"],
                death_date=data["death_date"],
                marital_status=data["marital_status"]
            )
            self.family.add_or_update_member(person)
            
            # Actualizar el botón del Ego usando el nuevo método
            self.update_ego_button()
            
            self.draw_tree()
            self.update_history_tab()
            # Guardar datos automáticamente
            self.save_data()

        PersonForm(self.root, title="Agregar Persona Principal", on_save=on_save)

    def draw_tree(self):
        """Método en tu clase principal (app.py)"""
        try:
            # Verificar si el canvas existe
            if hasattr(self, 'tree_canvas') and self.tree_canvas.winfo_exists():
                # Crear una nueva instancia del visualizador para asegurar datos frescos
                visualizer = FamilyGraphVisualizer()
                
                # ✅ CORRECCIÓN CLAVE: Nueva definición con orden correcto
                def custom_show_menu(event, person):
                    menu = tk.Menu(self.root, tearoff=0)
                    
                    # 👑 MENÚ ESPECIAL PARA EL EGO
                    if self.family.is_ego(person):
                        menu.add_command(
                            label="👑 Editar Ego (Tú)",
                            command=lambda: self.editar_persona(person),
                            font=("Arial", 9, "bold")
                        )
                        menu.add_separator()
                        
                        # Solo permitir agregar familiares, NO eliminar
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
                            label="� Ver relaciones",
                            command=lambda: self.mostrar_relaciones(person)
                        )
                        # NO incluir opción de eliminar para el Ego
                    else:
                        # MENÚ NORMAL PARA OTRAS PERSONAS
                        menu.add_command(
                            label="✏️ Editar Persona",
                            command=lambda: self.editar_persona(person)
                        )
                        menu.add_separator()
                        
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
                        menu.add_command(
                            label="🗑️ Eliminar Persona",
                            command=lambda: self.eliminar_persona(person)
                        )
                    
                    menu.tk_popup(event.x_root, event.y_root)
                    menu.grab_release()

                # ✅ Asignar el nuevo método con el orden correcto
                visualizer._show_menu = custom_show_menu
                
                # Dibujar el árbol
                visualizer.draw_family_tree(self.family, self.tree_canvas)
            else:
                # Recrear el canvas si no existe
                self.recreate_tree_canvas()
        except Exception as e:
            print(f"Error al dibujar árbol: {e}")
            # Intentar recrear el canvas
            self.recreate_tree_canvas()

    def recreate_tree_canvas(self):
        """Recrea el canvas del árbol en caso de que se haya destruido"""
        try:
            # Destruir canvas existente si existe
            if hasattr(self, 'tree_canvas') and self.tree_canvas.winfo_exists():
                self.tree_canvas.destroy()
            
            # Crear un nuevo canvas
            self.tree_canvas = tk.Canvas(self.tree_tab, bg="#2a2a2a", highlightthickness=0)
            self.tree_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Intentar dibujar el árbol nuevamente
            self.draw_tree()
        except Exception as e:
            print(f"Error al recrear el canvas: {e}")

    def _draw_basic_tree(self):
        canvas_width = self.tree_canvas.winfo_width() or 1200
        x_step = canvas_width / (len(self.family.members) + 1)
        y = 400

        for i, person in enumerate(self.family.members):
            x = (i + 1) * x_step
            color = "#3b8ed0" if person.alive else "#d35f5f"
            self.tree_canvas.create_oval(x-30, y-30, x+30, y+30, fill=color, outline="#1f7dbf", width=2)
            self.tree_canvas.create_text(x, y, text=f"{person.first_name}\n{person.last_name}", fill="white", font=("Arial", 10, "bold"))
            self.tree_canvas.create_text(x, y+25, text=person.cedula, fill="lightgray", font=("Arial", 8))

    # Fragmento de app.py - MÉTODO CORREGIDO
    def abrir_formulario_relacion(self, persona, tipo_relacion):
        def on_save(data):
            # Crear la nueva persona
            nueva_persona = Person(
                cedula=data["cedula"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                birth_date=data["birth_date"],
                gender=data["gender"],  # Ahora maneja "Masculino"/"Femenino" correctamente
                province=data["province"],
                death_date=data["death_date"],
                marital_status=data["marital_status"]
            )

            # Validar que no exista ya
            if self.family.get_member_by_cedula(nueva_persona.cedula):
                messagebox.showerror("Error", "Ya existe una persona con esa cédula")
                return

            # Agregar a la familia
            self.family.add_or_update_member(nueva_persona)

            # CORREGIDO: Usar funciones auxiliares para validar género
            def es_masculino(gender):
                return gender in ["M", "Masculino"]
            
            def es_femenino(gender):
                return gender in ["F", "Femenino"]

            # Establecer la relación según el tipo
            exito = False
            mensaje = ""

            if tipo_relacion == "padre":
                if es_masculino(nueva_persona.gender):
                    # Solo pasa father_cedula
                    exito, mensaje = RelacionService.registrar_padres(
                        self.family,
                        child_cedula=persona.cedula,
                        father_cedula=nueva_persona.cedula
                    )
                else:
                    messagebox.showerror("Error", "El padre debe ser masculino")
                    self.family.members.remove(nueva_persona)  # Eliminar si falla
                    return
            
            elif tipo_relacion == "madre":
                if es_femenino(nueva_persona.gender):
                    # Solo pasa mother_cedula
                    exito, mensaje = RelacionService.registrar_padres(
                        self.family,
                        child_cedula=persona.cedula,
                        mother_cedula=nueva_persona.cedula
                    )
                else:
                    messagebox.showerror("Error", "La madre debe ser femenina")
                    self.family.members.remove(nueva_persona)  # Eliminar si falla
                    return

            elif tipo_relacion == "conyuge":
                exito, mensaje = RelacionService.registrar_pareja(
                    self.family,
                    person1_cedula=persona.cedula,
                    person2_cedula=nueva_persona.cedula
                )

            elif tipo_relacion == "hijo":
                # USO CORRECTO: child_cedula es la NUEVA persona (hijo)
                exito, mensaje = RelacionService.registrar_hijo_con_pareja(
                    self.family,
                    persona.cedula,
                    nueva_persona.cedula
                )

            elif tipo_relacion == "hermano":
                # USO CORRECTO: child_cedula es la NUEVA persona (hermano)
                exito, mensaje = RelacionService.registrar_padres(
                    family=self.family,
                    child_cedula=nueva_persona.cedula,
                    father_cedula=persona.father.cedula if persona.father else None,
                    mother_cedula=persona.mother.cedula if persona.mother else None
                )

            # Resultado
            if exito:
                messagebox.showinfo("Éxito", f"{mensaje}\n{nueva_persona.first_name} ahora es {tipo_relacion} de {persona.first_name}")
                self.draw_tree()
                self.update_history_tab()
            else:
                messagebox.showerror("Error", mensaje)
                # Si falló, eliminar la persona recién creada
                if nueva_persona in self.family.members:
                    self.family.members.remove(nueva_persona)

        # Abrir formulario para NUEVA persona
        title_map = {
            "padre": "Agregar Nuevo Padre",
            "madre": "Agregar Nueva Madre",
            "conyuge": "Agregar Nuevo Cónyuge",
            "hijo": "Agregar Nuevo Hijo",
            "hermano": "Agregar Nuevo Hermano"
        }
        title = title_map.get(tipo_relacion, f"Agregar Nueva Persona como {tipo_relacion}")

        PersonForm(self.root, title=title, on_save=on_save)

    def editar_persona(self, person):
        """Abre formulario para editar una persona existente"""
        def on_save(data):
            # Actualizar los datos de la persona
            person.first_name = data["first_name"]
            person.last_name = data["last_name"]
            person.birth_date = data["birth_date"]
            person.gender = data["gender"]
            person.province = data["province"]
            person.death_date = data["death_date"]
            person.marital_status = data["marital_status"]
            
            # Actualizar en la familia
            self.family.add_or_update_member(person)
            
            if self.family.is_ego(person):
                messagebox.showinfo("Éxito", f"✅ Ego actualizado: {person.first_name} {person.last_name}")
            else:
                messagebox.showinfo("Éxito", f"✅ Persona actualizada: {person.first_name} {person.last_name}")
            
            self.draw_tree()
            self.update_history_tab()
            self.save_data()

        # Preparar datos actuales para el formulario
        current_data = {
            "cedula": person.cedula,
            "first_name": person.first_name,
            "last_name": person.last_name,
            "birth_date": person.birth_date,
            "gender": person.gender,
            "province": person.province,
            "death_date": person.death_date,
            "marital_status": person.marital_status
        }

        title = "👑 Editar Ego (Tú)" if self.family.is_ego(person) else f"✏️ Editar {person.first_name}"
        PersonForm(self.root, title=title, on_save=on_save, data=current_data)

    def eliminar_persona(self, person):
        """Método mejorado para eliminar una persona usando el servicio completo"""
        if messagebox.askyesno("Confirmar", f"¿Eliminar a {person.first_name} {person.last_name}?"):
            # Usar el servicio de eliminación completo
            exito, mensaje = PersonaService.eliminar_persona(self.family, person.cedula)
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                
                # 🔧 ACTUALIZAR botón Ego si se eliminó a alguien
                self.update_ego_button()
                
                self.draw_tree()
                self.update_history_tab()
            else:
                messagebox.showerror("Error", mensaje)

    def mostrar_relaciones(self, person):
        """Muestra un popup con las relaciones de la persona"""
        relaciones = []
        if person.father:
            relaciones.append(f"Padre: {person.father.first_name} {person.father.last_name}")
        if person.mother:
            relaciones.append(f"Madre: {person.mother.first_name} {person.mother.last_name}")
        if person.spouse:
            relaciones.append(f"Pareja: {person.spouse.first_name} {person.spouse.last_name}")
        if person.children:
            hijos = ", ".join([f"{c.first_name}" for c in person.children])
            relaciones.append(f"Hijos: {hijos}")
        if person.siblings:
            hermanos = ", ".join([f"{s.first_name}" for s in person.siblings])
            relaciones.append(f"Hermanos: {hermanos}")

        info = "\n".join(relaciones) if relaciones else "No hay relaciones registradas."
        messagebox.showinfo(f"Relaciones de {person.first_name}", info)

    def setup_history_tab(self):
        # CREAR EL PANEL DE HISTORIA CON SELF COMO PADRE (NO self.history_tab)
        self.history_panel = HistoryPanel(self.history_tab, self.family)
        self.history_panel.update_history()

    def update_history_tab(self):
        self.history_panel.update_history()
    
    def on_family_change(self):
        """Callback que se ejecuta cuando cambia la familia actual"""
        # Obtener la nueva familia actual
        self.family = self.family_manager.get_current_family()
        
        # Actualizar el título de la ventana
        if self.family:
            self.root.title(f"🌳 Árbol Genealógico - {self.family.name} (ID {self.family.id:03d})")
        else:
            self.root.title("🌳 Árbol Genealógico Familiar")
        
        # Actualizar los paneles que dependen de la familia
        try:
            # Actualizar el panel de consultas
            if hasattr(self, 'consultas_panel'):
                self.consultas_panel.family = self.family
                self.consultas_panel.actualizar_lista_personas()
            
            # Actualizar el panel de simulación
            if hasattr(self, 'simulation_panel'):
                self.simulation_panel.family = self.family
            
            # Actualizar el panel de historial
            if hasattr(self, 'history_panel'):
                self.history_panel.family = self.family
                self.history_panel.update_history()
            
            # 🔧 ACTUALIZAR BOTÓN DEL EGO EN EL ÁRBOL GENEALÓGICO
            self.update_ego_button()
            
            # Redibujar el árbol
            self.draw_tree()
            
            # Guardar cambios automáticamente
            self.save_data()
            
        except Exception as e:
            print(f"Error al actualizar paneles: {e}")
    
    def update_ego_button(self):
        """Actualiza la visibilidad del botón Agregar Ego según la familia actual"""
        if not hasattr(self, 'tree_tab') or not self.family:
            return
            
        # Obtener el frame principal del árbol
        tree_frame = None
        for child in self.tree_tab.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                tree_frame = child
                break
        
        if not tree_frame:
            return
        
        # Si la familia no tiene miembros, mostrar el botón del Ego
        if not self.family.members:
            # Si ya existe un botón del Ego, no hacer nada
            if hasattr(self, 'add_ego_button') and self.add_ego_button and self.add_ego_button.winfo_exists():
                return
            
            # Crear el botón del Ego
            self.add_ego_button = ctk.CTkButton(
                tree_frame,
                text="➕ Agregar Persona Principal (Ego)",
                command=self.open_person_form_for_ego,
                font=("Arial", 14, "bold"),
                fg_color="#1db954",
                hover_color="#1ed760"
            )
            self.add_ego_button.pack(pady=20, before=self.tree_canvas)
        else:
            # Si la familia tiene miembros, ocultar el botón del Ego
            if hasattr(self, 'add_ego_button') and self.add_ego_button and self.add_ego_button.winfo_exists():
                self.add_ego_button.destroy()
                self.add_ego_button = None
    
    def save_data(self) -> bool:
        """Guarda todos los datos de las familias"""
        try:
            success = self.persistence_service.save_family_manager(self.family_manager)
            if success:
                print("💾 Datos guardados exitosamente")
                return True
            else:
                print("❌ Error al guardar datos")
                return False
        except Exception as e:
            print(f"❌ Error al guardar: {e}")
            return False
    
    def auto_save(self):
        """Guardado automático cada 30 segundos"""
        self.save_data()
        # Programar próximo guardado automático
        self.root.after(30000, self.auto_save)  # 30 segundos
    
    def create_backup(self):
        """Crea una copia de seguridad de los datos"""
        try:
            success = self.persistence_service.backup_data()
            if success:
                messagebox.showinfo("Backup", "Copia de seguridad creada exitosamente")
            else:
                messagebox.showerror("Error", "Error al crear copia de seguridad")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear backup: {e}")
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        try:
            # Guardar datos antes de cerrar
            success = self.save_data()
            if success:
                print("💾 Datos guardados antes del cierre")
            else:
                # Preguntar al usuario si quiere cerrar sin guardar
                result = messagebox.askyesno(
                    "Error al Guardar",
                    "No se pudieron guardar los datos.\n¿Desea cerrar la aplicación de todas formas?\n\nSe perderán los cambios realizados."
                )
                if not result:
                    return  # No cerrar si el usuario cancela
            
        except Exception as e:
            print(f"Error durante el cierre: {e}")
        
        # Cerrar la aplicación
        self.root.destroy()

    def run(self):
        # Iniciar guardado automático
        self.root.after(30000, self.auto_save)  # Primer guardado automático en 30 segundos
        self.root.mainloop()


if __name__ == "__main__":
    root = ctk.CTk()
    app = GenealogyApp(root)
    app.run()