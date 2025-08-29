class SimulationConfig:
    def __init__(self):
        # Tiempos - ESPECIFICACIÓN: 10 segundos por ciclo
        self.birthday_interval = 10  # segundos reales = 1 año simulado
        self.events_interval = 10    # 10 SEGUNDOS POR CICLO según especificación
        
        # Probabilidades balanceadas
        self.birth_probability = 0.25  # 25% por ciclo para parejas compatibles
        self.death_probability_base = 0.002  # Base muy baja
        self.find_partner_probability = 0.08  # 8% por ciclo para solteros elegibles
        self.remarriage_probability = 0.05  # 5% para viudos
        
        # Umbrales
        self.compatibility_threshold = 70  # 70% mínimo para unión
        self.emotional_health_threshold = 30  # Bajo este nivel, riesgo aumenta
        
        # Edades críticas
        self.min_marriage_age = 18
        self.max_female_fertility = 45
        self.max_male_fertility = 65