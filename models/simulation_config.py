class SimulationConfig:
    """Configuración para la simulación"""
    def __init__(self):
        self.real_time_per_year = 0.5  # segundos reales por año de simulación
        self.events_interval = 1  # años entre eventos
        self.birth_probability = 0.45  # 45% de probabilidad de nacimiento (aumentado)
        self.death_probability_base = 0.003  # probabilidad base de fallecimiento (aumentado)
        self.find_partner_probability = 0.15  # 15% de probabilidad de encontrar pareja (aumentado)
        self.compatibility_threshold = 60  # umbral de compatibilidad para pareja (%)