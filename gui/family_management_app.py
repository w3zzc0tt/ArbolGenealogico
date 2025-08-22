import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import datetime

class Family:
    """Clase que representa una familia en el sistema"""
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.members = []  # Lista de personas
        self.current_year = datetime.datetime.now().year  # Año actual en la simulación

class Person:
    """Clase que representa a una persona en el sistema"""
    def __init__(self, cedula, first_name, last_name, birth_date, death_date, gender, province, marital_status, family):
        self.cedula = cedula
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.death_date = death_date
        self.gender = gender
        self.province = province
        self.marital_status = marital_status
        self.spouse = None
        self.mother = None
        self.father = None
        self.children = []  # Lista de hijos
        self.family = family  # Referencia a la familia
        self.alive = True
        self.emotional_health = 100  # Salud emocional (0-100)
        self.interests = self.generate_interests()  # Intereses personales
        self.history = []  # Historial cronológico de eventos
        self.add_event("Nacimiento", birth_date)

    def generate_interests(self):
        """Genera intereses aleatorios para la persona"""
        all_interests = ["Deportes", "Lectura", "Música", "Arte", "Tecnología", "Cocina", "Viajes", "Naturaleza"]
        return random.sample(all_interests, 3)

    def calculate_age(self):
        """Calcula la edad actual de la persona"""
        if not self.birth_date:
            return 0
        
        try:
            birth = datetime.datetime.strptime(self.birth_date, "%Y-%m-%d")
            today = datetime.datetime.now()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            return age
        except:
            return 0

    def add_event(self, event_type, date=None):
        """Agrega un evento al historial cronológico"""
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.history.append((date, event_type))
        self.history.sort(key=lambda x: x[0])  # Ordenar por fecha

class FamilyManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión Familiar")
        self.root.geometry("1100x750")
        self.root.configure(bg="#f0f0f0")
        
        # Variables globales
        self.families = []
        self.next_family_id = 1
        self.current_family = None
        
        # Crear la interfaz
        self.create_main_interface()

    def create_main_interface(self):
        """Crea la interfaz principal con pestañas"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Crear las pestañas
        self.family_tab = ttk.Frame(self.notebook)
        self.members_tab = ttk.Frame(self.notebook)
        self.relationships_tab = ttk.Frame(self.notebook)
        self.tree_tab = ttk.Frame(self.notebook)
        self.simulation_tab = ttk.Frame(self.notebook)
        self.queries_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.family_tab, text="Gestión de Familias")
        self.notebook.add(self.members_tab, text="Integrantes")
        self.notebook.add(self.relationships_tab, text="Relaciones Familiares")
        self.notebook.add(self.tree_tab, text="Árbol Genealógico")
        self.notebook.add(self.simulation_tab, text="Simulación")
        self.notebook.add(self.queries_tab, text="Consultas Avanzadas")

        # Configurar cada pestaña
        self.setup_family_tab()
        self.setup_members_tab()
        self.setup_relationships_tab()
        self.setup_tree_tab()
        self.setup_simulation_tab()
        self.setup_queries_tab()

    def setup_family_tab(self):
        """Configura la pestaña de gestión de familias"""
        # Frame principal
        main_frame = ttk.Frame(self.family_tab, style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Frame para crear nueva familia
        create_frame = ttk.Frame(main_frame, style="Card.TFrame")
        create_frame.pack(fill=tk.X, pady=10, padx=10)

        ttk.Label(create_frame, text="Nueva Familia", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)

        # Formulario para crear familia
        form_frame = ttk.Frame(create_frame)
        form_frame.pack(fill=tk.X, padx=15, pady=10)

        ttk.Label(form_frame, text="Nombre de la familia:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.family_name_entry = ttk.Entry(form_frame, width=30)
        self.family_name_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Button(form_frame, text="Crear Familia", 
                  command=self.create_family,
                  style="Accent.TButton").grid(row=0, column=2, sticky="w", padx=10, pady=5)

    def create_family(self):
        """Crea una nueva familia"""
        name = self.family_name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "El nombre de la familia no puede estar vacío")
            return
            
        # Crear nueva familia
        new_family = Family(self.next_family_id, name)
        self.families.append(new_family)
        self.next_family_id += 1
        
        # Limpiar campo
        self.family_name_entry.delete(0, tk.END)
        
        messagebox.showinfo("Éxito", f"Familia '{name}' creada exitosamente")

    def setup_members_tab(self):
        """Configura la pestaña de gestión de integrantes"""
        # Frame principal
        main_frame = ttk.Frame(self.members_tab, style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Frame para crear nuevo integrante
        create_frame = ttk.Frame(main_frame, style="Card.TFrame")
        create_frame.pack(fill=tk.X, pady=10, padx=10)

        ttk.Label(create_frame, text="Nuevo Integrante", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)

        # Formulario para nuevo integrante
        form_frame = ttk.Frame(create_frame)
        form_frame.pack(fill=tk.X, padx=15, pady=10)

        # Fila 1: Cédula y Nombre
        ttk.Label(form_frame, text="Cédula:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.member_cedula_entry = ttk.Entry(form_frame, width=20)
        self.member_cedula_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=2, sticky="e", padx=15, pady=5)
        self.member_first_name_entry = ttk.Entry(form_frame, width=30)
        self.member_first_name_entry.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Botón de agregar
        ttk.Button(form_frame, text="Agregar Integrante", 
                  command=self.add_member,
                  style="Accent.TButton").grid(row=4, column=3, sticky="e", padx=5, pady=15)

        # Frame para listar integrantes
        list_frame = ttk.Frame(main_frame, style="Card.TFrame")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        ttk.Label(list_frame, text="Integrantes de la Familia", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)

        # Tabla de integrantes
        columns = ("cedula", "name", "last_name", "birth", "gender", "province", "status", "age", "alive")
        self.members_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)

        # Configurar encabezados
        self.members_tree.heading("cedula", text="Cédula")
        self.members_tree.heading("name", text="Nombre")
        self.members_tree.heading("last_name", text="Apellido")
        self.members_tree.heading("birth", text="Nacimiento")
        self.members_tree.heading("gender", text="Género")
        self.members_tree.heading("province", text="Provincia")
        self.members_tree.heading("status", text="Estado Civil")
        self.members_tree.heading("age", text="Edad")
        self.members_tree.heading("alive", text="Vivo")

        # Configurar columnas
        self.members_tree.column("cedula", width=100)
        self.members_tree.column("name", width=100)
        self.members_tree.column("last_name", width=100)
        self.members_tree.column("birth", width=100, anchor=tk.CENTER)
        self.members_tree.column("gender", width=80, anchor=tk.CENTER)
        self.members_tree.column("province", width=120)
        self.members_tree.column("status", width=100)
        self.members_tree.column("age", width=50, anchor=tk.CENTER)
        self.members_tree.column("alive", width=50, anchor=tk.CENTER)

        # Barra de desplazamiento
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.members_tree.yview)
        self.members_tree.configure(yscroll=scrollbar.set)

        # Ubicar elementos
        self.members_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

    def add_member(self):
        """Agrega un nuevo integrante a la familia"""
        cedula = self.member_cedula_entry.get().strip()
        first_name = self.member_first_name_entry.get().strip()

        if not cedula or not first_name:
            messagebox.showerror("Error", "La cédula y el nombre no pueden estar vacíos")
            return

        # Aquí se puede agregar la lógica para crear un nuevo objeto Person
        # y agregarlo a la familia actual.
        
        messagebox.showinfo("Éxito", f"Integrante '{first_name}' agregado exitosamente")

    def setup_relationships_tab(self):
        """Configura la pestaña de relaciones familiares"""
        main_frame = ttk.Frame(self.relationships_tab, style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(main_frame, text="Registrar Relaciones", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)

        # Aquí se pueden agregar más elementos para registrar relaciones
        # Por ejemplo, formularios para seleccionar padres e hijos, etc.

    def setup_tree_tab(self):
        """Configura la pestaña del árbol genealógico"""
        main_frame = ttk.Frame(self.tree_tab, style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(main_frame, text="Árbol Genealógico", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)

        # Aquí se pueden agregar más elementos para visualizar el árbol genealógico
        # Por ejemplo, un área de texto o un canvas para dibujar el árbol

# Punto de entrada
if __name__ == "__main__":
    root = tk.Tk()
    app = FamilyManagementApp(root)
    root.mainloop()
