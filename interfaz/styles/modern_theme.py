import customtkinter as ctk
from tkinter import StringVar
class ModernTheme:
	"""Clase para definir el tema moderno de la interfaz."""
	def __init__(self):
		self.primary_color = "#3498db"
		self.secondary_color = "#2ecc71"
		self.background_color = "#ecf0f1"
		self.text_color = "#2c3e50"

	def crear_entry_moderno(self, parent, **kwargs):
		"""Crea un Entry con el tema moderno."""
		import tkinter as tk
		if 'font' not in kwargs:
			kwargs['font'] = ("Arial", 11)
		entry = tk.Entry(parent, bg=self.background_color, fg=self.text_color, **kwargs)
		return entry

	def crear_label_subtitulo(self, parent, texto=None, text=None, **kwargs):
		"""Crea un Label de subtítulo con el tema moderno. Permite 'texto' o 'text' como argumento."""
		contenido = texto if texto is not None else text
		if 'text_color' not in kwargs:
			kwargs['text_color'] = self.primary_color
		if 'font' not in kwargs:
			kwargs['font'] = ("Segoe UI", 16, "bold")
		if 'anchor' not in kwargs:
			kwargs['anchor'] = "center"
		label = ctk.CTkLabel(
			parent, 
			text=contenido,
			**kwargs
		)
		return label

	def crear_card_frame(self, parent, **kwargs):
		"""Crea un Frame tipo 'card' con el tema moderno."""
		import tkinter as tk
		frame = tk.Frame(parent, bg=self.background_color, bd=2, relief=tk.RIDGE, **kwargs)
		return frame

	def aplicar_tema(self, widget):
		"""Aplica el tema moderno a un widget dado."""
		# Aplica el color de fondo
		widget.configure(bg=self.background_color)
		# Aplica el color de texto solo si el widget soporta 'fg'
		try:
			widget.configure(fg=self.text_color)
		except Exception:
			pass
			pass
