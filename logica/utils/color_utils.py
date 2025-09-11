
class ColorUtils:
	@staticmethod
	def generar_color_por_codigo(codigo: str) -> str:
		"""Genera un color hexadecimal basado en el código proporcionado."""
		# Algoritmo simple: usa hash del código para generar color
		hash_code = abs(hash(codigo))
		color = f"#{hash_code % 0xFFFFFF:06x}"
		return color
