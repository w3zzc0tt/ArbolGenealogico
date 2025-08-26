# main.py
import matplotlib
matplotlib.use('TkAgg')  # Configurar el backend de matplotlib explícitamente
import customtkinter as ctk
from gui.app import GenealogyApp
import logging

# Configurar logging para ver errores detallados
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    try:
        root = ctk.CTk()
        app = GenealogyApp(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"Error crítico al iniciar la aplicación: {str(e)}", exc_info=True)
        # Crear una ventana básica para mostrar el error
        error_root = ctk.CTk()
        error_root.title("Error de aplicación")
        error_root.geometry("500x300")
        
        error_frame = ctk.CTkFrame(error_root)
        error_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            error_frame, 
            text="¡Error al iniciar la aplicación!", 
            font=("Arial", 16, "bold"),
            text_color="red"
        ).pack(pady=10)
        
        ctk.CTkLabel(
            error_frame,
            text=f"Detalles del error:\n{str(e)}",
            wraplength=450,
            justify="left"
        ).pack(pady=10)
        
        ctk.CTkButton(
            error_frame,
            text="Cerrar",
            command=error_root.destroy,
            fg_color="#e74c3c"
        ).pack(pady=10)
        
        error_root.mainloop()