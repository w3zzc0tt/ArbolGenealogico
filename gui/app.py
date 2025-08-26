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
from gui.forms import PersonForm
from services.relacion_service import RelacionService
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

        self.family = Family(1, "Mi Familia")
        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Pestañas
        self.notebook = ctk.CTkTabview(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree_tab = self.notebook.add("Árbol Genealógico")
        self.history_tab = self.notebook.add("Historial")

        self.simulation_tab = self.notebook.add("Simulación")

        self.setup_tree_tab()
        self.setup_history_tab()
        self.setup_simulation_tab()

    def setup_simulation_tab(self):
        from gui.simulation_panel import SimulationPanel
        self.simulation_panel = SimulationPanel(self.simulation_tab, self.family)

    def setup_tree_tab(self):
        frame = ctk.CTkFrame(self.tree_tab)
        frame.pack(fill=tk.BOTH, expand=True)

        # Botón agregar Ego
        if not self.family.members:
            self.add_ego_button = ctk.CTkButton(
                frame,
                text="➕ Agregar Persona Principal (Ego)",
                command=self.open_person_form_for_ego,
                font=("Arial", 14, "bold"),
                fg_color="#1db954",
                hover_color="#1ed760"
            )
            self.add_ego_button.pack(pady=20)
        else:
            self.add_ego_button = None

        # Canvas para el árbol
        self.tree_canvas = tk.Canvas(frame, bg="#2a2a2a", highlightthickness=0)
        self.tree_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

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
            if self.add_ego_button:
                self.add_ego_button.destroy()
            self.draw_tree()
            self.update_history_tab()

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
                        label="🗑️ Eliminar Persona",
                        command=lambda: self.eliminar_persona(person)
                    )
                    menu.add_command(
                        label="🔍 Ver relaciones",
                        command=lambda: self.mostrar_relaciones(person)
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

    def abrir_formulario_relacion(self, persona, tipo_relacion):
        def on_save(data):
            # Crear la nueva persona
            nueva_persona = Person(
                cedula=data["cedula"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                birth_date=data["birth_date"],
                gender=data["gender"],
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

            # Establecer la relación según el tipo
            exito = False
            mensaje = ""

            if tipo_relacion == "padre":
                if nueva_persona.gender == "Masculino":
                    # ✅ Solo pasa father_cedula
                    exito, mensaje = RelacionService.registrar_padres(
                        self.family,
                        child_cedula=persona.cedula,
                        father_cedula=nueva_persona.cedula
                    )
                else:
                    messagebox.showerror("Error", "El padre debe ser masculino")
                    return
            
            elif tipo_relacion == "madre":
                if nueva_persona.gender == "Femenino":
                    # ✅ Solo pasa mother_cedula
                    exito, mensaje = RelacionService.registrar_padres(
                        self.family,
                        child_cedula=persona.cedula,
                        mother_cedula=nueva_persona.cedula
                    )
                else:
                    messagebox.showerror("Error", "La madre debe ser femenina")
                    return

            elif tipo_relacion == "conyuge":
                exito, mensaje = RelacionService.registrar_pareja(
                    self.family,
                    person1_cedula=persona.cedula,
                    person2_cedula=nueva_persona.cedula
                )

            elif tipo_relacion == "hijo":
                # ✅ USO CORRECTO: child_cedula es la NUEVA persona (hijo)
                exito, mensaje = RelacionService.registrar_hijo_con_pareja(
                    self.family,
                    persona.cedula,
                    nueva_persona.cedula
                )

            elif tipo_relacion == "hermano":
                # ✅ USO CORRECTO: child_cedula es la NUEVA persona (hermano)
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

    def eliminar_persona(self, person):
        """Método mejorado para eliminar una persona usando el servicio completo"""
        if messagebox.askyesno("Confirmar", f"¿Eliminar a {person.first_name} {person.last_name}?"):
            # Usar el servicio de eliminación completo
            exito, mensaje = PersonaService.eliminar_persona(self.family, person.cedula)
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
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

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = ctk.CTk()
    app = GenealogyApp(root)
    app.run()