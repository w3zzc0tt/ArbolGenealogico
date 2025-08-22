import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import datetime

# === CLASES DE DATOS ===
class Person:
    def __init__(self, cedula, first_name, last_name, birth_date, gender, province):
        self.cedula = cedula
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.death_date = None
        self.gender = gender
        self.province = province
        self.marital_status = "Soltero"
        self.spouse = None
        self.mother = None
        self.father = None
        self.children = []
        self.siblings = []
        self.alive = True
        self.history = [f"Nació en {birth_date}"]
        self.interests = ["Deportes", "Lectura", "Música"]  # Intereses base

    def add_event(self, event_type):
        self.history.append(f"{event_type}")

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.cedula})"


class Family:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.members = []


# === INTERFAZ GRÁFICA ===
class GenealogyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Árbol Genealógico")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")

        # Variables globales
        self.family = Family(1, "Mi Familia")
        self.current_person = None  # Persona seleccionada para agregar padre/hijo/etc.
        self.tree_canvas = None
        self.person_nodes = {}  # Mapa: persona -> ID del nodo en canvas
        self.node_id_counter = 0

        # Crear la interfaz
        self.create_widgets()

    def create_widgets(self):
        """Crear widgets principales"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Notebook para pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Pestañas
        self.tree_tab = ttk.Frame(self.notebook)
        self.form_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.tree_tab, text="Árbol Genealógico")
        self.notebook.add(self.form_tab, text="Formulario")

        # Configurar pestañas
        self.setup_tree_tab()
        self.setup_form_tab()

    def setup_tree_tab(self):
        """Configurar la pestaña del árbol"""
        frame = ttk.Frame(self.tree_tab)
        frame.pack(fill=tk.BOTH, expand=True)

        # Canvas para dibujar el árbol
        self.tree_canvas = tk.Canvas(frame, bg="white", bd=2, relief="sunken")
        self.tree_canvas.pack(fill=tk.BOTH, expand=True)

        # Botón para agregar Ego si no hay nadie
        if not self.family.members:
            self.add_ego_button = ttk.Button(
                frame, text="Agregar Persona Principal (Ego)", command=self.add_ego
            )
            self.add_ego_button.pack(pady=20)

        # Dibujar árbol inicial
        self.draw_tree()

    def setup_form_tab(self):
        """Configurar la pestaña de formulario (reutilizable)"""
        form_frame = ttk.Frame(self.form_tab)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(form_frame, text="Agregar Persona", font=("Arial", 14)).pack(pady=10)

        # Formulario con grid
        form = ttk.Frame(form_frame)
        form.pack(fill=tk.X, padx=10, pady=10)

        # Configurar columnas
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=3)

        # Cédula
        ttk.Label(form, text="Cédula:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.cedula_entry = ttk.Entry(form, width=20)
        self.cedula_entry.grid(row=0, column=1, padx=5, pady=5)

        # Nombre
        ttk.Label(form, text="Nombre:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = ttk.Entry(form, width=30)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)

        # Fecha nacimiento
        ttk.Label(form, text="Fecha Nac.:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.birth_entry = ttk.Entry(form, width=20)
        self.birth_entry.grid(row=2, column=1, padx=5, pady=5)

        # Género
        ttk.Label(form, text="Género:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.gender_var = tk.StringVar(value="Masculino")
        gender_combo = ttk.Combobox(form, textvariable=self.gender_var, values=["Masculino", "Femenino"])
        gender_combo.grid(row=3, column=1, padx=5, pady=5)

        # Provincia
        ttk.Label(form, text="Provincia:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.province_var = tk.StringVar(value="San José")
        province_combo = ttk.Combobox(form, textvariable=self.province_var,
                                     values=["San José", "Alajuela", "Cartago", "Heredia", "Guanacaste", "Puntarenas", "Limón"])
        province_combo.grid(row=4, column=1, padx=5, pady=5)

        # Botón guardar
        save_button = ttk.Button(form, text="Guardar Persona", command=self.save_person)
        save_button.grid(row=5, column=0, columnspan=2, pady=20, sticky="ew")

    def add_ego(self):
        """Agrega la persona principal (Ego) al árbol genealógico"""
        name = simpledialog.askstring("Nombre", "Ingrese el nombre completo de la persona principal (Ego):")
        if not name or not name.strip():
            return

        parts = name.strip().split()
        first_name = parts[0]
        last_name = " ".join(parts[1:]) if len(parts) > 1 else "Apellido"

        cedula = f"EGO{random.randint(100000, 999999)}"
        birth_date = "2000-01-01"
        gender = "Masculino"
        province = "San José"

        person = Person(cedula, first_name, last_name, birth_date, gender, province)
        self.family.members.append(person)
        self.current_person = person
        person.add_event("Registrado como Ego")

        # Eliminar botón Ego
        if hasattr(self, 'add_ego_button') and self.add_ego_button:
            self.add_ego_button.destroy()

        self.draw_tree()

    def save_person(self):
        """Guarda una nueva persona desde el formulario"""
        cedula = self.cedula_entry.get().strip()
        name = self.name_entry.get().strip()
        birth_date = self.birth_entry.get().strip()
        gender = self.gender_var.get()
        province = self.province_var.get()

        if not cedula or not name or not birth_date:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        # Procesar nombre
        name_parts = name.split()
        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else "Apellido"

        # Crear persona
        person = Person(cedula, first_name, last_name, birth_date, gender, province)
        self.family.members.append(person)

        # Si se está agregando como padre/madre/hijo/etc., conectar relaciones
        if self.current_person:
            # Aquí puedes agregar lógica para relaciones
            # Ejemplo: este nuevo integrante será padre del current_person
            pass

        # Limpiar y actualizar
        self.clear_form()
        self.draw_tree()

    def clear_form(self):
        """Limpia el formulario"""
        self.cedula_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.birth_entry.delete(0, tk.END)
        self.gender_var.set("Masculino")
        self.province_var.set("San José")

    def draw_tree(self):
        """Dibuja el árbol genealógico en el canvas"""
        self.tree_canvas.delete("all")
        if not self.family.members:
            self.tree_canvas.create_text(600, 400, text="No hay personas en el árbol", font=("Arial", 16))
            return

        # Dibujar cada persona
        for i, person in enumerate(self.family.members):
            x = 200 + (i % 3) * 300
            y = 100 + (i // 3) * 150
            self.draw_person_node(person, x, y)

    def draw_person_node(self, person, x, y):
        """Dibuja un nodo de persona en el canvas"""
        # Rectángulo de fondo
        self.tree_canvas.create_rectangle(x-100, y-50, x+100, y+50, fill="lightblue", outline="black")
        
        # Foto (círculo)
        self.tree_canvas.create_oval(x-40, y-40, x+40, y+40, fill="lightgray", outline="black")
        
        # Nombre y cédula
        text = f"{person.first_name}\n{person.last_name}\n{person.cedula}"
        self.tree_canvas.create_text(x, y-30, text=text, font=("Arial", 8), anchor="center")

        # Estado (vivo/fallecido)
        status = "Vivo" if person.alive else "Fallecido"
        self.tree_canvas.create_text(x, y+30, text=status, font=("Arial", 8), anchor="center")

        # Botón de menú (acciónes)
        menu_btn = self.tree_canvas.create_oval(x-15, y+55, x+15, y+75, fill="green", outline="black")
        self.tree_canvas.tag_bind(menu_btn, "<Button-1>", lambda e, p=person: self.show_menu(p))

    def show_menu(self, person):
        """Muestra menú contextual para agregar relaciones"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Agregar Padre", command=lambda: self.add_parent(person, "father"))
        menu.add_command(label="Agregar Madre", command=lambda: self.add_parent(person, "mother"))
        menu.add_command(label="Agregar Hijo", command=lambda: self.add_child(person))
        menu.add_command(label="Agregar Pareja", command=lambda: self.add_spouse(person))
        menu.add_command(label="Agregar Hermano", command=lambda: self.add_sibling(person))
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def add_parent(self, child, parent_type):
        """Prepara el formulario para agregar un padre o madre"""
        self.current_person = child
        self.notebook.select(self.form_tab)
        self.cedula_entry.focus()

    def add_child(self, parent):
        """Prepara el formulario para agregar un hijo"""
        self.current_person = parent
        self.notebook.select(self.form_tab)

    def add_spouse(self, person):
        """Prepara el formulario para agregar pareja"""
        self.current_person = person
        self.notebook.select(self.form_tab)

    def add_sibling(self, person):
        """Prepara el formulario para agregar hermano"""
        self.current_person = person
        self.notebook.select(self.form_tab)


# === PUNTO DE ENTRADA ===
if __name__ == "__main__":
    root = tk.Tk()
    app = GenealogyApp(root)
    root.mainloop()