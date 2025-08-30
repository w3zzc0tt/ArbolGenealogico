# services/persistence_service.py
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from models.family_manager import FamilyManager
from models.family import Family
from models.person import Person

class PersistenceService:
    """Servicio para guardar y cargar familias localmente"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.families_file = os.path.join(data_dir, "families.json")
        self.manager_file = os.path.join(data_dir, "manager_state.json")
        
        # Crear directorio si no existe
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def person_to_dict(self, person: Person) -> dict:
        """Convierte una persona a diccionario"""
        try:
            # Manejar fechas de manera segura
            birth_date_str = None
            if person.birth_date:
                if hasattr(person.birth_date, 'isoformat'):
                    birth_date_str = person.birth_date.isoformat()
                else:
                    # Si es string, mantenerlo como está
                    birth_date_str = str(person.birth_date)
            
            death_date_str = None
            if person.death_date:
                if hasattr(person.death_date, 'isoformat'):
                    death_date_str = person.death_date.isoformat()
                else:
                    # Si es string, mantenerlo como está
                    death_date_str = str(person.death_date)
            
            return {
                'cedula': person.cedula,
                'first_name': person.first_name,
                'last_name': person.last_name,
                'birth_date': birth_date_str,
                'death_date': death_date_str,
                'gender': person.gender,
                'province': person.province,
                'marital_status': person.marital_status,
                'alive': getattr(person, 'alive', True),  # Default a True si no existe
                # Relaciones (solo IDs para evitar referencias circulares)
                'father_cedula': person.father.cedula if person.father else None,
                'mother_cedula': person.mother.cedula if person.mother else None,
                'spouse_cedula': person.spouse.cedula if person.spouse else None,
                'children_cedulas': [child.cedula for child in person.children] if person.children else [],
                'siblings_cedulas': [sibling.cedula for sibling in person.siblings] if person.siblings else []
            }
        except Exception as e:
            print(f"Error al convertir persona a diccionario: {e}")
            print(f"Persona problemática: {person.first_name} {person.last_name}")
            raise
    
    def dict_to_person(self, data: dict) -> Person:
        """Convierte un diccionario a persona (sin relaciones)"""
        try:
            # Manejar fechas de manera segura
            birth_date = None
            if data.get('birth_date'):
                try:
                    birth_date = datetime.fromisoformat(data['birth_date'])
                except (ValueError, TypeError):
                    print(f"Advertencia: No se pudo parsear fecha de nacimiento: {data['birth_date']}")
                    birth_date = None
            
            death_date = None
            if data.get('death_date'):
                try:
                    death_date = datetime.fromisoformat(data['death_date'])
                except (ValueError, TypeError):
                    print(f"Advertencia: No se pudo parsear fecha de muerte: {data['death_date']}")
                    death_date = None
            
            person = Person(
                cedula=data['cedula'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                birth_date=birth_date,
                death_date=death_date,
                gender=data['gender'],
                province=data['province'],
                marital_status=data['marital_status']
            )
            person.alive = data.get('alive', True)
            return person
        except Exception as e:
            print(f"Error al convertir diccionario a persona: {e}")
            print(f"Datos problemáticos: {data}")
            raise
    
    def family_to_dict(self, family: Family) -> dict:
        """Convierte una familia a diccionario"""
        return {
            'id': family.id,
            'name': family.name,
            'description': family.description,
            'members': [self.person_to_dict(person) for person in family.members],
            'current_year': family.current_year
        }
    
    def dict_to_family(self, data: dict) -> Family:
        """Convierte un diccionario a familia"""
        family = Family(id=data['id'], name=data['name'])
        family.description = data.get('description', '')
        family.current_year = data.get('current_year', datetime.now().year)
        
        # Crear personas sin relaciones
        persons_dict = {}
        for person_data in data['members']:
            person = self.dict_to_person(person_data)
            family.members.append(person)
            persons_dict[person.cedula] = person
        
        # Establecer relaciones
        for person_data in data['members']:
            person = persons_dict[person_data['cedula']]
            
            # Establecer padre
            if person_data['father_cedula'] and person_data['father_cedula'] in persons_dict:
                person.father = persons_dict[person_data['father_cedula']]
            
            # Establecer madre
            if person_data['mother_cedula'] and person_data['mother_cedula'] in persons_dict:
                person.mother = persons_dict[person_data['mother_cedula']]
            
            # Establecer cónyuge
            if person_data['spouse_cedula'] and person_data['spouse_cedula'] in persons_dict:
                person.spouse = persons_dict[person_data['spouse_cedula']]
            
            # Establecer hijos
            person.children = []
            for child_cedula in person_data['children_cedulas']:
                if child_cedula in persons_dict:
                    person.children.append(persons_dict[child_cedula])
            
            # Establecer hermanos
            person.siblings = []
            for sibling_cedula in person_data['siblings_cedulas']:
                if sibling_cedula in persons_dict:
                    person.siblings.append(persons_dict[sibling_cedula])
        
        return family
    
    def save_family_manager(self, family_manager: FamilyManager) -> bool:
        """Guarda el estado completo del gestor de familias"""
        try:
            # Crear directorio si no existe
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
            
            # Guardar todas las familias
            families_data = {}
            for family_id, family in family_manager.families.items():
                try:
                    family_dict = self.family_to_dict(family)
                    families_data[str(family_id)] = family_dict
                except Exception as fe:
                    print(f"Error al convertir familia {family_id} a diccionario: {fe}")
                    import traceback
                    traceback.print_exc()
                    # Continuar con las otras familias
                    continue
            
            # Si no se pudo convertir ninguna familia pero hay familias, es un error
            if not families_data and family_manager.families:
                print("Error crítico: No se pudo convertir ninguna familia a diccionario")
                return False
            
            # Guardar familias
            with open(self.families_file, 'w', encoding='utf-8') as f:
                json.dump(families_data, f, indent=2, ensure_ascii=False)
            
            # Guardar estado del manager
            manager_state = {
                'next_id': family_manager.next_id,
                'current_family_id': family_manager.current_family_id,
                'deleted_ids': family_manager.deleted_ids,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.manager_file, 'w', encoding='utf-8') as f:
                json.dump(manager_state, f, indent=2, ensure_ascii=False)
            
            print("Datos guardados exitosamente")
            return True
            
        except Exception as e:
            print(f"Error al guardar el gestor de familias: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_family_manager(self) -> Optional[FamilyManager]:
        """Carga el estado completo del gestor de familias"""
        try:
            # Verificar que los archivos existan
            if not os.path.exists(self.families_file) or not os.path.exists(self.manager_file):
                return None
            
            # Cargar familias
            with open(self.families_file, 'r', encoding='utf-8') as f:
                families_data = json.load(f)
            
            # Cargar estado del manager
            with open(self.manager_file, 'r', encoding='utf-8') as f:
                manager_state = json.load(f)
            
            # Crear manager y restaurar estado
            family_manager = FamilyManager()
            family_manager.next_id = manager_state['next_id']
            family_manager.current_family_id = manager_state.get('current_family_id')
            family_manager.deleted_ids = manager_state.get('deleted_ids', [])
            
            # Cargar familias
            for family_id_str, family_data in families_data.items():
                family_id = int(family_id_str)
                family = self.dict_to_family(family_data)
                family_manager.families[family_id] = family
            
            return family_manager
            
        except Exception as e:
            print(f"Error al cargar datos: {e}")
            return None
    
    def backup_data(self) -> bool:
        """Crea una copia de seguridad de los datos"""
        try:
            backup_dir = os.path.join(self.data_dir, "backups")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Copiar archivo de familias
            if os.path.exists(self.families_file):
                backup_families = os.path.join(backup_dir, f"families_{timestamp}.json")
                import shutil
                shutil.copy2(self.families_file, backup_families)
            
            # Copiar estado del manager
            if os.path.exists(self.manager_file):
                backup_manager = os.path.join(backup_dir, f"manager_state_{timestamp}.json")
                import shutil
                shutil.copy2(self.manager_file, backup_manager)
            
            return True
            
        except Exception as e:
            print(f"Error al crear backup: {e}")
            return False
    
    def get_save_info(self) -> dict:
        """Obtiene información sobre el último guardado"""
        try:
            if os.path.exists(self.manager_file):
                with open(self.manager_file, 'r', encoding='utf-8') as f:
                    manager_state = json.load(f)
                
                saved_at = manager_state.get('saved_at')
                if saved_at:
                    saved_datetime = datetime.fromisoformat(saved_at)
                    return {
                        'exists': True,
                        'saved_at': saved_datetime,
                        'saved_at_str': saved_datetime.strftime("%d/%m/%Y %H:%M:%S")
                    }
            
            return {'exists': False}
            
        except Exception as e:
            print(f"Error al obtener info de guardado: {e}")
            return {'exists': False}
