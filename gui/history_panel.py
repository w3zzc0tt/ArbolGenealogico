# gui/history_panel.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from services.persona_service import PersonaService  # IMPORTAR EL SERVICIO DE PERSONAS

class HistoryPanel:
    def __init__(self, parent, family):
        self.parent = parent
        self.family = family
        self.setup_ui()

    def setup_ui(self):
        # Frame principal
        self.frame = ctk.CTkFrame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Texto del historial
        self.history_text = ctk.CTkTextbox(
            self.frame,
            bg_color="#2a2a2a",
            fg_color="#2a2a2a",
            text_color="white",
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5), pady=5)

        # Frame de botones
        self.button_frame = ctk.CTkFrame(self.frame)
        self.button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        # Botones
        self.add_buttons()

        # Actualizar historial
        self.update_history()

    def add_buttons(self):
        """Agrega todos los botones al panel"""
        # Limpiar Historial
        ctk.CTkButton(
            self.button_frame,
            text="🗑️ Limpiar Historial",
            command=self.limpiar_historial,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        ).pack(fill=tk.X, padx=2, pady=2)

        # Actualizar Historial
        ctk.CTkButton(
            self.button_frame,
            text="🔄 Actualizar Historial",
            command=self.update_history,
            fg_color="#3498db",
            hover_color="#2980b9"
        ).pack(fill=tk.X, padx=2, pady=2)

        # Agregar Evento Manualmente
        ctk.CTkButton(
            self.button_frame,
            text="➕ Agregar Evento Manualmente",
            command=self.agregar_evento_manual,
            fg_color="#1db954",
            hover_color="#1ed760"
        ).pack(fill=tk.X, padx=2, pady=2)

        # Buscar Persona
        ctk.CTkButton(
            self.button_frame,
            text="🔍 Buscar Persona",
            command=self.buscar_persona_en_historial,
            fg_color="#9b59b6",
            hover_color="#8e44ad"
        ).pack(fill=tk.X, padx=2, pady=2)

        # Ver Detalles de Persona
        ctk.CTkButton(
            self.button_frame,
            text="👤 Ver Detalles de Persona",
            command=self.ver_detalles_persona,
            fg_color="#f39c12",
            hover_color="#d35400"
        ).pack(fill=tk.X, padx=2, pady=2)

        # Eliminar Persona
        ctk.CTkButton(
            self.button_frame,
            text="🗑️ Eliminar Persona",
            command=self.eliminar_persona,
            fg_color="#e67e22",
            hover_color="#d35400"
        ).pack(fill=tk.X, padx=2, pady=2)

        # Actualizar Árbol
        ctk.CTkButton(
            self.button_frame,
            text="🔄 Actualizar Árbol",
            command=self.actualizar_arbol,
            fg_color="#34495e",
            hover_color="#2c3e50"
        ).pack(fill=tk.X, padx=2, pady=2)

        # Ver Timeline de Persona
        ctk.CTkButton(
            self.button_frame,
            text="🕰️ Ver Timeline",
            command=self.ver_timeline_persona,
            fg_color="#9b59b6",
            hover_color="#8e44ad"
        ).pack(fill=tk.X, padx=2, pady=2)

        # Exportar a GEDCOM
        ctk.CTkButton(
            self.button_frame,
            text="💾 Exportar a GEDCOM",
            command=self.exportar_gedcom,
            fg_color="#1db954",
            hover_color="#1ed760"
        ).pack(fill=tk.X, padx=2, pady=2)

    def limpiar_historial(self):
        if messagebox.askyesno("Confirmar", "¿Estás seguro de limpiar todo el historial?"):
            for person in self.family.members:
                person.history.clear()
            self.update_history()

    def agregar_evento_manual(self):
        if not self.family.members:
            messagebox.showwarning("Advertencia", "No hay personas en la familia.")
            return

        def on_save(data):
            cedula = data["cedula"]
            evento = data["event"]
            persona = self.family.get_member_by_cedula(cedula)
            if persona:
                persona.add_history(evento)
                self.update_history()
            else:
                messagebox.showerror("Error", "Cédula no encontrada.")

        from gui.forms import PersonForm
        PersonForm(self.parent, title="Agregar Evento Manualmente", on_save=on_save, is_event_form=True, family=self.family)

    def buscar_persona_en_historial(self):
        def on_search():
            cedula = entry.get().strip()
            if not cedula:
                messagebox.showerror("Error", "Ingrese una cédula")
                return
                
            persona = self.family.get_member_by_cedula(cedula)
            if persona:
                # Resaltar en el texto
                self.history_text.tag_remove("highlight", "1.0", tk.END)
                start = "1.0"
                found = False
                while True:
                    start = self.history_text.search(cedula, start, stopindex=tk.END)
                    if not start:
                        break
                    end = f"{start}+{len(cedula)}c"
                    self.history_text.tag_add("highlight", start, end)
                    start = end
                    found = True
                    
                if found:
                    self.history_text.tag_config("highlight", background="yellow", foreground="black")
                    messagebox.showinfo("Éxito", f"Se encontró a {persona.first_name}")
                else:
                    messagebox.showwarning("Advertencia", "No se encontró la cédula en el texto")
            else:
                messagebox.showerror("Error", "Cédula no encontrada.")
        
        # CREAR Y CONFIGURAR LA VENTANA EMERGENTE CORRECTAMENTE
        search_window = ctk.CTkToplevel(self.parent)
        search_window.title("Buscar Persona por Cédula")
        search_window.geometry("300x150")
        
        # Configuración crítica para ventanas modales
        search_window.transient(self.parent)  # Hacer que la ventana sea transitoria
        search_window.grab_set()  # Capturar el foco
        search_window.focus_force()  # Forzar el foco
        
        ctk.CTkLabel(search_window, text="Ingrese la cédula:").pack(pady=10)
        entry = ctk.CTkEntry(search_window, placeholder_text="Ej: 123456789")
        entry.pack(pady=5)
        
        ctk.CTkButton(
            search_window, 
            text="Buscar", 
            command=on_search,
            fg_color="#1db954"
        ).pack(pady=10)
        
        # Esperar a que la ventana se cierre
        self.parent.wait_window(search_window)

    def ver_timeline_persona(self):
        """Muestra timeline cronológico de una persona"""
        def on_timeline():
            cedula = entry.get().strip()
            if not cedula:
                messagebox.showerror("Error", "Ingrese una cédula")
                return
                
            persona = self.family.get_member_by_cedula(cedula)
            if persona:
                # Importar el visualizador de timeline
                from utils.timeline_visualizer import TimelineVisualizer
                TimelineVisualizer.create_timeline_window(persona)
            else:
                messagebox.showerror("Error", "Cédula no encontrada.")
        
        # Crear ventana de entrada
        search_window = ctk.CTkToplevel(self.parent)
        search_window.title("Ver Timeline de Persona")
        search_window.geometry("300x150")
        
        # Configuración crítica para ventanas modales
        search_window.transient(self.parent)
        search_window.grab_set()
        search_window.focus_force()
        
        ctk.CTkLabel(search_window, text="Ingrese la cédula:").pack(pady=10)
        entry = ctk.CTkEntry(search_window, placeholder_text="Ej: 123456789")
        entry.pack(pady=5)
        
        ctk.CTkButton(
            search_window, 
            text="Ver Timeline", 
            command=on_timeline,
            fg_color="#9b59b6"
        ).pack(pady=10)
        
        # Esperar a que la ventana se cierre
        self.parent.wait_window(search_window)

    def ver_detalles_persona(self):
        def on_view():
            cedula = entry.get().strip()
            if not cedula:
                messagebox.showerror("Error", "Ingrese una cédula")
                return
                
            persona = self.family.get_member_by_cedula(cedula)
            if persona:
                info = (
                    f"👤 {persona.first_name} {persona.last_name}\n"
                    f"🆔 Cédula: {persona.cedula}\n"
                    f"🎂 Fecha de Nacimiento: {persona.birth_date}\n"
                    f"🚻 Género: {persona.gender}\n"
                    f"🏠 Provincia: {persona.province}\n"
                    f"💍 Estado Civil: {persona.marital_status}\n"
                    f"✅ Vivo: {'Sí' if persona.alive else 'No'}\n"
                )
                if not persona.alive and persona.death_date:
                    info += f"⚰️ Fecha de Fallecimiento: {persona.death_date}\n"
                    
                # Relaciones
                relaciones = []
                if persona.father:
                    relaciones.append(f"👨 Padre: {persona.father.first_name} {persona.father.last_name}")
                if persona.mother:
                    relaciones.append(f"👩 Madre: {persona.mother.first_name} {persona.mother.last_name}")
                if persona.spouse:
                    relaciones.append(f"💑 Pareja: {persona.spouse.first_name} {persona.spouse.last_name}")
                if persona.children:
                    hijos = ", ".join([f"{c.first_name}" for c in persona.children])
                    relaciones.append(f"👶 Hijos: {hijos}")
                if persona.siblings:
                    hermanos = ", ".join([f"{s.first_name}" for s in persona.siblings])
                    relaciones.append(f"🧍 Hermanos: {hermanos}")
                    
                info += "\n" + "\n".join(relaciones) if relaciones else ""
                
                # Mostrar en popup
                detail_window = ctk.CTkToplevel(self.parent)
                detail_window.title(f"Detalles de {persona.first_name}")
                detail_window.geometry("400x500")
                
                # Configuración crítica para ventanas modales
                detail_window.transient(self.parent)
                detail_window.grab_set()
                detail_window.focus_force()
                
                text_widget = tk.Text(detail_window, bg="#2a2a2a", fg="white", font=("Arial", 10))
                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                text_widget.insert(tk.END, info)
                text_widget.config(state="disabled")
                
                # Botón para cerrar
                ctk.CTkButton(
                    detail_window,
                    text="Cerrar",
                    command=detail_window.destroy,
                    fg_color="#e74c3c"
                ).pack(pady=10)
                
                # Esperar a que la ventana se cierre
                self.parent.wait_window(detail_window)
            else:
                messagebox.showerror("Error", "Cédula no encontrada.")
        
        # CREAR Y CONFIGURAR LA VENTANA EMERGENTE CORRECTAMENTE
        search_window = ctk.CTkToplevel(self.parent)
        search_window.title("Ver Detalles de Persona")
        search_window.geometry("300x150")
        
        # Configuración crítica para ventanas modales
        search_window.transient(self.parent)
        search_window.grab_set()
        search_window.focus_force()
        
        ctk.CTkLabel(search_window, text="Ingrese la cédula:").pack(pady=10)
        entry = ctk.CTkEntry(search_window, placeholder_text="Ej: 123456789")
        entry.pack(pady=5)
        
        ctk.CTkButton(
            search_window, 
            text="Ver Detalles", 
            command=on_view,
            fg_color="#1db954"
        ).pack(pady=10)
        
        # Esperar a que la ventana se cierre
        self.parent.wait_window(search_window)

    def eliminar_persona(self):
        def on_delete():
            cedula = entry.get().strip()
            if not cedula:
                messagebox.showerror("Error", "Ingrese una cédula")
                return
                
            # USAR EL SERVICIO COMPLETO DE ELIMINACIÓN
            exito, mensaje = PersonaService.eliminar_persona(self.family, cedula)
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                # Actualizar historial y árbol
                self.update_history()
                try:
                    # Intentar actualizar el árbol de forma segura
                    if hasattr(self.parent, 'draw_tree'):
                        self.parent.draw_tree()
                except Exception as e:
                    print(f"Error al actualizar el árbol: {e}")
            else:
                messagebox.showerror("Error", mensaje)
        
        # CREAR Y CONFIGURAR LA VENTANA EMERGENTE CORRECTAMENTE
        delete_window = ctk.CTkToplevel(self.parent)
        delete_window.title("Eliminar Persona")
        delete_window.geometry("300x150")
        
        # Configuración crítica para ventanas modales
        delete_window.transient(self.parent)
        delete_window.grab_set()
        delete_window.focus_force()
        
        ctk.CTkLabel(delete_window, text="Cédula de la persona a eliminar:").pack(pady=10)
        entry = ctk.CTkEntry(delete_window, placeholder_text="Ej: 123456789")
        entry.pack(pady=5)
        
        ctk.CTkButton(
            delete_window, 
            text="Eliminar", 
            command=on_delete,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        ).pack(pady=10)
        
        # Esperar a que la ventana se cierre
        self.parent.wait_window(delete_window)

    def actualizar_arbol(self):
        self.parent.draw_tree()

    def exportar_gedcom(self):
        try:
            from services.persona_service import exportar_a_gedcom
            gedcom_content = exportar_a_gedcom(self.family)
            
            # Guardar en archivo
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".ged",
                filetypes=[("GEDCOM files", "*.ged"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(gedcom_content)
                messagebox.showinfo("Éxito", f"Árbol exportado a {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")

    def update_history(self):
        """Actualiza el contenido del historial"""
        self.history_text.delete(1.0, tk.END)
        for person in self.family.members:
            self.history_text.insert(tk.END, f"👤 {person}\n", "person")
            for event in person.history:
                self.history_text.insert(tk.END, f"  • {event}\n", "event")
            self.history_text.insert(tk.END, "\n")