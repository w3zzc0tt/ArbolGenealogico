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
        
        # Obtener eventos
        timeline = person.get_life_timeline()
        
        if not timeline:
            no_events_label = ctk.CTkLabel(
                main_frame,
                text="No hay eventos registrados",
                font=ctk.CTkFont(size=14)
            )
            no_events_label.pack(pady=20)
            return
        
        # Crear línea de tiempo visual
        for i, event in enumerate(timeline):
            # Frame para cada evento
            event_frame = ctk.CTkFrame(main_frame)
            event_frame.pack(fill=tk.X, pady=5, padx=10)
            
            # Información del evento
            year_label = ctk.CTkLabel(
                event_frame,
                text=f"{event['year']}",
                font=ctk.CTkFont(size=16, weight="bold"),
                width=80
            )
            year_label.pack(side=tk.LEFT, padx=10, pady=10)
            
            age_label = ctk.CTkLabel(
                event_frame,
                text=f"({event['age']} años)",
                font=ctk.CTkFont(size=12),
                width=80
            )
            age_label.pack(side=tk.LEFT, padx=5, pady=10)
            
            event_label = ctk.CTkLabel(
                event_frame,
                text=f"{event['icon']} {event['event']}",
                font=ctk.CTkFont(size=14),
                anchor="w"
            )
            event_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
            
            # Color según tipo de evento
            colors = {
                'birth': '#4CAF50',
                'marriage': '#FF6B9D',
                'childbirth': '#87CEEB',
                'widowhood': '#696969',
                'birthday': '#FFD700',
                'general': '#E0E0E0'
            }
            
            color = colors.get(event['type'], '#E0E0E0')
            event_frame.configure(border_color=color, border_width=2)