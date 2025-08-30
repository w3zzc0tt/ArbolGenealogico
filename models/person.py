from __future__ import annotations
import datetime
import random
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.family import Family

class Person:
    """Clase que representa a una persona en el árbol genealógico"""
    
    def __init__(self, cedula, first_name, last_name, birth_date, gender, province, 
                 death_date=None, marital_status="Soltero/a"):
        """
        Inicializa una nueva persona con sus datos básicos y relaciones familiares.
        
        Args:
            cedula (str): Número de cédula único
            first_name (str): Nombre de la persona
            last_name (str): Apellido de la persona
            birth_date (str): Fecha de nacimiento en formato YYYY-MM-DD
            gender (str): Género ('M' o 'F')
            province (str): Provincia de residencia
            death_date (str, optional): Fecha de fallecimiento en formato YYYY-MM-DD
            marital_status (str, optional): Estado civil
        """
        # Validar y normalizar género
        if gender == "Masculino":
            self.gender = "M"
        elif gender == "Femenino":
            self.gender = "F"
        elif gender in ["M", "F"]:
            self.gender = gender
        else:
            raise ValueError("El género debe ser 'M', 'F', 'Masculino' o 'Femenino'")
        
        self.cedula = cedula
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.death_date = death_date
        self.province = province
        self.marital_status = marital_status
        self.spouse = None
        self.mother = None
        self.father = None
        self.children = []
        self.siblings = []
        self.events = []
        self.alive = death_date is None
        self.history = [f"Nació el {birth_date}"]
        
        if not self.alive:
            self.history.append(f"Falleció el {death_date}")
        
        # Atributos para simulación
        self.emotional_health = 100
        self.interests = self.generate_interests()
        
        # === Edad virtual para la simulación ===
        self.virtual_age = self.calculate_age()  # Inicializar con la edad real

    def calculate_age(self) -> int:
        """Calcula la edad real basada en la fecha de nacimiento"""
        if not self.birth_date:
            return 20  # Edad por defecto si no hay fecha de nacimiento
        
        try:
            # Manejar tanto datetime objects como strings
            if isinstance(self.birth_date, datetime.datetime):
                birth = self.birth_date
            elif isinstance(self.birth_date, str):
                birth = datetime.datetime.strptime(self.birth_date, "%Y-%m-%d")
            else:
                return 20  # Tipo no reconocido
                
            today = datetime.datetime.now()
            return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        except (ValueError, TypeError) as e:
            print(f"Error al calcular edad para {self.get_full_name()}: {e}")
            return 20

    def calculate_virtual_age(self) -> int:
        """Calcula la edad virtual considerando el ciclo de simulación"""
        return self.virtual_age

    def incrementar_edad_virtual(self, years: int = 1) -> None:
        """Incrementa la edad virtual en el número especificado de años"""
        self.virtual_age += years

    def generate_interests(self) -> list:
        """Genera intereses aleatorios para la persona con categorías realistas"""
        # Intereses organizados por categorías
        interests_by_category = {
            "Arte y Cultura": ["Pintura", "Escultura", "Teatro", "Cine", "Música clásica", "Literatura"],
            "Deportes y Aire Libre": ["Fútbol", "Natación", "Ciclismo", "Senderismo", "Yoga", "Atletismo"],
            "Tecnología y Ciencia": ["Programación", "Robótica", "Astronomía", "Electrónica", "Inteligencia Artificial", "Ciencia"],
            "Gastronomía": ["Cocina", "Vinos", "Repostería", "Café", "Restaurantes", "Comida internacional"],
            "Aprendizaje": ["Idiomas", "Historia", "Filosofía", "Psicología", "Matemáticas", "Economía"],
            "Social": ["Voluntariado", "Política", "Activismo", "Redes sociales", "Eventos sociales", "Comunidad"],
            "Entretenimiento": ["Videojuegos", "Series", "Libros", "Conciertos", "Festivales", "Bailar"],
            "Salud y Bienestar": ["Meditación", "Nutrición", "Entrenamiento", "Mindfulness", "Terapias alternativas", "Yoga"]
        }
        
        # Seleccionar categorías aleatorias
        selected_categories = random.sample(list(interests_by_category.keys()), 2)
        
        # Obtener intereses de las categorías seleccionadas
        interests = []
        for category in selected_categories:
            interests.extend(random.sample(interests_by_category[category], 2))
        
        # Asegurar que haya 3-4 intereses únicos
        return list(set(interests))[:4]

    def set_death_date(self, death_date: str):
        """Establece la fecha de defunción y actualiza estado"""
        self.death_date = death_date
        self.alive = False
        self.history.append(f"Falleció el {death_date}")

    def get_full_name(self) -> str:
        """Devuelve el nombre completo de la persona"""
        return f"{self.first_name} {self.last_name}"

    def has_partner(self) -> bool:
        """Verifica si la persona tiene pareja"""
        return self.spouse is not None and self.spouse.alive

    def is_married_to(self, other_person: 'Person') -> bool:
        """Verifica si la persona está casada con otra persona específica"""
        return self.has_partner() and self.spouse == other_person

    def __str__(self):
        """Representación en cadena de la persona"""
        return f"{self.first_name} {self.last_name} ({self.cedula})"

    def add_history(self, event: str):
        """Agrega un evento manual al historial"""
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.history.append(f"{event} ({date})")

    def add_major_life_event(self, event_type: str, details: str = "", date: str = None):
        """
        Agrega un evento mayor de la vida con categorización
        
        Args:
            event_type (str): Tipo de evento (birth, marriage, divorce, death, etc.)
            details (str, optional): Detalles adicionales del evento
            date (str, optional): Fecha específica del evento
        """
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Categorías de eventos
        event_categories = {
            'birth': '👶',
            'marriage': '💍',
            'divorce': '💔',
            'death': '⚰️',
            'childbirth': '👶',
            'graduation': '🎓',
            'retirement': '🏖️',
            'widowhood': '🕯️',
            'other': '📝'
        }
        
        category_emoji = event_categories.get(event_type, '📝')
        event_str = f"{category_emoji} {event_type.capitalize()}"
        if details:
            event_str += f": {details}"
        
        self.events.append({"evento": event_str, "fecha": date})
        self.history.append(f"{event_str} ({date})")
        
    def add_event(self, event: str, date: str):
        """Agrega un evento a la lista de eventos"""
        self.events.append({"evento": event, "fecha": date})
        
    def can_have_children(self) -> bool:
        """Determina si la persona puede tener hijos"""
        age = self.calculate_virtual_age()
        return self.alive and self.gender == "F" and 18 <= age <= 45
    
    def get_relationship_to(self, other_person: 'Person', family: 'Family') -> str:
        """
        Determina la relación entre dos personas usando lógica de deducción familiar
        
        Args:
            other_person (Person): La otra persona
            family (Family): La familia a la que pertenecen
            
        Returns:
            str: Descripción de la relación según grados de consanguinidad
        """
        if self == other_person:
            return "Yo mismo/a"
        
        # === GRADO CERO - YO ===
        
        # === PRIMER GRADO - RELACIONES DIRECTAS ===
        
        # Padres
        if self.father == other_person:
            return "Padre"
        if self.mother == other_person:
            return "Madre"
        
        # Hijos
        if other_person in self.children:
            return "Hijo/a"
        
        # Cónyuge
        if self.spouse == other_person:
            return "Cónyuge"
        
        # === SEGUNDO GRADO - HERMANOS, ABUELOS, NIETOS ===
        
        # Hermanos
        if other_person in self.siblings:
            return "Hermano/a"
        
        # Verificar hermanos por padres comunes
        if (self.father and other_person.father and self.father == other_person.father) or \
           (self.mother and other_person.mother and self.mother == other_person.mother):
            return "Hermano/a"
        
        # Abuelos - padres de mis padres
        if self.father and (self.father.father == other_person or self.father.mother == other_person):
            return "Abuelo/a paterno/a"
        if self.mother and (self.mother.father == other_person or self.mother.mother == other_person):
            return "Abuelo/a materno/a"
        
        # Nietos - hijos de mis hijos
        for child in self.children:
            if other_person in child.children:
                return "Nieto/a"
        
        # === TERCER GRADO - TÍOS, SOBRINOS, BISABUELOS, BISNIETOS ===
        
        # Tíos - hermanos de mis padres
        if self.father:
            for sibling in self.father.siblings:
                if sibling == other_person:
                    return "Tío/a paterno/a"
        if self.mother:
            for sibling in self.mother.siblings:
                if sibling == other_person:
                    return "Tío/a materno/a"
        
        # Sobrinos - hijos de mis hermanos
        for sibling in self.siblings:
            if other_person in sibling.children:
                return "Sobrino/a"
        
        # Bisabuelos - padres de mis abuelos
        if self.father and self.father.father:
            if (self.father.father.father == other_person or self.father.father.mother == other_person):
                return "Bisabuelo/a paterno/a"
        if self.father and self.father.mother:
            if (self.father.mother.father == other_person or self.father.mother.mother == other_person):
                return "Bisabuelo/a paterno/a"
        if self.mother and self.mother.father:
            if (self.mother.father.father == other_person or self.mother.father.mother == other_person):
                return "Bisabuelo/a materno/a"
        if self.mother and self.mother.mother:
            if (self.mother.mother.father == other_person or self.mother.mother.mother == other_person):
                return "Bisabuelo/a materno/a"
        
        # Bisnietos - hijos de mis nietos
        for child in self.children:
            for grandchild in child.children:
                if other_person in grandchild.children:
                    return "Bisnieto/a"
        
        # === CUARTO GRADO - PRIMOS, TÍOS ABUELOS, SOBRINOS NIETOS ===
        
        # Primos hermanos - hijos de mis tíos
        if self.father:
            for uncle in self.father.siblings:
                if other_person in uncle.children:
                    return "Primo/a hermano/a (paterno/a)"
        if self.mother:
            for uncle in self.mother.siblings:
                if other_person in uncle.children:
                    return "Primo/a hermano/a (materno/a)"
        
        # Tíos abuelos - hermanos de mis abuelos
        if self.father and self.father.father:
            for great_uncle in self.father.father.siblings:
                if great_uncle == other_person:
                    return "Tío/a abuelo/a paterno/a"
        if self.father and self.father.mother:
            for great_uncle in self.father.mother.siblings:
                if great_uncle == other_person:
                    return "Tío/a abuelo/a paterno/a"
        if self.mother and self.mother.father:
            for great_uncle in self.mother.father.siblings:
                if great_uncle == other_person:
                    return "Tío/a abuelo/a materno/a"
        if self.mother and self.mother.mother:
            for great_uncle in self.mother.mother.siblings:
                if great_uncle == other_person:
                    return "Tío/a abuelo/a materno/a"
        
        # Sobrinos nietos - nietos de mis hermanos
        for sibling in self.siblings:
            for nephew in sibling.children:
                if other_person in nephew.children:
                    return "Sobrino/a nieto/a"
        
        # === QUINTO GRADO - PRIMOS SEGUNDOS ===
        
        # Primos segundos - hijos de los primos de mis padres
        if self.father:
            for uncle in self.father.siblings:
                for cousin in uncle.children:
                    if other_person in cousin.children:
                        return "Primo/a segundo/a (paterno/a)"
        if self.mother:
            for uncle in self.mother.siblings:
                for cousin in uncle.children:
                    if other_person in cousin.children:
                        return "Primo/a segundo/a (materno/a)"
        
        # === RELACIONES POLÍTICAS (POR MATRIMONIO) ===
        
        if self.spouse:
            # Suegros
            if self.spouse.father == other_person:
                return "Suegro"
            if self.spouse.mother == other_person:
                return "Suegra"
            
            # Cuñados
            if other_person in self.spouse.siblings:
                return "Cuñado/a"
            
            # Yernos/Nueras
            for child in self.children:
                if child.spouse == other_person:
                    return "Yerno/Nuera"
        
        # Si llegamos aquí, no hay relación directa identificable
        return "Sin relación familiar directa"

    def get_extended_family(self, family: 'Family', max_generations: int = 3) -> list:
        """
        Obtiene la familia extendida de una persona
        
        Args:
            family (Family): La familia a la que pertenece
            max_generations (int): Máximo de generaciones a incluir
            
        Returns:
            list: Lista de personas en la familia extendida
        """
        extended_family = []
        visited = set()
        
        def explore_relations(person, generation):
            if generation > max_generations or person.cedula in visited:
                return
                
            visited.add(person.cedula)
            extended_family.append(person)
            
            # Explorar padres
            if person.father:
                explore_relations(person.father, generation + 1)
            if person.mother:
                explore_relations(person.mother, generation + 1)
                
            # Explorar hijos
            for child in person.children:
                explore_relations(child, generation + 1)
                
            # Explorar pareja
            if person.spouse:
                explore_relations(person.spouse, generation)
                
            # Explorar hermanos
            for sibling in person.siblings:
                if sibling.cedula not in visited:
                    explore_relations(sibling, generation)
                
        explore_relations(self, 1)
        return extended_family
    
    def get_family_tree(self, family: 'Family', max_generations: int = 3) -> dict:
        """
        Obtiene el árbol genealógico de la persona
        
        Args:
            family (Family): La familia a la que pertenece
            max_generations (int): Máximo de generaciones a incluir
            
        Returns:
            dict: Árbol genealógico en formato de diccionario
        """
        def build_tree(person, generation):
            if generation > max_generations:
                return None
                
            tree = {
                'person': {
                    'cedula': person.cedula,
                    'nombre': person.get_full_name(),
                    'edad': person.calculate_age(),
                    'edad_virtual': person.calculate_virtual_age(),
                    'vivo': person.alive,
                    'genero': person.gender,
                    'estado_civil': person.marital_status
                },
                'padres': [],
                'hijos': [],
                'pareja': None
            }
            
            # Agregar pareja
            if person.spouse:
                tree['pareja'] = {
                    'cedula': person.spouse.cedula,
                    'nombre': person.spouse.get_full_name(),
                    'genero': person.spouse.gender
                }
            
            # Agregar padres
            if person.father:
                tree['padres'].append({
                    'relacion': 'padre',
                    'nodo': build_tree(person.father, generation + 1)
                })
            if person.mother:
                tree['padres'].append({
                    'relacion': 'madre',
                    'nodo': build_tree(person.mother, generation + 1)
                })
                
            # Agregar hijos
            for child in person.children:
                tree['hijos'].append(build_tree(child, generation + 1))
                
            return tree
            
        return build_tree(self, 1)
    
    def get_timeline_events(self) -> list:
        """
        Obtiene los eventos en orden cronológico para la línea de tiempo
        
        Returns:
            list: Lista de eventos ordenados por fecha
        """
        timeline = []
        
        # Agregar nacimiento
        if self.birth_date:
            timeline.append({
                'fecha': self.birth_date,
                'evento': 'Nacimiento',
                'descripcion': f"Nació en {self.province}",
                'categoria': 'birth'
            })
            
        # Agregar eventos registrados
        for event in self.events:
            # Extraer la categoría del evento
            category = 'other'
            for cat, emoji in [('birth', '👶'), ('marriage', '💍'), ('divorce', '💔'), 
                              ('death', '⚰️'), ('childbirth', '👶'), ('graduation', '🎓'),
                              ('retirement', '🏖️'), ('widowhood', '🕯️')]:
                if emoji in event['evento']:
                    category = cat
                    break
            
            # Extraer el texto del evento
            event_text = event['evento'].replace('👶', '').replace('💍', '').replace('💔', '').replace('⚰️', '') \
                             .replace('🎓', '').replace('🏖️', '').replace('🕯️', '').strip()
            
            timeline.append({
                'fecha': event['fecha'],
                'evento': event_text,
                'categoria': category
            })
            
        # Agregar fallecimiento si aplica
        if not self.alive and self.death_date:
            timeline.append({
                'fecha': self.death_date,
                'evento': 'Fallecimiento',
                'categoria': 'death'
            })
            
        # Ordenar por fecha
        timeline.sort(key=lambda x: x['fecha'])
        return timeline
    
    def get_statistics(self) -> dict:
        """
        Obtiene estadísticas personales
        
        Returns:
            dict: Diccionario con estadísticas de la persona
        """
        return {
            'edad': self.calculate_age(),
            'edad_virtual': self.virtual_age,
            'estado_vital': 'Vivo' if self.alive else 'Fallecido',
            'num_hijos': len(self.children),
            'num_hermanos': len(self.siblings),
            'salud_emocional': self.emotional_health,
            'num_eventos': len(self.events),
            'intereses_principales': self.interests[:3],
            'estado_civil': self.marital_status,
            'provincia': self.province,
            'genero': 'Masculino' if self.gender == 'M' else 'Femenino'
        }
    
    def update_relationships(self, family: 'Family'):
        """
        Actualiza las relaciones familiares para mantener consistencia
        
        Args:
            family (Family): La familia a la que pertenece
        """
        # Actualizar lista de hermanos
        self.siblings = []
        if self.mother:
            for child in self.mother.children:
                if child != self and child not in self.siblings:
                    self.siblings.append(child)
        if self.father:
            for child in self.father.children:
                if child != self and child not in self.siblings:
                    self.siblings.append(child)
                    
        # Actualizar relación con pareja
        if self.spouse and self not in self.spouse.children:
            if self.gender == "M":
                if self.alive:
                    if self.spouse.alive:
                        self.marital_status = "Casado"
                    else:
                        self.marital_status = "Viudo"
                else:
                    self.marital_status = "Fallecido"
            else:
                if self.alive:
                    if self.spouse.alive:
                        self.marital_status = "Casada"
                    else:
                        self.marital_status = "Viuda"
                else:
                    self.marital_status = "Fallecida"
                
    def validate_integrity(self, family: 'Family') -> bool:
        """
        Valida la integridad de las relaciones familiares
        
        Args:
            family (Family): La familia a la que pertenece
            
        Returns:
            bool: True si la integridad es correcta, False en caso contrario
        """
        errores = []
        
        # Verificar coherencia de estado vital
        if self.alive and self.death_date:
            errores.append(f"{self.first_name} está vivo pero tiene fecha de fallecimiento")
        if not self.alive and not self.death_date:
            errores.append(f"{self.first_name} está fallecido pero no tiene fecha de fallecimiento")
            
        # Verificar estado civil
        if self.spouse and "Casado" not in self.marital_status and "Viudo" not in self.marital_status:
            errores.append(f"{self.first_name} tiene pareja pero estado civil es '{self.marital_status}'")
            
        # Verificar padres
        if self.father and self not in self.father.children:
            errores.append(f"{self.first_name} tiene padre pero no está en sus hijos")
        if self.mother and self not in self.mother.children:
            errores.append(f"{self.first_name} tiene madre pero no está en sus hijos")
            
        # Verificar hijos
        for child in self.children:
            if self.gender == "M" and child.father != self:
                errores.append(f"{self.first_name} tiene a {child.first_name} como hijo pero no es su padre")
            if self.gender == "F" and child.mother != self:
                errores.append(f"{self.first_name} tiene a {child.first_name} como hijo pero no es su madre")
                
        # Verificar pareja
        if self.spouse and self.spouse.spouse != self:
            errores.append(f"{self.first_name} tiene pareja pero no es recíproca")
            
        if errores:
            for error in errores:
                print(f"ERROR DE INTEGRIDAD: {error}")
            return False
            
        return True
    
    def to_dict(self) -> dict:
        """
        Convierte la persona a un diccionario serializable
        
        Returns:
            dict: Diccionario con los datos de la persona
        """
        return {
            'cedula': self.cedula,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'birth_date': self.birth_date,
            'death_date': self.death_date,
            'gender': self.gender,
            'province': self.province,
            'marital_status': self.marital_status,
            'alive': self.alive,
            'emotional_health': self.emotional_health,
            'interests': self.interests,
            'virtual_age': self.virtual_age,
            'father_cedula': self.father.cedula if self.father else None,
            'mother_cedula': self.mother.cedula if self.mother else None,
            'spouse_cedula': self.spouse.cedula if self.spouse else None,
            'children_cedulas': [child.cedula for child in self.children],
            'siblings_cedulas': [sibling.cedula for sibling in self.siblings],
            'events': self.events,
            'history': self.history
        }
    
    @classmethod
    def from_dict(cls, data: dict, family: 'Family') -> 'Person':
        """
        Crea una persona a partir de un diccionario
        
        Args:
            data (dict): Diccionario con los datos de la persona
            family (Family): La familia a la que pertenece
            
        Returns:
            Person: Nueva instancia de Person
        """
        person = cls(
            cedula=data['cedula'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            birth_date=data['birth_date'],
            gender=data['gender'],
            province=data['province'],
            death_date=data['death_date'],
            marital_status=data['marital_status']
        )
        
        # Restaurar atributos adicionales
        person.alive = data['alive']
        person.emotional_health = data['emotional_health']
        person.interests = data['interests']
        person.virtual_age = data['virtual_age']
        person.events = data['events']
        person.history = data['history']
        
        # Las relaciones se establecerán después al cargar toda la familia
        return person