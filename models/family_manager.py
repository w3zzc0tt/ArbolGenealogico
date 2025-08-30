# models/family_manager.py
from typing import Dict, List, Optional
from .family import Family

class FamilyManager:
    """Gestor de familias con IDs autoincrementales y recuperación de IDs eliminados"""
    
    def __init__(self):
        self.families: Dict[int, Family] = {}  # ID -> Family
        self.deleted_ids: List[int] = []  # IDs disponibles para reutilizar
        self.next_id: int = 1  # Próximo ID a asignar
        self.current_family_id: Optional[int] = None  # Familia actualmente seleccionada
    
    def create_family(self, name: str, description: str = "") -> int:
        """
        Crea una nueva familia y retorna su ID
        
        Args:
            name: Nombre de la familia
            description: Descripción opcional
            
        Returns:
            ID de la familia creada
        """
        # Siempre usar el siguiente ID disponible (no reutilizar)
        family_id = self.next_id
        self.next_id += 1
        
        # Crear la familia
        family = Family()
        family.name = name
        family.description = description
        family.id = family_id
        
        # Almacenar en el diccionario
        self.families[family_id] = family
        
        # Si es la primera familia, establecerla como actual
        if self.current_family_id is None:
            self.current_family_id = family_id
        
        return family_id
    
    def delete_family(self, family_id: int) -> bool:
        """
        Elimina una familia y compacta los IDs posteriores
        
        Args:
            family_id: ID de la familia a eliminar
            
        Returns:
            True si se eliminó exitosamente, False si no existía
        """
        if family_id not in self.families:
            return False
        
        # Eliminar la familia
        del self.families[family_id]
        
        # Obtener todas las familias con ID mayor al eliminado
        families_to_reorder = {}
        for fid, family in list(self.families.items()):
            if fid > family_id:
                families_to_reorder[fid] = family
                del self.families[fid]
        
        # Reasignar IDs compactando hacia abajo
        new_id = family_id
        for old_id in sorted(families_to_reorder.keys()):
            family = families_to_reorder[old_id]
            family.id = new_id  # Actualizar el ID en el objeto familia
            self.families[new_id] = family
            new_id += 1
        
        # Ajustar el próximo ID disponible
        if self.families:
            self.next_id = max(self.families.keys()) + 1
        else:
            self.next_id = 1
        
        # Limpiar lista de IDs eliminados ya que ahora compactamos
        self.deleted_ids = []
        
        # Si era la familia actual, cambiar a otra o None
        if self.current_family_id == family_id:
            if self.families:
                self.current_family_id = min(self.families.keys())
            else:
                self.current_family_id = None
        elif self.current_family_id and self.current_family_id > family_id:
            # La familia actual tenía un ID mayor, ajustar
            self.current_family_id -= 1
        
        return True
    
    def get_family(self, family_id: int) -> Optional[Family]:
        """Obtiene una familia por su ID"""
        return self.families.get(family_id)
    
    def get_current_family(self) -> Optional[Family]:
        """Obtiene la familia actualmente seleccionada"""
        if self.current_family_id is None:
            return None
        return self.families.get(self.current_family_id)
    
    def set_current_family(self, family_id: int) -> bool:
        """
        Establece la familia actual
        
        Args:
            family_id: ID de la familia a establecer como actual
            
        Returns:
            True si se estableció exitosamente, False si no existe
        """
        if family_id in self.families:
            self.current_family_id = family_id
            return True
        return False
    
    def get_all_families(self) -> Dict[int, Family]:
        """Obtiene todas las familias"""
        return self.families.copy()
    
    def get_families_list(self) -> List[tuple]:
        """
        Obtiene una lista de tuplas (id, name, member_count) para mostrar en UI
        
        Returns:
            Lista de tuplas (id, name, member_count)
        """
        families_list = []
        for family_id, family in self.families.items():
            member_count = len(family.members)
            families_list.append((family_id, family.name, member_count))
        
        # Ordenar por ID
        families_list.sort(key=lambda x: x[0])
        return families_list
    
    def get_next_available_id(self) -> int:
        """Obtiene el próximo ID que se asignará"""
        return self.next_id
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas del gestor de familias"""
        total_families = len(self.families)
        total_members = sum(len(family.members) for family in self.families.values())
        
        return {
            'total_families': total_families,
            'total_members': total_members,
            'available_ids': 0,  # Ya no hay IDs disponibles, siempre se compacta
            'next_id': self.next_id,
            'current_family_id': self.current_family_id
        }
    
    def rename_family(self, family_id: int, new_name: str) -> bool:
        """
        Renombra una familia
        
        Args:
            family_id: ID de la familia a renombrar
            new_name: Nuevo nombre de la familia
            
        Returns:
            True si se renombró exitosamente, False si no existe
        """
        if family_id in self.families:
            self.families[family_id].name = new_name
            return True
        return False
