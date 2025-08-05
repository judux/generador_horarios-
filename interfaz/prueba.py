import tkinter as tk
from tkinter import ttk, messagebox, font
from tkinter import StringVar, BooleanVar
import sys
import os
from datetime import datetime
import calendar
import sqlite3

# --- Inicio: Ajuste de ruta para importar db_manager ---
# Obtener la ruta del directorio actual (donde está interfaz_avanzada_horarios.py, o sea, 'interfaz')
directorio_actual_interfaz = os.path.dirname(os.path.abspath(__file__))
# Subir un nivel para llegar a PROYECTO_RAIZ
proyecto_raiz = os.path.dirname(directorio_actual_interfaz)
# Añadir PROYECTO_RAIZ al sys.path para que Python pueda encontrar la carpeta 'database'
sys.path.append(proyecto_raiz)
# --- Fin: Ajuste de ruta ---

# Ahora podemos importar db_manager
from database import db_manager

# Constantes para la aplicación
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
HORAS_CLASE = ["07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00",
               "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]
COLORES_MATERIAS = [
    "#FFD700", "#FF6347", "#7FFFD4", "#DDA0DD", "#90EE90",
    "#87CEFA", "#FFA07A", "#FFFACD", "#98FB98", "#D8BFD8"
]

class AplicacionAvanzadaHorarios:
    def __init__(self, master_window):
        self.master = master_window
        self.master.title("Sistema Avanzado de Horarios - Lic. en Informática")
        self.master.geometry("1100x750")
        self.master.minsize(900, 600)

        # Variables de la aplicación
        self.conexion_db = None
        self.checkbox_vars_obligatorias = {} # {codigo_materia: BooleanVar()} para obligatorias
        self.checkbox_vars_electivas = {}    # {codigo_materia: BooleanVar()} para electivas
        self.materias_cursadas = {}  # {codigo_materia: BooleanVar()}
        self.materias_info = {}      # {codigo_materia: (nombre_materia, creditos, tipo_materia)}
        self.preferencia_turno_var = StringVar(value="cualquiera")
        self.current_tab = None      # Para rastrear la pestaña actual
        self.horario_generado = None # Para almacenar el último horario generado
        self.color_mapping = {}      # Mapeo de materias a colores
        self.MAX_MATERIAS_SELECCIONABLES = 5 # Límite de materias

        # Fuentes personalizadas
        self.fuente_titulo = font.Font(family="Helvetica", size=16, weight="bold")
        self.fuente_subtitulo = font.Font(family="Helvetica", size=12, weight="bold")
        self.fuente_normal = font.Font(family="Helvetica", size=10)

        # Inicializar la interfaz
        self._configurar_estilos_ttk()
        self._conectar_a_base_de_datos()

        if self.conexion_db:
            self._crear_widgets_principales()
            self._cargar_datos_materias() # Cargar TODAS las materias al inicio
            self._cargar_historial_materias() # Cargar historial al inicio
        else:
            error_label = ttk.Label(
                self.master,
                text="Error Crítico: No se pudo conectar a la base de datos.\n"
                     "La aplicación no puede funcionar.",
                font=self.fuente_titulo,
                foreground="red"
            )
            error_label.pack(padx=20, pady=50, expand=True)

        self.master.protocol("WM_DELETE_WINDOW", self._al_intentar_cerrar)

    def _configurar_estilos_ttk(self):
        """Configura los estilos visuales para la aplicación."""
        style = ttk.Style()
        available_themes = style.theme_names()

        # Usar un tema moderno si está disponible
        if 'clam' in available_themes:
            style.theme_use('clam')

        # Configuraciones de estilo para diferentes widgets
        style.configure("TLabelFrame.Label", font=("Helvetica", 12, "bold"))
        style.configure("Accent.TButton", font=("Helvetica", 11, "bold"), padding=5)
        style.configure("Header.TLabel", font=("Helvetica", 18, "bold"))
        style.configure("Subtitle.TLabel", font=("Helvetica", 14, "bold"))
        style.configure("Calendar.TFrame", background="#ffffff")
        style.configure("CalendarHeader.TLabel", font=("Helvetica", 11, "bold"), background="#f0f0f0")

        # Estilos para el calendario
        style.configure("DayHeader.TLabel", font=("Helvetica", 10, "bold"), background="#e0e0e0", anchor="center")
        style.configure("TimeSlot.TLabel", font=("Helvetica", 9), background="#f5f5f5", anchor="center")
        style.configure("HourLabel.TLabel", font=("Helvetica", 9), background="#e0e0e0", anchor="center")

        # Estilo para pestañas
        style.configure("TNotebook.Tab", padding=[10, 5], font=("Helvetica", 11))

        # Estilo para el botón de guardar historial
        style.configure("Save.TButton", font=("Helvetica", 10), padding=3)

        # Estilo para los Checkbuttons de materias
        style.configure("Materia.TCheckbutton", font=("Helvetica", 10))

    def _conectar_a_base_de_datos(self):
        """Establece la conexión con la base de datos SQLite."""
        try:
            self.conexion_db = db_manager.crear_conexion()

            if self.conexion_db is None:
                messagebox.showerror(
                    "Error de Base de Datos",
                    "No se pudo conectar a la base de datos 'horarios.db'.\n"
                    "Por favor, asegúrate de que 'database/horarios.db' exista y "
                    "que el script 'database/db_manager.py' se haya ejecutado para crearla y poblarla."
                )

            # Verificar si existe la tabla de historial; crearla si no existe
            self._crear_tabla_historial()

        except ImportError:
            messagebox.showerror(
                "Error de Importación",
                "No se pudo importar el módulo 'db_manager' desde la carpeta 'database'.\n"
                "Asegúrate de que la estructura de carpetas es correcta y que 'PROYECTO_RAIZ/database/' existe."
            )
        except Exception as e:
            messagebox.showerror("Error Inesperado de Conexión", f"Ocurrió un error: {e}")

    def _crear_tabla_historial(self):
        """Crea la tabla de historial de materias cursadas si no existe."""
        try:
            cursor = self.conexion_db.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS HistorialMateriasCursadas (
                    codigo_materia TEXT PRIMARY KEY,
                    fecha_registro TEXT,
                    nota REAL,
                    FOREIGN KEY (codigo_materia) REFERENCES Materias (codigo_materia) ON DELETE CASCADE ON UPDATE CASCADE
                );
            """)
            self.conexion_db.commit()
        except sqlite3.Error as e:
            print(f"Error al crear tabla de historial: {e}")

    def _crear_widgets_principales(self):
        """Crea la estructura principal de widgets para la interfaz."""
        # Título principal
        titulo = ttk.Label(self.master, text="Sistema Avanzado de Horarios Académicos", style="Header.TLabel")
        titulo.pack(pady=(20, 10))

        # Notebook (pestañas) para organizar la interfaz
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Crear las diferentes pestañas
        self.tab_generador = ttk.Frame(self.notebook)
        self.tab_historial = ttk.Frame(self.notebook)
        self.tab_calendario = ttk.Frame(self.notebook)
        self.tab_config = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_generador, text="Generador de Horarios")
        self.notebook.add(self.tab_historial, text="Historial Académico")
        self.notebook.add(self.tab_calendario, text="Vista Calendario")
        self.notebook.add(self.tab_config, text="Configuración")

        # Configurar el contenido de cada pestaña
        self._configurar_tab_generador()
        self._configurar_tab_historial()
        self._configurar_tab_calendario()
        self._configurar_tab_config()

        # Vincular evento de cambio de pestaña
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

    def _on_tab_change(self, event):
        """Maneja el cambio entre pestañas."""
        tab_id = self.notebook.select()
        tab_name = self.notebook.tab(tab_id, "text")

        if tab_name == "Vista Calendario" and self.horario_generado:
            # Actualizar la vista de calendario cuando se cambia a esa pestaña
            self._mostrar_horario_en_calendario(self.horario_generado)

    def _configurar_tab_generador(self):
        """Configura la pestaña del generador de horarios."""
        # Frame principal con scroll
        main_frame = ttk.Frame(self.tab_generador)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Sección de selección de materias obligatorias ---
        self.frame_obligatorias_contenedor = ttk.LabelFrame(main_frame, text="Materias Obligatorias del Pensum", padding=(10, 5))
        self.frame_obligatorias_contenedor.pack(padx=10, pady=5, fill="both", expand=True)

        self.canvas_obligatorias = tk.Canvas(self.frame_obligatorias_contenedor, borderwidth=0, background="#ffffff")
        self.frame_interno_obligatorias = ttk.Frame(self.canvas_obligatorias)
        scrollbar_vertical_obligatorias = ttk.Scrollbar(
            self.frame_obligatorias_contenedor,
            orient="vertical",
            command=self.canvas_obligatorias.yview
        )
        self.canvas_obligatorias.configure(yscrollcommand=scrollbar_vertical_obligatorias.set)
        scrollbar_vertical_obligatorias.pack(side="right", fill="y")
        self.canvas_obligatorias.pack(side="left", fill="both", expand=True)
        self.id_ventana_obligatorias = self.canvas_obligatorias.create_window(
            (0, 0), window=self.frame_interno_obligatorias, anchor="nw"
        )
        self.frame_interno_obligatorias.bind("<Configure>", self._on_frame_configure_obligatorias)
        self.canvas_obligatorias.bind("<Configure>", self._on_canvas_configure_obligatorias)
        self.canvas_obligatorias.bind_all("<MouseWheel>", self._on_mousewheel) # Aplica a ambos canvases


        # --- Sección de selección de materias electivas ---
        self.frame_electivas_contenedor = ttk.LabelFrame(main_frame, text="Materias Electivas Disponibles (Máx. 5 en total)", padding=(10, 5))
        self.frame_electivas_contenedor.pack(padx=10, pady=5, fill="both", expand=True)

        self.canvas_electivas = tk.Canvas(self.frame_electivas_contenedor, borderwidth=0, background="#ffffff")
        self.frame_interno_electivas = ttk.Frame(self.canvas_electivas)
        scrollbar_vertical_electivas = ttk.Scrollbar(
            self.frame_electivas_contenedor,
            orient="vertical",
            command=self.canvas_electivas.yview
        )
        self.canvas_electivas.configure(yscrollcommand=scrollbar_vertical_electivas.set)
        scrollbar_vertical_electivas.pack(side="right", fill="y")
        self.canvas_electivas.pack(side="left", fill="both", expand=True)
        self.id_ventana_electivas = self.canvas_electivas.create_window(
            (0, 0), window=self.frame_interno_electivas, anchor="nw"
        )
        self.frame_interno_electivas.bind("<Configure>", self._on_frame_configure_electivas)
        self.canvas_electivas.bind("<Configure>", self._on_canvas_configure_electivas)
        self.canvas_electivas.bind_all("<MouseWheel>", self._on_mousewheel) # Aplica a ambos canvases

        # --- Sección de preferencias ---
        frame_preferencias = ttk.LabelFrame(main_frame, text="Preferencias de horario", padding=(10, 5))
        frame_preferencias.pack(padx=10, pady=10, fill="x")

        # Fila 1: Turno preferido
        frame_turno = ttk.Frame(frame_preferencias)
        frame_turno.pack(fill="x", padx=5, pady=5)

        ttk.Label(frame_turno, text="Turno preferido:", width=15).pack(side=tk.LEFT, padx=(0, 5))

        turnos = [("Cualquiera", "cualquiera"), ("Mañana", "mañana"), ("Tarde", "tarde")]
        for texto, valor in turnos:
            rb = ttk.Radiobutton(frame_turno, text=texto, variable=self.preferencia_turno_var, value=valor)
            rb.pack(side=tk.LEFT, padx=5)

        # Fila 2: Otras preferencias (puedes expandir en el futuro)
        frame_otras_pref = ttk.Frame(frame_preferencias)
        frame_otras_pref.pack(fill="x", padx=5, pady=5)

        self.minimizar_huecos_var = BooleanVar(value=True)
        ttk.Checkbutton(
            frame_otras_pref,
            text="Minimizar huecos entre clases",
            variable=self.minimizar_huecos_var
        ).pack(side=tk.LEFT, padx=(0, 15))

        self.respetar_cursadas_var = BooleanVar(value=True)
        ttk.Checkbutton(
            frame_otras_pref,
            text="Respetar materias ya cursadas",
            variable=self.respetar_cursadas_var
        ).pack(side=tk.LEFT)

        # --- Botón para generar horario ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", padx=10, pady=10)

        btn_generar = ttk.Button(
            btn_frame,
            text="Generar Horario",
            command=self.accion_generar_horario_solicitado,
            style="Accent.TButton"
        )
        btn_generar.pack(side=tk.RIGHT, padx=5)

        btn_limpiar = ttk.Button(
            btn_frame,
            text="Limpiar Selección",
            command=self._limpiar_seleccion
        )
        btn_limpiar.pack(side=tk.RIGHT, padx=5)

    def _limpiar_seleccion(self):
        """Limpia la selección de todas las materias."""
        for var in self.checkbox_vars_obligatorias.values():
            var.set(False)
        for var in self.checkbox_vars_electivas.values():
            var.set(False)

    def _on_canvas_configure_obligatorias(self, event):
        """Ajusta el ancho del frame interno y el scrollregion del canvas de obligatorias."""
        canvas_width = event.width
        self.canvas_obligatorias.itemconfig(self.id_ventana_obligatorias, width=canvas_width)
        self._on_frame_configure_obligatorias()

    def _on_frame_configure_obligatorias(self, event=None):
        """Actualiza el scrollregion del canvas de obligatorias cuando el frame interno cambia."""
        self.canvas_obligatorias.configure(scrollregion=self.canvas_obligatorias.bbox("all"))
        self._ajustar_altura_canvas(self.canvas_obligatorias, self.frame_interno_obligatorias)

    def _on_canvas_configure_electivas(self, event):
        """Ajusta el ancho del frame interno y el scrollregion del canvas de electivas."""
        canvas_width = event.width
        self.canvas_electivas.itemconfig(self.id_ventana_electivas, width=canvas_width)
        self._on_frame_configure_electivas()

    def _on_frame_configure_electivas(self, event=None):
        """Actualiza el scrollregion del canvas de electivas cuando el frame interno cambia."""
        self.canvas_electivas.configure(scrollregion=self.canvas_electivas.bbox("all"))
        self._ajustar_altura_canvas(self.canvas_electivas, self.frame_interno_electivas)

    def _ajustar_altura_canvas(self, canvas_widget, inner_frame_widget):
        """Ajusta la altura del canvas para que sea solo la necesaria o un máximo."""
        inner_frame_widget.update_idletasks() # Asegurarse que el frame interno tiene su tamaño final
        required_height = inner_frame_widget.winfo_reqheight()
        
        max_canvas_height = 200 # Por ejemplo, un máximo de 200px para cada sección
        
        # Si la altura requerida es menor que el máximo, ajustamos a la requerida, si no, al máximo
        if required_height < max_canvas_height:
            canvas_widget.config(height=required_height)
        else:
            canvas_widget.config(height=max_canvas_height)

    def _on_mousewheel(self, event):
        """Maneja el evento de la rueda del mouse para los canvases de materias."""
        current_tab = self.notebook.select()
        tab_name = self.notebook.tab(current_tab, "text")

        if tab_name != "Generador de Horarios":
            return

        # Determina qué canvas está "activo" o sobre el que el mouse está
        # Podrías necesitar una lógica más sofisticada si el mouse puede estar sobre los dos
        # simultáneamente y solo quieres que uno scrollee.
        # Por simplicidad, aquí asumimos que el evento se aplica a ambos si están visibles.
        
        canvas_to_scroll = None
        if self.canvas_obligatorias.winfo_exists() and self.canvas_obligatorias.winfo_containing(event.x_root, event.y_root) == self.canvas_obligatorias:
            canvas_to_scroll = self.canvas_obligatorias
        elif self.canvas_electivas.winfo_exists() and self.canvas_electivas.winfo_containing(event.x_root, event.y_root) == self.canvas_electivas:
            canvas_to_scroll = self.canvas_electivas

        if canvas_to_scroll:
            if event.num == 4:  # Linux scroll up
                canvas_to_scroll.yview_scroll(-1, "units")
            elif event.num == 5:  # Linux scroll down
                canvas_to_scroll.yview_scroll(1, "units")
            else:  # Windows, macOS (delta)
                if abs(event.delta) >= 120:
                    scroll_val = int(-1 * (event.delta / 120))
                else:
                    scroll_val = -1 * event.delta
                canvas_to_scroll.yview_scroll(scroll_val, "units")


    def _configurar_tab_historial(self):
        """Configura la pestaña de historial académico."""
        # Frame principal
        main_frame = ttk.Frame(self.tab_historial)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título e instrucciones
        ttk.Label(
            main_frame,
            text="Historial de Materias Cursadas",
            style="Subtitle.TLabel"
        ).pack(pady=(0, 10))

        ttk.Label(
            main_frame,
            text="Marca las materias que ya has cursado y aprobado. Estas materias no serán consideradas al generar nuevos horarios.",
            wraplength=600
        ).pack(pady=(0, 15))

        # Marco para la lista de materias cursadas
        frame_cursadas = ttk.LabelFrame(main_frame, text="Materias Cursadas", padding=(10, 5))
        frame_cursadas.pack(fill="both", expand=True, padx=10, pady=5)

        # Panel con scroll para las materias
        canvas_cursadas = tk.Canvas(frame_cursadas, borderwidth=0, background="#ffffff")
        self.frame_cursadas_interno = ttk.Frame(canvas_cursadas) # Cambiado a self.frame_cursadas_interno
        scrollbar_cursadas = ttk.Scrollbar(frame_cursadas, orient="vertical", command=canvas_cursadas.yview)

        canvas_cursadas.configure(yscrollcommand=scrollbar_cursadas.set)

        scrollbar_cursadas.pack(side="right", fill="y")
        canvas_cursadas.pack(side="left", fill="both", expand=True)

        # Ventana del canvas para el frame interno
        self.id_ventana_cursadas = canvas_cursadas.create_window(
            (0, 0),
            window=self.frame_cursadas_interno,
            anchor="nw",
            width=frame_cursadas.winfo_width() - scrollbar_cursadas.winfo_width()
        )

        # Ajustar el canvas cuando cambia el tamaño
        self.frame_cursadas_interno.bind("<Configure>",
            lambda e: canvas_cursadas.configure(scrollregion=canvas_cursadas.bbox("all")))
        canvas_cursadas.bind("<Configure>",
            lambda e: canvas_cursadas.itemconfig(self.id_ventana_cursadas, width=e.width))

        # Almacenar referencias para acceder después
        self.canvas_cursadas = canvas_cursadas

        # Botones de acción
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", padx=10, pady=10)

        btn_guardar = ttk.Button(
            btn_frame,
            text="Guardar Historial",
            command=self._guardar_historial_materias,
            style="Save.TButton"
        )
        btn_guardar.pack(side=tk.RIGHT, padx=5)

        # Nuevo botón para borrar historial
        btn_borrar_historial = ttk.Button(
            btn_frame,
            text="Borrar Historial",
            command=self._borrar_historial_materias,
            style="Save.TButton" # Usar el mismo estilo de guardar
        )
        btn_borrar_historial.pack(side=tk.LEFT, padx=5)


    def _guardar_historial_materias(self):
        """Guarda el historial de materias cursadas en la base de datos."""
        if not self.conexion_db:
            messagebox.showerror("Error", "No hay conexión a la base de datos.")
            return

        try:
            cursor = self.conexion_db.cursor()
            fecha_actual = datetime.now().strftime("%Y-%m-%d")

            # Primero limpiamos registros antiguos (podría ser opcional)
            cursor.execute("DELETE FROM HistorialMateriasCursadas")

            # Insertamos los nuevos registros
            for codigo, var in self.materias_cursadas.items():
                if var.get():  # Si la materia está marcada como cursada
                    cursor.execute(
                        "INSERT INTO HistorialMateriasCursadas (codigo_materia, fecha_registro, nota) VALUES (?, ?, ?)",
                        (codigo, fecha_actual, 3.0)  # Nota por defecto 3.0 (aprobada)
                    )

            self.conexion_db.commit()
            messagebox.showinfo("Éxito", "El historial de materias cursadas ha sido guardado correctamente.")

        except sqlite3.Error as e:
            self.conexion_db.rollback()
            messagebox.showerror("Error al Guardar", f"No se pudo guardar el historial: {e}")

    def _borrar_historial_materias(self):
        """Borra todo el historial de materias cursadas de la base de datos."""
        if not self.conexion_db:
            messagebox.showerror("Error", "No hay conexión a la base de datos.")
            return

        if messagebox.askyesno("Confirmar Borrado", "¿Estás seguro de que quieres borrar todo el historial de materias cursadas?\n"
                                             "Esta acción es irreversible."):
            try:
                cursor = self.conexion_db.cursor()
                cursor.execute("DELETE FROM HistorialMateriasCursadas")
                self.conexion_db.commit()
                messagebox.showinfo("Éxito", "El historial de materias cursadas ha sido borrado.")
                # Actualizar la interfaz para reflejar el borrado
                self._cargar_historial_materias()
            except sqlite3.Error as e:
                self.conexion_db.rollback()
                messagebox.showerror("Error al Borrar", f"No se pudo borrar el historial: {e}")

    def _configurar_tab_calendario(self):
        """Configura la pestaña de vista de calendario."""
        # Frame principal
        main_frame = ttk.Frame(self.tab_calendario)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título e instrucciones
        ttk.Label(
            main_frame,
            text="Vista de Horario Semanal",
            style="Subtitle.TLabel"
        ).pack(pady=(0, 10))

        ttk.Label(
            main_frame,
            text="Aquí se visualizará el último horario generado en formato de calendario semanal.",
            wraplength=600
        ).pack(pady=(0, 15))

        # Marco para el calendario
        self.frame_calendario = ttk.LabelFrame(main_frame, text="Horario Semanal", padding=(10, 5))
        self.frame_calendario.pack(fill="both", expand=True, padx=10, pady=5)

        # Mostrar mensaje inicial
        self.label_calendario_mensaje = ttk.Label(
            self.frame_calendario,
            text="Aún no se ha generado ningún horario.\n"
                 "Ve a la pestaña 'Generador de Horarios' para crear uno nuevo.",
            justify=tk.CENTER
        )
        self.label_calendario_mensaje.pack(expand=True, pady=50)

        # Botones de acción
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", padx=10, pady=10)

        btn_exportar = ttk.Button(
            btn_frame,
            text="Exportar Horario (PDF)",
            command=self._exportar_horario,
            state="disabled"  # Inicialmente deshabilitado
        )
        btn_exportar.pack(side=tk.RIGHT, padx=5)

        # Guardar referencia para habilitar/deshabilitar después
        self.btn_exportar = btn_exportar

    def _exportar_horario(self):
        """Exporta el horario actual a un archivo PDF (simulado por ahora)."""
        if not self.horario_generado:
            messagebox.showinfo("Información", "No hay un horario para exportar.")
            return

        # Aquí se implementaría la exportación real a PDF
        # Por ahora mostramos un mensaje informativo
        messagebox.showinfo(
            "Exportar Horario",
            "La exportación a PDF será implementada en una versión futura.\n\n"
            "Esta función permitirá guardar tu horario en un archivo PDF para imprimirlo o guardarlo."
        )

    def _configurar_tab_config(self):
        """Configura la pestaña de ajustes y configuración."""
        # Frame principal
        main_frame = ttk.Frame(self.tab_config)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        ttk.Label(
            main_frame,
            text="Configuración del Sistema",
            style="Subtitle.TLabel"
        ).pack(pady=(0, 20))

        # Opciones de visualización
        frame_visual = ttk.LabelFrame(main_frame, text="Opciones de Visualización", padding=(15, 10))
        frame_visual.pack(fill="x", padx=10, pady=10)

        # Tema de la aplicación
        frame_tema = ttk.Frame(frame_visual)
        frame_tema.pack(fill="x", pady=5)

        ttk.Label(frame_tema, text="Tema de la aplicación:", width=20).pack(side=tk.LEFT, padx=(0, 10))

        tema_var = StringVar(value="clam")
        tema_combo = ttk.Combobox(
            frame_tema,
            textvariable=tema_var,
            values=list(ttk.Style().theme_names()),
            state="readonly",
            width=15
        )
        tema_combo.pack(side=tk.LEFT)

        ttk.Button(
            frame_tema,
            text="Aplicar",
            command=lambda: self._cambiar_tema(tema_var.get())
        ).pack(side=tk.LEFT, padx=10)

        # Otros ajustes de visualización
        frame_ajustes = ttk.Frame(frame_visual)
        frame_ajustes.pack(fill="x", pady=5)

        self.mostrar_creditos_var = BooleanVar(value=True)
        ttk.Checkbutton(
            frame_ajustes,
            text="Mostrar créditos de las materias",
            variable=self.mostrar_creditos_var
        ).pack(anchor="w", padx=5, pady=2)

        self.mostrar_docentes_var = BooleanVar(value=True)
        ttk.Checkbutton(
            frame_ajustes,
            text="Mostrar nombres de docentes en el calendario",
            variable=self.mostrar_docentes_var
        ).pack(anchor="w", padx=5, pady=2)

        # Opciones del generador de horarios
        frame_algoritmo = ttk.LabelFrame(main_frame, text="Algoritmo de Generación", padding=(15, 10))
        frame_algoritmo.pack(fill="x", padx=10, pady=10)

        ttk.Label(
            frame_algoritmo,
            text="Parámetros para la generación de horarios:",
            wraplength=500
        ).pack(anchor="w", pady=(0, 10))

        # Parámetros del algoritmo
        frame_params = ttk.Frame(frame_algoritmo)
        frame_params.pack(fill="x")

        ttk.Label(frame_params, text="Máximo número de horarios a generar:", width=30).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Spinbox(frame_params, from_=1, to=20, width=5).grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(frame_params, text="Prioridad de optimización:", width=30).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Combobox(
            frame_params,
            values=["Minimizar días de asistencia", "Minimizar huecos entre clases", "Balancear carga diaria"],
            state="readonly",
            width=25
        ).grid(row=1, column=1, sticky="w", padx=5, pady=2)

        # Botones de acción
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", padx=10, pady=20)

        ttk.Button(
            btn_frame,
            text="Restaurar Configuración Predeterminada",
            command=self._restaurar_config_predeterminada
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            btn_frame,
            text="Guardar Configuración",
            command=self._guardar_configuracion,
            style="Accent.TButton"
        ).pack(side=tk.RIGHT, padx=5)

    def _cambiar_tema(self, tema):
        """Cambia el tema visual de la aplicación."""
        style = ttk.Style()
        if tema in style.theme_names():
            style.theme_use(tema)
            messagebox.showinfo("Tema Cambiado", f"El tema ha sido cambiado a '{tema}'.")
        else:
            messagebox.showerror("Error", f"El tema '{tema}' no está disponible.")

    def _restaurar_config_predeterminada(self):
        """Restaura la configuración a los valores predeterminados."""
        # Aquí se implementaría la restauración real de configuración
        self.mostrar_creditos_var.set(True)
        self.mostrar_docentes_var.set(True)
        self.preferencia_turno_var.set("cualquiera")
        self.minimizar_huecos_var.set(True)
        messagebox.showinfo(
            "Restaurar Configuración",
            "La configuración ha sido restaurada a los valores predeterminadas."
        )

    def _guardar_configuracion(self):
        """Guarda la configuración actual."""
        # Aquí se implementaría el guardado real de configuración (por ejemplo, en un archivo de configuración)
        messagebox.showinfo(
            "Guardar Configuración",
            "La configuración ha sido guardada correctamente."
        )

    def _cargar_datos_materias(self):
        """Carga los datos de materias desde la base de datos y configura los widgets correspondientes."""
        if not self.conexion_db:
            return

        try:
            # Obtener las materias de la base de datos. Asumo que tienes una columna 'tipo_materia'
            # en tu tabla de Materias (e.g., 'obligatoria' o 'electiva').
            # Si no la tienes, necesitarás modificar tu db_manager o la base de datos.
            materias_tuplas = db_manager.obtener_todas_las_materias_con_tipo(self.conexion_db)

            if not materias_tuplas:
                ttk.Label(self.frame_interno_obligatorias, text="No se encontraron materias obligatorias en la base de datos.").pack(pady=10)
                ttk.Label(self.frame_interno_electivas, text="No se encontraron materias electivas en la base de datos.").pack(pady=10)
                return

            # Limpiar widgets existentes en los frames internos antes de recargar
            for widget in self.frame_interno_obligatorias.winfo_children():
                widget.destroy()
            for widget in self.frame_interno_electivas.winfo_children():
                widget.destroy()

            # Reiniciar variables de control
            self.checkbox_vars_obligatorias = {}
            self.checkbox_vars_electivas = {}
            self.materias_info = {} # Re-poblar con info completa

            row_obligatoria = 0
            col_obligatoria = 0
            row_electiva = 0
            col_electiva = 0
            max_cols = 3  # Número de columnas para los checkboxes

            for i, (codigo, nombre, creditos, tipo_materia) in enumerate(materias_tuplas):
                self.materias_info[codigo] = (nombre, creditos, tipo_materia)

                var_seleccion = BooleanVar(value=False)
                var_seleccion.trace_add("write", lambda name, index, mode, var=var_seleccion: self._verificar_limite_materias())

                if tipo_materia == "obligatoria":
                    self.checkbox_vars_obligatorias[codigo] = var_seleccion
                    cb_seleccion = ttk.Checkbutton(
                        self.frame_interno_obligatorias,
                        text=f"{nombre} ({codigo}) [{creditos} Créditos]",
                        variable=var_seleccion,
                        style="Materia.TCheckbutton"
                    )
                    cb_seleccion.grid(row=row_obligatoria, column=col_obligatoria, sticky="w", padx=5, pady=2)
                    col_obligatoria += 1
                    if col_obligatoria >= max_cols:
                        col_obligatoria = 0
                        row_obligatoria += 1
                elif tipo_materia == "electiva":
                    self.checkbox_vars_electivas[codigo] = var_seleccion
                    cb_seleccion = ttk.Checkbutton(
                        self.frame_interno_electivas,
                        text=f"{nombre} ({codigo}) [{creditos} Créditos]",
                        variable=var_seleccion,
                        style="Materia.TCheckbutton"
                    )
                    cb_seleccion.grid(row=row_electiva, column=col_electiva, sticky="w", padx=5, pady=2)
                    col_electiva += 1
                    if col_electiva >= max_cols:
                        col_electiva = 0
                        row_electiva += 1
                # Si tienes otros tipos, puedes añadir más `elif`

            self._on_frame_configure_obligatorias() # Ajustar scrollregion y tamaño
            self._on_frame_configure_electivas()   # Ajustar scrollregion y tamaño

        except sqlite3.Error as e:
            messagebox.showerror("Error de Carga", f"No se pudieron cargar las materias: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado al cargar materias: {e}")

    def _verificar_limite_materias(self):
        """Verifica que el usuario no seleccione más del límite de materias en total (obligatorias + electivas)."""
        materias_seleccionadas_count = sum(1 for var in self.checkbox_vars_obligatorias.values() if var.get())
        materias_seleccionadas_count += sum(1 for var in self.checkbox_vars_electivas.values() if var.get())

        if materias_seleccionadas_count > self.MAX_MATERIAS_SELECCIONABLES:
            messagebox.showwarning(
                "Límite de Selección",
                f"Solo puedes seleccionar un máximo de {self.MAX_MATERIAS_SELECCIONABLES} materias en total."
                "\nPor favor, deselecciona alguna materia para continuar."
            )
            # Desactivar la última materia seleccionada si excede el límite
            # Esto puede ser un poco complejo de rastrear cual fue la "última",
            # una opción más simple es recorrer y desmarcar una al azar si se excede.
            # O, mejor aún, deshabilitar los checkboxes una vez que se llega al límite.
            # Para este ejemplo, simplemente advertimos.
            
            # Una forma simple de forzar el límite (puede no ser la "última" desmarcada)
            # Iteramos en las electivas, si hay alguna marcada y se excede el límite, la desmarcamos.
            # Priorizamos desmarcar electivas porque las obligatorias son 'más importantes'
            if materias_seleccionadas_count > self.MAX_MATERIAS_SELECCIONABLES:
                for codigo, var in self.checkbox_vars_electivas.items():
                    if var.get():
                        var.set(False)
                        materias_seleccionadas_count -= 1
                        if materias_seleccionadas_count <= self.MAX_MATERIAS_SELECCIONABLES:
                            break
                # Si aún se excede (solo obligatorias), desmarcamos obligatorias (no es lo ideal para el flujo)
                if materias_seleccionadas_count > self.MAX_MATERIAS_SELECCIONABLES:
                     for codigo, var in self.checkbox_vars_obligatorias.items():
                        if var.get():
                            var.set(False)
                            materias_seleccionadas_count -= 1
                            if materias_seleccionadas_count <= self.MAX_MATERIAS_SELECCIONABLES:
                                break


    def accion_generar_horario_solicitado(self):
        """
        Recopila las materias seleccionadas (obligatorias y electivas) y genera un horario.
        """
        materias_seleccionadas = []
        
        # Recopilar materias obligatorias seleccionadas
        for codigo, var in self.checkbox_vars_obligatorias.items():
            if var.get():
                if codigo in self.materias_info:
                    materias_seleccionadas.append(codigo)
                else:
                    print(f"Advertencia: Materia obligatoria {codigo} no encontrada en materias_info.")

        # Recopilar materias electivas seleccionadas
        for codigo, var in self.checkbox_vars_electivas.items():
            if var.get():
                if codigo in self.materias_info:
                    materias_seleccionadas.append(codigo)
                else:
                    print(f"Advertencia: Materia electiva {codigo} no encontrada en materias_info.")

        if not materias_seleccionadas:
            messagebox.showwarning("Selección Vacía", "Por favor, selecciona al menos una materia para generar un horario.")
            return

        # Filtrar materias cursadas si la preferencia está activa
        if self.respetar_cursadas_var.get():
            materias_a_considerar = [
                m for m in materias_seleccionadas
                if not self.materias_cursadas.get(m, BooleanVar(value=False)).get()
            ]
            if not materias_a_considerar:
                messagebox.showinfo("Información", "Todas las materias seleccionadas ya han sido cursadas. No hay horario que generar.")
                self.horario_generado = None
                self._limpiar_calendario()
                self.btn_exportar.config(state="disabled")
                return
        else:
            materias_a_considerar = materias_seleccionadas

        if not materias_a_considerar:
             messagebox.showwarning("Atención", "No hay materias elegibles para generar el horario después de filtrar por materias cursadas.")
             self.horario_generado = None
             self._limpiar_calendario()
             self.btn_exportar.config(state="disabled")
             return

        preferencia_turno = self.preferencia_turno_var.get()
        minimizar_huecos = self.minimizar_huecos_var.get()

        # Obtener información detallada de las materias seleccionadas de la DB
        # Esto es importante para tener los horarios, docentes, etc.
        try:
            materias_con_detalles = db_manager.obtener_detalles_materias_por_codigos(self.conexion_db, materias_a_considerar)
            if not materias_con_detalles:
                messagebox.showerror("Error", "No se encontraron detalles para las materias seleccionadas. La base de datos podría estar vacía o dañada.")
                self.horario_generado = None
                self._limpiar_calendario()
                self.btn_exportar.config(state="disabled")
                return
        except Exception as e:
            messagebox.showerror("Error de Base de Datos", f"Error al obtener detalles de materias: {e}")
            self.horario_generado = None
            self._limpiar_calendario()
            self.btn_exportar.config(state="disabled")
            return


        # Generación de horarios (simulación)
        # Aquí deberías integrar tu lógica real de generación de horarios.
        # Por ahora, es una simulación basada en los datos de la DB.
        
        # Una simulación muy básica:
        # Se agrupan los horarios de cada materia y se intenta encontrar una combinación sin conflictos.
        # Esto debería ser reemplazado por un algoritmo de generación de horarios real.
        
        horarios_posibles = self._generar_horarios_simulados(materias_con_detalles, preferencia_turno, minimizar_huecos)

        if horarios_posibles:
            self.horario_generado = horarios_posibles[0] # Tomar el primer horario como el "mejor"
            self._mostrar_horario_en_calendario(self.horario_generado)
            self.btn_exportar.config(state="normal")
            messagebox.showinfo("Éxito", "Horario generado y visualizado en la pestaña 'Vista Calendario'.")
            self.notebook.select(self.tab_calendario) # Cambiar a la pestaña de calendario
        else:
            self.horario_generado = None
            self._limpiar_calendario()
            self.btn_exportar.config(state="disabled")
            messagebox.showwarning(
                "Sin Horario",
                "No se pudo generar un horario con las materias seleccionadas y preferencias dadas.\n"
                "Intenta modificar tu selección o preferencias."
            )

    def _generar_horarios_simulados(self, materias_con_detalles, preferencia_turno, minimizar_huecos):
        """
        Simula la generación de un horario.
        Esta es una versión simplificada y DEBE ser reemplazada por tu algoritmo real.
        Recibe una lista de diccionarios, donde cada diccionario contiene la información de una materia
        y sus secciones/horarios.

        Ejemplo de `materias_con_detalles`:
        [
            {'codigo_materia': 'INF201', 'nombre_materia': 'Programación I', 'creditos': 4,
             'secciones': [
                {'seccion_id': 1, 'dia': 'Lunes', 'hora_inicio': '08:00', 'hora_fin': '10:00', 'docente': 'Dr. Pérez'},
                {'seccion_id': 2, 'dia': 'Miércoles', 'hora_inicio': '08:00', 'hora_fin': '10:00', 'docente': 'Dr. Pérez'}
             ]},
            {'codigo_materia': 'MAT101', 'nombre_materia': 'Cálculo I', 'creditos': 5,
             'secciones': [
                {'seccion_id': 3, 'dia': 'Lunes', 'hora_inicio': '10:00', 'hora_fin': '12:00', 'docente': 'Ing. García'},
                {'seccion_id': 4, 'dia': 'Jueves', 'hora_inicio': '09:00', 'hora_fin': '11:00', 'docente': 'Ing. García'}
             ]}
        ]
        """
        horarios_generados = []
        
        # Este es un algoritmo de backtracking muy básico para encontrar UNA combinación.
        # Tu algoritmo real de generación debería ser mucho más robusto, considerar optimizaciones
        # (minimizar huecos, etc.), y generar múltiples opciones.

        def find_schedule_combinations(index, current_schedule, selected_sections):
            if index == len(materias_con_detalles):
                # Hemos asignado una sección a cada materia. Validar y añadir.
                horarios_generados.append(current_schedule.copy())
                return True # En esta simulación, solo buscamos el primer horario válido.

            materia = materias_con_detalles[index]
            materia_codigo = materia['codigo_materia']

            for seccion in materia['secciones']:
                # Verificar conflictos con el horario actual
                is_conflict = False
                for existing_class in current_schedule:
                    # Convierte horas a un formato comparable (e.g., minutos desde medianoche)
                    start1_min = self._time_to_minutes(seccion['hora_inicio'])
                    end1_min = self._time_to_minutes(seccion['hora_fin'])
                    start2_min = self._time_to_minutes(existing_class['hora_inicio'])
                    end2_min = self._time_to_minutes(existing_class['hora_fin'])

                    if seccion['dia'] == existing_class['dia'] and \
                       max(start1_min, start2_min) < min(end1_min, end2_min):
                        is_conflict = True
                        break
                
                # Verificar preferencias de turno
                if preferencia_turno != "cualquiera":
                    start_hour = int(seccion['hora_inicio'].split(':')[0])
                    if preferencia_turno == "mañana" and start_hour >= 13: # Asumimos mañana hasta 12:59
                        is_conflict = True
                    elif preferencia_turno == "tarde" and start_hour < 13: # Asumimos tarde desde 13:00
                        is_conflict = True

                if not is_conflict:
                    current_schedule.append({
                        'codigo_materia': materia_codigo,
                        'nombre_materia': materia['nombre_materia'],
                        'creditos': materia['creditos'],
                        'dia': seccion['dia'],
                        'hora_inicio': seccion['hora_inicio'],
                        'hora_fin': seccion['hora_fin'],
                        'docente': seccion['docente']
                    })
                    selected_sections[materia_codigo] = seccion['seccion_id'] # Guarda la sección elegida
                    
                    if find_schedule_combinations(index + 1, current_schedule, selected_sections):
                        return True # Found one schedule
                    
                    current_schedule.pop() # Backtrack
                    del selected_sections[materia_codigo]

            return False

        # Iniciar la búsqueda con una simulación de backtracking
        find_schedule_combinations(0, [], {})
        
        # En una implementación real, aquí se ordenarían los horarios por criterios de optimización
        # (ej. minimizar huecos, número de días, etc.) y se devolvería el mejor.
        
        return horarios_generados

    def _time_to_minutes(self, time_str):
        """Convierte una cadena de tiempo 'HH:MM' a minutos desde la medianoche."""
        h, m = map(int, time_str.split(':'))
        return h * 60 + m

    def _limpiar_calendario(self):
        """Limpia el contenido del frame del calendario y muestra el mensaje inicial."""
        for widget in self.frame_calendario.winfo_children():
            widget.destroy()
        self.label_calendario_mensaje = ttk.Label(
            self.frame_calendario,
            text="Aún no se ha generado ningún horario.\n"
                 "Ve a la pestaña 'Generador de Horarios' para crear uno nuevo.",
            justify=tk.CENTER
        )
        self.label_calendario_mensaje.pack(expand=True, pady=50)


    def _mostrar_horario_en_calendario(self, horario):
        """
        Muestra el horario generado en la pestaña de calendario.
        `horario` es una lista de diccionarios, cada uno representando una clase.
        """
        self._limpiar_calendario() # Limpiar el contenido anterior

        # Crear la estructura de la tabla del calendario
        grid_frame = ttk.Frame(self.frame_calendario, style="Calendar.TFrame")
        grid_frame.pack(fill=tk.BOTH, expand=True)

        # Configurar las columnas para que se expandan
        grid_frame.grid_columnconfigure(0, weight=0) # Columna de horas fija
        for i in range(len(DIAS_SEMANA)):
            grid_frame.grid_columnconfigure(i + 1, weight=1) # Días expandibles

        # Fila de encabezados de días
        ttk.Label(grid_frame, text="Hora", style="DayHeader.TLabel").grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        for i, dia in enumerate(DIAS_SEMANA):
            ttk.Label(grid_frame, text=dia, style="DayHeader.TLabel").grid(row=0, column=i + 1, sticky="nsew", padx=1, pady=1)

        # Filas de horas y celdas de materias
        self.celdas_horario = {} # Para almacenar referencias a las etiquetas de las celdas

        for r, hora_inicio in enumerate(HORAS_CLASE):
            grid_frame.grid_rowconfigure(r + 1, weight=1) # Filas de horas expandibles
            ttk.Label(grid_frame, text=hora_inicio, style="HourLabel.TLabel").grid(row=r + 1, column=0, sticky="nsew", padx=1, pady=1)
            for c, dia in enumerate(DIAS_SEMANA):
                celda_key = (dia, hora_inicio)
                label_celda = ttk.Label(
                    grid_frame,
                    text="",
                    relief="solid",
                    borderwidth=1,
                    background="#f9f9f9", # Color de fondo por defecto
                    anchor="center",
                    wraplength=100, # Para que el texto se ajuste
                    font=self.fuente_normal
                )
                label_celda.grid(row=r + 1, column=c + 1, sticky="nsew", padx=1, pady=1)
                self.celdas_horario[celda_key] = label_celda

        # Asignar colores a las materias si aún no lo están
        for clase in horario:
            codigo_materia = clase['codigo_materia']
            if codigo_materia not in self.color_mapping:
                # Asigna un color de la lista, ciclando si se acaban
                self.color_mapping[codigo_materia] = COLORES_MATERIAS[len(self.color_mapping) % len(COLORES_MATERIAS)]

        # Rellenar el calendario con las clases del horario generado
        for clase in horario:
            dia = clase['dia']
            hora_inicio_clase = clase['hora_inicio']
            hora_fin_clase = clase['hora_fin']
            nombre_materia = clase['nombre_materia']
            codigo_materia = clase['codigo_materia']
            docente = clase['docente']
            creditos = clase['creditos']

            # Calcular las horas que ocupa la clase
            inicio_idx = HORAS_CLASE.index(hora_inicio_clase)
            fin_idx = HORAS_CLASE.index(hora_fin_clase) if hora_fin_clase in HORAS_CLASE else len(HORAS_CLASE) # Handle end time if not in list

            # Asegurar que fin_idx sea al menos 1 hora después de inicio_idx
            if fin_idx <= inicio_idx:
                fin_idx = inicio_idx + 1 # Asume al menos 1 hora de duración

            # Obtener el color para esta materia
            color_fondo = self.color_mapping.get(codigo_materia, "#ADD8E6") # Color por defecto si no se mapeó

            # Iterar sobre las horas que abarca la clase
            for h_idx in range(inicio_idx, fin_idx):
                if h_idx < len(HORAS_CLASE): # Asegurarse de no exceder el rango de HORAS_CLASE
                    hora_celda = HORAS_CLASE[h_idx]
                    celda_key = (dia, hora_celda)
                    if celda_key in self.celdas_horario:
                        label = self.celdas_horario[celda_key]
                        
                        # Construir el texto de la celda
                        texto_celda = f"{nombre_materia} ({codigo_materia})"
                        if self.mostrar_creditos_var.get():
                            texto_celda += f"\nCréditos: {creditos}"
                        if self.mostrar_docentes_var.get() and docente:
                            texto_celda += f"\nDocente: {docente}"
                        
                        # Si la clase dura más de una hora, solo muestra el nombre completo en la primera hora
                        # y una abreviatura o vacío en las siguientes para evitar repetición excesiva.
                        if h_idx > inicio_idx:
                            label.config(text="") # O mostrar solo el código
                        else:
                            label.config(text=texto_celda)

                        label.config(background=color_fondo, foreground="black") # Letra negra para mejor contraste

    def _cargar_historial_materias(self):
        """
        Carga el historial de materias cursadas desde la base de datos
        y actualiza los checkboxes en la pestaña de historial.
        """
        if not self.conexion_db:
            return

        # Limpiar widgets existentes en el frame_cursadas_interno antes de recargar
        for widget in self.frame_cursadas_interno.winfo_children():
            widget.destroy()

        self.materias_cursadas = {} # Resetear el diccionario de variables

        try:
            # Obtener todas las materias (sean obligatorias o electivas)
            materias_disponibles = db_manager.obtener_todas_las_materias_simple(self.conexion_db)
            
            # Obtener las materias marcadas como cursadas del historial
            cursor = self.conexion_db.cursor()
            cursor.execute("SELECT codigo_materia FROM HistorialMateriasCursadas")
            cursadas_db = {row[0] for row in cursor.fetchall()} # Conjunto para búsqueda eficiente

            row = 0
            col = 0
            max_cols = 3 # Número de columnas para los checkboxes

            if not materias_disponibles:
                ttk.Label(self.frame_cursadas_interno, text="No hay materias disponibles para registrar el historial.").pack(pady=10)
                return

            for i, (codigo, nombre, creditos) in enumerate(materias_disponibles):
                var_cursada = BooleanVar(value=(codigo in cursadas_db))
                self.materias_cursadas[codigo] = var_cursada

                cb_cursada = ttk.Checkbutton(
                    self.frame_cursadas_interno,
                    text=f"{nombre} ({codigo}) [{creditos} Créditos]",
                    variable=var_cursada,
                    style="Materia.TCheckbutton"
                )
                cb_cursada.grid(row=row, column=col, sticky="w", padx=5, pady=2)

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            # Actualizar el scrollregion del canvas de historial
            self.frame_cursadas_interno.update_idletasks()
            self.canvas_cursadas.config(scrollregion=self.canvas_cursadas.bbox("all"))

        except sqlite3.Error as e:
            messagebox.showerror("Error al cargar historial", f"No se pudo cargar el historial de materias: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado al cargar historial: {e}")


    def _al_intentar_cerrar(self):
        """Maneja el evento de cierre de la ventana, cerrando la conexión a la base de datos."""
        if self.conexion_db:
            self.conexion_db.close()
            print("Conexión a la base de datos cerrada.")
        self.master.destroy()

# Para ejecutar la aplicación
if __name__ == "__main__":
    # Asegúrate de que la base de datos esté creada y poblada antes de ejecutar la interfaz.
    # Puedes ejecutar db_manager.py directamente una vez para esto.
    # Ejemplo: python database/db_manager.py
    
    root = tk.Tk()
    app = AplicacionAvanzadaHorarios(root)
    root.mainloop()
