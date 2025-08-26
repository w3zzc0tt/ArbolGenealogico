# main.py
import logging
import sys

# Configurar logging para ver errores detallados
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

try:
    # Intentar configurar matplotlib solo si es necesario
    try:
        import matplotlib
        matplotlib.use('TkAgg')  # Configurar el backend de matplotlib explícitamente
    except Exception as e:
        logging.warning(f"No se pudo configurar matplotlib backend: {str(e)}")
    
    import customtkinter as ctk
    from gui.app import GenealogyApp
    
    if __name__ == "__main__":
        try:
            root = ctk.CTk()
            app = GenealogyApp(root)
            root.mainloop()
        except Exception as e:
            logging.error(f"Error crítico al iniciar la aplicación: {str(e)}", exc_info=True)
            # Crear una ventana básica para mostrar el error
            try:
                error_root = ctk.CTk()
                error_root.title("Error de aplicación")
                error_root.geometry("500x300")
                error_frame = ctk.CTkFrame(error_root)
                error_frame.pack(fill="both", expand=True, padx=20, pady=20)
                ctk.CTkLabel(error_frame,
                            text="¡Error al iniciar la aplicación!",
                            font=("Arial", 16, "bold"),
                            text_color="red").pack(pady=10)
                ctk.CTkLabel(error_frame,
                            text=f"Detalles del error:\n{str(e)}",
                            wraplength=450,
                            justify="left").pack(pady=10)
                ctk.CTkButton(error_frame,
                            text="Cerrar",
                            command=error_root.destroy,
                            fg_color="#e74c3c").pack(pady=10)
                error_root.mainloop()
            except Exception as gui_error:
                # Si no podemos mostrar el error con GUI, imprimir en consola
                logging.error(f"Error al mostrar ventana de error: {str(gui_error)}", exc_info=True)
                print("\n" + "="*50)
                print("ERROR CRÍTICO AL INICIAR LA APLICACIÓN")
                print("="*50)
                print(f"Detalles del error:\n{str(e)}")
                print("\nNo se pudo mostrar la ventana de error debido a:")
                print(f"{str(gui_error)}")
                print("="*50)
                print("Por favor, revisa el archivo de log para más detalles.")
                print("="*50)
                sys.exit(1)

except Exception as import_error:
    # Manejar errores en los imports iniciales
    logging.critical(f"Error FATAL al importar módulos: {str(import_error)}", exc_info=True)
    print("\n" + "="*50)
    print("ERROR FATAL AL IMPORTAR MÓDULOS")
    print("="*50)
    print(f"Detalles del error:\n{str(import_error)}")
    print("\nPosibles causas:")
    print("1. customtkinter no está instalado correctamente")
    print("2. Falta una dependencia crítica")
    print("3. Error en los archivos del proyecto")
    print("="*50)
    print("Por favor, revisa:")
    print("1. Si has instalado todas las dependencias: pip install -r requirements.txt")
    print("2. Si los archivos del proyecto están completos")
    print("3. El archivo de log para más detalles")
    print("="*50)
    sys.exit(1)