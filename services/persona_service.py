# services/persona_service.py
from typing import Tuple, Optional
from models.family import Family
from models.person import Person
from utils.validators import validar_persona_completa

def exportar_a_gedcom(family: Family) -> str:
    """Exporta la familia a formato GEDCOM"""
    gedcom_lines = ["0 HEAD", "1 GEDC", "2 VERS 5.5", "2 FORM LINEAGE-LINKED", "1 CHAR UTF-8"]
    
    # Primero, identificar todas las familias únicas
    families = {}
    for person in family.members:
        # Si la persona tiene padre o madre, pertenece a una familia como hijo
        if person.father or person.mother:
            # Crear una clave única para la familia basada en los padres
            father_key = person.father.cedula if person.father else ""
            mother_key = person.mother.cedula if person.mother else ""
            family_key = f"{father_key}_{mother_key}"
            
            if family_key not in families:
                families[family_key] = {
                    "father": person.father,
                    "mother": person.mother,
                    "children": []
                }
            families[family_key]["children"].append(person)
    
    # Asignar referencias únicas a cada familia
    family_refs = {}
    for i, family_key in enumerate(families.keys(), 1):
        family_refs[family_key] = f"@F{i}@"
    
    # Exportar personas
    for i, person in enumerate(family.members, 1):
        ref = f"@I{i}@"
        gedcom_lines.append(f"0 {ref} INDI")
        gedcom_lines.append(f"1 NAME {person.first_name} {person.last_name}")
        gedcom_lines.append(f"1 SEX {'M' if person.gender == 'Masculino' else 'F'}")
        
        if person.birth_date:
            gedcom_lines.append("1 BIRT")
            gedcom_lines.append(f"2 DATE {person.birth_date}")
        
        if not person.alive and person.death_date:
            gedcom_lines.append("1 DEAT")
            gedcom_lines.append(f"2 DATE {person.death_date}")
        
        # Relaciones familiares
        # Si la persona es padre/madre, asignar FAMS
        if person.children:
            # Encontrar todas las familias donde esta persona es padre/madre
            for family_key, family_info in families.items():
                if (person == family_info["father"] or person == family_info["mother"]) and family_key in family_refs:
                    gedcom_lines.append(f"1 FAMS {family_refs[family_key]}")
        
        # Si la persona es hijo, asignar FAMC
        if person.father or person.mother:
            father_key = person.father.cedula if person.father else ""
            mother_key = person.mother.cedula if person.mother else ""
            family_key = f"{father_key}_{mother_key}"
            if family_key in family_refs:
                gedcom_lines.append(f"1 FAMC {family_refs[family_key]}")
    
    # Exportar familias
    for i, (family_key, family_info) in enumerate(families.items(), 1):
        fam_ref = f"@F{i}@"
        gedcom_lines.append(f"0 {fam_ref} FAM")
        
        if family_info["father"]:
            # Encontrar el índice del padre en family.members
            father_index = family.members.index(family_info["father"]) + 1
            gedcom_lines.append(f"1 HUSB @I{father_index}@")
        if family_info["mother"]:
            # Encontrar el índice de la madre en family.members
            mother_index = family.members.index(family_info["mother"]) + 1
            gedcom_lines.append(f"1 WIFE @I{mother_index}@")
        
        for child in family_info["children"]:
            # Encontrar el índice del hijo en family.members
            child_index = family.members.index(child) + 1
            gedcom_lines.append(f"1 CHIL @I{child_index}@")
    
    gedcom_lines.append("0 TRLR")
    return "\n".join(gedcom_lines)


class PersonaService:
    """Servicio para gestionar operaciones relacionadas con personas"""
    
    @staticmethod
    def crear_persona(family: Family, cedula: str, first_name: str, last_name: str, 
                    birth_date: str, death_date: str, gender: str, 
                    province: str, marital_status: str) -> Tuple[bool, Optional[Person], Optional[str]]:
        """Crea una nueva persona con validación completa"""
        # MODIFICACIÓN CLAVE: Pasar la provincia a la validación de cédula
        valido, error = validar_persona_completa(
            cedula, first_name, last_name, birth_date, 
            gender, province, marital_status, death_date
        )
        if not valido:
            return False, None, error
    
        # Verificar que la cédula sea única
        if not Family.validate_cedula_unique(cedula, family):
            return False, None, "La cédula ya existe en la familia"
    
        # Crear la persona
        person = Person(cedula, first_name, last_name, birth_date, 
                    death_date, gender, province, marital_status)
    
        # Agregar a la familia
        family.add_member(person)
        return True, person, "Persona creada exitosamente"
    
    @staticmethod
    def obtener_persona_por_cedula(family: Family, cedula: str) -> Optional[Person]:
        """Obtiene una persona por su cédula"""
        return family.get_member_by_cedula(cedula)
    
    @staticmethod
    def obtener_todas_personas(family: Family) -> list:
        """Obtiene todas las personas de la familia"""
        return family.members
    
    @staticmethod
    def obtener_personas_vivas(family: Family) -> list:
        """Obtiene todas las personas vivas de la familia"""
        return family.get_living_members()
    
    @staticmethod
    def obtener_personas_fallecidas(family: Family) -> list:
        """Obtiene todas las personas fallecidas de la familia"""
        return family.get_deceased_members()
    
    @staticmethod
    def actualizar_persona(person: Person, **kwargs) -> Tuple[bool, Optional[str]]:
        """Actualiza los datos de una persona"""
        campos_permitidos = ['first_name', 'last_name', 'birth_date', 'death_date', 
                           'gender', 'province', 'marital_status', 'emotional_health']
        
        for campo, valor in kwargs.items():
            if campo in campos_permitidos:
                setattr(person, campo, valor)
        
        # Si se actualizó death_date, actualizar estado alive
        if 'death_date' in kwargs:
            person.alive = not bool(kwargs['death_date'])
        
        return True, "Persona actualizada exitosamente"
    
    @staticmethod
    def eliminar_persona(family: Family, cedula: str) -> Tuple[bool, Optional[str]]:
        """Elimina una persona de la familia"""
        person = family.get_member_by_cedula(cedula)
        if not person:
            return False, "Persona no encontrada"
        
        # Verificar si tiene relaciones activas
        if person.children:
            return False, "No se puede eliminar una persona que tiene hijos"
        
        if person.spouse:
            return False, "No se puede eliminar una persona que tiene pareja"
        
        # Eliminar referencias de padres
        for member in family.members:
            if member.mother == person:
                member.mother = None
            if member.father == person:
                member.father = None
        
        # Eliminar de la lista de hijos de los padres
        if person.mother and person in person.mother.children:
            person.mother.children.remove(person)
        if person.father and person in person.father.children:
            person.father.children.remove(person)
        
        # Eliminar de la familia
        family.members.remove(person)
        
        return True, "Persona eliminada exitosamente"
    
    @staticmethod
    def obtener_informacion_completa(person: Person) -> dict:
        """Obtiene información completa de una persona"""
        return {
            'cedula': person.cedula,
            'nombre_completo': person.get_full_name(),
            'edad': person.calculate_age(),
            'vivo': person.alive,
            'genero': 'Masculino' if person.gender == 'M' else 'Femenino',
            'provincia': person.province,
            'estado_civil': person.marital_status,
            'salud_emocional': person.emotional_health,
            'intereses': person.interests,
            'historial': person.history,
            'madre': person.mother.get_full_name() if person.mother else None,
            'padre': person.father.get_full_name() if person.father else None,
            'pareja': person.spouse.get_full_name() if person.spouse else None,
            'hijos': [h.get_full_name() for h in person.children],
            'cantidad_hijos': len(person.children)
        }
    
    @staticmethod
    def buscar_personas_por_nombre(family: Family, nombre: str) -> list:
        """Busca personas por nombre o apellido"""
        resultados = []
        nombre_busqueda = nombre.lower()
        
        for person in family.members:
            if (nombre_busqueda in person.first_name.lower() or 
                nombre_busqueda in person.last_name.lower() or
                nombre_busqueda in person.get_full_name().lower()):
                resultados.append(person)
        
        return resultados
    
    @staticmethod
    def obtener_estadisticas_familia(family: Family) -> dict:
        """Obtiene estadísticas de la familia"""
        total = len(family.members)
        vivos = len(family.get_living_members())
        fallecidos = len(family.get_deceased_members())
        
        # Contar por género
        hombres = sum(1 for p in family.members if p.gender == 'M')
        mujeres = sum(1 for p in family.members if p.gender == 'F')
        
        # Contar por estado civil
        estados = {}
        for person in family.members:
            estados[person.marital_status] = estados.get(person.marital_status, 0) + 1
        
        # Edad promedio
        edades = [p.calculate_age() for p in family.members if p.alive]
        edad_promedio = sum(edades) / len(edades) if edades else 0
        
        return {
            'total_personas': total,
            'personas_vivas': vivos,
            'personas_fallecidas': fallecidos,
            'hombres': hombres,
            'mujeres': mujeres,
            'estados_civiles': estados,
            'edad_promedio': round(edad_promedio, 1),
            'porcentaje_vivos': round((vivos / total * 100), 1) if total > 0 else 0
        }