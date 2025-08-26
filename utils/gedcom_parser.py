# utils/gedcom_parser.py
from asyncio.log import logger
import re
from typing import Dict, List, Optional
from models.family import Family
from models.person import Person
from services.relacion_service import RelacionService

class GedcomParser:
    """Parser para archivos GEDCOM"""
    
    @staticmethod
    def parse(family: Family, gedcom_content: str) -> Family:
        """Parsea contenido GEDCOM y crea una familia"""
        gedcom_lines = gedcom_content.strip().split('\n')
        
        # Paso 1: Parsear individuos
        individuals = GedcomParser._parse_individuals(gedcom_lines)
        
        # Paso 2: Parsear familias
        families = GedcomParser._parse_families(gedcom_lines)
        
        # Paso 3: Construir el árbol familiar
        return GedcomParser._build_family_tree(family, individuals, families)
    
    @staticmethod
    def _parse_individuals(gedcom_lines: List[str]) -> Dict[str, dict]:
        """Parsea registros de individuos (INDI)"""
        individuals = {}
        current_id = None
        current_data = {}
        
        for line in gedcom_lines:
            if not line.strip():
                continue
                
            # Formato: nivel TAG [valor]
            parts = re.split(r'\s+', line.strip(), 2)
            if len(parts) < 2:
                continue
                
            level = int(parts[0])
            tag = parts[1]
            value = parts[2] if len(parts) > 2 else ""
            
            # Nuevos individuos empiezan con 0 @ID@ INDI
            if level == 0 and tag.startswith('@') and tag.endswith('@') and value == 'INDI':
                if current_id:
                    individuals[current_id] = current_data
                current_id = tag[1:-1]  # Remover @
                current_data = {
                    'name': '',
                    'first_name': '',
                    'last_name': '',
                    'sex': '',
                    'birth_date': '',
                    'death_date': '',
                    'family_id': None
                }
            
            elif level == 1:
                if tag == 'NAME':
                    # Formato: /Apellido/
                    name_parts = value.split('/')
                    current_data['first_name'] = name_parts[0].strip()
                    if len(name_parts) > 1:
                        current_data['last_name'] = name_parts[1].strip()
                    else:
                        current_data['last_name'] = ''
                    current_data['name'] = f"{current_data['first_name']} {current_data['last_name']}"
                
                elif tag == 'SEX':
                    current_data['sex'] = 'Masculino' if value == 'M' else 'Femenino'
                
                elif tag == 'BIRT':
                    current_data['birth_date'] = ''
                
                elif tag == 'DEAT':
                    current_data['death_date'] = ''
                
                elif tag == 'FAMC':
                    current_data['family_id'] = value[1:-1]  # Remover @
                
                elif tag == 'FAMS':
                    # Las personas pueden pertenecer a múltiples familias como padres
                    if 'fams' not in current_data:
                        current_data['fams'] = []
                    current_data['fams'].append(value[1:-1])
            
            elif level == 2:
                if tag == 'DATE':
                    if 'birth_date' in current_data and not current_data['birth_date']:
                        current_data['birth_date'] = value
                    elif 'death_date' in current_data and not current_data['death_date']:
                        current_data['death_date'] = value
        
        # Agregar el último individuo
        if current_id:
            individuals[current_id] = current_data
            
        return individuals
    
    @staticmethod
    def _parse_families(gedcom_lines: List[str]) -> Dict[str, dict]:
        """Parsea registros de familias (FAM)"""
        families = {}
        current_id = None
        current_data = {}
        
        for line in gedcom_lines:
            if not line.strip():
                continue
                
            parts = re.split(r'\s+', line.strip(), 2)
            if len(parts) < 2:
                continue
                
            level = int(parts[0])
            tag = parts[1]
            value = parts[2] if len(parts) > 2 else ""
            
            # Nuevas familias empiezan con 0 @ID@ FAM
            if level == 0 and tag.startswith('@') and tag.endswith('@') and value == 'FAM':
                if current_id:
                    families[current_id] = current_data
                current_id = tag[1:-1]  # Remover @
                current_data = {
                    'husband_id': None,
                    'wife_id': None,
                    'children_ids': []
                }
            
            elif level == 1:
                if tag == 'HUSB':
                    current_data['husband_id'] = value[1:-1]  # Remover @
                elif tag == 'WIFE':
                    current_data['wife_id'] = value[1:-1]  # Remover @
                elif tag == 'CHIL':
                    current_data['children_ids'].append(value[1:-1])  # Remover @
        
        # Agregar la última familia
        if current_id:
            families[current_id] = current_data
            
        return families
    
    @staticmethod
    def _build_family_tree(family: Family, individuals: Dict[str, dict], families: Dict[str, dict]) -> Family:
        """Construye el árbol familiar a partir de los datos parseados"""
        # Paso 1: Crear todas las personas
        person_map = {}
        for cedula, data in individuals.items():
            # Determinar si está vivo
            alive = not bool(data['death_date'])
            
            # Crear persona
            person = Person(
                cedula=cedula,
                first_name=data['first_name'],
                last_name=data['last_name'],
                birth_date=data['birth_date'],
                gender=data['sex'],
                province="San José",  # Default
                death_date=data['death_date'],
                marital_status="Soltero/a"  # Valor por defecto
            )
            
            # ✅ CORRECCIÓN: Establecer estado civil basado en relaciones
            if data.get('fams'):
                person.marital_status = "Casado/a"
            elif data.get('death_date') and data.get('spouse'):
                person.marital_status = "Viudo/a"
            
            # Añadir a la familia
            family.add_or_update_member(person)
            person_map[cedula] = person
        
        # Paso 2: Establecer relaciones familiares
        for fam_id, fam_data in families.items():
            # Registrar pareja
            if fam_data['husband_id'] and fam_data['wife_id']:
                husband = person_map.get(fam_data['husband_id'])
                wife = person_map.get(fam_data['wife_id'])
                
                if husband and wife:
                    # ✅ CORRECCIÓN: Registrar pareja usando el servicio
                    exito, mensaje = RelacionService.registrar_pareja(family, husband.cedula, wife.cedula)
                    if not exito:
                        logger.warning(f"No se pudo registrar pareja: {mensaje}")
            
            # Registrar hijos
            for child_id in fam_data['children_ids']:
                child = person_map.get(child_id)
                if child:
                    father = person_map.get(fam_data['husband_id'])
                    mother = person_map.get(fam_data['wife_id'])
                    
                    if father or mother:
                        # ✅ CORRECCIÓN: Registrar padres usando el servicio
                        exito, mensaje = RelacionService.registrar_padres(
                            family,
                            child_cedula=child.cedula,
                            father_cedula=father.cedula if father else None,
                            mother_cedula=mother.cedula if mother else None
                        )
                        if not exito:
                            logger.warning(f"No se pudo registrar padres: {mensaje}")
        
        # ✅ CORRECCIÓN: Verificar y corregir relaciones recíprocas
        for person in family.members:
            if person.spouse:
                # Asegurar que la relación sea recíproca
                if person.spouse.spouse != person:
                    person.spouse.spouse = person
                # Asegurar que el estado civil sea correcto
                if "Casado" not in person.marital_status:
                    person.marital_status = "Casado/a"
                if "Casado" not in person.spouse.marital_status:
                    person.spouse.marital_status = "Casado/a"
        
        return family