from familias import validate_family_has_members, get_person_by_cedula

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
    result = f"{indent}• {person.name} ({person.marital_status})\n"
    
    # Mostrar pareja
    if person.spouse:
        result += f"{indent}  ╰─ pareja con: {person.spouse.name}\n"
    
    # Mostrar hijos
    if person.children:
        result += f"{indent}  Hijos:\n"
        for child in person.children:
            result += display_person_tree(child, level + 1)
    
    return result