import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import re
import random
import datetime
from collections import deque
import math

# ======================================
# CLASES Y LÓGICA DEL SISTEMA (TODO AQUÍ)
# ======================================

class Person:
    """Clase que representa a una persona en el sistema"""
    def __init__(self, cedula, first_name, last_name, birth_date, death_date, gender, province, marital_status, family):
        self.cedula = cedula
        self.first_name = first_name  # Nombre propio
        self.last_name = last_name    # Apellido
        self.birth_date = birth_date
        self.death_date = death_date
        self.gender = gender  # 'M' o 'F'
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
    
    def has_partner(self):
        """Verifica si la persona tiene pareja"""
        return self.spouse is not None and self.alive and self.spouse.alive
    
    def can_have_children(self):
        """Verifica si la persona puede tener hijos"""
        age = self.calculate_age()
        return self.alive and self.gender == "F" and 15 <= age <= 49

class Family:
    """Clase que representa una familia en el sistema"""
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.members = []  # Lista de personas
        self.current_year = datetime.datetime.now().year  # Año actual en la simulación

def validate_cedula(cedula, family):
    """Verifica que la cédula no exista en la familia"""
    for member in family.members:
        if member.cedula == cedula:
            return False
    return True

def get_person_by_cedula(family, cedula):
    """Obtiene una persona por su cédula"""
    for member in family.members:
        if member.cedula == cedula:
            return member
    return None

def validate_family_has_members(family, min_members=1):
    """Verifica que la familia tenga suficientes miembros"""
    return len(family.members) >= min_members

def generate_cedula():
    """Genera una cédula aleatoria válida"""
    return str(random.randint(100000000, 999999999))

def generate_name(gender):
    """Genera un nombre aleatorio según el género"""
    male_first_names = ["Juan", "Carlos", "Pedro", "Miguel", "Andrés", "Luis", "José", "Mario", "Fernando", "Ricardo"]
    female_first_names = ["María", "Ana", "Laura", "Sofía", "Carolina", "Valentina", "Camila", "Daniela", "Paula", "Andrea"]
    
    last_names = ["García", "Rodríguez", "Martínez", "Hernández", "López", "González", "Pérez", "Sánchez", "Ramírez", "Torres"]
    
    if gender == "M":
        first_name = random.choice(male_first_names)
    else:
        first_name = random.choice(female_first_names)
    
    last_name = random.choice(last_names)
    return first_name, last_name

def add_person_to_family(family, cedula, first_name, last_name, birth_date, death_date, gender, province, marital_status):
    """Agrega una nueva persona a la familia"""
    person = Person(cedula, first_name, last_name, birth_date, death_date, gender, province, marital_status, family)
    family.members.append(person)
    return person

def register_parents(family, child_cedula, mother_cedula, father_cedula):
    """Registra la relación de padres para un hijo"""
    child = get_person_by_cedula(family, child_cedula)
    mother = get_person_by_cedula(family, mother_cedula)
    father = get_person_by_cedula(family, father_cedula)
    
    if not child or not mother or not father:
        return False, "Una o más personas no existen en la familia"
    
    if mother.gender != "F":
        return False, "La persona seleccionada como madre debe ser mujer"
    
    if father.gender != "M":
        return False, "La persona seleccionada como padre debe ser hombre"
    
    # Establecer relaciones
    child.mother = mother
    child.father = father
    
    # Asegurar que el hijo no esté duplicado en la lista de hijos
    if child not in mother.children:
        mother.children.append(child)
    if child not in father.children:
        father.children.append(child)
    
    return True, "Relación de padres registrada exitosamente"

def register_couple(family, person1_cedula, person2_cedula):
    """Registra una unión de pareja entre dos personas"""
    person1 = get_person_by_cedula(family, person1_cedula)
    person2 = get_person_by_cedula(family, person2_cedula)
    
    if not person1 or not person2:
        return False, "Una o más personas no existen en la familia"
    
    if person1 == person2:
        return False, "No se puede registrar pareja consigo mismo"
    
    if person1.gender == person2.gender:
        return False, "No se puede registrar pareja del mismo género"
    
    # Verificar si ya están registrados como pareja
    if person1.spouse == person2:
        return False, "Estas personas ya están registradas como pareja"
    
    # Establecer relación
    person1.spouse = person2
    person2.spouse = person1
    
    # Actualizar estado civil
    person1.marital_status = "Casado/a"
    person2.marital_status = "Casado/a"
    
    # Registrar evento en el historial
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    person1.add_event("Matrimonio", current_date)
    person2.add_event("Matrimonio", current_date)
    
    return True, "Pareja registrada exitosamente"

def get_family_tree(family):
    """Genera el árbol genealógico de la familia"""
    # Buscar personas sin padres (raíces del árbol)
    root_members = [p for p in family.members if p.mother is None and p.father is None]
    
    if not root_members:
        return "No se encontraron personas sin padres registrados.\nRegistre primero las relaciones de padres para construir el árbol."
    
    result = f"ÁRBOL GENEALÓGICO DE {family.name.upper()}\n\n"
    
    for person in root_members:
        result += display_person_tree(person, 0)
    
    return result

def display_person_tree(person, level):
    """Muestra el árbol genealógico de una persona de forma recursiva"""
    indent = "  " * level
    status = "VIVO" if person.alive else "FALLECIDO"
    result = f"{indent}• {person.first_name} {person.last_name} ({person.marital_status}) [{status}]\n"
    
    # Mostrar pareja
    if person.spouse and person.spouse.alive:
        result += f"{indent}  ╰─ pareja con: {person.spouse.first_name} {person.spouse.last_name}\n"
    
    # Mostrar hijos
    if person.children:
        result += f"{indent}  Hijos:\n"
        for child in person.children:
            result += display_person_tree(child, level + 1)
    
    return result

def calculate_compatibility(person1, person2):
    """
    Calcula el índice de compatibilidad entre dos personas
    Basado en:
    1. Diferencia de edad (máximo 15 años)
    2. Intereses comunes (al menos 2)
    3. Compatibilidad genética (simulación)
    """
    # 1. Compatibilidad por edad (máximo 15 años de diferencia)
    age1 = person1.calculate_age()
    age2 = person2.calculate_age()
    age_diff = abs(age1 - age2)
    
    # Si la diferencia es mayor a 15 años, baja mucho la compatibilidad
    if age_diff > 15:
        age_compatibility = max(0, 50 - (age_diff * 2))
    else:
        age_compatibility = 100 - (age_diff * 5)
    
    # 2. Compatibilidad por intereses (al menos 2 en común)
    common_interests = len(set(person1.interests) & set(person2.interests))
    interest_compatibility = min(100, common_interests * 33.3)  # 33.3% por interés en común
    
    # 3. Compatibilidad genética (simulación)
    # Aquí se podría implementar un algoritmo más complejo
    genetic_compatibility = random.randint(60, 100)  # Simulación aleatoria para el ejemplo
    
    # Combinar con pesos
    total_compatibility = (age_compatibility * 0.4) + (interest_compatibility * 0.4) + (genetic_compatibility * 0.2)
    
    return min(100, max(0, total_compatibility))

def check_if_can_marry(person1, person2):
    """Verifica si dos personas pueden casarse según las reglas"""
    # Deben ser mayores de 18 años
    if person1.calculate_age() < 18 or person2.calculate_age() < 18:
        return False, "Una o ambas personas son menores de 18 años"
    
    # No deben estar en una relación actual
    if person1.has_partner() or person2.has_partner():
        return False, "Una o ambas personas ya tienen pareja"
    
    # Compatibilidad suficiente
    compatibility = calculate_compatibility(person1, person2)
    if compatibility < 70:
        return False, f"Compatibilidad insuficiente ({compatibility:.1f}%). Mínimo requerido: 70%"
    
    return True, "Pueden formar una pareja"

def simulate_birthday(person, family):
    """Simula un cumpleaños para una persona"""
    person.add_event("Cumpleaños", datetime.datetime.now().strftime("%Y-%m-%d"))
    
    # Si la persona está viuda, la salud emocional puede disminuir
    if person.marital_status == "Viudo/a" and person.emotional_health > 20:
        person.emotional_health -= random.randint(1, 5)
    
    # Si está soltero/a por mucho tiempo, la salud emocional disminuye
    if person.marital_status == "Soltero/a" and person.calculate_age() > 30:
        years_single = family.current_year - int(person.birth_date[:4]) - 30
        if years_single > 0:
            person.emotional_health = max(10, person.emotional_health - (years_single * 2))
    
    # Afectar esperanza de vida si la salud emocional es baja
    if person.emotional_health < 30:
        # Aumentar probabilidad de fallecimiento
        if random.random() < 0.1:  # 10% de probabilidad
            simulate_death(person, family)

def simulate_death(person, family):
    """Simula el fallecimiento de una persona"""
    if not person.alive:
        return False, "La persona ya ha fallecido"
    
    # Actualizar estado
    person.alive = False
    person.death_date = datetime.datetime.now().strftime("%Y-%m-%d")
    person.marital_status = "Viudo/a" if person.spouse else "Fallecido/a"
    person.add_event("Fallecimiento", person.death_date)
    
    # Si tiene pareja, actualizar estado de la pareja
    if person.spouse and person.spouse.alive:
        person.spouse.marital_status = "Viudo/a"
        person.spouse.emotional_health = max(10, person.spouse.emotional_health - 30)
        person.spouse.add_event("Viudez", person.death_date)
    
    # Manejar hijos menores de edad
    handle_minor_children(person, family)
    
    return True, f"{person.first_name} {person.last_name} ha fallecido."

def handle_minor_children(parent, family):
    """Maneja los hijos menores cuando un padre fallece"""
    for child in parent.children:
        if child.alive and child.calculate_age() < 18:
            # Si el otro padre también falleció, buscar tutor
            if (parent.gender == "M" and child.mother and not child.mother.alive) or \
               (parent.gender == "F" and child.father and not child.father.alive):
                find_legal_guardian(child, family)

def find_legal_guardian(child, family):
    """Busca un tutor legal para un niño"""
    # Buscar abuelos
    grandparents = []
    if child.mother and child.mother.mother:
        grandparents.append(child.mother.mother)
    if child.mother and child.mother.father:
        grandparents.append(child.mother.father)
    if child.father and child.father.mother:
        grandparents.append(child.father.mother)
    if child.father and child.father.father:
        grandparents.append(child.father.father)
    
    # Filtrar abuelos vivos
    living_grandparents = [p for p in grandparents if p and p.alive]
    
    if living_grandparents:
        guardian = random.choice(living_grandparents)
        child.add_event(f"Tutor: {guardian.first_name} {guardian.last_name}", datetime.datetime.now().strftime("%Y-%m-%d"))
        return
    
    # Buscar tías/tíos
    aunts_uncles = []
    if child.mother and child.mother.mother:
        for sibling in child.mother.mother.children:
            if sibling != child.mother and sibling.alive:
                aunts_uncles.append(sibling)
    if child.father and child.father.mother:
        for sibling in child.father.mother.children:
            if sibling != child.father and sibling.alive:
                aunts_uncles.append(sibling)
    
    if aunts_uncles:
        guardian = random.choice(aunts_uncles)
        child.add_event(f"Tutor: {guardian.first_name} {guardian.last_name}", datetime.datetime.now().strftime("%Y-%m-%d"))
        return
    
    # Si no hay familiares cercanos, asignar tutor aleatorio
    living_members = [p for p in family.members if p.alive and p != child]
    if living_members:
        guardian = random.choice(living_members)
        child.add_event(f"Tutor: {guardian.first_name} {guardian.last_name}", datetime.datetime.now().strftime("%Y-%m-%d"))

def simulate_birth(parent1, parent2, family, current_year=None):
    """Simula el nacimiento de un hijo"""
    if not parent1.alive or not parent2.alive:
        return False, "Uno o ambos padres no están vivos"
    
    if not parent1.can_have_children() and not parent2.can_have_children():
        return False, "Los padres no pueden tener hijos en este momento"
    
    # Generar datos del bebé
    gender = "F" if random.random() < 0.5 else "M"
    first_name, _ = generate_name(gender)
    last_name = parent1.last_name  # Hereda el apellido del padre
    cedula = generate_cedula()
    
    # Usar el año actual de la simulación para la fecha de nacimiento
    if current_year is None:
        current_year = family.current_year
    
    birth_date = f"{current_year}-01-01"
    
    # Crear el bebé
    baby = add_person_to_family(family, cedula, first_name, last_name, birth_date, "", gender, parent1.province, "Soltero/a")
    
    # Registrar como hijos de ambos padres
    success, _ = register_parents(family, baby.cedula, parent1.cedula, parent2.cedula)
    
    if success:
        baby.add_event("Nacimiento", birth_date)
        return True, f"¡Felicitaciones! {parent1.first_name} {parent1.last_name} y {parent2.first_name} {parent2.last_name} tuvieron un bebé: {baby.first_name} {baby.last_name}"
    else:
        return False, "Error al registrar el nacimiento"

def find_relationship(person1, person2):
    """Encuentra la relación entre dos personas"""
    if not person1 or not person2 or person1 == person2:
        return "No hay relación"
    
    # Padres
    if person1 == person2.father or person1 == person2.mother:
        return "Padre/Madre"
    
    # Hijos
    if person2 in person1.children:
        return "Hijo/Hija"
    
    # Hermanos
    if person1.mother and person2.mother and person1.mother == person2.mother and person1.father == person2.father:
        return "Hermano/Hermana"
    
    # Abuelos
    if person1 == person2.father.father or person1 == person2.father.mother or \
       person1 == person2.mother.father or person1 == person2.mother.mother:
        return "Abuelo/Abuela"
    
    # Nietos
    for child in person1.children:
        if person2 in child.children:
            return "Nieto/Nieta"
    
    # Tíos
    if person1.mother and person2.mother and person1.mother == person2.mother.father:
        return "Tío/Tía paterno"
    if person1.mother and person2.mother and person1.mother == person2.mother.mother:
        return "Tío/Tía materno"
    
    # Sobrinos
    for sibling in person1.children:
        if person2 in sibling.children:
            return "Sobrino/Sobrina"
    
    # Primos
    if person1.mother and person2.mother and person1.mother.mother == person2.mother.mother:
        return "Primo/Prima"
    
    return "Relación no identificada"

def get_first_degree_cousins(person):
    """Obtiene los primos de primer grado de una persona"""
    cousins = []
    
    # Obtener hermanos de los padres
    if person.father:
        for sibling in person.father.mother.children:
            if sibling != person.father and sibling.alive:
                for child in sibling.children:
                    if child.alive:
                        cousins.append(child)
    
    if person.mother:
        for sibling in person.mother.mother.children:
            if sibling != person.mother and sibling.alive:
                for child in sibling.children:
                    if child.alive:
                        cousins.append(child)
    
    return cousins

def get_motherline_ancestors(person):
    """Obtiene todos los antepasados maternos de una persona"""
    ancestors = []
    current = person
    
    while current.mother:
        ancestors.append(current.mother)
        current = current.mother
    
    return ancestors

def get_living_descendants(person):
    """Obtiene todos los descendientes vivos de una persona"""
    descendants = []
    
    # Función recursiva para encontrar descendientes
    def find_descendants(current):
        for child in current.children:
            if child.alive:
                descendants.append(child)
            find_descendants(child)
    
    find_descendants(person)
    return descendants

def get_births_last_10_years(family):
    """Obtiene cuántas personas nacieron en los últimos 10 años"""
    current_year = family.current_year
    count = 0
    
    for person in family.members:
        if person.birth_date:
            birth_year = int(person.birth_date[:4])
            if current_year - birth_year <= 10:
                count += 1
    
    return count

def get_couples_with_multiple_children(family):
    """Obtiene las parejas actuales con 2 o más hijos en común"""
    couples = []
    
    for person in family.members:
        if person.spouse and person.alive and person.spouse.alive:
            # Contar hijos en común
            common_children = set(person.children) & set(person.spouse.children)
            if len(common_children) >= 2:
                couples.append((person, person.spouse))
    
    return couples

def get_deaths_before_50(family):
    """Obtiene cuántas personas fallecieron antes de cumplir 50 años"""
    count = 0
    
    for person in family.members:
        if person.death_date and person.birth_date:
            birth_year = int(person.birth_date[:4])
            death_year = int(person.death_date[:4])
            if death_year - birth_year < 50:
                count += 1
    
    return count

def validate_date(date_str):
    """Valida que la fecha esté en el rango permitido (1820-01-01 a 2025-01-01)"""
    try:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        min_date = datetime.datetime(1820, 1, 1)
        max_date = datetime.datetime(2025, 1, 1)
        
        if min_date <= date <= max_date:
            return True
        return False
    except:
        return False

# ======================================
# INTERFAZ GRÁFICA COMPLETA
# ======================================

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
        self.simulation_running = False
        self.simulation_interval = 10000  # 10 segundos en milisegundos
        self.simulation_id = None
        self.selected_persons = []  # Para consultas y eventos manuales
        self.query_persons_selection = []  # Para guardar selección en consultas
        
        # Configurar estilos
        self.setup_styles()
        
        # Crear la interfaz
        self.create_main_interface()
        
    def setup_styles(self):
        """Configura los estilos para la interfaz"""
        style = ttk.Style()
        
        # Estilos para botones
        style.configure("TButton", 
                        font=("Arial", 10, "bold"),
                        padding=6)
        style.configure("Accent.TButton",
                        background="#4a6fa5",
                        foreground="white")
        style.map("Accent.TButton",
                  background=[("active", "#3a5a80")])
        style.configure("Success.TButton",
                        background="#27ae60",
                        foreground="white")
        style.map("Success.TButton",
                  background=[("active", "#219653")])
        style.configure("Danger.TButton",
                        background="#e74c3c",
                        foreground="white")
        style.map("Danger.TButton",
                  background=[("active", "#c0392b")])
        
        # Estilos para labels
        style.configure("Header.TLabel", 
                        font=("Arial", 16, "bold"),
                        background="#f0f0f0",
                        foreground="#2c3e50")
        style.configure("SubHeader.TLabel", 
                        font=("Arial", 12, "bold"),
                        background="#f0f0f0",
                        foreground="#34495e")
        style.configure("TLabel", 
                        font=("Arial", 10),
                        background="#f0f0f0")
        style.configure("Status.TLabel", 
                        font=("Arial", 9, "italic"),
                        background="#f0f0f0",
                        foreground="#7f8c8d")
        
        # Estilos para frames
        style.configure("Card.TFrame", 
                        background="white",
                        relief="solid",
                        borderwidth=1)
        style.configure("Main.TFrame", 
                        background="#f0f0f0")
        style.configure("Info.TFrame",
                        background="#e8f4fc",
                        relief="solid",
                        borderwidth=1)
        
    def create_main_interface(self):
        """Crea la interfaz principal con pestañas"""
        # Crear el notebook (pestañas)
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
        
        # Frame para listar familias
        list_frame = ttk.Frame(main_frame, style="Card.TFrame")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        ttk.Label(list_frame, text="Familias Registradas", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)
        
        # Tabla de familias
        columns = ("id", "name", "members", "year")
        self.families_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        # Configurar encabezados
        self.families_tree.heading("id", text="ID")
        self.families_tree.heading("name", text="Nombre")
        self.families_tree.heading("members", text="Integrantes")
        self.families_tree.heading("year", text="Año Actual")
        
        # Configurar columnas
        self.families_tree.column("id", width=50, anchor=tk.CENTER)
        self.families_tree.column("name", width=200)
        self.families_tree.column("members", width=100, anchor=tk.CENTER)
        self.families_tree.column("year", width=100, anchor=tk.CENTER)
        
        # Barra de desplazamiento
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.families_tree.yview)
        self.families_tree.configure(yscroll=scrollbar.set)
        
        # Ubicar elementos
        self.families_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Botones de acción
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Button(btn_frame, text="Seleccionar Familia", 
                  command=self.select_family,
                  style="Accent.TButton").pack(side=tk.LEFT)
        
        ttk.Button(btn_frame, text="Eliminar Familia", 
                  command=self.delete_family,
                  style="Danger.TButton").pack(side=tk.LEFT, padx=10)
    
    def setup_members_tab(self):
        """Configura la pestaña de gestión de integrantes"""
        # Frame principal
        main_frame = ttk.Frame(self.members_tab, style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame para selección de familia
        family_frame = ttk.Frame(main_frame, style="Card.TFrame")
        family_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(family_frame, text="Familia Seleccionada", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)
        
        self.selected_family_label = ttk.Label(family_frame, text="Ninguna familia seleccionada", 
                                             font=("Arial", 10, "italic"), foreground="#7f8c8d")
        self.selected_family_label.pack(padx=15, pady=5, anchor="w")
        
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
        
        ttk.Label(form_frame, text="Apellido:").grid(row=1, column=2, sticky="e", padx=15, pady=5)
        self.member_last_name_entry = ttk.Entry(form_frame, width=30)
        self.member_last_name_entry.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        
        # Fila 2: Fechas
        ttk.Label(form_frame, text="Fecha Nacimiento (YYYY-MM-DD):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.member_birth_entry = ttk.Entry(form_frame, width=12)
        self.member_birth_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(form_frame, text="Fecha Fallecimiento:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.member_death_entry = ttk.Entry(form_frame, width=12)
        self.member_death_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Fila 3: Género, Provincia y Estado Civil
        ttk.Label(form_frame, text="Género:").grid(row=2, column=2, sticky="e", padx=15, pady=5)
        self.member_gender_var = tk.StringVar()
        gender_frame = ttk.Frame(form_frame)
        gender_frame.grid(row=2, column=3, sticky="w", padx=5, pady=5)
        
        ttk.Radiobutton(gender_frame, text="Masculino", variable=self.member_gender_var, value="M").pack(side=tk.LEFT)
        ttk.Radiobutton(gender_frame, text="Femenino", variable=self.member_gender_var, value="F").pack(side=tk.LEFT, padx=10)
        
        ttk.Label(form_frame, text="Provincia:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        provinces = ["Alajuela", "Heredia", "San José", "Limón", "Puntarenas", "Guanacaste", "Cartago"]
        self.member_province_cb = ttk.Combobox(form_frame, values=provinces, width=20, state="readonly")
        self.member_province_cb.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(form_frame, text="Estado Civil:").grid(row=3, column=2, sticky="e", padx=15, pady=5)
        marital_statuses = ["Casado/a", "Divorciado/a", "Soltero/a", "Viudo/a"]
        self.member_marital_cb = ttk.Combobox(form_frame, values=marital_statuses, width=20, state="readonly")
        self.member_marital_cb.grid(row=3, column=3, sticky="w", padx=5, pady=5)
        
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
        
        # Botón para actualizar lista
        ttk.Button(list_frame, text="Actualizar Lista", 
                  command=self.refresh_members_list,
                  style="Accent.TButton").pack(pady=5)
    
    def setup_relationships_tab(self):
        """Configura la pestaña de gestión de relaciones familiares"""
        # Frame principal
        main_frame = ttk.Frame(self.relationships_tab, style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame para selección de familia
        family_frame = ttk.Frame(main_frame, style="Card.TFrame")
        family_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(family_frame, text="Familia Seleccionada para Relaciones", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)
        
        self.relationships_family_label = ttk.Label(family_frame, text="Ninguna familia seleccionada", 
                                                 font=("Arial", 10, "italic"), foreground="#7f8c8d")
        self.relationships_family_label.pack(padx=15, pady=5, anchor="w")
        
        # Frame para relaciones de padres
        parents_frame = ttk.Frame(main_frame, style="Card.TFrame")
        parents_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(parents_frame, text="Registrar Padres", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)
        
        # Formulario para registrar padres
        form_frame = ttk.Frame(parents_frame)
        form_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Label(form_frame, text="Hijo/a:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.child_var = tk.StringVar()
        self.child_cb = ttk.Combobox(form_frame, textvariable=self.child_var, width=30, state="readonly")
        self.child_cb.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(form_frame, text="Madre:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.mother_var = tk.StringVar()
        self.mother_cb = ttk.Combobox(form_frame, textvariable=self.mother_var, width=30, state="readonly")
        self.mother_cb.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(form_frame, text="Padre:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.father_var = tk.StringVar()
        self.father_cb = ttk.Combobox(form_frame, textvariable=self.father_var, width=30, state="readonly")
        self.father_cb.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Button(form_frame, text="Registrar Padres", 
                  command=self.register_parents,
                  style="Accent.TButton").grid(row=3, column=1, sticky="w", padx=5, pady=15)
        
        # Frame para relaciones de pareja
        couple_frame = ttk.Frame(main_frame, style="Card.TFrame")
        couple_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(couple_frame, text="Registrar Pareja", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)
        
        # Formulario para registrar pareja
        couple_form_frame = ttk.Frame(couple_frame)
        couple_form_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Label(couple_form_frame, text="Persona 1:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.person1_var = tk.StringVar()
        self.person1_cb = ttk.Combobox(couple_form_frame, textvariable=self.person1_var, width=30, state="readonly")
        self.person1_cb.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(couple_form_frame, text="Persona 2:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.person2_var = tk.StringVar()
        self.person2_cb = ttk.Combobox(couple_form_frame, textvariable=self.person2_var, width=30, state="readonly")
        self.person2_cb.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Button(couple_form_frame, text="Registrar Pareja", 
                  command=self.register_couple,
                  style="Accent.TButton").grid(row=2, column=1, sticky="w", padx=5, pady=15)
        
        # Botón para actualizar listas
        ttk.Button(main_frame, text="Actualizar Datos", 
                  command=self.refresh_relationships_data,
                  style="Accent.TButton").pack(pady=10)
    
    def setup_tree_tab(self):
        """Configura la pestaña del árbol genealógico"""
        # Frame principal
        main_frame = ttk.Frame(self.tree_tab, style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame para selección de familia
        family_frame = ttk.Frame(main_frame, style="Card.TFrame")
        family_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(family_frame, text="Familia para Visualizar Árbol", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)
        
        self.tree_family_label = ttk.Label(family_frame, text="Ninguna familia seleccionada", 
                                         font=("Arial", 10, "italic"), foreground="#7f8c8d")
        self.tree_family_label.pack(padx=15, pady=5, anchor="w")
        
        # Frame para el árbol genealógico
        tree_frame = ttk.Frame(main_frame, style="Card.TFrame")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        ttk.Label(tree_frame, text="Árbol Genealógico", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)
        
        # Área de texto para el árbol
        self.tree_text = scrolledtext.ScrolledText(tree_frame, wrap=tk.WORD, 
                                                 font=("Courier", 10),
                                                 bg="white",
                                                 relief="solid")
        self.tree_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        self.tree_text.config(state=tk.DISABLED)
        
        # Botón para generar árbol
        ttk.Button(main_frame, text="Generar Árbol Genealógico", 
                  command=self.generate_family_tree,
                  style="Accent.TButton").pack(pady=10)
    
    def setup_simulation_tab(self):
        """Configura la pestaña de simulación"""
        # Frame principal
        main_frame = ttk.Frame(self.simulation_tab, style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame para selección de familia
        family_frame = ttk.Frame(main_frame, style="Card.TFrame")
        family_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(family_frame, text="Familia para Simulación", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)
        
        self.simulation_family_label = ttk.Label(family_frame, text="Ninguna familia seleccionada", 
                                               font=("Arial", 10, "italic"), foreground="#7f8c8d")
        self.simulation_family_label.pack(padx=15, pady=5, anchor="w")
        
        # Frame para personas de la familia
        persons_frame = ttk.Frame(main_frame, style="Card.TFrame")
        persons_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(persons_frame, text="Personas de la Familia", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)
        
        # Lista de personas
        self.simulation_persons_listbox = tk.Listbox(persons_frame, height=5, font=("Arial", 10), selectmode=tk.MULTIPLE)
        self.simulation_persons_listbox.pack(fill=tk.X, padx=15, pady=10)
        
        # Botones de control
        btn_frame = ttk.Frame(persons_frame)
        btn_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Button(btn_frame, text="Actualizar Lista", 
                  command=self.refresh_simulation_persons,
                  style="Accent.TButton").pack(side=tk.LEFT)
        
        ttk.Button(btn_frame, text="Limpiar Selección", 
                  command=lambda: self.simulation_persons_listbox.selection_clear(0, tk.END),
                  style="Danger.TButton").pack(side=tk.LEFT, padx=10)
        
        # Frame para controles de simulación
        controls_frame = ttk.Frame(main_frame, style="Card.TFrame")
        controls_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(controls_frame, text="Controles de Simulación", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)
        
        # Botones de control
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.pack(fill=tk.X, padx=15, pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="Iniciar Simulación", 
                                   command=self.start_simulation,
                                   style="Success.TButton")
        self.start_btn.pack(side=tk.LEFT)
        
        self.stop_btn = ttk.Button(btn_frame, text="Detener Simulación", 
                                  command=self.stop_simulation,
                                  style="Danger.TButton",
                                  state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Frame para eventos manuales
        events_frame = ttk.Frame(main_frame, style="Card.TFrame")
        events_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        ttk.Label(events_frame, text="Eventos Manuales", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)
        
        # Botones de eventos
        events_btn_frame = ttk.Frame(events_frame)
        events_btn_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Button(events_btn_frame, text="Cumpleaños Manual", 
                  command=self.manual_birthday,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(events_btn_frame, text="Nacimiento Manual", 
                  command=self.manual_birth,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(events_btn_frame, text="Fallecimiento Manual", 
                  command=self.manual_death,
                  style="Danger.TButton").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(events_btn_frame, text="Unión Manual", 
                  command=self.manual_union,
                  style="Success.TButton").pack(side=tk.LEFT, padx=5)
        
        # Frame para estado de la simulación
        status_frame = ttk.Frame(main_frame, style="Info.TFrame")
        status_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(status_frame, text="Estado de la Simulación", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)
        
        self.simulation_status = ttk.Label(status_frame, 
                                         text="La simulación está detenida",
                                         font=("Arial", 10, "bold"),
                                         foreground="#e74c3c")
        self.simulation_status.pack(padx=15, pady=5, anchor="w")
        
        self.simulation_info = ttk.Label(status_frame, 
                                       text="Seleccione una familia y presione 'Iniciar Simulación'",
                                       font=("Arial", 9, "italic"),
                                       foreground="#7f8c8d")
        self.simulation_info.pack(padx=15, pady=5, anchor="w", fill=tk.X)
    
    def setup_queries_tab(self):
        """Configura la pestaña de consultas avanzadas"""
        # Frame principal
        main_frame = ttk.Frame(self.queries_tab, style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame para selección de familia
        family_frame = ttk.Frame(main_frame, style="Card.TFrame")
        family_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(family_frame, text="Familia para Consultas", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)
        
        self.queries_family_label = ttk.Label(family_frame, text="Ninguna familia seleccionada", 
                                            font=("Arial", 10, "italic"), foreground="#7f8c8d")
        self.queries_family_label.pack(padx=15, pady=5, anchor="w")
        
        # Frame para personas de la familia
        persons_frame = ttk.Frame(main_frame, style="Card.TFrame")
        persons_frame.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Label(persons_frame, text="Personas de la Familia", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)
        
        # Lista de personas
        self.queries_persons_listbox = tk.Listbox(persons_frame, height=5, font=("Arial", 10), selectmode=tk.MULTIPLE)
        self.queries_persons_listbox.pack(fill=tk.X, padx=15, pady=10)
        
        # Botones de control
        btn_frame = ttk.Frame(persons_frame)
        btn_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Button(btn_frame, text="Actualizar Lista", 
                  command=self.refresh_queries_persons,
                  style="Accent.TButton").pack(side=tk.LEFT)
        
        ttk.Button(btn_frame, text="Limpiar Selección", 
                  command=lambda: self.queries_persons_listbox.selection_clear(0, tk.END),
                  style="Danger.TButton").pack(side=tk.LEFT, padx=10)
        
        # Botón para guardar selección
        self.save_selection_btn = ttk.Button(btn_frame, text="Guardar Selección", 
                                           command=self.save_query_selection,
                                           style="Success.TButton")
        self.save_selection_btn.pack(side=tk.LEFT, padx=10)
        
        # Frame para consultas
        queries_frame = ttk.Frame(main_frame, style="Card.TFrame")
        queries_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        ttk.Label(queries_frame, text="Consultas Avanzadas", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)
        
        # Lista de consultas
        self.queries_listbox = tk.Listbox(queries_frame, height=7, font=("Arial", 10))
        queries = [
            "1. ¿Cuál es la relación entre persona A y persona B?",
            "2. ¿Quiénes son los primos de primer grado de X?",
            "3. ¿Cuáles son todos los antepasados maternos de X?",
            "4. ¿Cuáles descendientes de X están vivos actualmente?",
            "5. ¿Cuántas personas nacieron en los últimos 10 años?",
            "6. ¿Cuáles parejas actuales tienen 2 o más hijos en común?",
            "7. ¿Cuántas personas fallecieron antes de cumplir 50 años?"
        ]
        
        for query in queries:
            self.queries_listbox.insert(tk.END, query)
        
        self.queries_listbox.pack(fill=tk.X, padx=15, pady=10)
        
        # Botón para ejecutar consulta
        ttk.Button(queries_frame, text="Ejecutar Consulta Seleccionada", 
                  command=self.execute_query,
                  style="Accent.TButton").pack(pady=10)
        
        # Frame para resultados
        results_frame = ttk.Frame(main_frame, style="Card.TFrame")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        ttk.Label(results_frame, text="Resultados", style="SubHeader.TLabel").pack(pady=10, anchor="w", padx=15)
        
        # Área de texto para resultados
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, 
                                                    font=("Arial", 10),
                                                    bg="white",
                                                    relief="solid",
                                                    height=10)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        self.results_text.config(state=tk.DISABLED)
    
    # Métodos de funcionalidad
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
        
        # Actualizar lista
        self.refresh_families_list()
        messagebox.showinfo("Éxito", f"Familia '{name}' creada exitosamente")
    
    def refresh_families_list(self):
        """Actualiza la lista de familias en la tabla"""
        # Limpiar tabla
        for item in self.families_tree.get_children():
            self.families_tree.delete(item)
        
        # Agregar familias
        for family in self.families:
            member_count = len(family.members)
            self.families_tree.insert("", tk.END, values=(family.id, family.name, member_count, family.current_year))
    
    def select_family(self):
        """Selecciona una familia de la lista"""
        selected = self.families_tree.selection()
        if not selected:
            messagebox.showinfo("Información", "Por favor, seleccione una familia de la lista")
            return
            
        item = self.families_tree.item(selected[0])
        family_id = item['values'][0]
        
        # Encontrar la familia
        for family in self.families:
            if family.id == family_id:
                self.current_family = family
                self.selected_family_label.config(text=f"Familia seleccionada: {family.name} (ID: {family.id})")
                self.relationships_family_label.config(text=f"Familia seleccionada: {family.name} (ID: {family.id})")
                self.tree_family_label.config(text=f"Familia seleccionada: {family.name} (ID: {family.id})")
                self.simulation_family_label.config(text=f"Familia seleccionada: {family.name} (ID: {family.id})")
                self.queries_family_label.config(text=f"Familia seleccionada: {family.name} (ID: {family.id})")
                
                # Actualizar listas en otras pestañas
                self.refresh_members_list()
                self.refresh_relationships_data()
                self.refresh_simulation_persons()
                self.refresh_queries_persons()
                break
    
    def delete_family(self):
        """Elimina una familia seleccionada"""
        if not self.current_family:
            messagebox.showinfo("Información", "Por favor, seleccione una familia para eliminar")
            return
            
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la familia '{self.current_family.name}'?"):
            self.families = [f for f in self.families if f.id != self.current_family.id]
            self.current_family = None
            self.selected_family_label.config(text="Ninguna familia seleccionada")
            self.relationships_family_label.config(text="Ninguna familia seleccionada")
            self.tree_family_label.config(text="Ninguna familia seleccionada")
            self.simulation_family_label.config(text="Ninguna familia seleccionada")
            self.queries_family_label.config(text="Ninguna familia seleccionada")
            self.refresh_families_list()
            messagebox.showinfo("Éxito", "Familia eliminada correctamente")
    
    def add_member(self):
        """Agrega un nuevo integrante a la familia seleccionada"""
        if not self.current_family:
            messagebox.showerror("Error", "Primero debe seleccionar una familia")
            return
            
        # Obtener datos del formulario
        cedula = self.member_cedula_entry.get().strip()
        first_name = self.member_first_name_entry.get().strip()
        last_name = self.member_last_name_entry.get().strip()
        birth_date = self.member_birth_entry.get().strip()
        death_date = self.member_death_entry.get().strip()
        gender = self.member_gender_var.get()
        province = self.member_province_cb.get()
        marital_status = self.member_marital_cb.get()
        
        # Validaciones
        if not cedula:
            messagebox.showerror("Error", "La cédula es obligatoria")
            return
            
        if not re.match(r"^\d{9,12}$", cedula):
            messagebox.showerror("Error", "La cédula debe ser numérica y tener entre 9 y 12 dígitos")
            return
            
        if not first_name:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
            
        if not last_name:
            messagebox.showerror("Error", "El apellido es obligatorio")
            return
            
        if not birth_date:
            messagebox.showerror("Error", "La fecha de nacimiento es obligatoria")
            return
            
        # Validar rango de fechas (1820-01-01 a 2025-01-01)
        if not validate_date(birth_date):
            messagebox.showerror("Error", "La fecha de nacimiento debe estar entre 1820-01-01 y 2025-01-01")
            return
            
        if death_date and not re.match(r"^\d{4}-\d{2}-\d{2}$", death_date):
            messagebox.showerror("Error", "Formato de fecha de fallecimiento inválido (YYYY-MM-DD)")
            return
            
        if death_date and not validate_date(death_date):
            messagebox.showerror("Error", "La fecha de fallecimiento debe estar entre 1820-01-01 y 2025-01-01")
            return
            
        if not gender:
            messagebox.showerror("Error", "Debe seleccionar un género")
            return
            
        if not province:
            messagebox.showerror("Error", "Debe seleccionar una provincia")
            return
            
        if not marital_status:
            messagebox.showerror("Error", "Debe seleccionar un estado civil")
            return
        
        # Verificar cédula única en la familia
        for member in self.current_family.members:
            if member.cedula == cedula:
                messagebox.showerror("Error", "Ya existe un integrante con esta cédula en la familia")
                return
        
        # Crear nueva persona
        add_person_to_family(self.current_family, cedula, first_name, last_name, birth_date, death_date, gender, province, marital_status)
        
        # Limpiar formulario
        self.member_cedula_entry.delete(0, tk.END)
        self.member_first_name_entry.delete(0, tk.END)
        self.member_last_name_entry.delete(0, tk.END)
        self.member_birth_entry.delete(0, tk.END)
        self.member_death_entry.delete(0, tk.END)
        self.member_gender_var.set("")
        self.member_province_cb.set("")
        self.member_marital_cb.set("")
        
        # Actualizar lista
        self.refresh_members_list()
        self.refresh_simulation_persons()
        self.refresh_queries_persons()
        messagebox.showinfo("Éxito", "Integrante agregado correctamente")
    
    def refresh_members_list(self):
        """Actualiza la lista de miembros en la tabla"""
        if not self.current_family:
            return
            
        # Limpiar tabla
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)
        
        # Agregar miembros
        for member in self.current_family.members:
            gender_text = "Masculino" if member.gender == "M" else "Femenino"
            status = "Vivo" if member.alive else "Fallecido"
            age = member.calculate_age()
            self.members_tree.insert("", tk.END, values=(
                member.cedula, 
                member.first_name,
                member.last_name,
                member.birth_date,
                gender_text,
                member.province,
                member.marital_status,
                age,
                status
            ))
    
    def refresh_relationships_data(self):
        """Actualiza los datos para las relaciones"""
        if not self.current_family:
            return
            
        # Actualizar listas de personas
        person_names = [f"{p.first_name} {p.last_name} (Cédula: {p.cedula})" for p in self.current_family.members]
        
        self.child_cb['values'] = person_names
        self.mother_cb['values'] = [name for name in person_names 
                                   if " (Cédula: " in name and self.get_person_by_name(name).gender == "F"]
        self.father_cb['values'] = [name for name in person_names 
                                   if " (Cédula: " in name and self.get_person_by_name(name).gender == "M"]
        self.person1_cb['values'] = person_names
        self.person2_cb['values'] = person_names
    
    def refresh_simulation_persons(self):
        """Actualiza la lista de personas para la simulación"""
        if not self.current_family:
            return
            
        # Limpiar lista
        self.simulation_persons_listbox.delete(0, tk.END)
        
        # Agregar personas
        for person in self.current_family.members:
            gender_text = "M" if person.gender == "M" else "F"
            status = "VIVO" if person.alive else "FALLECIDO"
            self.simulation_persons_listbox.insert(tk.END, f"{person.first_name} {person.last_name} ({gender_text}) [{status}]")
    
    def refresh_queries_persons(self):
        """Actualiza la lista de personas para las consultas"""
        if not self.current_family:
            return
            
        # Limpiar lista
        self.queries_persons_listbox.delete(0, tk.END)
        
        # Agregar personas
        for person in self.current_family.members:
            gender_text = "M" if person.gender == "M" else "F"
            status = "VIVO" if person.alive else "FALLECIDO"
            self.queries_persons_listbox.insert(tk.END, f"{person.first_name} {person.last_name} ({gender_text}) [{status}]")
    
    def get_person_by_name(self, name_with_cedula):
        """Obtiene una persona por su nombre con cédula"""
        if not self.current_family or not name_with_cedula:
            return None
            
        # Extraer cédula del formato "Nombre (Cédula: XXX)"
        cedula = name_with_cedula.split("Cédula: ")[1].split(")")[0]
        
        for person in self.current_family.members:
            if person.cedula == cedula:
                return person
        return None
    
    def get_selected_persons(self, listbox):
        """Obtiene las personas seleccionadas de un listbox"""
        selected_indices = listbox.curselection()
        selected_persons = []
        
        if not selected_indices:
            return selected_persons
        
        for index in selected_indices:
            person_info = listbox.get(index)
            # Extraer nombre de la información
            name = person_info.split(" (")[0]
            
            # Buscar la persona en la familia
            for person in self.current_family.members:
                if f"{person.first_name} {person.last_name}" == name:
                    selected_persons.append(person)
                    break
        
        return selected_persons
    
    def save_query_selection(self):
        """Guarda la selección actual de personas para consultas"""
        self.query_persons_selection = self.get_selected_persons(self.queries_persons_listbox)
        
        if self.query_persons_selection:
            messagebox.showinfo("Éxito", f"Selección guardada: {len(self.query_persons_selection)} persona(s) seleccionada(s)")
        else:
            messagebox.showinfo("Información", "No hay personas seleccionadas para guardar")
    
    def register_parents(self):
        """Registra la relación de padres para un hijo"""
        if not self.current_family:
            messagebox.showerror("Error", "Primero debe seleccionar una familia")
            return
            
        # Obtener selecciones
        child_name = self.child_var.get()
        mother_name = self.mother_var.get()
        father_name = self.father_var.get()
        
        if not child_name or not mother_name or not father_name:
            messagebox.showerror("Error", "Debe seleccionar hijo, madre y padre")
            return
            
        # Obtener cédulas
        child_cedula = child_name.split("Cédula: ")[1].split(")")[0]
        mother_cedula = mother_name.split("Cédula: ")[1].split(")")[0]
        father_cedula = father_name.split("Cédula: ")[1].split(")")[0]
        
        # Registrar relación
        success, message = register_parents(self.current_family, child_cedula, mother_cedula, father_cedula)
        
        if success:
            messagebox.showinfo("Éxito", message)
            self.refresh_relationships_data()
        else:
            messagebox.showerror("Error", message)
    
    def register_couple(self):
        """Registra una unión de pareja entre dos personas"""
        if not self.current_family:
            messagebox.showerror("Error", "Primero debe seleccionar una familia")
            return
            
        # Obtener selecciones
        person1_name = self.person1_var.get()
        person2_name = self.person2_var.get()
        
        if not person1_name or not person2_name:
            messagebox.showerror("Error", "Debe seleccionar dos personas")
            return
            
        if person1_name == person2_name:
            messagebox.showerror("Error", "No puede seleccionar la misma persona dos veces")
            return
            
        # Obtener cédulas
        person1_cedula = person1_name.split("Cédula: ")[1].split(")")[0]
        person2_cedula = person2_name.split("Cédula: ")[1].split(")")[0]
        
        # Registrar pareja
        success, message = register_couple(self.current_family, person1_cedula, person2_cedula)
        
        if success:
            messagebox.showinfo("Éxito", message)
            self.refresh_members_list()
            self.refresh_relationships_data()
        else:
            messagebox.showerror("Error", message)
    
    def generate_family_tree(self):
        """Genera y muestra el árbol genealógico"""
        if not self.current_family:
            messagebox.showerror("Error", "Primero debe seleccionar una familia")
            return
            
        # Limpiar área de texto
        self.tree_text.config(state=tk.NORMAL)
        self.tree_text.delete(1.0, tk.END)
        
        # Generar árbol
        tree_text = get_family_tree(self.current_family)
        
        # Mostrar árbol
        self.tree_text.insert(tk.END, tree_text)
        self.tree_text.config(state=tk.DISABLED)
    
    # Métodos de simulación
    def start_simulation(self):
        """Inicia la simulación automática"""
        if not self.current_family:
            messagebox.showerror("Error", "Primero debe seleccionar una familia")
            return
            
        if self.simulation_running:
            return
            
        self.simulation_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.simulation_status.config(text="La simulación está en ejecución", foreground="#27ae60")
        self.simulation_info.config(text="La simulación avanza cada 10 segundos (simulación de 1 año por ciclo)")
        
        # Iniciar el ciclo de simulación
        self.run_simulation_cycle()
    
    def stop_simulation(self):
        """Detiene la simulación automática"""
        if not self.simulation_running:
            return
            
        self.simulation_running = False
        if self.simulation_id:
            self.root.after_cancel(self.simulation_id)
            self.simulation_id = None
            
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.simulation_status.config(text="La simulación está detenida", foreground="#e74c3c")
        self.simulation_info.config(text="Seleccione una familia y presione 'Iniciar Simulación'")
    
    def run_simulation_cycle(self):
        """Ejecuta un ciclo de simulación"""
        if not self.simulation_running or not self.current_family:
            self.stop_simulation()
            return
            
        # Incrementar el año en la simulación
        self.current_family.current_year += 1
        
        # Procesar eventos para cada persona
        for person in self.current_family.members:
            if person.alive:
                # Cumpleaños
                simulate_birthday(person, self.current_family)
                
                # Probabilidad de fallecimiento aleatorio
                age = person.calculate_age()
                death_probability = 0.01 * (age - 60) if age > 60 else 0.001
                if random.random() < death_probability:
                    simulate_death(person, self.current_family)
            
            # Actualizar estado de salud emocional
            if person.marital_status == "Viudo/a" and person.emotional_health > 20:
                person.emotional_health -= random.randint(1, 5)
            
            # Probabilidad de encontrar pareja
            if person.marital_status == "Soltero/a" and person.calculate_age() >= 18:
                if random.random() < 0.05:  # 5% de probabilidad
                    self.try_find_partner(person)
        
        # Probabilidad de nacimientos
        for person in self.current_family.members:
            if person.can_have_children() and person.has_partner():
                # Verificar que ambos padres estén vivos
                if person.alive and person.spouse.alive:
                    if random.random() < 0.3:  # 30% de probabilidad de tener un hijo
                        success, _ = simulate_birth(person, person.spouse, self.current_family, self.current_family.current_year)
        
        # Actualizar interfaz
        self.refresh_members_list()
        self.refresh_families_list()
        self.refresh_simulation_persons()
        
        # Programar el próximo ciclo
        self.simulation_id = self.root.after(self.simulation_interval, self.run_simulation_cycle)
    
    def try_find_partner(self, person):
        """Intenta encontrar una pareja para una persona soltera"""
        if not person.alive or person.has_partner():
            return False
            
        # Buscar posibles parejas
        possible_partners = []
        for potential in self.current_family.members:
            if potential != person and potential.alive and not potential.has_partner():
                can_marry, _ = check_if_can_marry(person, potential)
                if can_marry:
                    possible_partners.append(potential)
        
        # Seleccionar una pareja al azar
        if possible_partners:
            partner = random.choice(possible_partners)
            success, _ = register_couple(self.current_family, person.cedula, partner.cedula)
            return success
            
        return False
    
    def manual_birthday(self):
        """Simula un cumpleaños manual para una persona seleccionada"""
        if not self.current_family:
            messagebox.showerror("Error", "Primero debe seleccionar una familia")
            return
            
        selected_persons = self.get_selected_persons(self.simulation_persons_listbox)
        if not selected_persons:
            messagebox.showinfo("Información", "Por favor, seleccione una persona de la lista")
            return
            
        person = selected_persons[0]
        simulate_birthday(person, self.current_family)
        self.refresh_members_list()
        self.refresh_simulation_persons()
        messagebox.showinfo("Éxito", f"{person.first_name} {person.last_name} ha cumplido un año más")
    
    def manual_birth(self):
        """Simula un nacimiento manual entre dos personas seleccionadas"""
        if not self.current_family:
            messagebox.showerror("Error", "Primero debe seleccionar una familia")
            return
            
        selected_persons = self.get_selected_persons(self.simulation_persons_listbox)
        if len(selected_persons) < 2:
            messagebox.showinfo("Información", "Por favor, seleccione dos personas de la lista")
            return
            
        person1 = selected_persons[0]
        person2 = selected_persons[1]
        
        # Verificar que ambos estén vivos
        if not person1.alive or not person2.alive:
            messagebox.showerror("Error", "Ambas personas deben estar vivas para tener un hijo")
            return
            
        if person1 and person2:
            success, message = simulate_birth(person1, person2, self.current_family, self.current_family.current_year)
            if success:
                self.refresh_members_list()
                self.refresh_simulation_persons()
                messagebox.showinfo("Éxito", message)
            else:
                messagebox.showerror("Error", message)
    
    def manual_death(self):
        """Simula un fallecimiento manual para una persona seleccionada"""
        if not self.current_family:
            messagebox.showerror("Error", "Primero debe seleccionar una familia")
            return
            
        selected_persons = self.get_selected_persons(self.simulation_persons_listbox)
        if not selected_persons:
            messagebox.showinfo("Información", "Por favor, seleccione una persona de la lista")
            return
            
        person = selected_persons[0]
        success, message = simulate_death(person, self.current_family)
        if success:
            self.refresh_members_list()
            self.refresh_simulation_persons()
            messagebox.showinfo("Éxito", message)
        else:
            messagebox.showerror("Error", message)
    
    def manual_union(self):
        """Simula una unión manual entre dos personas seleccionadas"""
        if not self.current_family:
            messagebox.showerror("Error", "Primero debe seleccionar una familia")
            return
            
        selected_persons = self.get_selected_persons(self.simulation_persons_listbox)
        if len(selected_persons) < 2:
            messagebox.showinfo("Información", "Por favor, seleccione dos personas de la lista")
            return
            
        person1 = selected_persons[0]
        person2 = selected_persons[1]
        
        if person1 and person2:
            can_marry, reason = check_if_can_marry(person1, person2)
            if can_marry:
                success, message = register_couple(self.current_family, person1.cedula, person2.cedula)
                if success:
                    self.refresh_members_list()
                    self.refresh_simulation_persons()
                    messagebox.showinfo("Éxito", message)
                else:
                    messagebox.showerror("Error", message)
            else:
                messagebox.showerror("Error", f"No pueden formar pareja: {reason}")
    
    # Métodos de consultas avanzadas
    def execute_query(self):
        """Ejecuta la consulta seleccionada"""
        if not self.current_family:
            messagebox.showerror("Error", "Primero debe seleccionar una familia")
            return
            
        selection = self.queries_listbox.curselection()
        if not selection:
            messagebox.showinfo("Información", "Por favor, seleccione una consulta de la lista")
            return
            
        query_num = selection[0] + 1
        
        # Limpiar resultados
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        # Verificar si hay selección guardada
        if not self.query_persons_selection:
            self.results_text.insert(tk.END, "ERROR: No hay personas seleccionadas. Use el botón 'Guardar Selección' antes de ejecutar la consulta.")
            self.results_text.config(state=tk.DISABLED)
            return
            
        # Ejecutar la consulta correspondiente
        if query_num == 1:
            self.query_relationship()
        elif query_num == 2:
            self.query_first_degree_cousins()
        elif query_num == 3:
            self.query_motherline_ancestors()
        elif query_num == 4:
            self.query_living_descendants()
        elif query_num == 5:
            self.query_births_last_10_years()
        elif query_num == 6:
            self.query_couples_with_multiple_children()
        elif query_num == 7:
            self.query_deaths_before_50()
        
        # Limpiar selección después de ejecutar la consulta
        self.query_persons_selection = []
        self.queries_persons_listbox.selection_clear(0, tk.END)
        self.results_text.config(state=tk.DISABLED)
    
    def query_relationship(self):
        """Consulta 1: ¿Cuál es la relación entre persona A y persona B?"""
        # Seleccionar dos personas
        if len(self.query_persons_selection) < 2:
            self.results_text.insert(tk.END, "ERROR: Debe seleccionar dos personas de la lista para esta consulta.")
            return
            
        person1 = self.query_persons_selection[0]
        person2 = self.query_persons_selection[1]
        
        if person1 and person2:
            relationship = find_relationship(person1, person2)
            self.results_text.insert(tk.END, f"La relación entre {person1.first_name} {person1.last_name} y {person2.first_name} {person2.last_name} es: {relationship}")
        else:
            self.results_text.insert(tk.END, "ERROR: No se pudieron encontrar las personas seleccionadas.")
    
    def query_first_degree_cousins(self):
        """Consulta 2: ¿Quiénes son los primos de primer grado de X?"""
        # Seleccionar una persona
        if not self.query_persons_selection:
            self.results_text.insert(tk.END, "ERROR: Debe seleccionar una persona de la lista para esta consulta.")
            return
            
        person = self.query_persons_selection[0]
        
        if person:
            cousins = get_first_degree_cousins(person)
            if cousins:
                result = f"Los primos de primer grado de {person.first_name} {person.last_name} son:\n"
                for cousin in cousins:
                    result += f"- {cousin.first_name} {cousin.last_name} ({cousin.gender})\n"
                self.results_text.insert(tk.END, result)
            else:
                self.results_text.insert(tk.END, f"{person.first_name} {person.last_name} no tiene primos de primer grado registrados.")
        else:
            self.results_text.insert(tk.END, "ERROR: No se pudo encontrar la persona seleccionada.")
    
    def query_motherline_ancestors(self):
        """Consulta 3: ¿Cuáles son todos los antepasados maternos de X?"""
        # Seleccionar una persona
        if not self.query_persons_selection:
            self.results_text.insert(tk.END, "ERROR: Debe seleccionar una persona de la lista para esta consulta.")
            return
            
        person = self.query_persons_selection[0]
        
        if person:
            ancestors = get_motherline_ancestors(person)
            if ancestors:
                result = f"Los antepasados maternos de {person.first_name} {person.last_name} son:\n"
                for i, ancestor in enumerate(ancestors, 1):
                    result += f"{i}. {ancestor.first_name} {ancestor.last_name} ({ancestor.gender})\n"
                self.results_text.insert(tk.END, result)
            else:
                self.results_text.insert(tk.END, f"{person.first_name} {person.last_name} no tiene antepasados maternos registrados.")
        else:
            self.results_text.insert(tk.END, "ERROR: No se pudo encontrar la persona seleccionada.")
    
    def query_living_descendants(self):
        """Consulta 4: ¿Cuáles descendientes de X están vivos actualmente?"""
        # Seleccionar una persona
        if not self.query_persons_selection:
            self.results_text.insert(tk.END, "ERROR: Debe seleccionar una persona de la lista para esta consulta.")
            return
            
        person = self.query_persons_selection[0]
        
        if person:
            descendants = get_living_descendants(person)
            if descendants:
                result = f"Los descendientes vivos de {person.first_name} {person.last_name} son:\n"
                for i, descendant in enumerate(descendants, 1):
                    result += f"{i}. {descendant.first_name} {descendant.last_name} ({descendant.gender}, {descendant.calculate_age()} años)\n"
                self.results_text.insert(tk.END, result)
            else:
                self.results_text.insert(tk.END, f"{person.first_name} {person.last_name} no tiene descendientes vivos registrados.")
        else:
            self.results_text.insert(tk.END, "ERROR: No se pudo encontrar la persona seleccionada.")
    
    def query_births_last_10_years(self):
        """Consulta 5: ¿Cuántas personas nacieron en los últimos 10 años?"""
        count = get_births_last_10_years(self.current_family)
        self.results_text.insert(tk.END, f"En los últimos 10 años han nacido {count} personas en la familia.")
    
    def query_couples_with_multiple_children(self):
        """Consulta 6: ¿Cuáles parejas actuales tienen 2 o más hijos en común?"""
        couples = get_couples_with_multiple_children(self.current_family)
        if couples:
            result = "Las parejas actuales con 2 o más hijos en común son:\n"
            for i, (person1, person2) in enumerate(couples, 1):
                common_children = set(person1.children) & set(person2.children)
                result += f"{i}. {person1.first_name} {person1.last_name} y {person2.first_name} {person2.last_name} ({len(common_children)} hijos en común)\n"
            self.results_text.insert(tk.END, result)
        else:
            self.results_text.insert(tk.END, "No hay parejas actuales con 2 o más hijos en común.")
    
    def query_deaths_before_50(self):
        """Consulta 7: ¿Cuántas personas fallecieron antes de cumplir 50 años?"""
        count = get_deaths_before_50(self.current_family)
        self.results_text.insert(tk.END, f"{count} personas fallecieron antes de cumplir 50 años.")

# ======================================
# PUNTO DE ENTRADA DEL PROGRAMA
# ======================================
if __name__ == "__main__":
    root = tk.Tk()
    app = FamilyManagementApp(root)
    root.mainloop()