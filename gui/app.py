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

try:
    from utils.graph_visualizer import FamilyGraphVisualizer
    HAS_VISUALIZER = True
except ImportError:
    HAS_VISUALIZER = False
    print("Advertencia: No se pudo importar FamilyGraphVisualizer")


class GenealogyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌳 Árbol Genealógico Familiar")
        self.root.geometry("1200x800")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.family = Family(1, "Mi Familia")
        self.selected_person = None
        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Pestañas
        self.notebook = ctk.CTkTabview(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree_tab = self.notebook.add("Árbol Genealógico")
        self.history_tab = self.notebook.add("Historial")

        self.setup_tree_tab()
        self.setup_history_tab()

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
            self.family.add_member(person)
            if self.add_ego_button:
                self.add_ego_button.destroy()
            self.draw_tree()
            self.update_history_tab()

        PersonForm(self.root, title="Agregar Persona Principal", on_save=on_save)

    def draw_tree(self):
        self.tree_canvas.delete("all")
        if not self.family.members:
            self.tree_canvas.create_text(600, 400, text="No hay personas en el árbol", fill="white", font=("Arial", 16))
            return

        if HAS_VISUALIZER:
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
                    label="🔍 Ver relaciones",
                    command=lambda: self.mostrar_relaciones(person)
                )
                menu.tk_popup(event.x_root, event.y_root)
                menu.grab_release()

            # ✅ Asignar el nuevo método con el orden correcto
            visualizer._show_menu = custom_show_menu
            
            visualizer.draw_family_tree(self.family, self.tree_canvas)
        else:
            self._draw_basic_tree()

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
        """Abre un formulario para seleccionar una persona y establecer una relación"""
        form = ctk.CTkToplevel(self.root)
        form.title(f"Agregar {tipo_relacion}")
        form.geometry("400x300")
        form.transient(self.root)
        form.grab_set()

        ctk.CTkLabel(form, text=f"Selecciona una persona para ser {tipo_relacion} de {persona.first_name}").pack(pady=10)

        # Lista de personas (excepto la misma persona)
        opciones = [p for p in self.family.members if p.cedula != persona.cedula]
        if not opciones:
            ctk.CTkLabel(form, text="No hay otras personas en la familia").pack(pady=20)
            return

        nombres = [f"{p.first_name} {p.last_name} ({p.cedula})" for p in opciones]
        combo = ctk.CTkComboBox(form, values=nombres, width=300)
        combo.pack(pady=10)

        def guardar():
            seleccion = combo.get()
            cedula_destino = seleccion.split("(")[-1].rstrip(")")

            exito = False
            mensaje = ""

            if tipo_relacion == "padre":
                exito, mensaje = RelacionService.registrar_padres(
                    self.family, cedula_destino, mother_cedula="", father_cedula=persona.cedula
                )
            elif tipo_relacion == "madre":
                exito, mensaje = RelacionService.registrar_padres(
                    self.family, cedula_destino, mother_cedula=persona.cedula, father_cedula=""
                )
            elif tipo_relacion == "conyuge":
                exito, mensaje = RelacionService.registrar_pareja(self.family, persona.cedula, cedula_destino)
            elif tipo_relacion == "hijo":
                exito, mensaje = RelacionService.registrar_padres(
                    self.family, cedula_destino, mother_cedula="", father_cedula=""
                )
                # Lo manejamos al revés: hijo → padre/madre
                madre = next((p for p in self.family.members if p.cedula == cedula_destino), None)
                if madre and madre.gender == "Femenino":
                    exito, mensaje = RelacionService.registrar_padres(self.family, cedula_destino, mother_cedula=persona.cedula, father_cedula="")
                else:
                    exito, mensaje = RelacionService.registrar_padres(self.family, cedula_destino, mother_cedula="", father_cedula=persona.cedula)
            elif tipo_relacion == "hermano":
                # Asumimos que comparten al menos un padre/madre
                exito, mensaje = True, "Hermano agregado (funcionalidad básica)"
                persona.siblings.append(next((p for p in self.family.members if p.cedula == cedula_destino), None))

            if exito:
                form.destroy()
                self.draw_tree()
                self.update_history_tab()
                messagebox.showinfo("Éxito", mensaje)
            else:
                messagebox.showerror("Error", mensaje)

        ctk.CTkButton(form, text="Guardar", command=guardar, fg_color="#1db954").pack(pady=20)

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
        self.history_text = tk.Text(self.history_tab, bg="#2a2a2a", fg="white", font=("Consolas", 10))
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.update_history_tab()

    def update_history_tab(self):
        self.history_text.delete(1.0, tk.END)
        for person in self.family.members:
            self.history_text.insert(tk.END, f"👤 {person}\n", "person")
            for event in person.history:
                self.history_text.insert(tk.END, f"  • {event}\n", "event")
            self.history_text.insert(tk.END, "\n")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = ctk.CTk()
    app = GenealogyApp(root)
    app.run()