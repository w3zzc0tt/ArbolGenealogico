import customtkinter as ctk
import tkinter as tk
import sys
import os

# Agregar el directorio raíz al path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from utils.graph_visualizer import FamilyGraphVisualizer
    HAS_VISUALIZER = True
except ImportError:
    HAS_VISUALIZER = False
    print("Advertencia: No se pudo importar FamilyGraphVisualizer")

try:
    from forms import PersonForm
    from models import Family, Person
except ImportError:
    from forms import PersonForm
    from models import Family, Person

class GenealogyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Árbol Genealógico")
        self.root.geometry("1200x800")

        # Variables
        self.family = Family(1, "Mi Familia")
        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Solo pestaña del árbol (sin formulario)
        self.notebook = ctk.CTkTabview(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree_tab = self.notebook.add("Árbol Genealógico")

        self.setup_tree_tab()

    def setup_tree_tab(self):
        frame = ctk.CTkFrame(self.tree_tab)
        frame.pack(fill=tk.BOTH, expand=True)

        # Canvas para el árbol
        self.tree_canvas = tk.Canvas(frame, bg="#2a2a2a", highlightthickness=0)
        self.tree_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Botón para agregar Ego si no hay nadie
        if not self.family.members:
            self.add_ego_button = ctk.CTkButton(
                frame,
                text="➕ Agregar Persona Principal (Ego)",
                command=self.open_person_form_for_ego,
                font=("Arial", 14, "bold"),
                fg_color="#1db954",
                hover_color="#1ed760"
            )
            self.add_ego_button.pack(pady=20)

        self.draw_tree()

    def open_person_form_for_ego(self):
        """Abre el formulario para agregar al Ego"""
        def on_save(data):
            person = Person(
                cedula=data["cedula"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                birth_date=data["birth_date"],
                gender=data["gender"],
                province=data["province"],
                death_date=data["death_date"]
            )
            # Establecer el estado civil desde el formulario
            person.marital_status = data["marital_status"]
            self.family.members.append(person)
            if hasattr(self, 'add_ego_button'):
                self.add_ego_button.destroy()
            self.draw_tree()

        form = PersonForm(self.root, title="Agregar Persona Principal (Ego)", on_save=on_save)
        form.focus()

    def draw_tree(self):
        """Dibuja el árbol genealógico"""
        self.tree_canvas.delete("all")
        if not self.family.members:
            self.tree_canvas.create_text(
                600, 400,
                text="No hay personas en el árbol",
                font=("Arial", 16),
                fill="white"
            )
            return

        try:
            # Usar el visualizador de grafos para dibujar el árbol
            if HAS_VISUALIZER:
                visualizer = FamilyGraphVisualizer()
                visualizer.draw_family_tree(self.family, self.tree_canvas)
                
                # Conectar el menú contextual a los nodos
                self._connect_menu_to_nodes()
            else:
                # Dibujo básico si no hay visualizador
                self._draw_basic_tree()
                
        except Exception as e:
            print(f"Error al dibujar el árbol: {e}")
            self.tree_canvas.create_text(
                600, 400,
                text=f"Error al dibujar el árbol: {str(e)}",
                font=("Arial", 12),
                fill="red"
            )

    def _draw_basic_tree(self):
        """Dibuja un árbol básico cuando no hay visualizador disponible"""
        canvas_width = self.tree_canvas.winfo_width() or 1200
        canvas_height = self.tree_canvas.winfo_height() or 800
        
        # Posicionamiento simple
        x_spacing = canvas_width / (len(self.family.members) + 1)
        y = canvas_height / 2
        
        for i, person in enumerate(self.family.members):
            x = (i + 1) * x_spacing
            
            # Dibujar nodo básico
            radius = 25
            color = "#3b8ed0" if person.alive else "#d35f5f"
            self.tree_canvas.create_oval(x-radius, y-radius, x+radius, y+radius, 
                                       fill=color, outline="#1f7dbf", width=2)
            
            # Nombre
            name_text = f"{person.first_name}\n{person.last_name}"
            self.tree_canvas.create_text(x, y-10, text=name_text, font=("Arial", 8, "bold"), 
                                       fill="white", anchor="center")
            
            # Cédula
            self.tree_canvas.create_text(x, y+10, text=person.cedula, font=("Arial", 7), 
                                       fill="lightgray", anchor="center")

    def _connect_menu_to_nodes(self):
        """Conecta el menú contextual a todos los nodos del canvas"""
        # Buscar todos los elementos ovalados (nodos) en el canvas
        nodes = self.tree_canvas.find_withtag("oval")
        
        for node in nodes:
            # Vincular evento de clic derecho para menú contextual
            self.tree_canvas.tag_bind(node, "<Button-3>", self._show_context_menu)
            
            # También vincular clic izquierdo para selección
            self.tree_canvas.tag_bind(node, "<Button-1>", self._select_node)

    def _show_context_menu(self, event):
        """Muestra el menú contextual para el nodo"""
        # Encontrar el nodo más cercano al clic
        closest = self.tree_canvas.find_closest(event.x, event.y)
        if closest:
            print(f"Menú contextual para nodo {closest[0]}")
            # Aquí se puede implementar un menú contextual real
            
    def _select_node(self, event):
        """Selecciona un nodo al hacer clic"""
        closest = self.tree_canvas.find_closest(event.x, event.y)
        if closest:
            print(f"Nodo seleccionado: {closest[0]}")

# === PUNTO DE ENTRADA ===
if __name__ == "__main__":
    root = ctk.CTk()
    app = GenealogyApp(root)
    root.mainloop()
