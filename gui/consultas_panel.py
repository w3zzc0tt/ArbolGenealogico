# gui/consultas_panel.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from services.relacion_service import RelacionService

class ConsultasPanel:
    def __init__(self, parent, family):
        self.parent = parent
        self.family = family
        self.setup_ui()
    
    def setup_ui(self):
        self.frame = ctk.CTkFrame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ctk.CTkLabel(
            self.frame,
            text="🔍 Consultas Genealógicas",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=10)
        
        # Frame principal para dividir en dos columnas
        main_frame = ctk.CTkFrame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Columna izquierda - Selección de personas
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Columna derecha - Resultados
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Sección de selección de personas
        selection_frame = ctk.CTkFrame(left_frame)
        selection_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ctk.CTkLabel(selection_frame, text="Seleccionar Persona:", font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=5)
        
        # Lista de personas
        self.personas = [p for p in self.family.members]
        nombres_personas = [f"{p.first_name} {p.last_name} (Cédula: {p.cedula})" for p in self.personas]
        
        if nombres_personas:
            self.persona_var = ctk.StringVar(value=nombres_personas[0])
            self.persona_combo = ctk.CTkComboBox(
                selection_frame,
                values=nombres_personas,
                variable=self.persona_var,
                width=300
            )
            self.persona_combo.pack(padx=5, pady=5, fill=tk.X)
        else:
            ctk.CTkLabel(selection_frame, text="No hay personas en el árbol familiar", text_color="red").pack(padx=5, pady=5)
        
        # Sección para dos personas (para relación entre A y B)
        personas_frame = ctk.CTkFrame(left_frame)
        personas_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ctk.CTkLabel(personas_frame, text="Persona A:", font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=2)
        self.persona_a_var = ctk.StringVar(value=nombres_personas[0] if nombres_personas else "")
        self.persona_a_combo = ctk.CTkComboBox(
            personas_frame,
            values=nombres_personas,
            variable=self.persona_a_var,
            width=300
        )
        self.persona_a_combo.pack(padx=5, pady=2, fill=tk.X)
        
        ctk.CTkLabel(personas_frame, text="Persona B:", font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=2)
        self.persona_b_var = ctk.StringVar(value=nombres_personas[0] if nombres_personas else "")
        self.persona_b_combo = ctk.CTkComboBox(
            personas_frame,
            values=nombres_personas,
            variable=self.persona_b_var,
            width=300
        )
        self.persona_b_combo.pack(padx=5, pady=2, fill=tk.X)
        
        # Botón para ejecutar consulta
        btn_consultar = ctk.CTkButton(
            left_frame,
            text="🔍 Ejecutar Consulta",
            command=self.ejecutar_consulta,
            fg_color="#1db954",
            font=("Arial", 12, "bold")
        )
        btn_consultar.pack(pady=10, padx=5)
        
        # Área de resultados
        result_frame = ctk.CTkFrame(right_frame)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(result_frame, text="Resultados:", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=5)
        
        self.result_text = ctk.CTkTextbox(
            result_frame,
            font=("Consolas", 12),
            wrap=tk.WORD
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Historial de consultas
        history_frame = ctk.CTkFrame(right_frame)
        history_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ctk.CTkLabel(history_frame, text="Consultas disponibles:", font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=5)
        
        consultas = [
            "1. ¿Cuál es la relación entre persona A y persona B?",
            "2. ¿Quiénes son los primos de primer grado de X?",
            "3. ¿Cuáles son todos los antepasados maternos de X?",
            "4. ¿Cuáles descendientes de X están vivos actualmente?",
            "5. ¿Cuántas personas nacieron en los últimos 10 años?",
            "6. ¿Cuáles parejas actuales tienen 2 o más hijos en común?",
            "7. ¿Cuántas personas fallecieron antes de cumplir 50 años?"
        ]
        
        for consulta in consultas:
            ctk.CTkLabel(
                history_frame,
                text=consulta,
                font=("Arial", 10),
                wraplength=300,
                justify="left"
            ).pack(anchor="w", padx=10, pady=2)
    
    def ejecutar_consulta(self):
        """Ejecuta la consulta seleccionada"""
        if not self.personas:
            messagebox.showwarning("Advertencia", "No hay personas en el árbol familiar")
            return
        
        # Limpiar resultados anteriores
        self.result_text.delete("1.0", "end")
        
        # Obtener persona seleccionada
        persona_idx = self.persona_combo.get()
        persona = None
        for p in self.personas:
            if f"{p.first_name} {p.last_name} (Cédula: {p.cedula})" == persona_idx:
                persona = p
                break
        
        # Obtener personas A y B
        persona_a_idx = self.persona_a_combo.get()
        persona_b_idx = self.persona_b_combo.get()
        persona_a = None
        persona_b = None
        
        for p in self.personas:
            if f"{p.first_name} {p.last_name} (Cédula: {p.cedula})" == persona_a_idx:
                persona_a = p
            if f"{p.first_name} {p.last_name} (Cédula: {p.cedula})" == persona_b_idx:
                persona_b = p
        
        # Ejecutar todas las consultas
        self.result_text.insert("end", "📊 RESULTADOS DE CONSULTAS\n", "header")
        self.result_text.insert("end", "=" * 50 + "\n\n")
        
        # 1. Relación entre persona A y persona B
        if persona_a and persona_b:
            relacion = RelacionService.encontrar_relacion(persona_a, persona_b)
            self.result_text.insert("end", f"1. Relación entre {persona_a.first_name} y {persona_b.first_name}:\n")
            self.result_text.insert("end", f"   {relacion}\n\n")
        
        # 2. Primos de primer grado de X
        if persona:
            primos = RelacionService.obtener_primos_primer_grado(persona)
            self.result_text.insert("end", f"2. Primos de primer grado de {persona.first_name}:\n")
            if primos:
                for primo in primos:
                    self.result_text.insert("end", f"   • {primo.first_name} {primo.last_name}\n")
            else:
                self.result_text.insert("end", "   No tiene primos de primer grado\n")
            self.result_text.insert("end", "\n")
        
        # 3. Antepasados maternos de X
        if persona:
            antepasados = RelacionService.obtener_antepasados_maternos(persona)
            self.result_text.insert("end", f"3. Antepasados maternos de {persona.first_name}:\n")
            if antepasados:
                for ancestro in antepasados:
                    self.result_text.insert("end", f"   • {ancestro.first_name} {ancestro.last_name} ({ancestro.gender})\n")
            else:
                self.result_text.insert("end", "   No tiene antepasados maternos registrados\n")
            self.result_text.insert("end", "\n")
        
        # 4. Descendientes vivos de X
        if persona:
            descendientes = RelacionService.obtener_descendientes_vivos(persona)
            self.result_text.insert("end", f"4. Descendientes vivos de {persona.first_name}:\n")
            if descendientes:
                for desc in descendientes:
                    self.result_text.insert("end", f"   • {desc.first_name} {desc.last_name} ({desc.calculate_age()} años)\n")
            else:
                self.result_text.insert("end", "   No tiene descendientes vivos\n")
            self.result_text.insert("end", "\n")
        
        # 5. Personas nacidas en los últimos 10 años
        nacimientos = RelacionService.obtener_nacimientos_ultimos_10_años(self.family)
        self.result_text.insert("end", f"5. Personas nacidas en los últimos 10 años:\n")
        self.result_text.insert("end", f"   {nacimientos} personas\n\n")
        
        # 6. Parejas con 2 o más hijos en común
        parejas = RelacionService.obtener_parejas_con_hijos(self.family, min_hijos=2)
        self.result_text.insert("end", f"6. Parejas con 2 o más hijos en común:\n")
        if parejas:
            for pareja in parejas:
                comunes = len(set(pareja[0].children) & set(pareja[1].children))
                self.result_text.insert("end", f"   • {pareja[0].first_name} y {pareja[1].first_name}: {comunes} hijos en común\n")
        else:
            self.result_text.insert("end", "   No hay parejas con 2 o más hijos en común\n")
        self.result_text.insert("end", "\n")
        
        # 7. Personas fallecidas antes de los 50 años
        fallecidos = RelacionService.obtener_fallecidos_antes_50(self.family)
        self.result_text.insert("end", f"7. Personas fallecidas antes de cumplir 50 años:\n")
        self.result_text.insert("end", f"   {fallecidos} personas\n\n")
        
        # Configurar estilos
        self.result_text.tag_configure("header", font=("Arial", 14, "bold"))
        
        # Hacer el texto no editable
        self.result_text.configure(state="disabled")