import sqlite3
import os
import json
import logging
from datetime import datetime, timedelta


# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE_NAME = "horarios.db"
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATABASE_NAME)

def crear_conexion():
    """Crea una conexión a la base de datos SQLite."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        logging.info(f"Conexión exitosa a la base de datos: {DATABASE_PATH}")
    except sqlite3.Error as e:
        logging.error(f"Error al conectar con la base de datos: {e}")
    return conn

def crear_tablas(conn):
    """Crea las tablas en la base de datos si no existen."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Materias (
                codigo_materia TEXT PRIMARY KEY,
                nombre_materia TEXT NOT NULL,
                creditos INTEGER
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS GruposMateria (
                id_grupo_materia INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_materia_fk TEXT NOT NULL,
                nombre_grupo TEXT NOT NULL,
                cupos INTEGER,
                FOREIGN KEY (codigo_materia_fk) REFERENCES Materias (codigo_materia) ON DELETE CASCADE ON UPDATE CASCADE
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS SesionesClase (
                id_sesion INTEGER PRIMARY KEY AUTOINCREMENT,
                id_grupo_materia_fk INTEGER NOT NULL,
                tipo_sesion TEXT NOT NULL,
                dia_semana TEXT NOT NULL,
                hora_inicio TEXT NOT NULL,
                hora_fin TEXT NOT NULL,
                docente TEXT,
                salon TEXT,
                FOREIGN KEY (id_grupo_materia_fk) REFERENCES GruposMateria (id_grupo_materia) ON DELETE CASCADE ON UPDATE CASCADE
            );git
        """)
        conn.commit()
        logging.info("Tablas creadas o ya existentes.")
    except sqlite3.Error as e:
        logging.error(f"Error al crear las tablas: {e}")

def insertar_materia(conn, codigo_materia, nombre_materia, creditos=None):
    """Inserta una nueva materia en la base de datos."""
    sql = ''' INSERT INTO Materias(codigo_materia, nombre_materia, creditos)
              VALUES(?,?,?) '''
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (codigo_materia, nombre_materia, creditos))
        conn.commit()
        logging.info(f"Materia insertada: {codigo_materia} - {nombre_materia}")
        return True
    except sqlite3.IntegrityError:
        logging.info(f"La materia con código {codigo_materia} ya existe. No se reinsertará.")
        return False
    except sqlite3.Error as e:
        logging.error(f"Error al insertar materia {codigo_materia}: {e}")
        return False

def insertar_grupo_materia(conn, codigo_materia_fk, nombre_grupo, cupos=None):
    """Inserta un nuevo grupo de materia en la base de datos."""
    sql = ''' INSERT INTO GruposMateria(codigo_materia_fk, nombre_grupo, cupos)
              VALUES(?,?,?) '''
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (codigo_materia_fk, nombre_grupo, cupos))
        conn.commit()
        id_grupo_materia = cursor.lastrowid
        logging.info(f"Grupo de materia insertado: ID {id_grupo_materia} para {codigo_materia_fk} (Grupo {nombre_grupo})")
        return id_grupo_materia
    except sqlite3.Error as e:
        logging.error(f"Error al insertar grupo de materia para {codigo_materia_fk} (Grupo {nombre_grupo}): {e}")
        return None

def insertar_sesion_clase(conn, id_grupo_materia_fk, tipo_sesion, dia_semana,
                          hora_inicio, hora_fin, docente=None, salon=None):
    """Inserta una nueva sesión de clase en la base de datos."""
    sql = ''' INSERT INTO SesionesClase(id_grupo_materia_fk, tipo_sesion, dia_semana,
                                        hora_inicio, hora_fin, docente, salon)
              VALUES(?,?,?,?,?,?,?) '''
    try:
        # Validación básica de formato de hora
        datetime.strptime(hora_inicio, "%H:%M")
        datetime.strptime(hora_fin, "%H:%M")

        cursor = conn.cursor()
        cursor.execute(sql, (id_grupo_materia_fk, tipo_sesion, dia_semana,
                             hora_inicio, hora_fin, docente, salon))
        conn.commit()
        return cursor.lastrowid
    except ValueError:
        logging.error(f"Error de formato de hora para la sesión del grupo ID {id_grupo_materia_fk}. Use HH:MM.")
        return None
    except sqlite3.Error as e:
        logging.error(f"Error al insertar sesión de clase para grupo ID {id_grupo_materia_fk}: {e}")
        return None

# --- Nuevas Funciones para Obtener Entidades Individuales ---
def obtener_materia_por_codigo(conn, codigo_materia):
    """Obtiene la información de una materia por su código."""
    sql = "SELECT codigo_materia, nombre_materia, creditos FROM Materias WHERE codigo_materia = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (codigo_materia,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Error al obtener materia por código {codigo_materia}: {e}")
        return None

def obtener_grupo_por_id(conn, id_grupo):
    """Obtiene la información de un grupo por su ID."""
    sql = "SELECT id_grupo_materia, codigo_materia_fk, nombre_grupo, cupos FROM GruposMateria WHERE id_grupo_materia = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (id_grupo,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Error al obtener grupo por ID {id_grupo}: {e}")
        return None

def obtener_sesion_por_id(conn, id_sesion):
    """Obtiene la información de una sesión por su ID."""
    sql = """
    SELECT id_sesion, id_grupo_materia_fk, tipo_sesion, dia_semana, hora_inicio, hora_fin, docente, salon
    FROM SesionesClase WHERE id_sesion = ?
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (id_sesion,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Error al obtener sesión por ID {id_sesion}: {e}")
        return None

# --- Nuevas Funciones de Actualización ---
def actualizar_materia(conn, codigo_materia, nuevo_nombre=None, nuevos_creditos=None):
    """Actualiza los datos de una materia existente."""
    sets = []
    params = []
    if nuevo_nombre is not None:
        sets.append("nombre_materia = ?")
        params.append(nuevo_nombre)
    if nuevos_creditos is not None:
        sets.append("creditos = ?")
        params.append(nuevos_creditos)

    if not sets:
        print("No hay datos para actualizar para la materia.")
        return False

    sql = f"UPDATE Materias SET {', '.join(sets)} WHERE codigo_materia = ?"
    params.append(codigo_materia)

    try:
        cursor = conn.cursor()
        cursor.execute(sql, tuple(params))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Materia {codigo_materia} actualizada exitosamente.")
            return True
        else:
            print(f"Materia {codigo_materia} no encontrada para actualizar.")
            return False
    except sqlite3.Error as e:
        print(f"Error al actualizar materia {codigo_materia}: {e}")
        return False

def actualizar_grupo_materia(conn, id_grupo_materia, nuevo_nombre_grupo=None, nuevos_cupos=None):
    """Actualiza los datos de un grupo de materia existente."""
    sets = []
    params = []
    if nuevo_nombre_grupo is not None:
        sets.append("nombre_grupo = ?")
        params.append(nuevo_nombre_grupo)
    if nuevos_cupos is not None:
        sets.append("cupos = ?")
        params.append(nuevos_cupos)

    if not sets:
        print("No hay datos para actualizar para el grupo.")
        return False

    sql = f"UPDATE GruposMateria SET {', '.join(sets)} WHERE id_grupo_materia = ?"
    params.append(id_grupo_materia)

    try:
        cursor = conn.cursor()
        cursor.execute(sql, tuple(params))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Grupo de materia ID {id_grupo_materia} actualizado exitosamente.")
            return True
        else:
            print(f"Grupo de materia ID {id_grupo_materia} no encontrado para actualizar.")
            return False
    except sqlite3.Error as e:
        print(f"Error al actualizar grupo de materia ID {id_grupo_materia}: {e}")
        return False

def actualizar_sesion_clase(conn, id_sesion, tipo_sesion=None, dia_semana=None,
                            hora_inicio=None, hora_fin=None, docente=None, salon=None):
    """Actualiza los datos de una sesión de clase existente."""
    sets = []
    params = []
    if tipo_sesion is not None:
        sets.append("tipo_sesion = ?")
        params.append(tipo_sesion)
    if dia_semana is not None:
        sets.append("dia_semana = ?")
        params.append(dia_semana)
    if hora_inicio is not None:
        sets.append("hora_inicio = ?")
        params.append(hora_inicio)
    if hora_fin is not None:
        sets.append("hora_fin = ?")
        params.append(hora_fin)
    if docente is not None:
        sets.append("docente = ?")
        params.append(docente)
    if salon is not None:
        sets.append("salon = ?")
        params.append(salon)
    
    if not sets:
        print("No hay datos para actualizar para la sesión.")
        return False

    # Validación de formato de hora si se proporciona
    try:
        if hora_inicio is not None:
            datetime.strptime(hora_inicio, "%H:%M")
        if hora_fin is not None:
            datetime.strptime(hora_fin, "%H:%M")
    except ValueError:
        print(f"Error de formato de hora para la sesión ID {id_sesion}. Use HH:MM.")
        return False

    sql = f"UPDATE SesionesClase SET {', '.join(sets)} WHERE id_sesion = ?"
    params.append(id_sesion)

    try:
        cursor = conn.cursor()
        cursor.execute(sql, tuple(params))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Sesión de clase ID {id_sesion} actualizada exitosamente.")
            return True
        else:
            print(f"Sesión de clase ID {id_sesion} no encontrada para actualizar.")
            return False
    except sqlite3.Error as e:
        print(f"Error al actualizar sesión de clase ID {id_sesion}: {e}")
        return False

# --- Nuevas Funciones de Eliminación ---
def eliminar_materia(conn, codigo_materia):
    """Elimina una materia y todos sus grupos y sesiones asociados."""
    sql = "DELETE FROM Materias WHERE codigo_materia = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (codigo_materia,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Materia {codigo_materia} eliminada exitosamente (y sus grupos/sesiones).")
            return True
        else:
            print(f"Materia {codigo_materia} no encontrada para eliminar.")
            return False
    except sqlite3.Error as e:
        print(f"Error al eliminar materia {codigo_materia}: {e}")
        return False

def eliminar_grupo_materia(conn, id_grupo_materia):
    """Elimina un grupo de materia y todas sus sesiones asociadas."""
    sql = "DELETE FROM GruposMateria WHERE id_grupo_materia = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (id_grupo_materia,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Grupo de materia ID {id_grupo_materia} eliminado exitosamente (y sus sesiones).")
            return True
        else:
            print(f"Grupo de materia ID {id_grupo_materia} no encontrado para eliminar.")
            return False
    except sqlite3.Error as e:
        print(f"Error al eliminar grupo de materia ID {id_grupo_materia}: {e}")
        return False

def eliminar_sesion_clase(conn, id_sesion):
    """Elimina una sesión de clase específica."""
    sql = "DELETE FROM SesionesClase WHERE id_sesion = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (id_sesion,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Sesión de clase ID {id_sesion} eliminada exitosamente.")
            return True
        else:
            print(f"Sesión de clase ID {id_sesion} no encontrada para eliminar.")
            return False
    except sqlite3.Error as e:
        print(f"Error al eliminar sesión de clase ID {id_sesion}: {e}")
        return False

def obtener_todas_las_materias_simple(conn):
    """Obtiene una lista simple de todas las materias."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT codigo_materia, nombre_materia, creditos FROM Materias ORDER BY nombre_materia")
        materias = cursor.fetchall()
        return materias
    except sqlite3.Error as e:
        print(f"Error al obtener todas las materias: {e}")
        return []

# --- NUEVA FUNCIÓN AGREGADA ---
def obtener_horarios_de_materia(conn, codigo_materia):
    """
    Obtiene todos los horarios de todos los grupos para una materia específica.
    """
    sql = """
        SELECT
            T2.dia_semana,
            T2.hora_inicio,
            T2.hora_fin,
            T1.nombre_grupo,
            T2.docente,
            T2.salon,
            T2.tipo_sesion
        FROM GruposMateria AS T1
        INNER JOIN SesionesClase AS T2
        ON T1.id_grupo_materia = T2.id_grupo_materia_fk
        WHERE T1.codigo_materia_fk = ?
        ORDER BY T1.nombre_grupo, T2.dia_semana, T2.hora_inicio;
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (codigo_materia,))
        resultados = cursor.fetchall()

        # Convertir a una lista de diccionarios para facilitar el uso
        columnas = ["dia_semana", "hora_inicio", "hora_fin", "nombre_grupo", "docente", "salon", "tipo_sesion"]
        horarios_list = [dict(zip(columnas, row)) for row in resultados]
        return horarios_list
    except sqlite3.Error as e:
        print(f"Error al obtener horarios para la materia {codigo_materia}: {e}")
        return []

def obtener_materia_con_detalles(conn, codigo_materia_buscado):
    """Obtiene una materia con todos sus grupos y sesiones."""
    materia_info = None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT codigo_materia, nombre_materia, creditos FROM Materias WHERE codigo_materia = ?",
                       (codigo_materia_buscado,))
        materia_db = cursor.fetchone()

        if materia_db:
            materia_info = {
                "codigo": materia_db[0],
                "nombre": materia_db[1],
                "creditos": materia_db[2],
                "grupos_materia": []
            }
            cursor.execute("""
                SELECT id_grupo_materia, nombre_grupo, cupos, codigo_materia_fk
                FROM GruposMateria WHERE codigo_materia_fk = ?
                ORDER BY nombre_grupo
            """, (codigo_materia_buscado,))
            grupos_db = cursor.fetchall()

            for grupo_db in grupos_db:
                grupo_info = {
                    "id_db_grupo": grupo_db[0],
                    "nombre_grupo_original": grupo_db[1],
                    "cupos": grupo_db[2],
                    "codigo_materia_fk": grupo_db[3],
                    "sesiones": []
                }
                cursor.execute("""
                    SELECT id_sesion, tipo_sesion, dia_semana, hora_inicio, hora_fin, docente, salon
                    FROM SesionesClase WHERE id_grupo_materia_fk = ? ORDER BY dia_semana, hora_inicio
                """, (grupo_db[0],))
                sesiones_db = cursor.fetchall()
                for sesion_db in sesiones_db:
                    sesion_info = {
                        "id_db_sesion": sesion_db[0], "tipo": sesion_db[1], "dia": sesion_db[2],
                        "hora_inicio": sesion_db[3], "hora_fin": sesion_db[4],
                        "docente": sesion_db[5], "salon": sesion_db[6]
                    }
                    grupo_info["sesiones"].append(sesion_info)
                materia_info["grupos_materia"].append(grupo_info)
        return materia_info
    except sqlite3.Error as e:
        print(f"Error al obtener detalles de la materia {codigo_materia_buscado}: {e}")
        return None

def insertar_datos_personalizados(conn):
    """Inserta el conjunto de datos de materias proporcionado por el usuario."""
    print("\n--- Insertando Datos Personalizados ---")
    creditos_default = 2
    cupos_default = None # Según instrucción del usuario

    materias_data = [
        {"codigo": "9797", "nombre": "ADMINISTRACION EDUCATIVA", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "TEORICA", "docente": "HERRERA FIGUEROA EDGAR HUMBERTO", "sesiones": [
                {"dia": "Jueves", "inicio": "15:00", "fin": "17:00", "salon": "Aula A306 (BLOQUE 3)"},
                {"dia": "Viernes", "inicio": "13:00", "fin": "15:00", "salon": "Aula A306 (BLOQUE 3)"}
            ]}
        ]},
        {"codigo": "9807", "nombre": "AMBIENTES DE APRENDIZAJE", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "PRACTICA", "docente": "JOJOA JOJOA HAROLD ANTONIO", "sesiones": [
                {"dia": "Miércoles", "inicio": "11:00", "fin": "13:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"},
                {"dia": "Jueves", "inicio": "09:00", "fin": "11:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "9790", "nombre": "AMBIENTES VIRTUALES DE APRENDIZAJE", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "TEORICA", "docente": "DOMINGUEZ DE LA ROSA JOHN JAIRO", "sesiones": [
                {"dia": "Lunes", "inicio": "11:00", "fin": "13:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"}
            ]},
            {"nombre_grupo": "Grupo 2", "tipo_sesion_predominante": "PRACTICA", "docente": "DOMINGUEZ DE LA ROSA JOHN JAIRO", "sesiones": [
                {"dia": "Martes", "inicio": "11:00", "fin": "13:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "9788", "nombre": "APLICACIONES WEB", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "PRACTICA", "docente": "JATIVA ERAZO JAIRO OMAR", "sesiones": [
                {"dia": "Martes", "inicio": "07:00", "fin": "09:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"},
                {"dia": "Miércoles", "inicio": "07:00", "fin": "09:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "9789", "nombre": "APLICACIONES WEB EN SERIVIDOR", "grupos": [ # Corregido: SERVIDOR
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "PRACTICA", "docente": "NARVAEZ CALVACHE DARIO FAVIER", "sesiones": [
                {"dia": "Martes", "inicio": "09:00", "fin": "11:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"},
                {"dia": "Miércoles", "inicio": "09:00", "fin": "11:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "9808", "nombre": "COMUNICACION Y REDES", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "PRACTICA", "docente": "CARLOS FERNANDO GONZALEZ GUZMAN", "sesiones": [
                {"dia": "Lunes", "inicio": "17:00", "fin": "19:00", "salon": "Aula A408 (BLOQUE TECNOLOGICO)"},
                {"dia": "Miércoles", "inicio": "15:00", "fin": "17:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "9791", "nombre": "COMUNICACION VISUAL", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "TEORICA", "docente": "PAZ SAAVEDRA LUIS EDUARDO", "sesiones": [
                {"dia": "Jueves", "inicio": "17:00", "fin": "19:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"}
            ]},
            {"nombre_grupo": "Grupo 2", "tipo_sesion_predominante": "PRACTICA", "docente": "PAZ SAAVEDRA LUIS EDUARDO", "sesiones": [
                {"dia": "Viernes", "inicio": "15:00", "fin": "17:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "8320", "nombre": "CORRIENTES PEDAGOGICAS", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "TEORICA", "docente": "JATIVA ERAZO JAIRO OMAR", "sesiones": [
                {"dia": "Jueves", "inicio": "09:00", "fin": "11:00", "salon": "Aula A303 (BLOQUE 3)"},
                {"dia": "Viernes", "inicio": "09:00", "fin": "11:00", "salon": "Aula A303 (BLOQUE 3)"}
            ]}
        ]},
        {"codigo": "9785", "nombre": "DESARROLLO DE SOFTWARE", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "TEORICA", "docente": "DOMINGUEZ DE LA ROSA JOHN JAIRO", "sesiones": [
                {"dia": "Martes", "inicio": "15:00", "fin": "17:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"}
            ]},
            {"nombre_grupo": "Grupo 2", "tipo_sesion_predominante": "PRACTICA", "docente": "DOMINGUEZ DE LA ROSA JOHN JAIRO", "sesiones": [
                {"dia": "Miércoles", "inicio": "15:00", "fin": "17:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "9787", "nombre": "DESARROLLO DE SOFTWARE EDUCATIVO", "grupos": [
            {"nombre_grupo": "Grupo 2", "tipo_sesion_predominante": "TEORICA", "docente": "DOMINGUEZ DE LA ROSA JOHN JAIRO", "sesiones": [ # Grupo 2 TEORICA
                {"dia": "Miércoles", "inicio": "13:00", "fin": "15:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"}
            ]},
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "PRACTICA", "docente": "DOMINGUEZ DE LA ROSA JOHN JAIRO", "sesiones": [ # Grupo 1 PRACTICA
                {"dia": "Viernes", "inicio": "13:00", "fin": "15:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "4553", "nombre": "DIDACTICA DE LA INFORMATICA", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "TEORICA", "docente": "DELGADO ACHICANOY NATALIA FERNANDA", "sesiones": [
                {"dia": "Lunes", "inicio": "17:00", "fin": "19:00", "salon": "Aula A301 (Bloque 1 Sur B)"},
                {"dia": "Jueves", "inicio": "15:00", "fin": "17:00", "salon": "Aula A302 (BLOQUE 3)"}
            ]}
        ]},
        {"codigo": "9786", "nombre": "DISEÑO GRAFICO Y ANIMACION", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "PRACTICA", "docente": "DELGADO ACHICANOY NATALIA FERNANDA", "sesiones": [
                {"dia": "Lunes", "inicio": "15:00", "fin": "17:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"},
                {"dia": "Jueves", "inicio": "17:00", "fin": "19:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "FHILO_ED_SC", "nombre": "FILOSOFIA E HISTORIA DE LA EDUCACION", "grupos": [ # Codigo SIN_CODIGO cambiado
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "TEORICA", "docente": "PAZ SAAVEDRA LUIS EDUARDO", "sesiones": [
                {"dia": "Miércoles", "inicio": "13:00", "fin": "15:00", "salon": "Aula A402 (Bloque 1 Sur B)"},
                {"dia": "Jueves", "inicio": "13:00", "fin": "15:00", "salon": "Aula A102 (BLOQUE 3)"}
            ]}
        ]},
        {"codigo": "6537", "nombre": "HARDWARE Y SISTEMAS OPERATIVOS", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "TEORICA", "docente": "ROSERO CALDERON OSCAR ANDRES", "sesiones": [
                {"dia": "Lunes", "inicio": "15:00", "fin": "17:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"},
                {"dia": "Jueves", "inicio": "17:00", "fin": "19:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"}
            ]},
            {"nombre_grupo": "Grupo 2", "tipo_sesion_predominante": "TEORICA", "docente": "ROSERO CALDERON OSCAR ANDRES", "sesiones": [
                {"dia": "Lunes", "inicio": "17:00", "fin": "19:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"},
                {"dia": "Jueves", "inicio": "15:00", "fin": "17:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "9809", "nombre": "INVESTIGACION CUALITATIVA", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "TEORICA", "docente": "JOJOA JOJOA HAROLD ANTONIO", "sesiones": [
                {"dia": "Martes", "inicio": "13:00", "fin": "15:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"}
            ]},
            {"nombre_grupo": "Grupo 2", "tipo_sesion_predominante": "PRACTICA", "docente": "JOJOA JOJOA HAROLD ANTONIO", "sesiones": [
                {"dia": "Viernes", "inicio": "09:00", "fin": "11:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "1313", "nombre": "PRACTICA DOCENTE 1", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "TEORICA", "docente": "ROMO GUERRON JOSE LUIS", "sesiones": [
                {"dia": "Lunes", "inicio": "15:00", "fin": "17:00", "salon": "Aula A102 (BLOQUE 3)"}
            ]}
        ]},
        {"codigo": "1314", "nombre": "PRACTICA DOCENTE 2", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "PRACTICA", "docente": "ROMO GUERRON JOSE LUIS", "sesiones": [
                {"dia": "Lunes", "inicio": "17:00", "fin": "19:00", "salon": "Aula A102 (BLOQUE 3)"}
            ]}
        ]},
        {"codigo": "8325", "nombre": "PEDAGOGIA COMPARADA", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "TEORICA", "docente": "ROMO GUERRON JOSE LUIS", "sesiones": [
                {"dia": "Miércoles", "inicio": "07:00", "fin": "09:00", "salon": "Aula A306 (BLOQUE 3)"},
                {"dia": "Jueves", "inicio": "07:00", "fin": "09:00", "salon": "Aula A306 (BLOQUE 3)"}
            ]}
        ]},
        {"codigo": "9792", "nombre": "PROYECTO DE GRADO 1", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "TEORICA", "docente": "NARVAEZ CALVACHE DARIO FAVIER", "sesiones": [
                {"dia": "Lunes", "inicio": "07:00", "fin": "09:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"}
            ]},
            {"nombre_grupo": "Grupo 2", "tipo_sesion_predominante": "PRACTICA", "docente": "NARVAEZ CALVACHE DARIO FAVIER", "sesiones": [
                {"dia": "Lunes", "inicio": "09:00", "fin": "11:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "9794", "nombre": "PROYECTO DE GRADO 2", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "PRACTICA", "docente": "NARVAEZ CALVACHE DARIO FAVIER", "sesiones": [
                {"dia": "Lunes", "inicio": "09:00", "fin": "11:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"}
            ]},
            {"nombre_grupo": "Grupo 2", "tipo_sesion_predominante": "TEORICA", "docente": "NARVAEZ CALVACHE DARIO FAVIER", "sesiones": [
                {"dia": "Lunes", "inicio": "07:00", "fin": "09:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "9793", "nombre": "SIMULACION", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "TEORICA", "docente": "CHAVEZ SANCHEZ OSCAR DARIO", "sesiones": [
                {"dia": "Martes", "inicio": "17:00", "fin": "19:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"},
                {"dia": "Miércoles", "inicio": "17:00", "fin": "19:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "4554", "nombre": "SOCIEDAD, EDUCACION Y TECNOLOGIA", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "TEORICA", "docente": "DELGADO ACHICANOY NATALIA FERNANDA", "sesiones": [
                {"dia": "Martes", "inicio": "09:00", "fin": "11:00", "salon": "Aula A306 (BLOQUE 3)"},
                {"dia": "Miércoles", "inicio": "11:00", "fin": "13:00", "salon": "Aula A306 (BLOQUE 3)"}
            ]}
        ]},
        {"codigo": "5423", "nombre": "TECNOLOGIAS Y MEDIOS EDUCATIVOS", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "PRACTICA", "docente": "ROMO GUERRON JOSE LUIS", "sesiones": [
                {"dia": "Jueves", "inicio": "11:00", "fin": "13:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"},
                {"dia": "Viernes", "inicio": "11:00", "fin": "13:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"}
            ]}
        ]}
    ]

    for materia in materias_data:
        codigo = materia["codigo"]
        nombre = materia["nombre"]
        insertar_materia(conn, codigo, nombre)
        for grupo in materia["grupos"]:
            nombre_grupo = grupo["nombre_grupo"]
            id_grupo = insertar_grupo_materia(conn, codigo, nombre_grupo, cupos_default)
            if id_grupo:
                for sesion in grupo["sesiones"]:
                    insertar_sesion_clase(
                        conn=conn,
                        id_grupo_materia_fk=id_grupo,
                        tipo_sesion=grupo["tipo_sesion_predominante"],
                        dia_semana=sesion["dia"],
                        hora_inicio=sesion["inicio"],
                        hora_fin=sesion["fin"],
                        docente=grupo["docente"],
                        salon=sesion["salon"]
                    )
    print("--- Datos Personalizados Insertados con Éxito ---")
    
# Código de inicialización de la base de datos
if __name__ == '__main__':
    conn = crear_conexion()
    if conn:
        crear_tablas(conn)
        insertar_datos_personalizados(conn)
        
        # Ejemplo de uso de la nueva función
        horarios_aplicaciones_web = obtener_horarios_de_materia(conn, '9788')
        print("\nHorarios de APLICACIONES WEB:")
        print(json.dumps(horarios_aplicaciones_web, indent=2, ensure_ascii=False))

        conn.close()
