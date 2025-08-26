import datetime
import random

class Person:
    def __init__(self, cedula, first_name, last_name, birth_date, gender, province, death_date=None, marital_status="Soltero/a"):
        # === MODIFICACIÓN CLAVE AQUÍ ===
        # Convertir "Masculino"/"Femenino" a "M"/"F" para mantener consistencia
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

    def set_death_date(self, death_date: str):
        """Establece la fecha de defunción y actualiza estado"""
        self.death_date = death_date
        self.alive = False
        self.add_event("Fallecimiento", death_date)

    def set_alive(self):
        """Establece que la persona está viva"""
        self.death_date = None
        self.alive = True
        self.add_event("Regreso a la vida")

        # Atributos para simulación
        self.emotional_health = 100
        self.interests = self.generate_interests()

    def generate_interests(self):
        all_interests = ["Deportes", "Lectura", "Música", "Arte", "Tecnología", "Cocina", "Viajes", "Naturaleza"]
        return random.sample(all_interests, 3)

    def add_event(self, event_type, date=None):
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.history.append(f"{event_type} ({date})")
        self.history.sort(key=lambda x: x.split('(')[1].rstrip(')') if '(' in x else "")

    def calculate_age(self):
        try:
            birth = datetime.datetime.strptime(self.birth_date, "%Y-%m-%d")
            today = datetime.datetime.now()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            return age
        except:
            return 0

    def get_full_name(self) -> str:
        """Obtiene el nombre completo de la persona"""
        return f"{self.first_name} {self.last_name}"

    def can_have_children(self) -> bool:
        """Determina si la persona puede tener hijos"""
        if not self.alive:
            return False
        if self.gender == "F":
            age = self.calculate_age()
            return 18 <= age <= 45
        else:
            age = self.calculate_age()
            return 18 <= age <= 65

    def has_partner(self) -> bool:
        """Verifica si la persona tiene pareja"""
        # ✅ CORRECCIÓN: Verificar tanto spouse como estado civil
        if self.spouse and self.spouse.alive and self.spouse.spouse == self:
            return True
        # Si el estado civil indica que está casado/a pero no hay spouse, corregir
        if "Casado" in self.marital_status and not self.spouse:
            self.marital_status = "Soltero/a"
        return False

    def is_married_to(self, other_person: 'Person') -> bool:
        """Verifica si esta persona está casada con otra persona específica"""
        return self.has_partner() and self.spouse == other_person

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.cedula})"
    
    def add_history(self, event: str):
        """Agrega un evento manual al historial"""
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")
        self.history.append(f"{event} ({date})")

    def add_major_life_event(self, event_type: str, details: str = "", date: str = None):
        """Agrega un evento mayor de la vida con categorización"""
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Categorías de eventos
        event_categories = {
            'birth': '👶',
            'marriage': '💍',
            'divorce': '💔',
            'widowhood': '🖤',
            'childbirth': '🍼',
            'death': '⚱️',
            'education': '🎓',
            'career': '💼',
            'health': '🏥',
            'travel': '✈️',
            'achievement': '🏆'
        }
        
        icon = event_categories.get(event_type, '📅')
        formatted_event = f"{icon} {details} ({date})"
        
        # Agregar al historial manteniendo orden cronológico
        self.history.append(formatted_event)
        self.history.sort(key=lambda x: self._extract_date(x))
        
        # Mantener eventos categorizados
        if not hasattr(self, 'life_events'):
            self.life_events = {}
        
        if event_type not in self.life_events:
            self.life_events[event_type] = []
        
        self.life_events[event_type].append({
            'date': date,
            'details': details,
            'age': getattr(self, 'virtual_age', self.calculate_age())
        })

    def get_life_timeline(self) -> list:
        """Obtiene línea de tiempo organizada de eventos importantes"""
        timeline = []
        
        # Evento de nacimiento
        if self.birth_date:
            timeline.append({
                'year': int(self.birth_date[:4]),
                'age': 0,
                'event': 'Nacimiento',
                'type': 'birth',
                'icon': '👶'
            })
        
        # Procesar eventos del historial
        for event in self.history:
            date_match = re.search(r'\((\d{4}-\d{2}-\d{2})\)', event)
            if date_match:
                date_str = date_match.group(1)
                year = int(date_str[:4])
                age = year - int(self.birth_date[:4]) if self.birth_date else 0
                
                # Categorizar evento
                if '💍' in event or 'matrimonio' in event.lower() or 'pareja' in event.lower():
                    event_type = 'marriage'
                    icon = '💍'
                elif '👶' in event or 'nacimiento' in event.lower() or 'nació' in event.lower():
                    event_type = 'childbirth'
                    icon = '👶'
                elif '💔' in event or 'viud' in event.lower() or 'fallecimiento' in event.lower():
                    event_type = 'widowhood'
                    icon = '💔'
                elif '🎂' in event or 'cumpleaños' in event.lower():
                    event_type = 'birthday'
                    icon = '🎂'
                else:
                    event_type = 'general'
                    icon = '📅'
                
                timeline.append({
                    'year': year,
                    'age': age,
                    'event': event.replace(f'({date_str})', '').strip(),
                    'type': event_type,
                    'icon': icon
                })
        
        # Ordenar cronológicamente
        timeline.sort(key=lambda x: x['year'])
        return timeline

    def _extract_date(self, event_string: str) -> str:
        """Extrae fecha de un string de evento para ordenamiento"""
        date_match = re.search(r'\((\d{4}-\d{2}-\d{2})\)', event_string)
        return date_match.group(1) if date_match else "9999-12-31"
    
    
