import logging
import random
from database.connection import DatabaseManager

# --- Configuración ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CARRERAS_PRUEBA = ["Ingeniería de Sistemas", "Derecho", "Medicina"]
PERIODOS_PRUEBA = ["A2025", "B2025"]

def populate_grupos_data():
    """
    Asigna aleatoriamente carreras y periodos académicos a los registros existentes
    en la tabla GruposMateria que no tengan esa información.
    """
    logging.info("Iniciando el poblado de datos de prueba para GruposMateria...")
    db_manager = DatabaseManager()
    
    try:
        with db_manager.transaccion() as conn:
            cursor = conn.cursor()
            
            # 1. Obtener todos los grupos que necesitan ser actualizados
            cursor.execute("SELECT id_grupo_materia FROM GruposMateria WHERE carrera IS NULL OR periodo_academico IS NULL")
            grupos_a_actualizar = cursor.fetchall()
            
            if not grupos_a_actualizar:
                logging.info("No hay grupos que necesiten ser actualizados. Todos los registros ya tienen datos.")
                return

            logging.info(f"Se actualizarán {len(grupos_a_actualizar)} grupos.")
            
            # 2. Actualizar cada grupo con datos aleatorios
            for grupo_id_tuple in grupos_a_actualizar:
                grupo_id = grupo_id_tuple[0]
                carrera_aleatoria = random.choice(CARRERAS_PRUEBA)
                periodo_aleatorio = random.choice(PERIODOS_PRUEBA)
                
                update_query = "UPDATE GruposMateria SET carrera = ?, periodo_academico = ? WHERE id_grupo_materia = ?"
                cursor.execute(update_query, (carrera_aleatoria, periodo_aleatorio, grupo_id))
            
            logging.info("Poblado de datos completado exitosamente.")
            
    except Exception as e:
        logging.error(f"Ocurrió un error durante el poblado de datos: {e}")
        # El context manager de transacción se encargará del rollback
    finally:
        db_manager.cerrar_conexion()
        logging.info("Conexión a la base de datos cerrada.")

if __name__ == "__main__":
    populate_grupos_data()
