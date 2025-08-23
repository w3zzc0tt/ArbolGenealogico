import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import random
import datetime

# Configuración de customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# === CLASES DE DATOS ===
class Person:
    def __init__(self, cedula, first_name, last_name, birth_date, gender, province, death_date=None):
        self.cedula = cedula
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.death_date = death_date
        self.gender = gender
        self.province = province
        self.marital_status = "Soltero"
        self.spouse = None
        self.mother = None
        self.father = None
        self.children = []
        self.siblings = []
        self.alive = death_date is None
        self.history = [f"Nació en {birth_date}"]
        if not self.alive:
            self.history.append(f"Falleció en {death_date}")

    def add_event(self, event_type, date=None):
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.history.append(f"{event_type} ({date})")
        self.history.sort(key=lambda x: x.split('(')[1].rstrip(')') if '(' in x else "")

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.cedula})"


class Family:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.members = []


# === FORMULARIO EMERGENTE REUTILIZABLE ===
class PersonForm(ctk.CTkToplevel):
    def __init__(self, parent, title="Agregar Persona", on_save=None, data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("500x650")
        self.resizable(False, False)
        self.on_save = on_save
        self.data = data or {}

        # Centrar ventana
        self.transient(parent)
        self.grab_set()

        self.setup_ui()

    def setup_ui(self):
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ctk.CTkLabel(form_frame, text="📋 Registrar Persona", font=("Arial", 18, "bold")).pack(pady=15)

        form = ctk.CTkFrame(form_frame)
        form.pack(fill=tk.X, padx=10, pady=10)
        form.columnconfigure(1, weight=1)

        # Cédula
        ctk.CTkLabel(form, text="Cédula:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.cedula_entry = ctk.CTkEntry(form, placeholder_text="9-12 dígitos, solo números", width=220)
        self.cedula_entry.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        self.cedula_entry.insert(0, self.data.get("cedula", ""))

        # Nombre
        ctk.CTkLabel(form, text="Nombre:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=10, pady=8)
        self.first_name_entry = ctk.CTkEntry(form, placeholder_text="Ej: María", width=220)
        self.first_name_entry.grid(row=1, column=1, padx=10, pady=8, sticky="ew")
        self.first_name_entry.insert(0, self.data.get("first_name", ""))

        # Apellidos
        ctk.CTkLabel(form, text="Apellidos:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", padx=10, pady=8)
        self.last_name_entry = ctk.CTkEntry(form, placeholder_text="Ej: López Fernández", width=220)
        self.last_name_entry.grid(row=2, column=1, padx=10, pady=8, sticky="ew")
        self.last_name_entry.insert(0, self.data.get("last_name", ""))

        # Fecha nacimiento
        ctk.CTkLabel(form, text="Fecha Nac.:", font=("Arial", 12)).grid(row=3, column=0, sticky="w", padx=10, pady=8)
        self.birth_entry = ctk.CTkEntry(form, placeholder_text="YYYY-MM-DD", width=220)
        self.birth_entry.grid(row=3, column=1, padx=10, pady=8, sticky="ew")
        self.birth_entry.insert(0, self.data.get("birth_date", ""))

        # Género
        ctk.CTkLabel(form, text="Género:", font=("Arial", 12)).grid(row=4, column=0, sticky="w", padx=10, pady=8)
        self.gender_var = ctk.StringVar(value=self.data.get("gender", "Masculino"))
        gender_combo = ctk.CTkComboBox(form, values=["Masculino", "Femenino"], variable=self.gender_var, width=220, state="readonly")
        gender_combo.grid(row=4, column=1, padx=10, pady=8, sticky="ew")

        # Provincia
        ctk.CTkLabel(form, text="Provincia:", font=("Arial", 12)).grid(row=5, column=0, sticky="w", padx=10, pady=8)
        self.province_var = ctk.StringVar(value=self.data.get("province", "San José"))
        province_combo = ctk.CTkComboBox(form, values=[
            "San José", "Alajuela", "Cartago", "Heredia", "Guanacaste", "Puntarenas", "Limón"
        ], variable=self.province_var, width=220, state="readonly")
        province_combo.grid(row=5, column=1, padx=10, pady=8, sticky="ew")

        # Estado civil
        ctk.CTkLabel(form, text="Estado Civil:", font=("Arial", 12)).grid(row=6, column=0, sticky="w", padx=10, pady=8)
        self.marital_status_var = ctk.StringVar(value=self.data.get("marital_status", "Soltero/a"))
        marital_status_combo = ctk.CTkComboBox(form, values=[
            "Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a"
        ], variable=self.marital_status_var, width=220, state="readonly")
        marital_status_combo.grid(row=6, column=1, padx=10, pady=8, sticky="ew")

        # Estado: Vivo / Fallecido
        ctk.CTkLabel(form, text="Estado:", font=("Arial", 12)).grid(row=7, column=0, sticky="w", padx=10, pady=8)
        self.status_var = ctk.StringVar(value="Vivo" if self.data.get("death_date") is None else "Fallecido")
        status_frame = ctk.CTkFrame(form)
        status_frame.grid(row=7, column=1, sticky="w", padx=10, pady=8)

        ctk.CTkRadioButton(status_frame, text="Vivo", variable=self.status_var, value="Vivo",
                           command=self.toggle_death_field).pack(side="left", padx=5)
        ctk.CTkRadioButton(status_frame, text="Fallecido", variable=self.status_var, value="Fallecido",
                           command=self.toggle_death_field).pack(side="left", padx=5)

        # Frame para fecha de fallecimiento
        self.death_frame = ctk.CTkFrame(form)
        self.death_frame.grid(row=8, column=1, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(self.death_frame, text="Fecha Fallec.:").pack(side="left")
        self.death_entry = ctk.CTkEntry(self.death_frame, placeholder_text="YYYY-MM-DD", width=150)
        self.death_entry.pack(side="left", padx=5)
        if self.data.get("death_date"):
            self.death_entry.insert(0, self.data["death_date"])

        # Ocultar si está vivo
        if self.status_var.get() == "Vivo":
            self.death_frame.grid_remove()
        else:
            self.death_frame.grid()

        # Botones
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy, fg_color="gray").pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Guardar", command=self.save, fg_color="#007acc").pack(side="left", padx=5)

    def toggle_death_field(self):
        if self.status_var.get() == "Fallecido":
            self.death_frame.grid()
        else:
            self.death_frame.grid_remove()

    def validate_cedula(self, cedula):
        return cedula.isdigit() and 9 <= len(cedula) <= 12

    def save(self):
        cedula = self.cedula_entry.get().strip()
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        birth_date = self.birth_entry.get().strip()
        gender = self.gender_var.get()
        province = self.province_var.get()
        marital_status = self.marital_status_var.get()
        status = self.status_var.get()
        death_date = self.death_entry.get().strip() if status == "Fallecido" else None

        if not all([cedula, first_name, last_name, birth_date]):
            messagebox.showerror("Error", "Todos los campos obligatorios deben llenarse")
            return

        if not self.validate_cedula(cedula):
            messagebox.showerror("Error", "La cédula debe tener entre 9 y 12 dígitos y contener solo números")
            return

        try:
            datetime.datetime.strptime(birth_date, "%Y-%m-%d")
            if death_date:
                datetime.datetime.strptime(death_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
            return

        data = {
            "cedula": cedula,
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": birth_date,
            "gender": gender,
            "province": province,
            "marital_status": marital_status,
            "death_date": death_date
        }

        if self.on_save:
            self.on_save(data)
        self.destroy()


# === INTERFAZ PRINCIPAL ===
class GenealogyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Árbol Genealógico")
        self.root.geometry("1200x800")

        # Variables
        self.family = Family(1, "Mi Familia")
        self.current_person = None  # Para relaciones
        self.tree_canvas = None
        self.person_nodes = {}
        self.node_id_counter = 0

        # Crear widgets
        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Solo pestaña del árbol (sin formulario)
        self.notebook = ctk.CTkTabview(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree_tab = self.notebook.add("Árbol Genealógico")

        self.setup_tree_tab()

    def setup_tree_tab(self):
        frame = ctk.CTkFrame(self.tree_tab)
        frame.pack(fill=tk.BOTH, expand=True)

        # Canvas para el árbol
        self.tree_canvas = tk.Canvas(frame, bg="#2a2a2a", highlightthickness=0)
        self.tree_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Botón para agregar Ego si no hay nadie
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

        self.draw_tree()

    def open_person_form_for_ego(self):
        """Abre el formulario para agregar al Ego"""
        def on_save(data):
            person = Person(
                cedula=data["cedula"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                birth_date=data["birth_date"],
                gender=data["gender"],
                province=data["province"],
                death_date=data["death_date"]
            )
            # Establecer el estado civil desde el formulario
            person.marital_status = data["marital_status"]
            self.family.members.append(person)
            if hasattr(self, 'add_ego_button'):
                self.add_ego_button.destroy()
            self.draw_tree()

        form = PersonForm(self.root, title="Agregar Persona Principal (Ego)", on_save=on_save)
        form.focus()

    def open_person_form_for_relation(self, parent, relation_type):
        """Abre el formulario para agregar una relación"""
        def on_save(data):
            child = Person(
                cedula=data["cedula"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                birth_date=data["birth_date"],
                gender=data["gender"],
                province=data["province"],
                death_date=data["death_date"]
            )
            # Establecer el estado civil desde el formulario
            child.marital_status = data["marital_status"]
            self.family.members.append(child)

            # Conectar relación
            if relation_type == "father":
                child.father = parent
                parent.children.append(child)
            elif relation_type == "mother":
                child.mother = parent
                parent.children.append(child)
            elif relation_type == "child":
                parent.children.append(child)
                if parent.gender == "Masculino":
                    child.father = parent
                else:
                    child.mother = parent
            elif relation_type == "spouse":
                parent.spouse = child
                child.spouse = parent
                child.marital_status = "Casado/a"
                parent.marital_status = "Casado/a"
            elif relation_type == "sibling":
                if parent.father:
                    child.father = parent.father
                    parent.father.children.append(child)
                if parent.mother:
                    child.mother = parent.mother
                    parent.mother.children.append(child)
                parent.siblings.append(child)
                child.siblings.append(parent)

            parent.add_event(f"Se agregó {relation_type}: {child.first_name}")
            child.add_event(f"Nació como {relation_type} de {parent.first_name}")
            self.draw_tree()

        form = PersonForm(self.root, title=f"Agregar {relation_type.title()}", on_save=on_save)
        form.focus()

    def draw_tree(self):
        """Dibuja el árbol genealógico"""
        self.tree_canvas.delete("all")
        if not self.family.members:
            self.tree_canvas.create_text(
                600, 400,
                text="No hay personas en el árbol",
                font=("Arial", 16),
                fill="white"
            )
            return

        for i, person in enumerate(self.family.members):
            x = 200 + (i % 3) * 300
            y = 100 + (i // 3) * 150
            self.draw_person_node(person, x, y)

    def draw_person_node(self, person, x, y):
        """Dibuja un nodo de persona"""
        color = "#3b8ed0" if person.alive else "#d35f5f"
        status_text = "Vivo" if person.alive else "Fallecido"
        status_color = "lightgreen" if person.alive else "red"

        self.tree_canvas.create_rectangle(x-100, y-50, x+100, y+50, fill=color, outline="#1f7dbf", width=2)
        self.tree_canvas.create_oval(x-40, y-40, x+40, y+40, fill="#59a8e2", outline="white", width=2)

        text = f"{person.first_name}\n{person.last_name}\n{person.cedula}\n{person.marital_status}"
        self.tree_canvas.create_text(x, y-35, text=text, font=("Arial", 8, "bold"), fill="white", anchor="center")
        self.tree_canvas.create_text(x, y+30, text=status_text, font=("Arial", 9, "italic"), fill=status_color, anchor="center")

        menu_btn = self.tree_canvas.create_oval(x-15, y+55, x+15, y+75, fill="#1db954", outline="white", width=2)
        self.tree_canvas.tag_bind(menu_btn, "<Button-1>", lambda e, p=person: self.show_menu(p))

    def show_menu(self, person):
        menu = tk.Menu(self.root, tearoff=0, bg="#2e2e2e", fg="white")
        menu.add_command(label="Agregar Padre", command=lambda: self.open_person_form_for_relation(person, "father"))
        menu.add_command(label="Agregar Madre", command=lambda: self.open_person_form_for_relation(person, "mother"))
        menu.add_command(label="Agregar Hijo", command=lambda: self.open_person_form_for_relation(person, "child"))
        menu.add_command(label="Agregar Pareja", command=lambda: self.open_person_form_for_relation(person, "spouse"))
        menu.add_command(label="Agregar Hermano", command=lambda: self.open_person_form_for_relation(person, "sibling"))
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())


# === PUNTO DE ENTRADA ===
if __name__ == "__main__":
    root = ctk.CTk()
    app = GenealogyApp(root)
    root.mainloop()