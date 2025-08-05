# PROYECTO_RAIZ/interfaz/interfaz_horarios.py

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# --- Inicio: Ajuste de ruta para importar db_manager ---
# Obtener la ruta del directorio actual (donde está interfaz_horarios.py, o sea, 'interfaz')
directorio_actual_interfaz = os.path.dirname(os.path.abspath(__file__))
# Subir un nivel para llegar a PROYECTO_RAIZ
proyecto_raiz = os.path.dirname(directorio_actual_interfaz)
# Añadir PROYECTO_RAIZ al sys.path para que Python pueda encontrar la carpeta 'database'
sys.path.append(proyecto_raiz)
# --- Fin: Ajuste de ruta ---

# Ahora podemos importar db_manager
from database import db_manager

class AplicacionGeneradorHorarios:
    def __init__(self, master_window):
        self.master = master_window
        self.master.title("Generador de Horarios - Lic. en Informática")
        self.master.geometry("800x600")

        self.conexion_db = None # Para la conexión a la BD
        self.checkbox_vars_materias = {} # {codigo_materia: tk.BooleanVar()}
        self.preferencia_turno_var = tk.StringVar(value="cualquiera")

        self._configurar_estilos_ttk()
        self._conectar_a_base_de_datos() # Intentar conectar primero
        
        if self.conexion_db: # Solo crear interfaz si la conexión fue exitosa
            self._crear_widgets_principales()
            self._cargar_materias_en_checkboxes()
        else:
            # Si no hay conexión, mostrar un mensaje y quizás deshabilitar la UI o cerrar.
            # El mensaje de error ya se muestra en _conectar_a_base_de_datos
            # Podríamos añadir un label grande en la ventana indicando el problema.
            error_label = ttk.Label(self.master, 
                                   text="Error Crítico: No se pudo conectar a la base de datos.\n"
                                        "La aplicación no puede funcionar.",
                                   font=("Helvetica", 14, "bold"), foreground="red")
            error_label.pack(padx=20, pady=50, expand=True)


        self.master.protocol("WM_DELETE_WINDOW", self._al_intentar_cerrar)

    def _configurar_estilos_ttk(self):
        style = ttk.Style()
        # Puedes probar otros temas si 'clam' no te gusta o no está disponible: 
        # 'alt', 'default', 'classic'
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam') 
        
        style.configure("TLabelFrame.Label", font=("Helvetica", 12, "bold"))
        style.configure("Accent.TButton", font=("Helvetica", 11, "bold"), padding=5)
        style.configure("Header.TLabel", font=("Helvetica", 18, "bold"))

    def _conectar_a_base_de_datos(self):
        try:
            # La ruta a la base de datos es relativa a PROYECTO_RAIZ
            # db_manager.DATABASE_PATH ya debería estar configurado correctamente
            # dentro de db_manager.py para apuntar a 'database/horarios.db'
            self.conexion_db = db_manager.crear_conexion() 
            if self.conexion_db is None:
                # El error ya se imprime desde db_manager.crear_conexion
                messagebox.showerror(
                    "Error de Base de Datos",
                    "No se pudo conectar a la base de datos 'horarios.db'.\n"
                    "Por favor, asegúrate de que 'database/horarios.db' exista y "
                    "que el script 'database/db_manager.py' se haya ejecutado para crearla y poblarla."
                )
        except ImportError:
            messagebox.showerror(
                "Error de Importación",
                "No se pudo importar el módulo 'db_manager' desde la carpeta 'database'.\n"
                "Asegúrate de que la estructura de carpetas es correcta y que 'PROYECTO_RAIZ/database/' existe."
            )
        except Exception as e:
            messagebox.showerror("Error Inesperado de Conexión", f"Ocurrió un error: {e}")

    def _crear_widgets_principales(self):
        # Título
        titulo = ttk.Label(self.master, text="Sistema Generador de Horarios", style="Header.TLabel")
        titulo.pack(pady=20)

        # --- Sección de selección de materias (con scroll) ---
        frame_materias_contenedor = ttk.LabelFrame(self.master, text="Selecciona tus materias deseadas", padding=(10, 5))
        frame_materias_contenedor.pack(padx=10, pady=10, fill="x")

        # Canvas para la lista scrollable de materias
        self.canvas_materias = tk.Canvas(frame_materias_contenedor, borderwidth=0, background="#ffffff", height=200) # Altura inicial
        
        # Frame que irá dentro del Canvas y contendrá los checkboxes
        self.frame_interno_checkboxes = ttk.Frame(self.canvas_materias) # No aplicar estilo aquí directamente si el canvas es blanco
        
        scrollbar_vertical_materias = ttk.Scrollbar(frame_materias_contenedor, orient="vertical", command=self.canvas_materias.yview)
        self.canvas_materias.configure(yscrollcommand=scrollbar_vertical_materias.set)

        scrollbar_vertical_materias.pack(side="right", fill="y")
        self.canvas_materias.pack(side="left", fill="both", expand=True)
        
        # Añadir el frame interno al canvas
        self.id_ventana_frame_interno = self.canvas_materias.create_window((0, 0), window=self.frame_interno_checkboxes, anchor="nw")

        # Cuando el frame interno cambie de tamaño, actualizar el scrollregion del canvas
        self.frame_interno_checkboxes.bind("<Configure>", self._on_frame_configure)
        
        # Bindings para la rueda del mouse (multiplataforma)
        self.canvas_materias.bind_all("<MouseWheel>", self._on_mousewheel) # Windows, macOS
        self.canvas_materias.bind_all("<Button-4>", self._on_mousewheel)   # Linux (scroll up)
        self.canvas_materias.bind_all("<Button-5>", self._on_mousewheel)   # Linux (scroll down)


        # --- Preferencias de horario ---
        frame_preferencias = ttk.LabelFrame(self.master, text="Preferencias de horario", padding=(10, 5))
        frame_preferencias.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frame_preferencias, text="Turno preferido:").pack(side=tk.LEFT, padx=(0,5))
        turnos = [("Cualquiera", "cualquiera"), ("Mañana", "mañana"), ("Tarde", "tarde")]
        for texto, valor in turnos:
            rb = ttk.Radiobutton(frame_preferencias, text=texto, variable=self.preferencia_turno_var, value=valor)
            rb.pack(side=tk.LEFT, padx=5)


        # --- Botón para generar horario ---
        btn_generar = ttk.Button(self.master, text="Generar Horario", command=self.accion_generar_horario_solicitado, style="Accent.TButton")
        btn_generar.pack(pady=20)
        
        # --- Área para mostrar resultados ---
        self.frame_resultados_horarios = ttk.LabelFrame(self.master, text="Horarios Sugeridos", padding=(10,5))
        self.frame_resultados_horarios.pack(padx=10, pady=10, fill="both", expand=True)
        ttk.Label(self.frame_resultados_horarios, text="Los horarios generados se mostrarán aquí...").pack(pady=10, padx=10)


    def _on_frame_configure(self, event=None):
        """Actualiza el scrollregion del canvas cuando el frame interno cambia."""
        self.canvas_materias.configure(scrollregion=self.canvas_materias.bbox("all"))

    def _on_mousewheel(self, event):
        """Maneja el evento de la rueda del mouse para el canvas de materias."""
        if event.num == 4: # Linux scroll up
            self.canvas_materias.yview_scroll(-1, "units")
        elif event.num == 5: # Linux scroll down
            self.canvas_materias.yview_scroll(1, "units")
        else: # Windows, macOS (delta)
             # A veces delta es 120 o -120, otras veces 1 o -1. Normalizar.
            if abs(event.delta) >= 120:
                scroll_val = int(-1 * (event.delta / 120))
            else:
                scroll_val = -1 * event.delta
            self.canvas_materias.yview_scroll(scroll_val, "units")


    def _cargar_materias_en_checkboxes(self):
        if not self.conexion_db:
            # Este caso debería ser manejado por el chequeo en __init__
            # Pero por si acaso, y para el frame específico:
            ttk.Label(self.frame_interno_checkboxes, text="No se pueden cargar materias: Sin conexión a BD.").pack()
            return

        try:
            # Obtener (codigo_materia, nombre_materia, creditos)
            materias_tuplas = db_manager.obtener_todas_las_materias_simple(self.conexion_db)

            if not materias_tuplas:
                ttk.Label(self.frame_interno_checkboxes, text="No hay materias disponibles en la base de datos.").pack()
                return

            # Limpiar checkboxes anteriores si esta función se llamara de nuevo (para refrescar)
            for widget in self.frame_interno_checkboxes.winfo_children():
                widget.destroy()
            self.checkbox_vars_materias.clear()

            for codigo, nombre, creditos in materias_tuplas:
                var = tk.BooleanVar(value=False) # Por defecto no seleccionada
                texto_chk = f"{nombre} ({codigo})"
                if creditos is not None:
                    texto_chk += f" - {creditos} créd."
                
                checkbox = ttk.Checkbutton(self.frame_interno_checkboxes, text=texto_chk, variable=var)
                checkbox.pack(anchor="w", padx=5, pady=2) # "w" (West) alinea a la izquierda
                self.checkbox_vars_materias[codigo] = var
            
            # Es crucial actualizar el frame interno para que el canvas obtenga el tamaño correcto
            # y configure bien la scrollregion.
            self.frame_interno_checkboxes.update_idletasks()
            self._on_frame_configure() # Llama a la función que ajusta el scrollregion

        except Exception as e:
            messagebox.showerror("Error al Cargar Materias", f"Ocurrió un error: {e}")
            ttk.Label(self.frame_interno_checkboxes, text=f"Error al cargar: {e}").pack()


    def accion_generar_horario_solicitado(self):
        if not self.conexion_db:
            messagebox.showerror("Error", "No hay conexión a la base de datos para generar horarios.")
            return

        materias_elegidas_codigos = [
            codigo for codigo, var in self.checkbox_vars_materias.items() if var.get()
        ]
        
        preferencia_turno_seleccionada = self.preferencia_turno_var.get()

        if not materias_elegidas_codigos:
            messagebox.showwarning("Sin Selección", "Por favor, selecciona al menos una materia.")
            return

        # Limpiar resultados anteriores
        for widget in self.frame_resultados_horarios.winfo_children():
            widget.destroy()
        
        progreso_label = ttk.Label(self.frame_resultados_horarios, text="Generando horarios, por favor espera...")
        progreso_label.pack(pady=10, padx=10)
        self.master.update_idletasks() # Forzar actualización de la UI

        print(f"LOG: Materias para generar horario: {materias_elegidas_codigos}")
        print(f"LOG: Preferencia de turno: {preferencia_turno_seleccionada}")

        # --- Aquí es donde se llamaría a la lógica de la Fase 2 y se mostrarían los resultados (Fase 4) ---
        # from logic import scheduler
        # horarios = scheduler.generar_horarios_posibles(
        #     self.conexion_db, 
        #     materias_elegidas_codigos,
        #     preferencias={'turno': preferencia_turno_seleccionada}
        # )
        # self._mostrar_horarios_generados(horarios) # Una nueva función para la Fase 4

        # Simulación por ahora:
        progreso_label.destroy() # Quitar el mensaje de "Generando..."
        if materias_elegidas_codigos:
            info_texto = f"Solicitud para generar horarios con:\n" \
                         f"Materias: {', '.join(materias_elegidas_codigos)}\n" \
                         f"Preferencia de Turno: {preferencia_turno_seleccionada.capitalize()}\n\n" \
                         "(La visualización de horarios reales se implementará en la Fase 4)"
            ttk.Label(self.frame_resultados_horarios, text=info_texto, justify=tk.LEFT).pack(anchor="w", padx=10, pady=5)
        else:
            ttk.Label(self.frame_resultados_horarios, text="No se seleccionaron materias.").pack(pady=10, padx=10)


    def _al_intentar_cerrar(self):
        if messagebox.askokcancel("Confirmar Salida", "¿Estás seguro de que quieres salir?"):
            if self.conexion_db:
                self.conexion_db.close()
                print("LOG: Conexión a la base de datos cerrada.")
            self.master.destroy()

# --- Punto de entrada para ejecutar la aplicación ---
if __name__ == "__main__":
    ventana_raiz_tk = tk.Tk()
    app = AplicacionGeneradorHorarios(ventana_raiz_tk)
    ventana_raiz_tk.mainloop()
