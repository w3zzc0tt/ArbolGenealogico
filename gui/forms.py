# gui/forms.py - VERSIÓN CORREGIDA Y OPTIMIZADA
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import datetime
import sys
import os
import re

# Añadir el directorio raíz del proyecto para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.person import Person
from models.family import Family

try:
    from utils.validators import (
        validar_cedula,
        validar_fecha,
        validar_fechas_coherentes,
        validar_nombre,
        validar_genero,
        validar_provincia,
        validar_estado_civil,
    )
    HAS_VALIDATORS = True
except ImportError:
    HAS_VALIDATORS = False
    print("Advertencia: No se pudieron importar las utilidades de validación")


class PersonForm(ctk.CTkToplevel):
    def __init__(self, parent, family=None, title="Agregar Persona", on_save=None, data=None, is_event_form=False):
        """
        Inicializa el formulario para personas.
        
        Args:
            parent: Ventana padre
            family: Objeto Family (opcional)
            title: Título del formulario
            on_save: Función callback para guardar
            data: Datos para edición (opcional)
            is_event_form: Si es un formulario de evento
        """
        super().__init__(parent)
        self.title(title)
        self.geometry("500x700")
        self.resizable(False, False)
        self.on_save = on_save
        self.data = data or {}
        self.family = family
        self.is_event_form = is_event_form

        # Centrar y bloquear ventana principal
        self.transient(parent)
        self.grab_set()
        self.parent = parent

        self.setup_ui()

    def setup_ui(self):
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            form_frame,
            text="📋 Registrar Persona" if not self.is_event_form else "📅 Agregar Evento",
            font=("Arial", 18, "bold")
        ).pack(pady=15)

        form = ctk.CTkFrame(form_frame)
        form.pack(fill=tk.X, padx=10, pady=10)
        form.columnconfigure(1, weight=1)

        # Cédula (oculto si es evento)
        if not self.is_event_form:
            ctk.CTkLabel(form, text="Cédula:", font=("Arial", 12)).grid(
                row=0, column=0, sticky="w", padx=10, pady=6
            )
            self.cedula_entry = ctk.CTkEntry(
                form, placeholder_text="9-12 dígitos", width=220
            )
            self.cedula_entry.grid(row=0, column=1, padx=10, pady=6, sticky="ew")
            self.cedula_entry.insert(0, self.data.get("cedula", ""))
        else:
            # Si es un evento, mostrar persona seleccionada
            ctk.CTkLabel(form, text="Persona:", font=("Arial", 12)).grid(
                row=0, column=0, sticky="w", padx=10, pady=6
            )
            person_name = self.data.get("first_name", "") + " " + self.data.get("last_name", "")
            ctk.CTkLabel(form, text=person_name, font=("Arial", 12, "bold")).grid(
                row=0, column=1, sticky="w", padx=10, pady=6
            )

        # Nombre
        if not self.is_event_form:
            ctk.CTkLabel(form, text="Nombre:", font=("Arial", 12)).grid(
                row=1, column=0, sticky="w", padx=10, pady=6
            )
            self.first_name_entry = ctk.CTkEntry(
                form, placeholder_text="Ej: María", width=220
            )
            self.first_name_entry.grid(row=1, column=1, padx=10, pady=6, sticky="ew")
            self.first_name_entry.insert(0, self.data.get("first_name", ""))

        # Apellidos
        if not self.is_event_form:
            ctk.CTkLabel(form, text="Apellidos:", font=("Arial", 12)).grid(
                row=2, column=0, sticky="w", padx=10, pady=6
            )
            self.last_name_entry = ctk.CTkEntry(
                form, placeholder_text="Ej: López Fernández", width=220
            )
            self.last_name_entry.grid(row=2, column=1, padx=10, pady=6, sticky="ew")
            self.last_name_entry.insert(0, self.data.get("last_name", ""))

        # Fecha de nacimiento
        if not self.is_event_form:
            ctk.CTkLabel(form, text="Fecha Nac.:", font=("Arial", 12)).grid(
                row=3, column=0, sticky="w", padx=10, pady=6
            )
            self.birth_entry = ctk.CTkEntry(
                form, placeholder_text="YYYY-MM-DD (cualquier año)", width=220
            )
            self.birth_entry.grid(row=3, column=1, padx=10, pady=6, sticky="ew")
            # Limpiar fecha para mostrar solo YYYY-MM-DD
            birth_date_value = self.data.get("birth_date", "")
            if birth_date_value:
                birth_date_str = str(birth_date_value)
                # Manejar formato ISO con T: "2006-11-09T00:00:00"
                if 'T' in birth_date_str:
                    birth_date_value = birth_date_str.split('T')[0]
                # Manejar formato con espacio: "2006-11-09 00:00:00"
                elif ' ' in birth_date_str and ':' in birth_date_str:
                    birth_date_value = birth_date_str.split(' ')[0]
            self.birth_entry.insert(0, birth_date_value)

        # Género - CÓDIGO CORREGIDO
        if not self.is_event_form:
            ctk.CTkLabel(form, text="Género:", font=("Arial", 12)).grid(
                row=4, column=0, sticky="w", padx=10, pady=6
            )
            
            # Configurar los valores del combobox
            gender_values = ["Masculino", "Femenino"]
            
            # Determinar el valor inicial
            initial_gender = "Masculino"  # Valor por defecto
            if self.data and "gender" in self.data:
                # Manejar diferentes formatos de género
                data_gender = self.data["gender"]
                if data_gender in ["M", "Masculino"]:
                    initial_gender = "Masculino"
                elif data_gender in ["F", "Femenino"]:
                    initial_gender = "Femenino"
            
            # Crear la variable de control
            self.gender_var = ctk.StringVar(value=initial_gender)
            
            # Crear el combobox
            gender_combo = ctk.CTkComboBox(
                form,
                values=gender_values,
                variable=self.gender_var,
                width=220,
                state="readonly",
            )
            gender_combo.grid(row=4, column=1, padx=10, pady=6, sticky="ew")

        # Provincia
        if not self.is_event_form:
            ctk.CTkLabel(form, text="Provincia:", font=("Arial", 12)).grid(
                row=5, column=0, sticky="w", padx=10, pady=6
            )
            self.province_var = ctk.StringVar(
                value=self.data.get("province", "San José")
            )
            province_combo = ctk.CTkComboBox(
                form,
                values=[
                    "San José",
                    "Alajuela",
                    "Cartago",
                    "Heredia",
                    "Guanacaste",
                    "Puntarenas",
                    "Limón",
                ],
                variable=self.province_var,
                width=220,
                state="readonly",
            )
            province_combo.grid(row=5, column=1, padx=10, pady=6, sticky="ew")

        # Estado civil
        if not self.is_event_form:
            ctk.CTkLabel(form, text="Estado Civil:", font=("Arial", 12)).grid(
                row=6, column=0, sticky="w", padx=10, pady=6
            )
            self.marital_status_var = ctk.StringVar(
                value=self.data.get("marital_status", "Soltero/a")
            )
            marital_status_combo = ctk.CTkComboBox(
                form,
                values=[
                    "Soltero/a",
                    "Casado/a",
                    "Divorciado/a",
                    "Viudo/a",
                    "Unión Libre",
                ],
                variable=self.marital_status_var,
                width=220,
                state="readonly",
            )
            marital_status_combo.grid(row=6, column=1, padx=10, pady=6, sticky="ew")

        # Estado: Vivo / Fallecido
        if not self.is_event_form:
            ctk.CTkLabel(form, text="Estado:", font=("Arial", 12)).grid(
                row=7, column=0, sticky="w", padx=10, pady=6
            )
            self.status_var = ctk.StringVar(
                value="Vivo" if self.data.get("death_date") is None else "Fallecido"
            )
            status_frame = ctk.CTkFrame(form)
            status_frame.grid(row=7, column=1, sticky="w", padx=10, pady=6)
            ctk.CTkRadioButton(
                status_frame,
                text="Vivo",
                variable=self.status_var,
                value="Vivo",
                command=self.toggle_death_field,
            ).pack(side="left", padx=5)
            ctk.CTkRadioButton(
                status_frame,
                text="Fallecido",
                variable=self.status_var,
                value="Fallecido",
                command=self.toggle_death_field,
            ).pack(side="left", padx=5)

        # Fecha de fallecimiento
        if not self.is_event_form:
            self.death_frame = ctk.CTkFrame(form)
            self.death_frame.grid(row=8, column=1, sticky="ew", padx=10, pady=5)
            ctk.CTkLabel(self.death_frame, text="Fecha Fallec.:").pack(side="left")
            self.death_entry = ctk.CTkEntry(
                self.death_frame, placeholder_text="YYYY-MM-DD (cualquier año)", width=150
            )
            self.death_entry.pack(side="left", padx=5)
            if self.data.get("death_date"):
                # Limpiar fecha para mostrar solo YYYY-MM-DD
                death_date_value = str(self.data["death_date"])
                # Manejar formato ISO con T: "2006-11-09T00:00:00"
                if 'T' in death_date_value:
                    death_date_value = death_date_value.split('T')[0]
                # Manejar formato con espacio: "2006-11-09 00:00:00"
                elif ' ' in death_date_value and ':' in death_date_value:
                    death_date_value = death_date_value.split(' ')[0]
                self.death_entry.insert(0, death_date_value)

            # Ocultar si está vivo
            if not self.is_event_form and self.status_var.get() == "Vivo":
                self.death_frame.grid_remove()

        # Formulario de evento (solo para eventos)
        if self.is_event_form:
            # Tipo de evento
            ctk.CTkLabel(form, text="Tipo de evento:", font=("Arial", 12)).grid(
                row=1, column=0, sticky="w", padx=10, pady=6
            )
            self.event_type_var = ctk.StringVar(value="Otro")
            event_type_combo = ctk.CTkComboBox(
                form,
                values=[
                    "Nacimiento",
                    "Matrimonio",
                    "Divorcio",
                    "Fallecimiento",
                    "Otro"
                ],
                variable=self.event_type_var,
                width=220,
                state="readonly",
            )
            event_type_combo.grid(row=1, column=1, padx=10, pady=6, sticky="ew")
            
            # Descripción
            ctk.CTkLabel(form, text="Descripción:", font=("Arial", 12)).grid(
                row=2, column=0, sticky="w", padx=10, pady=6
            )
            self.description_entry = ctk.CTkEntry(
                form, placeholder_text="Detalles del evento", width=220
            )
            self.description_entry.grid(row=2, column=1, padx=10, pady=6, sticky="ew")
            
            # Fecha
            ctk.CTkLabel(form, text="Fecha:", font=("Arial", 12)).grid(
                row=3, column=0, sticky="w", padx=10, pady=6
            )
            self.event_date_entry = ctk.CTkEntry(
                form, placeholder_text="YYYY-MM-DD", width=220
            )
            self.event_date_entry.grid(row=3, column=1, padx=10, pady=6, sticky="ew")
            self.event_date_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))

        # Botones
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(pady=20)

        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.destroy,
            fg_color="gray",
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            button_frame,
            text="Guardar",
            command=self.save,
            fg_color="#1db954",
        ).pack(side="left", padx=5)

    def toggle_death_field(self):
        """Muestra u oculta el campo de fecha de fallecimiento"""
        if not hasattr(self, 'death_frame') or not hasattr(self, 'status_var'):
            return
            
        if self.status_var.get() == "Fallecido":
            self.death_frame.grid()
        else:
            self.death_entry.delete(0, "end")
            self.death_frame.grid_remove()

    def save(self):
        """Valida y guarda los datos del formulario - SIN LÍMITES DE FECHA"""
        if self.is_event_form:
            return self.save_event()
            
        cedula = self.cedula_entry.get().strip()
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        birth_date = self.birth_entry.get().strip()
        gender = self.gender_var.get()
        province = self.province_var.get()
        marital_status = self.marital_status_var.get()
        status = self.status_var.get()
        death_date = self.death_entry.get().strip() if status == "Fallecido" else None

        # Validación de campos obligatorios
        missing_fields = []
        if not cedula: 
            missing_fields.append("Cédula")
        if not first_name: 
            missing_fields.append("Nombre")
        if not last_name: 
            missing_fields.append("Apellidos")
        if not birth_date: 
            missing_fields.append("Fecha de Nacimiento")
        if not gender or gender == "Seleccionar género": 
            missing_fields.append("Género")
        
        if missing_fields:
            error_msg = "Los siguientes campos son obligatorios:\n" + "\n".join(f"- {field}" for field in missing_fields)
            messagebox.showerror("Campos obligatorios", error_msg)
            return

        # === Validaciones mejoradas ===
        if HAS_VALIDATORS:
            try:
                # Validar cédula con provincia
                valido_cedula, mensaje_cedula = validar_cedula(cedula, province)
                if not valido_cedula:
                    messagebox.showerror("Error de validación", mensaje_cedula)
                    return

                # Validar nombre
                valido_nombre, mensaje_nombre = validar_nombre(first_name, "nombre")
                if not valido_nombre:
                    messagebox.showerror("Error de validación", mensaje_nombre)
                    return

                # Validar apellido
                valido_apellido, mensaje_apellido = validar_nombre(last_name, "apellido")
                if not valido_apellido:
                    messagebox.showerror("Error de validación", mensaje_apellido)
                    return

                # Validar fecha de nacimiento
                valido_nacimiento, mensaje_nacimiento = validar_fecha(birth_date, "nacimiento")
                if not valido_nacimiento:
                    messagebox.showerror("Error de validación", mensaje_nacimiento)
                    return

                # Validar fecha de fallecimiento (si existe)
                if death_date:
                    valido_fallecimiento, mensaje_fallecimiento = validar_fecha(death_date, "fallecimiento")
                    if not valido_fallecimiento:
                        messagebox.showerror("Error de validación", mensaje_fallecimiento)
                        return
                    
                    # Validar coherencia entre fechas
                    valido_coherencia, mensaje_coherencia = validar_fechas_coherentes(birth_date, death_date)
                    if not valido_coherencia:
                        messagebox.showerror("Error de validación", mensaje_coherencia)
                        return

                # Validar género - CORREGIDO: Ahora acepta "Masculino"/"Femenino"
                valido_genero, mensaje_genero = validar_genero(gender)
                if not valido_genero:
                    messagebox.showerror("Error de validación", "Debe seleccionar un género válido")
                    return

                # Validar provincia
                valido_provincia, mensaje_provincia = validar_provincia(province)
                if not valido_provincia:
                    messagebox.showerror("Error de validación", mensaje_provincia)
                    return

                # Validar estado civil
                valido_estado, mensaje_estado = validar_estado_civil(marital_status)
                if not valido_estado:
                    messagebox.showerror("Error de validación", mensaje_estado)
                    return

            except Exception as e:
                messagebox.showerror("Error", f"Error en validación: {str(e)}")
                return
        else:
            # === Validaciones fallback SIN LÍMITES DE FECHA ===
            # Validar cédula
            if not cedula.isdigit():
                messagebox.showerror("Error de validación", "La cédula debe contener solo números")
                return
            if not (9 <= len(cedula) <= 12):
                messagebox.showerror("Error de validación", "La cédula debe tener entre 9 y 12 dígitos")
                return
                
            # Verificar que el primer dígito coincida con la provincia
            provincia_digitos = {
                "San José": "1",
                "Alajuela": "2", 
                "Cartago": "3",
                "Heredia": "4",
                "Guanacaste": "5",
                "Puntarenas": "6",
                "Limón": "7"
            }
            
            if province in provincia_digitos:
                digito_esperado = provincia_digitos[province]
                if cedula[0] != digito_esperado:
                    provincia_correcta = next((prov for prov, dig in provincia_digitos.items() 
                                            if dig == cedula[0]), None)
                    if provincia_correcta:
                        messagebox.showerror("Error de validación", 
                                        f"Error de provincia: La cédula {cedula} corresponde a {provincia_correcta}, no a {province}")
                    else:
                        messagebox.showerror("Error de validación", 
                                        f"El primer dígito de la cédula ({cedula[0]}) no corresponde a ninguna provincia válida")
                    return
            
            # Validar nombre
            if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-]+$", first_name) or len(first_name.strip()) < 2:
                messagebox.showerror("Error de validación", 
                                "Nombre inválido (solo letras, espacios y guiones, mínimo 2 caracteres)")
                return
            
            # Validar apellido
            if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-]+$", last_name) or len(last_name.strip()) < 2:
                messagebox.showerror("Error de validación", 
                                "Apellidos inválidos (solo letras, espacios y guiones, mínimo 2 caracteres)")
                return
            
            # ✅ VALIDACIÓN DE FECHAS SIN LÍMITES DE RANGO
            try:
                birth_datetime = datetime.datetime.strptime(birth_date, "%Y-%m-%d")
                    
                if death_date:
                    death_datetime = datetime.datetime.strptime(death_date, "%Y-%m-%d")
                    
                    # Verificar coherencia entre fechas
                    if birth_datetime >= death_datetime:
                        messagebox.showerror(
                            "Error de validación", 
                            "La fecha de fallecimiento debe ser posterior a la de nacimiento"
                        )
                        return
            except ValueError:
                messagebox.showerror("Error de validación", 
                                "Formato de fecha inválido. Use el formato YYYY-MM-DD")
                return

        # === Datos validados correctamente ===
        
        # NUEVA VERIFICACIÓN: Límite generacional para personas agregadas manualmente
        if self.family and hasattr(self.family, 'members') and len(self.family.members) > 0:
            generation_check = self._verificar_limite_generacional_manual()
            if not generation_check['allowed']:
                messagebox.showerror("Límite Generacional", generation_check['reason'])
                return
        
        data = {
            "cedula": cedula,
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": birth_date,
            "gender": "M" if gender == "Masculino" else "F",  # Convertir a M/F
            "province": province,
            "marital_status": marital_status,
            "death_date": death_date,
        }

        if self.on_save:
            self.on_save(data)
            self.destroy()
        else:
            messagebox.showerror("Error", "No se puede guardar: falta función on_save")
            
    def save_event(self):
        """Guarda un evento manualmente para una persona"""
        event_type = self.event_type_var.get()
        description = self.description_entry.get().strip()
        event_date = self.event_date_entry.get().strip()
        
        # Validar campos obligatorios
        if not description:
            messagebox.showerror("Error", "La descripción del evento es obligatoria")
            return
            
        if not event_date:
            messagebox.showerror("Error", "La fecha del evento es obligatoria")
            return
            
        # Validar formato de fecha
        try:
            datetime.datetime.strptime(event_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
            return
            
        # Crear evento
        event_data = {
            "event_type": event_type,
            "description": description,
            "date": event_date,
            "cedula": self.data.get("cedula")
        }
        
        if self.on_save:
            self.on_save(event_data)
            self.destroy()
        else:
            messagebox.showerror("Error", "No se puede guardar: falta función on_save")


class RelationshipForm:
    def __init__(self, parent, family, person, relation_type):
        self.parent = parent
        self.family = family
        self.person = person
        self.relation_type = relation_type
        self.setup_ui()
    
    def setup_ui(self):
        self.form_window = ctk.CTkToplevel(self.parent)
        self.form_window.title(f"Agregar {self.relation_type.capitalize()}")
        self.form_window.geometry("400x300")
        self.form_window.transient(self.parent)
        self.form_window.grab_set()
        
        form_frame = ctk.CTkFrame(self.form_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configuración según el tipo de relación
        if self.relation_type in ["padre", "madre"]:
            ctk.CTkLabel(self.form_window, text=f"Registrar {self.relation_type} para {self.person.get_full_name()}").pack(pady=10)
            
            # Buscar posibles padres/madres
            possible_parents = []
            for p in self.family.members:
                if p != self.person and p.gender == ("M" if self.relation_type == "padre" else "F"):
                    possible_parents.append(p)
            
            if not possible_parents:
                ctk.CTkLabel(form_frame, text="No hay personas del género adecuado en la familia", text_color="red").pack(pady=10)
                ctk.CTkButton(form_frame, text="Cerrar", command=self.form_window.destroy, fg_color="#e74c3c").pack(pady=10)
                return
            
            # Selector de persona
            self.parent_var = ctk.StringVar()
            parent_dropdown = ctk.CTkComboBox(
                form_frame,
                values=[f"{p.first_name} {p.last_name}" for p in possible_parents],
                variable=self.parent_var
            )
            parent_dropdown.pack(fill=tk.X, pady=10)
            
            # Botón de registro
            ctk.CTkButton(
                form_frame,
                text="Registrar",
                command=lambda: self.registrar_parentesco(possible_parents),
                fg_color="#1db954"
            ).pack(pady=10)
        
        elif self.relation_type == "conyuge":
            ctk.CTkLabel(self.form_window, text=f"Registrar conyuge para {self.person.get_full_name()}").pack(pady=10)
            
            # Buscar posibles conyuges
            possible_partners = []
            for p in self.family.members:
                if (p != self.person and p.gender != self.person.gender and 
                    not p.has_partner() and p.alive and p.calculate_virtual_age() >= 18):
                    possible_partners.append(p)
            
            if not possible_partners:
                ctk.CTkLabel(form_frame, text="No hay personas elegibles para ser conyuge", text_color="red").pack(pady=10)
                ctk.CTkButton(form_frame, text="Cerrar", command=self.form_window.destroy, fg_color="#e74c3c").pack(pady=10)
                return
            
            # Selector de persona
            self.partner_var = ctk.StringVar()
            partner_dropdown = ctk.CTkComboBox(
                form_frame,
                values=[f"{p.first_name} {p.last_name} ({p.calculate_virtual_age()} años)" for p in possible_partners],
                variable=self.partner_var
            )
            partner_dropdown.pack(fill=tk.X, pady=10)
            
            # Botón de registro
            ctk.CTkButton(
                form_frame,
                text="Registrar",
                command=lambda: self.registrar_conyuge(possible_partners),
                fg_color="#1db954"
            ).pack(pady=10)
        
        elif self.relation_type == "hijo":
            ctk.CTkLabel(self.form_window, text=f"Registrar hijo para {self.person.get_full_name()}").pack(pady=10)
            
            # Determinar género del padre/madre
            gender = "M" if self.person.gender == "F" else "F"
            
            # Buscar posible pareja
            possible_spouse = None
            if self.person.spouse and self.person.spouse.gender == gender:
                possible_spouse = self.person.spouse
            
            # Si no hay pareja, buscar personas del género adecuado
            if not possible_spouse:
                for p in self.family.members:
                    if p.gender == gender and not p.has_partner() and p.alive:
                        possible_spouse = p
                        break
            
            # Crear formulario para el bebé
            ctk.CTkLabel(form_frame, text="Datos del bebé:", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
            
            # Nombre
            ctk.CTkLabel(form_frame, text="Nombre:", font=("Arial", 11)).pack(anchor="w", padx=10)
            self.child_name = ctk.CTkEntry(form_frame, placeholder_text="Nombre del bebé")
            self.child_name.pack(fill=tk.X, padx=10, pady=5)
            
            # Apellido
            ctk.CTkLabel(form_frame, text="Apellido:", font=("Arial", 11)).pack(anchor="w", padx=10)
            self.child_lastname = ctk.CTkEntry(form_frame, placeholder_text="Apellido del bebé")
            self.child_lastname.pack(fill=tk.X, padx=10, pady=5)
            self.child_lastname.insert(0, self.person.last_name)
            
            # Género
            self.child_gender = ctk.StringVar(value="F")
            ctk.CTkLabel(form_frame, text="Género:", font=("Arial", 11)).pack(anchor="w", padx=10)
            gender_frame = ctk.CTkFrame(form_frame)
            gender_frame.pack(fill=tk.X, padx=10, pady=5)
            ctk.CTkRadioButton(
                gender_frame,
                text="Femenino",
                variable=self.child_gender,
                value="F"
            ).pack(side="left", padx=5)
            ctk.CTkRadioButton(
                gender_frame,
                text="Masculino",
                variable=self.child_gender,
                value="M"
            ).pack(side="left", padx=5)
            
            # Botón de registro
            ctk.CTkButton(
                form_frame,
                text="Registrar Hijo",
                command=lambda: self.registrar_hijo(possible_spouse),
                fg_color="#1db954"
            ).pack(pady=10, fill=tk.X, padx=10)
        
        elif self.relation_type == "hermano":
            ctk.CTkLabel(self.form_window, text=f"Registrar hermano para {self.person.get_full_name()}").pack(pady=10)
            
            # Buscar padres
            parents = []
            if self.person.mother:
                parents.append(self.person.mother)
            if self.person.father:
                parents.append(self.person.father)
            
            if not parents:
                ctk.CTkLabel(form_frame, text="Primero registre al menos un padre/madre", text_color="red").pack(pady=10)
                ctk.CTkButton(form_frame, text="Cerrar", command=self.form_window.destroy, fg_color="#e74c3c").pack(pady=10)
                return
            
            # Crear formulario para el hermano
            ctk.CTkLabel(form_frame, text="Datos del hermano:", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
            
            # Nombre
            ctk.CTkLabel(form_frame, text="Nombre:", font=("Arial", 11)).pack(anchor="w", padx=10)
            self.sibling_name = ctk.CTkEntry(form_frame, placeholder_text="Nombre del hermano")
            self.sibling_name.pack(fill=tk.X, padx=10, pady=5)
            
            # Apellido
            ctk.CTkLabel(form_frame, text="Apellido:", font=("Arial", 11)).pack(anchor="w", padx=10)
            self.sibling_lastname = ctk.CTkEntry(form_frame, placeholder_text="Apellido del hermano")
            self.sibling_lastname.pack(fill=tk.X, padx=10, pady=5)
            self.sibling_lastname.insert(0, self.person.last_name)
            
            # Género
            self.sibling_gender = ctk.StringVar(value="F")
            ctk.CTkLabel(form_frame, text="Género:", font=("Arial", 11)).pack(anchor="w", padx=10)
            gender_frame = ctk.CTkFrame(form_frame)
            gender_frame.pack(fill=tk.X, padx=10, pady=5)
            ctk.CTkRadioButton(
                gender_frame,
                text="Femenino",
                variable=self.sibling_gender,
                value="F"
            ).pack(side="left", padx=5)
            ctk.CTkRadioButton(
                gender_frame,
                text="Masculino",
                variable=self.sibling_gender,
                value="M"
            ).pack(side="left", padx=5)
            
            # Botón de registro
            ctk.CTkButton(
                form_frame,
                text="Registrar Hermano",
                command=self.registrar_hermano,
                fg_color="#1db954"
            ).pack(pady=10, fill=tk.X, padx=10)
    
    def registrar_parentesco(self, possible_parents):
        selected_index = [p.get_full_name() for p in possible_parents].index(self.parent_var.get())
        parent = possible_parents[selected_index]
        
        # Registrar la relación
        from services.relacion_service import RelacionService
        
        if self.relation_type == "padre":
            success, message = RelacionService.registrar_padres(
                self.family, 
                self.person.cedula, 
                father_cedula=parent.cedula
            )
        else:  # madre
            success, message = RelacionService.registrar_padres(
                self.family, 
                self.person.cedula, 
                mother_cedula=parent.cedula
            )
        
        if success:
            messagebox.showinfo("Éxito", message)
            self.form_window.destroy()
        else:
            messagebox.showerror("Error", message)
    
    def registrar_conyuge(self, possible_partners):
        selected_index = [p.get_full_name() for p in possible_partners].index(self.partner_var.get())
        partner = possible_partners[selected_index]
        
        # ✅ CORRECCIÓN: Importar utils_service LOCALMENTE para evitar importación circular
        try:
            from services.utils_service import verificar_requisitos_union
            validation = verificar_requisitos_union(self.person, partner, self.family)
            if not validation[0]:
                messagebox.showerror("Error", validation[1])
                return
        except ImportError:
            # Fallback si no está disponible
            if self.person.has_partner():
                messagebox.showerror("Error", f"{self.person.first_name} ya está en una relación")
                return
            if partner.has_partner():
                messagebox.showerror("Error", f"{partner.first_name} ya está en una relación")
                return
            if self.person.calculate_virtual_age() < 18 or partner.calculate_virtual_age() < 18:
                messagebox.showerror("Error", "Ambas personas deben ser mayores de 18 años")
                return
        
        # Registrar la pareja
        from services.relacion_service import RelacionService
        success, message = RelacionService.registrar_pareja(
            self.family, 
            self.person.cedula, 
            partner.cedula
        )
        
        if success:
            messagebox.showinfo("Éxito", message)
            self.form_window.destroy()
        else:
            messagebox.showerror("Error", message)
    
    def registrar_hijo(self, spouse):
        # Obtener datos del formulario
        name = self.child_name.get().strip()
        lastname = self.child_lastname.get().strip()
        gender = self.child_gender.get()
        
        # Validar datos
        if not name:
            messagebox.showerror("Error", "El nombre del bebé es obligatorio")
            return
        if not lastname:
            messagebox.showerror("Error", "El apellido del bebé es obligatorio")
            return
        
        # Generar cédula única
        from models.family import Family
        cedula = Family.generate_cedula()
        while not Family.validate_cedula_unique(cedula, self.family):
            cedula = Family.generate_cedula()
        
        # Crear bebé
        from models.person import Person
        birth_date = f"{self.family.current_year}-01-01"
        baby = Person(
            cedula=cedula,
            first_name=name,
            last_name=lastname,
            birth_date=birth_date,
            gender=gender,
            province=self.person.province,
            marital_status="Soltero/a"
        )
        
        # Establecer edad virtual
        baby.virtual_age = 0
        
        # Agregar a la familia
        self.family.add_or_update_member(baby)
        
        # Registrar relación
        from services.relacion_service import RelacionService
        if spouse:
            success, message = RelacionService.registrar_padres(
                self.family, 
                baby.cedula, 
                mother_cedula=self.person.cedula if self.person.gender == "F" else spouse.cedula,
                father_cedula=self.person.cedula if self.person.gender == "M" else spouse.cedula
            )
        else:
            success, message = RelacionService.registrar_padres(
                self.family, 
                baby.cedula, 
                mother_cedula=self.person.cedula if self.person.gender == "F" else None,
                father_cedula=self.person.cedula if self.person.gender == "M" else None
            )
        
        if success:
            messagebox.showinfo("Éxito", message)
            self.form_window.destroy()
        else:
            messagebox.showerror("Error", message)
    
    def registrar_hermano(self):
        # Obtener datos del formulario
        name = self.sibling_name.get().strip()
        lastname = self.sibling_lastname.get().strip()
        gender = self.sibling_gender.get()
        
        # Validar datos
        if not name:
            messagebox.showerror("Error", "El nombre del hermano es obligatorio")
            return
        if not lastname:
            messagebox.showerror("Error", "El apellido del hermano es obligatorio")
            return
        
        # Generar cédula única
        from models.family import Family
        cedula = Family.generate_cedula()
        while not Family.validate_cedula_unique(cedula, self.family):
            cedula = Family.generate_cedula()
        
        # Crear hermano
        from models.person import Person
        birth_date = f"{self.family.current_year}-01-01"
        sibling = Person(
            cedula=cedula,
            first_name=name,
            last_name=lastname,
            birth_date=birth_date,
            gender=gender,
            province=self.person.province,
            marital_status="Soltero/a"
        )
        
        # Establecer edad virtual
        sibling.virtual_age = self.person.virtual_age  # Misma edad aproximada
        
        # Agregar a la familia
        self.family.add_or_update_member(sibling)
        
        # Registrar relación
        from services.relacion_service import RelacionService
        
        # Registrar padres
        if self.person.mother:
            RelacionService.registrar_padres(
                self.family, 
                sibling.cedula, 
                mother_cedula=self.person.mother.cedula
            )
        if self.person.father:
            RelacionService.registrar_padres(
                self.family, 
                sibling.cedula, 
                father_cedula=self.person.father.cedula
            )
        
        # Registrar hermanos
        sibling.siblings = [self.person] + self.person.siblings
        for bro in [self.person] + self.person.siblings:
            if sibling not in bro.siblings:
                bro.siblings.append(sibling)
        
        messagebox.showinfo("Éxito", "Hermano registrado exitosamente")
        self.form_window.destroy()
    
    def _verificar_limite_generacional_manual(self) -> dict:
        """
        Verifica el límite generacional para personas agregadas manualmente.
        
        Para personas agregadas manualmente, asumimos que pueden ser de cualquier generación
        existente, pero no pueden crear una 6ta generación (bisnietos).
        
        Returns:
            dict: {'allowed': bool, 'reason': str}
        """
        try:
            # Importar aquí para evitar dependencias circulares
            from utils.graph_visualizer import FamilyGraphVisualizer
            
            # Calcular niveles generacionales actuales
            visualizer = FamilyGraphVisualizer()
            levels = visualizer._assign_levels(self.family)
            
            if not levels:
                # Si no hay niveles definidos, permitir
                return {'allowed': True, 'reason': 'Primera persona en la familia'}
            
            # Encontrar el nivel más bajo (más profundo) actual
            max_current_level = max(levels.values()) if levels else 0
            
            # Verificar límite de 5 generaciones (niveles 0-4)
            MAX_GENERATION_LEVEL = 4  # Nietos = nivel 4 (última generación permitida)
            
            if max_current_level >= MAX_GENERATION_LEVEL:
                generation_names = {
                    0: "Bisabuelos",
                    1: "Abuelos", 
                    2: "Padres",
                    3: "Hijos",
                    4: "Nietos"
                }
                
                current_deepest = generation_names.get(max_current_level, f"Generación {max_current_level}")
                
                return {
                    'allowed': False,
                    'reason': f'🚫 Límite generacional alcanzado\n\n'
                             f'El árbol genealógico ya contiene la generación más profunda permitida: {current_deepest} (nivel {max_current_level}).\n\n'
                             f'Sistema limitado a 5 generaciones:\n'
                             f'• Bisabuelos → Abuelos → Padres → Hijos → Nietos\n\n'
                             f'No se pueden agregar más descendientes (bisnietos).'
                }
            
            return {'allowed': True, 'reason': f'Persona puede agregarse en generaciones existentes (hasta nivel {MAX_GENERATION_LEVEL})'}
            
        except Exception as e:
            # En caso de error, permitir por defecto para no bloquear la creación
            print(f"⚠️ Error verificando límite generacional manual: {e}")
            return {'allowed': True, 'reason': 'Error en verificación generacional'}