# PROYECTO_RAIZ/interfaz/interfaz_horarios_manual_mejorada.py

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import random
from datetime import datetime, timedelta

# --- Inicio: Ajuste de ruta para importar db_manager ---
directorio_actual_interfaz = os.path.dirname(os.path.abspath(__file__))
proyecto_raiz = os.path.dirname(directorio_actual_interfaz)
sys.path.append(proyecto_raiz)
# --- Fin: Ajuste de ruta ---

from database import db_manager

class AplicacionHorarioModerna:
    def __init__(self, master_window):
        self.master = master_window
        self.master.title("📚 Generador de Horarios - Lic. en Informática")
        self.master.geometry("1600x900")  # Aumenté la ventana para acomodar mejor el contenido
        self.master.state('zoomed')  # Maximizar en Windows
        self.master.configure(bg="#F8F9FA")
        
        self.conexion_db = None
        self.materias_data = {}  
        self.horario_asignado = {}  
        self.colores_materias = {}  
        self.widgets_grupos_expandidos = {}
        self.busqueda_var = tk.StringVar()
        self.busqueda_var.trace('w', self._filtrar_materias)
        
        # Configuración de horarios
        self.dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        self.horas = [f"{h:02d}:00" for h in range(7, 20)]
        
        # Variables de estado
        self.total_creditos = 0
        self.materias_filtradas = {}
        self.hover_celda = None
        
        self._configurar_estilos_modernos()
        self._conectar_a_base_de_datos()
        
        if self.conexion_db:
            self._cargar_datos_materias()
            self._crear_interfaz_moderna()
        else:
            self._mostrar_error_conexion()

    def _configurar_estilos_modernos(self):
        """Configuración de estilos modernos y minimalistas"""
        style = ttk.Style()
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        
        # Colores principales
        self.colores = {
            'bg_principal': '#F8F9FA',
            'bg_sidebar': '#FFFFFF',
            'bg_card': '#FFFFFF',
            'primary': '#3B82F6',
            'primary_light': '#DBEAFE',
            'secondary': '#6B7280',
            'success': '#10B981',
            'warning': '#F59E0B',
            'danger': '#EF4444',
            'text_primary': '#111827',
            'text_secondary': '#6B7280',
            'border': '#E5E7EB',
            'hover': '#F3F4F6'
        }
        
        # Estilos personalizados
        style.configure("Toolbar.TFrame", background=self.colores['bg_principal'])
        style.configure("Sidebar.TFrame", background=self.colores['bg_sidebar'])
        style.configure("Card.TFrame", background=self.colores['bg_card'], relief="flat")
        
        style.configure("Title.TLabel", 
                        font=("Segoe UI", 18, "bold"), 
                        background=self.colores['bg_principal'],
                        foreground=self.colores['text_primary'])
        
        style.configure("Subtitle.TLabel", 
                        font=("Segoe UI", 12, "bold"), 
                        background=self.colores['bg_sidebar'],
                        foreground=self.colores['text_primary'])
        
        style.configure("Body.TLabel", 
                        font=("Segoe UI", 9), 
                        background=self.colores['bg_card'],
                        foreground=self.colores['text_secondary'])
        
        style.configure("Primary.TButton",
                        font=("Segoe UI", 9, "bold"))

    def _conectar_a_base_de_datos(self):
        try:
            self.conexion_db = db_manager.crear_conexion()
            if self.conexion_db is None:
                messagebox.showerror(
                    "Error de Base de Datos",
                    "No se pudo conectar a la base de datos 'horarios.db'.\n"
                    "Asegúrate de que existe y está correctamente configurada."
                )
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"Error inesperado: {e}")

    def _mostrar_error_conexion(self):
        error_frame = tk.Frame(self.master, bg=self.colores['bg_principal'])
        error_frame.pack(fill=tk.BOTH, expand=True)
        
        error_label = tk.Label(
            error_frame, 
            text="⚠️ Error Crítico\n\nNo se pudo conectar a la base de datos.\nLa aplicación no puede funcionar.",
            font=("Segoe UI", 16, "bold"), 
            fg=self.colores['danger'],
            bg=self.colores['bg_principal'],
            justify=tk.CENTER
        )
        error_label.pack(expand=True)

    def _cargar_datos_materias(self):
        """Carga todas las materias desde la BD"""
        try:
            materias_tuplas = db_manager.obtener_todas_las_materias_simple(self.conexion_db)
            
            for codigo, nombre, creditos in materias_tuplas:
                horarios = db_manager.obtener_horarios_de_materia(self.conexion_db, codigo)
                
                grupos = {}
                for horario in horarios:
                    nombre_grupo = horario.get('nombre_grupo', 'Sin Grupo')
                    if nombre_grupo not in grupos:
                        grupos[nombre_grupo] = {
                            'sesiones': [],
                            'docente': horario.get('docente', 'N/A')
                        }
                    grupos[nombre_grupo]['sesiones'].append(horario)

                self.materias_data[codigo] = {
                    'nombre': nombre,
                    'creditos': creditos or 0,
                    'grupos': grupos
                }
                
                self.colores_materias[codigo] = self._generar_color_moderno()
            
            self.materias_filtradas = self.materias_data.copy()
            
        except Exception as e:
            messagebox.showerror("Error al Cargar Datos", f"No se pudieron cargar las materias: {e}")

    def _generar_color_moderno(self):
        """Genera colores modernos y sutiles"""
        colores_modernos = [
            "#EEF2FF", "#F0F9FF", "#ECFDF5", "#FFFBEB", "#FAF5FF",
            "#FDF2F8", "#F0FDF4", "#FEFCE8", "#EFF6FF", "#FEF7ED"
        ]
        return random.choice(colores_modernos)

    def _crear_interfaz_moderna(self):
        """Crea la interfaz principal moderna"""
        # Toolbar superior
        self._crear_toolbar()
        
        # Container principal
        main_container = tk.Frame(self.master, bg=self.colores['bg_principal'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Sidebar izquierdo (más ancho)
        self._crear_sidebar_moderno(main_container)
        
        # Área principal del horario
        self._crear_area_horario_moderna(main_container)

    def _crear_toolbar(self):
        """Crea la barra de herramientas superior"""
        toolbar = tk.Frame(self.master, bg=self.colores['bg_principal'], height=80)
        toolbar.pack(fill=tk.X, padx=20, pady=20)
        toolbar.pack_propagate(False)
        
        # Título principal
        title_label = tk.Label(
            toolbar, 
            text="📚 Generador de Horarios",
            font=("Segoe UI", 24, "bold"),
            bg=self.colores['bg_principal'],
            fg=self.colores['text_primary']
        )
        title_label.pack(side=tk.LEFT, pady=10)
        
        # Frame para controles de la derecha
        controls_frame = tk.Frame(toolbar, bg=self.colores['bg_principal'])
        controls_frame.pack(side=tk.RIGHT, pady=10)
        
        # Indicador de créditos
        self.creditos_label = tk.Label(
            controls_frame,
            text="📊 0 créditos",
            font=("Segoe UI", 12, "bold"),
            bg=self.colores['primary_light'],
            fg=self.colores['primary'],
            padx=15, pady=8,
            relief="flat"
        )
        self.creditos_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botones de acción
        btn_limpiar = tk.Button(
            controls_frame,
            text="🗑️ Limpiar",
            font=("Segoe UI", 10, "bold"),
            bg=self.colores['danger'],
            fg="white",
            padx=15, pady=8,
            relief="flat",
            cursor="hand2",
            command=self._limpiar_horario
        )
        btn_limpiar.pack(side=tk.LEFT, padx=5)
        
        btn_guardar = tk.Button(
            controls_frame,
            text="💾 Guardar",
            font=("Segoe UI", 10, "bold"),
            bg=self.colores['success'],
            fg="white",
            padx=15, pady=8,
            relief="flat",
            cursor="hand2",
            command=self._guardar_horario
        )
        btn_guardar.pack(side=tk.LEFT, padx=5)

    def _crear_sidebar_moderno(self, parent):
        """Crea el sidebar izquierdo moderno con ancho aumentado"""
        sidebar = tk.Frame(parent, bg=self.colores['bg_sidebar'], width=450)  # Aumenté de 320 a 450
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        sidebar.pack_propagate(False)
        
        # Header del sidebar
        header_frame = tk.Frame(sidebar, bg=self.colores['bg_sidebar'], height=60)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        title_sidebar = tk.Label(
            header_frame,
            text="📖 Materias Disponibles",
            font=("Segoe UI", 16, "bold"),
            bg=self.colores['bg_sidebar'],
            fg=self.colores['text_primary']
        )
        title_sidebar.pack(anchor="w")
        
        # Barra de búsqueda
        search_frame = tk.Frame(sidebar, bg=self.colores['bg_sidebar'])
        search_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        search_icon = tk.Label(
            search_frame,
            text="🔍",
            font=("Segoe UI", 12),
            bg=self.colores['bg_sidebar'],
            fg=self.colores['text_secondary']
        )
        search_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.busqueda_var,
            font=("Segoe UI", 11),
            bg="white",
            fg=self.colores['text_primary'],
            relief="flat",
            bd=1
        )
        self.search_entry.pack(fill=tk.X)
        self.search_entry.bind("<FocusIn>", self._on_search_focus)
        self.search_entry.bind("<FocusOut>", self._on_search_blur)
        
        # Área de scroll para materias
        self._crear_area_materias_scroll(sidebar)

    def _crear_area_materias_scroll(self, parent):
        """Crea el área scrolleable de materias"""
        canvas_frame = tk.Frame(parent, bg=self.colores['bg_sidebar'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        self.canvas_materias = tk.Canvas(
            canvas_frame, 
            bg=self.colores['bg_sidebar'],
            highlightthickness=0,
            bd=0
        )
        
        scrollbar_materias = ttk.Scrollbar(
            canvas_frame, 
            orient="vertical", 
            command=self.canvas_materias.yview
        )
        
        self.canvas_materias.configure(yscrollcommand=scrollbar_materias.set)
        
        scrollbar_materias.pack(side="right", fill="y")
        self.canvas_materias.pack(side="left", fill="both", expand=True)
        
        self.frame_materias_scroll = tk.Frame(self.canvas_materias, bg=self.colores['bg_sidebar'])
        self.canvas_materias.create_window((0, 0), window=self.frame_materias_scroll, anchor="nw")
        
        self._crear_lista_materias_moderna()
        
        self.frame_materias_scroll.bind(
            "<Configure>", 
            lambda e: self.canvas_materias.configure(scrollregion=self.canvas_materias.bbox("all"))
        )
        
        # Scroll con mouse wheel
        self.canvas_materias.bind_all("<MouseWheel>", self._on_mousewheel)

    def _crear_lista_materias_moderna(self):
        """Crea la lista moderna de materias"""
        for widget in self.frame_materias_scroll.winfo_children():
            widget.destroy()
        
        for codigo, data in self.materias_filtradas.items():
            self._crear_card_materia_moderna(codigo, data)

    def _crear_card_materia_moderna(self, codigo, data):
        """Crea una card moderna para cada materia"""
        # Card principal
        card_frame = tk.Frame(
            self.frame_materias_scroll,
            bg="white",
            relief="flat",
            bd=1
        )
        card_frame.pack(fill="x", pady=(0, 15))
        
        # Header de la card
        header_frame = tk.Frame(card_frame, bg="white")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        # Botón de expansión moderno
        self.btn_expand = tk.Label(
            header_frame,
            text="▶",
            font=("Segoe UI", 12),
            bg="white",
            fg=self.colores['secondary'],
            cursor="hand2",
            width=2
        )
        self.btn_expand.pack(side=tk.LEFT)
        self.btn_expand.bind("<Button-1>", lambda e, c=codigo: self._toggle_grupos_moderno(c))
        
        # Info de la materia
        info_frame = tk.Frame(header_frame, bg="white")
        info_frame.pack(side=tk.LEFT, fill="x", expand=True, padx=(10, 0))
        
        nombre_label = tk.Label(
            info_frame,
            text=data['nombre'],
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg=self.colores['text_primary'],
            anchor="w",
            justify="left"
        )
        nombre_label.pack(fill="x")
        
        codigo_creditos = tk.Label(
            info_frame,
            text=f"{codigo} • {data['creditos']} créditos",
            font=("Segoe UI", 9),
            bg="white",
            fg=self.colores['text_secondary'],
            anchor="w"
        )
        codigo_creditos.pack(fill="x")
        
        # Frame para grupos (inicialmente oculto)
        grupos_frame = tk.Frame(card_frame, bg="white")
        
        self.widgets_grupos_expandidos[codigo] = {
            'frame': grupos_frame,
            'btn_toggle': self.btn_expand,
            'expandido': False,
            'card_frame': card_frame
        }
        
        # Crear widgets para cada grupo
        for nombre_grupo, grupo_data in data['grupos'].items():
            self._crear_grupo_moderno(grupos_frame, codigo, nombre_grupo, grupo_data)

    def _crear_grupo_moderno(self, parent, codigo_materia, nombre_grupo, grupo_data):
        """Crea un widget moderno para cada grupo con mejor distribución"""
        grupo_frame = tk.Frame(
            parent,
            bg=self.colores_materias[codigo_materia],
            relief="flat"
        )
        grupo_frame.pack(fill="x", padx=15, pady=(0, 10))

        # Header del grupo con mejor distribución
        grupo_header = tk.Frame(grupo_frame, bg=self.colores_materias[codigo_materia])
        grupo_header.pack(fill="x", padx=10, pady=(10, 5))

        # Botón de agregar - posicionado primero a la derecha
        btn_agregar = tk.Label(
            grupo_header,
            text="➕",
            font=("Segoe UI", 16, "bold"),  # Aumenté el tamaño del icono
            bg=self.colores['success'],
            fg="white",
            cursor="hand2",
            padx=10, pady=6,  # Aumenté el padding para hacer el botón más grande
            relief="flat"
        )
        btn_agregar.pack(side=tk.RIGHT, padx=(10, 0))  # Mayor separación del texto
        btn_agregar.bind("<Button-1>", lambda e, c=codigo_materia, g=nombre_grupo: self._agregar_grupo_al_horario(c, g))

        # Etiqueta del docente y grupo - ahora con más espacio
        docente_label = tk.Label(
            grupo_header,
            text=f"👨‍🏫 {grupo_data['docente']} • Grupo {nombre_grupo}",
            font=("Segoe UI", 10, "bold"),
            bg=self.colores_materias[codigo_materia],
            fg=self.colores['text_primary'],
            anchor="w",
            justify="left",
            wraplength=320  # Aumenté el wraplength para aprovechar el ancho extra
        )
        docente_label.pack(side=tk.LEFT, fill="x", expand=True, pady=4)

        # Horarios del grupo
        for sesion in grupo_data['sesiones']:
            horario_label = tk.Label(
                grupo_frame,
                text=f"📅 {sesion['tipo_sesion']}: {sesion['dia_semana']} {sesion['hora_inicio']}-{sesion['hora_fin']}",
                font=("Segoe UI", 9),
                bg=self.colores_materias[codigo_materia],
                fg=self.colores['text_secondary'],
                anchor="w"
            )
            horario_label.pack(fill="x", padx=15, pady=(0, 5))

    def _crear_area_horario_moderna(self, parent):
        """Crea el área principal del horario moderna con ancho ajustado"""
        horario_frame = tk.Frame(parent, bg=self.colores['bg_card'])
        horario_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Header del área de horario
        header_horario = tk.Frame(horario_frame, bg=self.colores['bg_card'], height=60)
        header_horario.pack(fill=tk.X, padx=20, pady=(20, 0))
        header_horario.pack_propagate(False)
        
        title_horario = tk.Label(
            header_horario,
            text="📅 Horario Semanal",
            font=("Segoe UI", 18, "bold"),
            bg=self.colores['bg_card'],
            fg=self.colores['text_primary']
        )
        title_horario.pack(side=tk.LEFT, pady=15)
        
        # Mini resumen
        self.resumen_label = tk.Label(
            header_horario,
            text="0 materias • 0 créditos",
            font=("Segoe UI", 11),
            bg=self.colores['bg_card'],
            fg=self.colores['text_secondary']
        )
        self.resumen_label.pack(side=tk.RIGHT, pady=15)
        
        # Canvas para la grilla
        canvas_container = tk.Frame(horario_frame, bg=self.colores['bg_card'])
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))
        
        self.canvas_horario = tk.Canvas(
            canvas_container, 
            bg="white",
            highlightthickness=0,
            bd=0
        )
        
        scrollbar_v = ttk.Scrollbar(canvas_container, orient="vertical", command=self.canvas_horario.yview)
        scrollbar_h = ttk.Scrollbar(canvas_container, orient="horizontal", command=self.canvas_horario.xview)
        
        self.canvas_horario.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        scrollbar_v.pack(side="right", fill="y")
        scrollbar_h.pack(side="bottom", fill="x")
        self.canvas_horario.pack(side="left", fill="both", expand=True)
        
        self.frame_grilla = tk.Frame(self.canvas_horario, bg="white")
        self.canvas_horario.create_window((0, 0), window=self.frame_grilla, anchor="nw")
        
        self._crear_grilla_moderna()
        
        self.frame_grilla.bind(
            "<Configure>", 
            lambda e: self.canvas_horario.configure(scrollregion=self.canvas_horario.bbox("all"))
        )

    def _crear_grilla_moderna(self):
        """Crea la grilla moderna del horario con celdas más anchas"""
        self.grilla_widgets = {}
        
        # Header de horas (esquina)
        header_hora = tk.Label(
            self.frame_grilla, 
            text="⏰ Hora",
            font=("Segoe UI", 11, "bold"),
            bg=self.colores['primary'],
            fg="white",
            relief="flat",
            padx=10, pady=12
        )
        header_hora.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        
        # Headers de días
        for i, dia in enumerate(self.dias):
            header_dia = tk.Label(
                self.frame_grilla, 
                text=f"📅 {dia}",
                font=("Segoe UI", 11, "bold"),
                bg=self.colores['primary'],
                fg="white",
                relief="flat",
                padx=15, pady=12
            )
            header_dia.grid(row=0, column=i+1, sticky="nsew", padx=1, pady=1)
        
        # Celdas de horas y horario
        for i, hora in enumerate(self.horas):
            # Etiqueta de hora
            label_hora = tk.Label(
                self.frame_grilla, 
                text=hora,
                font=("Segoe UI", 10, "bold"),
                bg=self.colores['primary_light'],
                fg=self.colores['primary'],
                relief="flat",
                padx=10, pady=15
            )
            label_hora.grid(row=i+1, column=0, sticky="nsew", padx=1, pady=1)
            
            # Celdas del horario - aumenté el ancho
            for j, dia in enumerate(self.dias):
                celda_frame = tk.Frame(
                    self.frame_grilla, 
                    bg="white",
                    relief="solid",
                    bd=1,
                    width=200,  # Aumenté de 180 a 200
                    height=55   # Aumenté ligeramente la altura también
                )
                celda_frame.grid(row=i+1, column=j+1, sticky="nsew", padx=1, pady=1)
                celda_frame.grid_propagate(False)
                
                self.grilla_widgets[(dia, hora)] = celda_frame
                
                # Label vacío inicial
                label_vacio = tk.Label(
                    celda_frame, 
                    text="",
                    bg="white",
                    fg=self.colores['text_secondary'],
                    font=("Segoe UI", 8)
                )
                label_vacio.pack(fill="both", expand=True)
        # Configurar grid weights
        for i in range(len(self.horas) + 1):
            self.frame_grilla.grid_rowconfigure(i, weight=1)
        for j in range(len(self.dias) + 1):
            self.frame_grilla.grid_columnconfigure(j, weight=1)

    # Métodos de eventos y funcionalidad

    def _on_search_focus(self, event):
        """Maneja el evento de focus en la búsqueda"""
        if self.search_entry.get() == "":
            self.search_entry.configure(bg=self.colores['primary_light'])

    def _on_search_blur(self, event):
        """Maneja el evento de blur en la búsqueda"""
        self.search_entry.configure(bg="white")

    def _filtrar_materias(self, *args):
        """Filtra las materias según el texto de búsqueda"""
        texto_busqueda = self.busqueda_var.get().lower()
        
        if texto_busqueda == "":
            self.materias_filtradas = self.materias_data.copy()
        else:
            self.materias_filtradas = {
                codigo: data for codigo, data in self.materias_data.items()
                if texto_busqueda in data['nombre'].lower() or texto_busqueda in codigo.lower()
            }
        
        self._crear_lista_materias_moderna()

    def _on_mousewheel(self, event):
        """Maneja el scroll con rueda del mouse"""
        self.canvas_materias.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_celda_hover(self, dia, hora):
        """Maneja el hover sobre las celdas del horario"""
        self.hover_celda = (dia, hora)
        if (dia, hora) not in self.horario_asignado:
            celda = self.grilla_widgets[(dia, hora)]
            celda.configure(bg=self.colores['hover'])

    def _on_celda_leave(self):
        """Maneja cuando el mouse sale de una celda"""
        if self.hover_celda and self.hover_celda not in self.horario_asignado:
            celda = self.grilla_widgets[self.hover_celda]
            celda.configure(bg="white")
        self.hover_celda = None

    def _toggle_grupos_moderno(self, codigo):
        """Toggle moderno para expandir/colapsar grupos"""
        widget_info = self.widgets_grupos_expandidos[codigo]
        
        if widget_info['expandido']:
            widget_info['frame'].pack_forget()
            widget_info['btn_toggle'].configure(text="▶")
        else:
            widget_info['frame'].pack(fill="x")
            widget_info['btn_toggle'].configure(text="▼")
            
        widget_info['expandido'] = not widget_info['expandido']
        
        # Actualizar scroll
        self.frame_materias_scroll.update_idletasks()
        self.canvas_materias.configure(scrollregion=self.canvas_materias.bbox("all"))

    def _agregar_grupo_al_horario(self, codigo_materia, nombre_grupo):
        """Agrega un grupo al horario con validación mejorada"""
        materia_info = self.materias_data.get(codigo_materia)
        if not materia_info:
            self._mostrar_mensaje_error("❌ Error", f"No se encontró información para la materia {codigo_materia}.")
            return
        
        grupo_info = materia_info['grupos'].get(nombre_grupo)
        if not grupo_info:
            self._mostrar_mensaje_error("❌ Error", f"No se encontró el grupo {nombre_grupo}.")
            return
            
        horarios_a_agregar = grupo_info['sesiones']
        conflictos = []
        
        # Verificar conflictos
        for horario in horarios_a_agregar:
            dia = horario['dia_semana']
            inicio = horario['hora_inicio']
            fin = horario['hora_fin']
            
            hora_inicio_dt = datetime.strptime(inicio, "%H:%M")
            hora_fin_dt = datetime.strptime(fin, "%H:%M")
            
            hora_actual_dt = hora_inicio_dt
            while hora_actual_dt < hora_fin_dt:
                hora_str = hora_actual_dt.strftime("%H:%M")
                if (dia, hora_str) in self.horario_asignado:
                    conflictos.append({
                        "dia": dia, 
                        "hora": hora_str, 
                        "materia_existente": self.horario_asignado[(dia, hora_str)]['info']['nombre']
                    })
                hora_actual_dt += timedelta(hours=1)

        if conflictos:
            mensaje_conflicto = "⚠️ Conflictos de Horario\n\nLos siguientes horarios ya están ocupados:\n\n"
            for c in conflictos:
                mensaje_conflicto += f"• {c['dia']} a las {c['hora']} - {c['materia_existente']}\n"
            
            self._mostrar_mensaje_warning("Conflicto", mensaje_conflicto)
            return
            
        # Agregar al horario
        for horario in horarios_a_agregar:
            dia = horario['dia_semana']
            inicio = horario['hora_inicio']
            fin = horario['hora_fin']
            
            hora_inicio_dt = datetime.strptime(inicio, "%H:%M")
            hora_fin_dt = datetime.strptime(fin, "%H:%M")
            
            hora_actual_dt = hora_inicio_dt
            while hora_actual_dt < hora_fin_dt:
                hora_str = hora_actual_dt.strftime("%H:%M")
                self.horario_asignado[(dia, hora_str)] = {
                    'codigo': codigo_materia,
                    'info': materia_info,
                    'nombre_grupo': nombre_grupo,
                    'horario_sesion': horario
                }
                hora_actual_dt += timedelta(hours=1)
        
        # Actualizar totales
        self.total_creditos += materia_info['creditos']
        self._actualizar_grilla_horarios()
        self._actualizar_indicadores()
        self._mostrar_mensaje_success("✅ Grupo Agregado", f"'{nombre_grupo}' de {materia_info['nombre']} agregado al horario")

    def _actualizar_grilla_horarios(self):
        """Actualiza la grilla del horario con animaciones suaves"""
        # Limpiar celdas
        for celda in self.grilla_widgets.values():
            for widget in celda.winfo_children():
                widget.destroy()
            tk.Label(celda, text="", bg="white").pack(fill="both", expand=True)

        # Agregar materias asignadas
        for (dia, hora), data in self.horario_asignado.items():
            if (dia, hora) in self.grilla_widgets:
                frame_celda = self.grilla_widgets[(dia, hora)]
                color = self.colores_materias.get(data['codigo'], "white")
                
                # Limpiar celda
                for widget in frame_celda.winfo_children():
                    widget.destroy()

                # Container principal de la celda
                container = tk.Frame(frame_celda, bg=color, relief="flat")
                container.pack(fill="both", expand=True, padx=2, pady=2)
                
                # Botón de eliminar (aparece en hover)
                btn_eliminar = tk.Label(
                    container,
                    text="❌",
                    font=("Segoe UI", 8),
                    bg=self.colores['danger'],
                    fg="white",
                    cursor="hand2",
                    padx=2, pady=1
                )
                btn_eliminar.place(relx=1.0, rely=0.0, anchor="ne")
                btn_eliminar.bind("<Button-1>", lambda e, d=dia, h=hora: self._eliminar_de_horario(d, h))
                
                # Información de la materia
                info_frame = tk.Frame(container, bg=color)
                info_frame.pack(fill="both", expand=True, padx=5, pady=3)
                
                # Nombre de la materia (con mejor manejo de texto largo)
                nombre_display = data['info']['nombre']
                if len(nombre_display) > 18:  # Aumenté el límite
                    nombre_display = nombre_display[:15] + "..."
                
                label_materia = tk.Label(
                    info_frame,
                    text=nombre_display,
                    bg=color,
                    font=("Segoe UI", 9, "bold"),
                    fg=self.colores['text_primary'],
                    justify=tk.CENTER,
                    wraplength=180  # Añadí wraplength para mejor ajuste
                )
                label_materia.pack()
                
                # Información adicional
                info_adicional = f"{data['nombre_grupo']}\n{data['horario_sesion']['tipo_sesion'][:3]}"
                label_info = tk.Label(
                    info_frame,
                    text=info_adicional,
                    bg=color,
                    font=("Segoe UI", 7),
                    fg=self.colores['text_secondary'],
                    justify=tk.CENTER
                )
                label_info.pack()
                
                # Tooltip con información completa
                self._crear_tooltip(container, self._generar_texto_tooltip(data))

    def _eliminar_de_horario(self, dia, hora):
        """Elimina una materia específica del horario"""
        if (dia, hora) in self.horario_asignado:
            data = self.horario_asignado[(dia, hora)]
            codigo_materia = data['codigo']
            nombre_grupo = data['nombre_grupo']
            creditos = data['info']['creditos']
            
            # Encontrar y eliminar todas las horas de este grupo
            horas_a_eliminar = []
            for (d, h), asignacion in self.horario_asignado.items():
                if (asignacion['codigo'] == codigo_materia and 
                    asignacion['nombre_grupo'] == nombre_grupo):
                    horas_a_eliminar.append((d, h))
            
            for hora_eliminar in horas_a_eliminar:
                del self.horario_asignado[hora_eliminar]
            
            # Actualizar créditos
            self.total_creditos -= creditos
            self._actualizar_grilla_horarios()
            self._actualizar_indicadores()
            
            self._mostrar_mensaje_info("🗑️ Eliminado", f"Grupo {nombre_grupo} eliminado del horario")

    def _actualizar_indicadores(self):
        """Actualiza los indicadores de créditos y resumen"""
        num_materias = len(set(data['codigo'] for data in self.horario_asignado.values()))
        
        # Actualizar label de créditos en toolbar
        self.creditos_label.configure(text=f"📊 {self.total_creditos} créditos")
        
        # Actualizar resumen en área de horario
        self.resumen_label.configure(text=f"{num_materias} materias • {self.total_creditos} créditos")
        
        # Cambiar color según la cantidad de créditos
        if self.total_creditos <= 12:
            bg_color = self.colores['primary_light']
            fg_color = self.colores['primary']
        elif self.total_creditos <= 18:
            bg_color = "#FEF3C7"  # Amarillo claro
            fg_color = "#D97706"  # Amarillo oscuro
        else:
            bg_color = "#FEE2E2"  # Rojo claro
            fg_color = self.colores['danger']
            
        self.creditos_label.configure(bg=bg_color, fg=fg_color)

    def _limpiar_horario(self):
        """Limpia completamente el horario"""
        if not self.horario_asignado:
            self._mostrar_mensaje_info("ℹ️ Información", "El horario ya está vacío")
            return
            
        if messagebox.askyesno("🗑️ Confirmar", "¿Estás seguro de que quieres limpiar todo el horario?"):
            self.horario_asignado = {}
            self.total_creditos = 0
            self._actualizar_grilla_horarios()
            self._actualizar_indicadores()
            self._mostrar_mensaje_success("✅ Limpiado", "Horario limpiado completamente")

    def _guardar_horario(self):
        """Guarda el horario actual (placeholder)"""
        if not self.horario_asignado:
            self._mostrar_mensaje_warning("⚠️ Aviso", "No hay materias en el horario para guardar")
            return
        
        # Aquí se implementaría la lógica de guardado real
        self._mostrar_mensaje_success("💾 Guardado", "Horario guardado exitosamente")

    def _generar_texto_tooltip(self, data):
        """Genera el texto del tooltip con información completa"""
        horario = data['horario_sesion']
        return (f"{data['info']['nombre']}\n"
                f"Código: {data['codigo']}\n"
                f"Grupo: {data['nombre_grupo']}\n"
                f"Docente: {horario.get('docente', 'N/A')}\n"
                f"Tipo: {horario['tipo_sesion']}\n"
                f"Horario: {horario['hora_inicio']}-{horario['hora_fin']}\n"
                f"Créditos: {data['info']['creditos']}")

    def _crear_tooltip(self, widget, texto):
        """Crea un tooltip para un widget"""
        def mostrar_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(
                tooltip,
                text=texto,
                justify='left',
                background=self.colores['text_primary'],
                foreground='white',
                relief='flat',
                borderwidth=1,
                font=("Segoe UI", 9),
                padx=10, pady=8
            )
            label.pack()
            
            def ocultar_tooltip():
                tooltip.destroy()
            
            tooltip.after(3000, ocultar_tooltip)  # Auto-hide después de 3 segundos
            
        def ocultar_tooltip_inmediato(event):
            # Esta función se llamaría si quisiéramos ocultar al salir del widget
            pass
            
        widget.bind("<Enter>", mostrar_tooltip)

    # Métodos de mensajes modernos
    def _mostrar_mensaje_success(self, titulo, mensaje):
        """Muestra un mensaje de éxito moderno"""
        self._mostrar_mensaje_custom(titulo, mensaje, "info", self.colores['success'])

    def _mostrar_mensaje_error(self, titulo, mensaje):
        """Muestra un mensaje de error moderno"""
        self._mostrar_mensaje_custom(titulo, mensaje, "error", self.colores['danger'])

    def _mostrar_mensaje_warning(self, titulo, mensaje):
        """Muestra un mensaje de advertencia moderno"""
        self._mostrar_mensaje_custom(titulo, mensaje, "warning", self.colores['warning'])

    def _mostrar_mensaje_info(self, titulo, mensaje):
        """Muestra un mensaje informativo moderno"""
        self._mostrar_mensaje_custom(titulo, mensaje, "info", self.colores['primary'])

    def _mostrar_mensaje_custom(self, titulo, mensaje, tipo, color):
        """Muestra un mensaje personalizado"""
        # Para simplicidad, usamos messagebox estándar
        # En una implementación más avanzada, se podría crear un dialog personalizado
        if tipo == "error":
            messagebox.showerror(titulo, mensaje)
        elif tipo == "warning":
            messagebox.showwarning(titulo, mensaje)
        else:
            messagebox.showinfo(titulo, mensaje)

    def run(self):
        """Inicia la aplicación"""
        self.master.mainloop()
        
    def __del__(self):
        """Destructor para cerrar la conexión a la BD"""
        if hasattr(self, 'conexion_db') and self.conexion_db:
            self.conexion_db.close()

# Función principal para ejecutar la aplicación
def main():
    root = tk.Tk()
    app = AplicacionHorarioModerna(root)
    app.run()

if __name__ == "__main__":
    main()
