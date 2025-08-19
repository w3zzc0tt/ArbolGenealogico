class Person:
    """Clase que representa a una persona en el sistema"""
    def __init__(self, cedula, name, birth_date, death_date, gender, province, marital_status):
        self.cedula = cedula
        self.name = name
        self.birth_date = birth_date
        self.death_date = death_date
        self.gender = gender  # 'M' o 'F'
        self.province = province
        self.marital_status = marital_status
        self.spouse = None
        self.mother = None
        self.father = None
        self.children = []

def validate_cedula(cedula, family):
    """Verifica que la cédula no exista en la familia"""
    for member in family.members:
        if member.cedula == cedula:
            return False
    return True

def display_person_info(person):
    """Muestra información detallada de una persona"""
    info = f"--- {person.name} (Cédula: {person.cedula}) ---\n"
    info += f"Fecha nacimiento: {person.birth_date}\n"
    if person.death_date:
        info += f"Fecha fallecimiento: {person.death_date}\n"
    info += f"Género: {'Masculino' if person.gender == 'M' else 'Femenino'}\n"
    info += f"Provincia: {person.province}\n"
    info += f"Estado civil: {person.marital_status}\n"
    
    # Mostrar relaciones
    if person.mother:
        info += f"Madre: {person.mother.name}\n"
    if person.father:
        info += f"Padre: {person.father.name}\n"
    if person.spouse:
        info += f"Pareja: {person.spouse.name}\n"
    if person.children:
        info += "Hijos: " + ", ".join([child.name for child in person.children]) + "\n"
    
    return info