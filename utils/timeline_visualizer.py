#utils/timeline_visualizer.py

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

class TimelineVisualizer:
    """Visualizador de línea de tiempo para personas"""
    
    @staticmethod
    def create_timeline_window(person):
        """Crea ventana con línea de tiempo de una persona"""
        timeline_window = ctk.CTkToplevel()
        timeline_window.title(f"Línea de Tiempo - {person.first_name} {person.last_name}")
        timeline_window.geometry("800x600")
        
        # Frame principal con scroll
        main_frame = ctk.CTkScrollableFrame(timeline_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame, 
            text=f"🕰️ Línea de Tiempo de {person.first_name} {person.last_name}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Obtener eventos de la timeline
        timeline_events = person.get_timeline_events()
        
        if not timeline_events:
            no_events_label = ctk.CTkLabel(
                main_frame,
                text="No hay eventos registrados",
                font=ctk.CTkFont(size=14)
            )
            no_events_label.pack(pady=20)
            return
        
        # Crear línea de tiempo visual
        for i, event in enumerate(timeline_events):
            # Frame para cada evento
            event_frame = ctk.CTkFrame(main_frame)
            event_frame.pack(fill=tk.X, pady=5, padx=10)
            
            # Información del evento - usar estructura actual de los eventos
            date_label = ctk.CTkLabel(
                event_frame,
                text=f"{event['fecha']}",
                font=ctk.CTkFont(size=16, weight="bold"),
                width=120
            )
            date_label.pack(side=tk.LEFT, padx=10, pady=10)
            
            # Calcular edad en el evento
            try:
                from datetime import datetime
                birth_year = int(person.birth_date.split('-')[0])
                event_year = int(event['fecha'].split('-')[0])
                age_at_event = event_year - birth_year
                
                age_label = ctk.CTkLabel(
                    event_frame,
                    text=f"({age_at_event} años)",
                    font=ctk.CTkFont(size=12),
                    width=80
                )
                age_label.pack(side=tk.LEFT, padx=5, pady=10)
            except:
                # Si no se puede calcular la edad, continuar sin mostrarla
                pass
            
            # Evento - usar emoji según categoría
            category_emojis = {
                'birth': '👶',
                'marriage': '💍',
                'divorce': '💔',
                'death': '⚰️',
                'childbirth': '🍼',
                'widowhood': '🕯️',
                'graduation': '🎓',
                'retirement': '🏖️',
                'other': '📝'
            }
            
            category = event.get('categoria', 'other')
            emoji = category_emojis.get(category, '📝')
            
            # Frame para el contenido del evento
            content_frame = ctk.CTkFrame(event_frame)
            content_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
            
            # Evento principal
            event_label = ctk.CTkLabel(
                content_frame,
                text=f"{emoji} {event['evento']}",
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            event_label.pack(anchor="w", padx=5, pady=(5, 2))
            
            # Descripción adicional si existe
            if event.get('descripcion'):
                desc_label = ctk.CTkLabel(
                    content_frame,
                    text=event['descripcion'],
                    font=ctk.CTkFont(size=11),
                    anchor="w",
                    text_color="gray"
                )
                desc_label.pack(anchor="w", padx=5, pady=(0, 5))
            
            # Color según tipo de evento
            colors = {
                'birth': '#4CAF50',
                'marriage': '#FF6B9D', 
                'divorce': '#FF5722',
                'death': '#424242',
                'childbirth': '#81C784',
                'widowhood': '#616161',
                'graduation': '#3F51B5',
                'retirement': '#FF9800',
                'other': '#9E9E9E'
            }
            
            color = colors.get(category, '#E0E0E0')
            event_frame.configure(border_color=color, border_width=2)