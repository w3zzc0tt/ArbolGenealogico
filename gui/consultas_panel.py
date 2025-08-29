# gui/consultas_panel.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from services.relacion_service import RelacionService
from utils.gedcom_parser import GedcomParser
import os

class ConsultasPanel:
    def __init__(self, parent, family):
        self.parent = parent
        self.family = family
        self.consulta_actual = ctk.StringVar(value="1")
        self.setup_ui()
    
    def setup_ui(self):
        self.frame = ctk.CTkFrame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header con título y acciones principales
        self.setup_header()
        
        # Contenido principal en dos columnas
        self.setup_main_content()
        
    def setup_header(self):
        """Configura el encabezado con título y botones principales"""
        header_frame = ctk.CTkFrame(self.frame, height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        # Título principal
        title_label = ctk.CTkLabel(
            header_frame,
            text="🔍 Panel de Consultas Genealógicas",
            font=("Arial", 20, "bold"),
            text_color="#1e88e5"
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Botones de acción en el header
        buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        buttons_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        btn_importar = ctk.CTkButton(
            buttons_frame,
            text="📥 Importar Ejemplo",
            command=self.importar_ejemplo,
            fg_color="#4CAF50",
            hover_color="#45a049",
            font=("Arial", 12, "bold"),
            width=140,
            height=35
        )
        btn_importar.pack(side=tk.TOP, pady=2)
        
        btn_cargar = ctk.CTkButton(
            buttons_frame,
            text="📁 Cargar GEDCOM",
            command=self.cargar_archivo,
            fg_color="#FF9800",
            hover_color="#f57c00",
            font=("Arial", 12, "bold"),
            width=140,
            height=35
        )
        btn_cargar.pack(side=tk.TOP, pady=2)
    
    def setup_main_content(self):
        """Configura el contenido principal en dos columnas"""
        main_frame = ctk.CTkFrame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Columna izquierda - Panel de control
        left_frame = ctk.CTkFrame(main_frame, width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_frame.pack_propagate(False)
        
        # Columna derecha - Resultados
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.setup_control_panel(left_frame)
        self.setup_results_panel(right_frame)
    
    def setup_control_panel(self, parent):
        """Configura el panel de control izquierdo"""
        # Título del panel de control
        control_title = ctk.CTkLabel(
            parent,
            text="⚙️ Panel de Control",
            font=("Arial", 16, "bold"),
            text_color="#1976d2"
        )
        control_title.pack(pady=10)
        
        # Estado del árbol familiar
        self.setup_family_status(parent)
        
        # Selector de tipo de consulta
        self.setup_query_selector(parent)
        
        # Selector de personas
        self.setup_person_selector(parent)
        
        # Botón de ejecución
        self.setup_execution_button(parent)
    
    def setup_family_status(self, parent):
        """Muestra el estado actual del árbol familiar"""
        status_frame = ctk.CTkFrame(parent)
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkLabel(
            status_frame,
            text="📊 Estado del Árbol Familiar",
            font=("Arial", 12, "bold")
        ).pack(pady=5)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text=self.get_family_status(),
            font=("Arial", 10),
            wraplength=350,
            justify="left"
        )
        self.status_label.pack(padx=10, pady=5)
    
    def setup_query_selector(self, parent):
        """Configura el selector de tipo de consulta"""
        query_frame = ctk.CTkFrame(parent)
        query_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkLabel(
            query_frame,
            text="🔍 Tipo de Consulta",
            font=("Arial", 12, "bold")
        ).pack(pady=5)
        
        # Radio buttons para cada tipo de consulta
        consultas = [
            ("1", "Relación entre dos personas"),
            ("2", "Primos de primer grado"),
            ("3", "Antepasados maternos"),
            ("4", "Descendientes vivos"),
            ("5", "Nacimientos últimos 10 años"),
            ("6", "Parejas con múltiples hijos"),
            ("7", "Fallecidos antes de 50 años"),
            ("all", "Ejecutar todas las consultas")
        ]
        
        for value, text in consultas:
            radio = ctk.CTkRadioButton(
                query_frame,
                text=text,
                variable=self.consulta_actual,
                value=value,
                font=("Arial", 10),
                command=self.on_query_type_change
            )
            radio.pack(anchor="w", padx=15, pady=2)
    
    def setup_person_selector(self, parent):
        """Configura los selectores de personas"""
        person_frame = ctk.CTkFrame(parent)
        person_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkLabel(
            person_frame,
            text="👥 Selección de Personas",
            font=("Arial", 12, "bold")
        ).pack(pady=5)
        
        # Actualizar lista de personas
        self.actualizar_lista_personas()
        
        # Persona principal (para consultas 2, 3, 4)
        self.persona_label = ctk.CTkLabel(
            person_frame,
            text="Persona principal:",
            font=("Arial", 10, "bold")
        )
        self.persona_label.pack(anchor="w", padx=10, pady=(10, 2))
        
        self.persona_var = ctk.StringVar()
        self.persona_combo = ctk.CTkComboBox(
            person_frame,
            variable=self.persona_var,
            width=350,
            font=("Arial", 10)
        )
        self.persona_combo.pack(padx=10, pady=2)
        
        # Persona A (para consulta 1 - relación entre dos personas)
        self.persona_a_label = ctk.CTkLabel(
            person_frame,
            text="Primera persona:",
            font=("Arial", 10, "bold")
        )
        self.persona_a_label.pack(anchor="w", padx=10, pady=(10, 2))
        
        self.persona_a_var = ctk.StringVar()
        self.persona_a_combo = ctk.CTkComboBox(
            person_frame,
            variable=self.persona_a_var,
            width=350,
            font=("Arial", 10)
        )
        self.persona_a_combo.pack(padx=10, pady=2)
        
        # Persona B (para consulta 1 - relación entre dos personas)
        self.persona_b_label = ctk.CTkLabel(
            person_frame,
            text="Segunda persona:",
            font=("Arial", 10, "bold")
        )
        self.persona_b_label.pack(anchor="w", padx=10, pady=(10, 2))
        
        self.persona_b_var = ctk.StringVar()
        self.persona_b_combo = ctk.CTkComboBox(
            person_frame,
            variable=self.persona_b_var,
            width=350,
            font=("Arial", 10)
        )
        self.persona_b_combo.pack(padx=10, pady=(2, 10))
        
        # Inicialmente mostrar/ocultar controles según el tipo de consulta
        self.on_query_type_change()
    
    def setup_execution_button(self, parent):
        """Configura el botón de ejecución"""
        btn_ejecutar = ctk.CTkButton(
            parent,
            text="� Ejecutar Consulta",
            command=self.ejecutar_consulta,
            fg_color="#1976d2",
            hover_color="#1565c0",
            font=("Arial", 14, "bold"),
            height=40,
            width=200
        )
        btn_ejecutar.pack(pady=20)
    
    def setup_results_panel(self, parent):
        """Configura el panel de resultados"""
        # Título del panel de resultados
        results_title = ctk.CTkLabel(
            parent,
            text="📈 Resultados de Consultas",
            font=("Arial", 16, "bold"),
            text_color="#1976d2"
        )
        results_title.pack(pady=10)
        
        # Área de resultados con scroll
        results_frame = ctk.CTkFrame(parent)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.result_text = ctk.CTkTextbox(
            results_frame,
            font=("Consolas", 11),
            wrap=tk.WORD
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel de información de ayuda
        help_frame = ctk.CTkFrame(parent, height=120)
        help_frame.pack(fill=tk.X, padx=10, pady=5)
        help_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            help_frame,
            text="💡 Ayuda",
            font=("Arial", 12, "bold")
        ).pack(pady=5)
        
        help_text = (
            "1. Importa un ejemplo o carga un archivo GEDCOM\n"
            "2. Selecciona el tipo de consulta que deseas ejecutar\n"
            "3. Selecciona las personas necesarias según el tipo\n"
            "4. Haz clic en 'Ejecutar Consulta' para ver resultados"
        )
        
        ctk.CTkLabel(
            help_frame,
            text=help_text,
            font=("Arial", 9),
            justify="left"
        ).pack(padx=10, pady=5)
    
    def on_query_type_change(self):
        """Maneja el cambio de tipo de consulta"""
        query_type = self.consulta_actual.get()
        
        # Ocultar todos los controles inicialmente
        if hasattr(self, 'persona_label'):
            self.persona_label.pack_forget()
        if hasattr(self, 'persona_combo'):
            self.persona_combo.pack_forget()
        if hasattr(self, 'persona_a_label'):
            self.persona_a_label.pack_forget()
        if hasattr(self, 'persona_a_combo'):
            self.persona_a_combo.pack_forget()
        if hasattr(self, 'persona_b_label'):
            self.persona_b_label.pack_forget()
        if hasattr(self, 'persona_b_combo'):
            self.persona_b_combo.pack_forget()
        
        # Mostrar controles según el tipo de consulta
        if query_type == "1":  # Relación entre dos personas
            if hasattr(self, 'persona_a_label'):
                self.persona_a_label.pack(anchor="w", padx=10, pady=(10, 2))
            if hasattr(self, 'persona_a_combo'):
                self.persona_a_combo.pack(padx=10, pady=2)
            if hasattr(self, 'persona_b_label'):
                self.persona_b_label.pack(anchor="w", padx=10, pady=(10, 2))
            if hasattr(self, 'persona_b_combo'):
                self.persona_b_combo.pack(padx=10, pady=(2, 10))
        elif query_type in ["2", "3", "4"]:  # Consultas que requieren una persona
            if hasattr(self, 'persona_label'):
                self.persona_label.pack(anchor="w", padx=10, pady=(10, 2))
            if hasattr(self, 'persona_combo'):
                self.persona_combo.pack(padx=10, pady=(2, 10))
    
    def get_family_status(self):
        """Obtiene el estado actual del árbol familiar"""
        if not self.family.members:
            return "❌ No hay personas cargadas.\nUsa 'Importar Ejemplo' para comenzar."
        
        vivos = sum(1 for p in self.family.members if p.alive)
        fallecidos = len(self.family.members) - vivos
        
        return f"✅ Familia cargada: {self.family.name}\n👥 Total: {len(self.family.members)} personas\n💚 Vivos: {vivos} | ⚰️ Fallecidos: {fallecidos}"
    
    def actualizar_lista_personas(self):
        """Actualiza las listas de personas en los comboboxes"""
        self.personas = [p for p in self.family.members]
        nombres_personas = [f"{p.first_name} {p.last_name} (Cédula: {p.cedula})" for p in self.personas]
        
        print(f"DEBUG: Actualizando lista de personas. Total: {len(self.personas)}")
        for i, p in enumerate(self.personas):
            print(f"  {i+1}. {p.first_name} {p.last_name} (ID: {p.cedula})")
        
        if nombres_personas:
            print(f"DEBUG: Configurando comboboxes con {len(nombres_personas)} personas")
            # Actualizar valores de los comboboxes
            if hasattr(self, 'persona_combo'):
                self.persona_combo.configure(values=nombres_personas)
                self.persona_var.set(nombres_personas[0])
                # Forzar actualización visual múltiple
                self.persona_combo.update_idletasks()
                self.persona_combo.update()
                print(f"DEBUG: persona_combo configurado con: {nombres_personas[0]}")
            
            if hasattr(self, 'persona_a_combo'):
                self.persona_a_combo.configure(values=nombres_personas)
                self.persona_a_var.set(nombres_personas[0])
                # Forzar actualización visual múltiple
                self.persona_a_combo.update_idletasks()
                self.persona_a_combo.update()
                print(f"DEBUG: persona_a_combo configurado con: {nombres_personas[0]}")
            
            if hasattr(self, 'persona_b_combo'):
                self.persona_b_combo.configure(values=nombres_personas)
                if len(nombres_personas) > 1:
                    self.persona_b_var.set(nombres_personas[1])
                    print(f"DEBUG: persona_b_combo configurado con: {nombres_personas[1]}")
                else:
                    self.persona_b_var.set(nombres_personas[0])
                    print(f"DEBUG: persona_b_combo configurado con: {nombres_personas[0]}")
                # Forzar actualización visual múltiple
                self.persona_b_combo.update_idletasks()
                self.persona_b_combo.update()
            
            # Forzar actualización del panel completo
            self.update_idletasks()
            self.update()
        else:
            print("DEBUG: No hay personas, limpiando comboboxes")
            # No hay personas, limpiar comboboxes
            valores_vacios = ["No hay personas en el árbol"]
            if hasattr(self, 'persona_combo'):
                self.persona_combo.configure(values=valores_vacios)
                self.persona_var.set(valores_vacios[0])
            if hasattr(self, 'persona_a_combo'):
                self.persona_a_combo.configure(values=valores_vacios)
                self.persona_a_var.set(valores_vacios[0])
            if hasattr(self, 'persona_b_combo'):
                self.persona_b_combo.configure(values=valores_vacios)
                self.persona_b_var.set(valores_vacios[0])
        
        # Actualizar estado del árbol familiar
        if hasattr(self, 'status_label'):
            self.status_label.configure(text=self.get_family_status())
            self.status_label.update()
            print(f"DEBUG: Estado actualizado: {self.get_family_status()}")
    
    def importar_ejemplo(self):
        """Importa el archivo de ejemplo predefinido"""
        try:
            ejemplo_path = os.path.join("simulations", "ejemplo.ged")
            
            if not os.path.exists(ejemplo_path):
                messagebox.showerror("Error", f"No se encontró el archivo de ejemplo en: {ejemplo_path}")
                return
            
            # Leer archivo GEDCOM
            with open(ejemplo_path, "r", encoding="utf-8") as f:
                gedcom_content = f.read()
            
            # Limpiar familia actual
            self.family.members.clear()
            self.family.name = "Familia de Ejemplo"
            self.family.description = "Árbol familiar de ejemplo cargado desde archivo GEDCOM"
            
            # Parsear GEDCOM
            self.family = GedcomParser.parse(self.family, gedcom_content)
            
            # Actualizar interfaz con retraso para asegurar que el parseo esté completo
            self.parent.after(100, self.actualizar_lista_personas)
            
            # Mostrar mensaje de éxito en el área de resultados
            self.result_text.delete("1.0", "end")
            self.result_text.insert("end", "✅ ARCHIVO DE EJEMPLO CARGADO EXITOSAMENTE\n\n")
            self.result_text.insert("end", f"📊 Familia: {self.family.name}\n")
            self.result_text.insert("end", f"👥 Total de miembros: {len(self.family.members)}\n\n")
            self.result_text.insert("end", "📋 Miembros cargados:\n")
            
            for i, persona in enumerate(self.family.members, 1):
                estado = "💚 Vivo" if persona.alive else "⚰️ Fallecido"
                edad = f" ({persona.calculate_age()} años)" if persona.alive else ""
                self.result_text.insert("end", f"{i:2d}. {persona.first_name} {persona.last_name} - {estado}{edad}\n")
            
            self.result_text.insert("end", "\n🎯 ¡Ahora puedes ejecutar consultas sobre esta familia!")
            
            messagebox.showinfo("Éxito", f"Archivo de ejemplo cargado exitosamente.\nSe cargaron {len(self.family.members)} personas.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar archivo de ejemplo: {str(e)}")
            self.result_text.delete("1.0", "end")
            self.result_text.insert("end", f"❌ ERROR AL CARGAR EJEMPLO\n\n{str(e)}")
    
    def cargar_archivo(self):
        """Permite al usuario cargar un archivo GEDCOM personalizado"""
        try:
            file_path = filedialog.askopenfilename(
                title="Seleccionar archivo GEDCOM",
                filetypes=[("Archivos GEDCOM", "*.ged"), ("Todos los archivos", "*.*")]
            )
            
            if not file_path:
                return
            
            # Leer archivo GEDCOM
            with open(file_path, "r", encoding="utf-8") as f:
                gedcom_content = f.read()
            
            # Limpiar familia actual
            self.family.members.clear()
            self.family.name = f"Familia desde {os.path.basename(file_path)}"
            self.family.description = f"Árbol familiar cargado desde: {file_path}"
            
            # Parsear GEDCOM
            self.family = GedcomParser.parse(self.family, gedcom_content)
            
            # Actualizar interfaz con retraso para asegurar que el parseo esté completo
            self.parent.after(100, self.actualizar_lista_personas)
            
            # Mostrar mensaje de éxito
            self.result_text.delete("1.0", "end")
            self.result_text.insert("end", "✅ ARCHIVO GEDCOM CARGADO EXITOSAMENTE\n\n")
            self.result_text.insert("end", f"📁 Archivo: {os.path.basename(file_path)}\n")
            self.result_text.insert("end", f"👥 Total de miembros: {len(self.family.members)}\n\n")
            
            messagebox.showinfo("Éxito", f"Archivo cargado exitosamente.\nSe cargaron {len(self.family.members)} personas.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar archivo: {str(e)}")
            self.result_text.delete("1.0", "end")
            self.result_text.insert("end", f"❌ ERROR AL CARGAR ARCHIVO\n\n{str(e)}")
    
    def ejecutar_consulta(self):
        """Ejecuta la consulta seleccionada"""
        if not self.personas:
            messagebox.showwarning("Advertencia", "No hay personas en el árbol familiar. Importa un ejemplo o carga un archivo GEDCOM.")
            return
        
        # Limpiar resultados anteriores
        self.result_text.delete("1.0", "end")
        
        query_type = self.consulta_actual.get()
        
        # Ejecutar consulta específica o todas
        if query_type == "all":
            self.ejecutar_todas_consultas()
        else:
            self.ejecutar_consulta_especifica(query_type)
    
    def ejecutar_consulta_especifica(self, query_type):
        """Ejecuta una consulta específica"""
        self.result_text.insert("end", f"🔍 RESULTADO DE CONSULTA {query_type}\n")
        self.result_text.insert("end", "=" * 50 + "\n\n")
        
        try:
            if query_type == "1":
                self.ejecutar_consulta_relacion()
            elif query_type == "2":
                self.ejecutar_consulta_primos()
            elif query_type == "3":
                self.ejecutar_consulta_antepasados_maternos()
            elif query_type == "4":
                self.ejecutar_consulta_descendientes_vivos()
            elif query_type == "5":
                self.ejecutar_consulta_nacimientos_recientes()
            elif query_type == "6":
                self.ejecutar_consulta_parejas_con_hijos()
            elif query_type == "7":
                self.ejecutar_consulta_fallecidos_joven()
        
        except Exception as e:
            self.result_text.insert("end", f"❌ Error al ejecutar consulta: {str(e)}")
    
    def ejecutar_consulta_relacion(self):
        """Ejecuta consulta de relación entre dos personas"""
        persona_a = self.obtener_persona_por_combo(self.persona_a_var.get())
        persona_b = self.obtener_persona_por_combo(self.persona_b_var.get())
        
        if not persona_a or not persona_b:
            self.result_text.insert("end", "❌ Error: Selecciona ambas personas válidas\n")
            return
        
        relacion = RelacionService.encontrar_relacion(persona_a, persona_b)
        self.result_text.insert("end", f"👥 Relación entre {persona_a.first_name} y {persona_b.first_name}:\n")
        self.result_text.insert("end", f"   📍 {relacion}\n\n")
    
    def ejecutar_consulta_primos(self):
        """Ejecuta consulta de primos de primer grado"""
        persona = self.obtener_persona_por_combo(self.persona_var.get())
        if not persona:
            self.result_text.insert("end", "❌ Error: Selecciona una persona válida\n")
            return
        
        primos = RelacionService.obtener_primos_primer_grado(persona)
        self.result_text.insert("end", f"👫 Primos de primer grado de {persona.first_name}:\n")
        if primos:
            for primo in primos:
                self.result_text.insert("end", f"   • {primo.first_name} {primo.last_name}\n")
        else:
            self.result_text.insert("end", "   📭 No tiene primos de primer grado\n")
        self.result_text.insert("end", "\n")
    
    def ejecutar_consulta_antepasados_maternos(self):
        """Ejecuta consulta de antepasados maternos"""
        persona = self.obtener_persona_por_combo(self.persona_var.get())
        if not persona:
            self.result_text.insert("end", "❌ Error: Selecciona una persona válida\n")
            return
        
        antepasados = RelacionService.obtener_antepasados_maternos(persona)
        self.result_text.insert("end", f"👩‍👧‍👦 Antepasados maternos de {persona.first_name}:\n")
        if antepasados:
            for ancestro in antepasados:
                self.result_text.insert("end", f"   • {ancestro.first_name} {ancestro.last_name} ({ancestro.gender})\n")
        else:
            self.result_text.insert("end", "   📭 No tiene antepasados maternos registrados\n")
        self.result_text.insert("end", "\n")
    
    def ejecutar_consulta_descendientes_vivos(self):
        """Ejecuta consulta de descendientes vivos"""
        persona = self.obtener_persona_por_combo(self.persona_var.get())
        if not persona:
            self.result_text.insert("end", "❌ Error: Selecciona una persona válida\n")
            return
        
        descendientes = RelacionService.obtener_descendientes_vivos(persona)
        self.result_text.insert("end", f"👶 Descendientes vivos de {persona.first_name}:\n")
        if descendientes:
            for desc in descendientes:
                edad = desc.calculate_age()
                self.result_text.insert("end", f"   • {desc.first_name} {desc.last_name} ({edad} años)\n")
        else:
            self.result_text.insert("end", "   📭 No tiene descendientes vivos\n")
        self.result_text.insert("end", "\n")
    
    def ejecutar_consulta_nacimientos_recientes(self):
        """Ejecuta consulta de nacimientos en últimos 10 años"""
        nacimientos = RelacionService.obtener_nacimientos_ultimos_10_años(self.family)
        self.result_text.insert("end", "🍼 Personas nacidas en los últimos 10 años:\n")
        self.result_text.insert("end", f"   📊 Total: {nacimientos} personas\n\n")
    
    def ejecutar_consulta_parejas_con_hijos(self):
        """Ejecuta consulta de parejas con múltiples hijos"""
        parejas = RelacionService.obtener_parejas_con_hijos(self.family, min_hijos=2)
        self.result_text.insert("end", "👨‍👩‍👧‍👦 Parejas con 2 o más hijos en común:\n")
        if parejas:
            for pareja in parejas:
                hijos_comunes = len(set(pareja[0].children) & set(pareja[1].children))
                self.result_text.insert("end", f"   • {pareja[0].first_name} y {pareja[1].first_name}: {hijos_comunes} hijos\n")
        else:
            self.result_text.insert("end", "   📭 No hay parejas con 2 o más hijos en común\n")
        self.result_text.insert("end", "\n")
    
    def ejecutar_consulta_fallecidos_joven(self):
        """Ejecuta consulta de fallecidos antes de 50 años"""
        fallecidos = RelacionService.obtener_fallecidos_antes_50(self.family)
        self.result_text.insert("end", "⚰️ Personas fallecidas antes de cumplir 50 años:\n")
        self.result_text.insert("end", f"   📊 Total: {fallecidos} personas\n\n")
    
    def ejecutar_todas_consultas(self):
        """Ejecuta todas las consultas disponibles"""
        self.result_text.insert("end", "📊 REPORTE COMPLETO DE CONSULTAS GENEALÓGICAS\n")
        self.result_text.insert("end", "=" * 60 + "\n\n")
        
        # Obtener personas para consultas que las requieren
        persona_principal = self.obtener_persona_por_combo(self.persona_var.get()) if self.personas else None
        persona_a = self.obtener_persona_por_combo(self.persona_a_var.get()) if self.personas else None
        persona_b = self.obtener_persona_por_combo(self.persona_b_var.get()) if self.personas else None
        
        try:
            # 1. Relación entre personas
            if persona_a and persona_b:
                relacion = RelacionService.encontrar_relacion(persona_a, persona_b)
                self.result_text.insert("end", f"1️⃣ Relación entre {persona_a.first_name} y {persona_b.first_name}:\n")
                self.result_text.insert("end", f"   📍 {relacion}\n\n")
            
            # 2-4. Consultas que requieren persona principal
            if persona_principal:
                # Primos de primer grado
                primos = RelacionService.obtener_primos_primer_grado(persona_principal)
                self.result_text.insert("end", f"2️⃣ Primos de primer grado de {persona_principal.first_name}:\n")
                if primos:
                    for primo in primos:
                        self.result_text.insert("end", f"   • {primo.first_name} {primo.last_name}\n")
                else:
                    self.result_text.insert("end", "   📭 No tiene primos de primer grado\n")
                self.result_text.insert("end", "\n")
                
                # Antepasados maternos
                antepasados = RelacionService.obtener_antepasados_maternos(persona_principal)
                self.result_text.insert("end", f"3️⃣ Antepasados maternos de {persona_principal.first_name}:\n")
                if antepasados:
                    for ancestro in antepasados:
                        self.result_text.insert("end", f"   • {ancestro.first_name} {ancestro.last_name} ({ancestro.gender})\n")
                else:
                    self.result_text.insert("end", "   📭 No tiene antepasados maternos registrados\n")
                self.result_text.insert("end", "\n")
                
                # Descendientes vivos
                descendientes = RelacionService.obtener_descendientes_vivos(persona_principal)
                self.result_text.insert("end", f"4️⃣ Descendientes vivos de {persona_principal.first_name}:\n")
                if descendientes:
                    for desc in descendientes:
                        edad = desc.calculate_age()
                        self.result_text.insert("end", f"   • {desc.first_name} {desc.last_name} ({edad} años)\n")
                else:
                    self.result_text.insert("end", "   📭 No tiene descendientes vivos\n")
                self.result_text.insert("end", "\n")
            
            # 5-7. Consultas estadísticas
            nacimientos = RelacionService.obtener_nacimientos_ultimos_10_años(self.family)
            self.result_text.insert("end", "5️⃣ Personas nacidas en los últimos 10 años:\n")
            self.result_text.insert("end", f"   📊 Total: {nacimientos} personas\n\n")
            
            parejas = RelacionService.obtener_parejas_con_hijos(self.family, min_hijos=2)
            self.result_text.insert("end", "6️⃣ Parejas con 2 o más hijos en común:\n")
            if parejas:
                for pareja in parejas:
                    hijos_comunes = len(set(pareja[0].children) & set(pareja[1].children))
                    self.result_text.insert("end", f"   • {pareja[0].first_name} y {pareja[1].first_name}: {hijos_comunes} hijos\n")
            else:
                self.result_text.insert("end", "   📭 No hay parejas con 2 o más hijos en común\n")
            self.result_text.insert("end", "\n")
            
            fallecidos = RelacionService.obtener_fallecidos_antes_50(self.family)
            self.result_text.insert("end", "7️⃣ Personas fallecidas antes de cumplir 50 años:\n")
            self.result_text.insert("end", f"   📊 Total: {fallecidos} personas\n\n")
            
        except Exception as e:
            self.result_text.insert("end", f"❌ Error durante la ejecución: {str(e)}")
    
    def obtener_persona_por_combo(self, combo_value):
        """Obtiene el objeto Person basado en el valor del combobox"""
        if not combo_value or combo_value == "No hay personas en el árbol":
            return None
        
        for persona in self.personas:
            if f"{persona.first_name} {persona.last_name} (Cédula: {persona.cedula})" == combo_value:
                return persona
        return None