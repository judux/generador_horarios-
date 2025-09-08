import sqlite3
import os
import json
from datetime import datetime, timedelta

# Nombre del archivo de la base de datos
DATABASE_NAME = "horarios.db"
# Ruta al archivo de la base de datos
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATABASE_NAME)

def crear_conexion():
    """Crea una conexión a la base de datos SQLite."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        print(f"Conexión exitosa a la base de datos: {DATABASE_PATH}")
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
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
            );
        """)
        conn.commit()
        print("Tablas creadas o ya existentes.")
    except sqlite3.Error as e:
        print(f"Error al crear las tablas: {e}")

def insertar_materia(conn, codigo_materia, nombre_materia, creditos=None):
    """Inserta una nueva materia en la base de datos."""
    sql = ''' INSERT INTO Materias(codigo_materia, nombre_materia, creditos)
              VALUES(?,?,?) '''
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (codigo_materia, nombre_materia, creditos))
        conn.commit()
        print(f"Materia insertada: {codigo_materia} - {nombre_materia}")
        return True
    except sqlite3.IntegrityError:
        print(f"INFO: La materia con código {codigo_materia} ya existe. No se reinsertará.")
        return False
    except sqlite3.Error as e:
        print(f"Error al insertar materia {codigo_materia}: {e}")
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
        print(f"Grupo de materia insertado: ID {id_grupo_materia} para {codigo_materia_fk} (Grupo {nombre_grupo})")
        return id_grupo_materia
    except sqlite3.Error as e:
        print(f"Error al insertar grupo de materia para {codigo_materia_fk} (Grupo {nombre_grupo}): {e}")
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
        print(f"Error de formato de hora para la sesión del grupo ID {id_grupo_materia_fk}. Use HH:MM.")
        return None
    except sqlite3.Error as e:
        print(f"Error al insertar sesión de clase para grupo ID {id_grupo_materia_fk}: {e}")
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
                FROM GruposMateria WHERE codigo_materia_fk = ? ORDER BY nombre_grupo
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
                {"dia": "Lunes", "inicio": "15:00", "fin": "17:00", "salon": "Aula A306 (BLOQUE 3)"}
            ]},
            {"nombre_grupo": "Grupo 2", "tipo_sesion_predominante": "TEORICA", "docente": "ROMO GUERRON JOSE LUIS", "sesiones": [
                {"dia": "Lunes", "inicio": "17:00", "fin": "19:00", "salon": "Aula A306 (BLOQUE 3)"}
            ]},
            {"nombre_grupo": "Grupo 3", "tipo_sesion_predominante": "TEORICA", "docente": "ROMO GUERRON JOSE LUIS", "sesiones": [
                {"dia": "Martes", "inicio": "15:00", "fin": "17:00", "salon": "Aula A302 (BLOQUE 3)"}
            ]},
            {"nombre_grupo": "Grupo 4", "tipo_sesion_predominante": "PRACTICA", "docente": "ROMO GUERRON JOSE LUIS", "sesiones": [
                {"dia": "Martes", "inicio": "17:00", "fin": "19:00", "salon": "Aula A302 (BLOQUE 3)"}
            ]},
            {"nombre_grupo": "Grupo 5", "tipo_sesion_predominante": "PRACTICA", "docente": "ROMO GUERRON JOSE LUIS", "sesiones": [
                {"dia": "Miércoles", "inicio": "15:00", "fin": "17:00", "salon": "Aula A306 (BLOQUE 3)"}
            ]},
            {"nombre_grupo": "Grupo 6", "tipo_sesion_predominante": "PRACTICA", "docente": "ROMO GUERRON JOSE LUIS", "sesiones": [
                {"dia": "Miércoles", "inicio": "17:00", "fin": "19:00", "salon": "Aula A306 (BLOQUE 3)"}
            ]}
        ]},
        {"codigo": "5841", "nombre": "PROGRAMACION 1", "grupos": [
            {"nombre_grupo": "Grupo 13", "tipo_sesion_predominante": "PRACTICA", "docente": "INSUASTY PORTILLA EDWIN GIOVANNI", "sesiones": [
                {"dia": "Martes", "inicio": "17:00", "fin": "19:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"},
                {"dia": "Miércoles", "inicio": "15:00", "fin": "17:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"}
            ]},
            {"nombre_grupo": "Grupo 14", "tipo_sesion_predominante": "TEORICA", "docente": "INSUASTY PORTILLA EDWIN GIOVANNI", "sesiones": [ # Asumido TEORICA
                {"dia": "Martes", "inicio": "15:00", "fin": "17:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"},
                {"dia": "Miércoles", "inicio": "17:00", "fin": "19:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "9792", "nombre": "PROGRAMACION DE VIDEOJUEGOS", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "PRACTICA", "docente": "NARVAEZ CALVACHE DARIO FAVIER", "sesiones": [
                {"dia": "Martes", "inicio": "15:00", "fin": "17:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"},
                {"dia": "Jueves", "inicio": "07:00", "fin": "09:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "9810", "nombre": "PROGRAMACION 3", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "PRACTICA", "docente": "NARVAEZ CALVACHE DARIO FAVIER", "sesiones": [
                {"dia": "Martes", "inicio": "17:00", "fin": "19:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"},
                {"dia": "Jueves", "inicio": "11:00", "fin": "13:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "8064", "nombre": "PROYECTOS INFORMATICOS", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "TEORICA", "docente": "DOMINGUEZ DE LA ROSA JOHN JAIRO", "sesiones": [
                {"dia": "Viernes", "inicio": "15:00", "fin": "17:00", "salon": "Aula A401 (BLOQUE TECNOLOGICO)"}
            ]},
            {"nombre_grupo": "Grupo 2", "tipo_sesion_predominante": "PRACTICA", "docente": "DOMINGUEZ DE LA ROSA JOHN JAIRO", "sesiones": [
                {"dia": "Jueves", "inicio": "13:00", "fin": "15:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "9793", "nombre": "ROBOTICA EDUCATIVA", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "TEORICA", "docente": "ORDONEZ QUINTERO CRISTIAN CAMILO", "sesiones": [
                {"dia": "Lunes", "inicio": "07:00", "fin": "09:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"}
            ]},
            {"nombre_grupo": "Grupo 2", "tipo_sesion_predominante": "PRACTICA", "docente": "ORDONEZ QUINTERO CRISTIAN CAMILO", "sesiones": [
                {"dia": "Viernes", "inicio": "07:00", "fin": "09:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "9812", "nombre": "SOFTWARE DE AUTORIA", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "PRACTICA", "docente": "ORDONEZ QUINTERO CRISTIAN CAMILO", "sesiones": [
                {"dia": "Lunes", "inicio": "15:00", "fin": "17:00", "salon": "Aula A401 (BLOQUE TECNOLOGICO)"},
                {"dia": "Viernes", "inicio": "17:00", "fin": "19:00", "salon": "Aula A405 (BLOQUE TECNOLOGICO)"}
            ]}
        ]},
        {"codigo": "8061", "nombre": "TECNOLOGIA", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "TEORICA", "docente": "HERRERA FIGUEROA EDGAR HUMBERTO", "sesiones": [
                {"dia": "Martes", "inicio": "13:00", "fin": "15:00", "salon": "Aula A408 (BLOQUE TECNOLOGICO)"}
            ]},
            {"nombre_grupo": "Grupo 2", "tipo_sesion_predominante": "PRACTICA", "docente": "HERRERA FIGUEROA EDGAR HUMBERTO", "sesiones": [
                {"dia": "Jueves", "inicio": "13:00", "fin": "15:00", "salon": "Aula A406 (BLOQUE TECNOLOGICO)"}
            ]},
            {"nombre_grupo": "Grupo 3", "tipo_sesion_predominante": "PRACTICA", "docente": "HERRERA FIGUEROA EDGAR HUMBERTO", "sesiones": [
                {"dia": "Viernes", "inicio": "15:00", "fin": "17:00", "salon": None} # Salón N/A
            ]}
        ]},
        {"codigo": "9748", "nombre": "TIC PARA LA EDUCACION", "grupos": [
            {"nombre_grupo": "Grupo 1", "tipo_sesion_predominante": "TEORICA", "docente": "MORA OVIEDO LUIS EDUARDO", "sesiones": [
                {"dia": "Miércoles", "inicio": "17:00", "fin": "19:00", "salon": "Aula A407 (BLOQUE TECNOLOGICO)"}
            ]},
            {"nombre_grupo": "Grupo 3", "tipo_sesion_predominante": "TEORICA", "docente": "MORA OVIEDO LUIS EDUARDO", "sesiones": [ # Grupo 3 TEORICA
                {"dia": "Miércoles", "inicio": "15:00", "fin": "17:00", "salon": "Aula A302 (BLOQUE TECNOLOGICO)"} # Asumo que es BLOQUE 3, no TECNOLOGICO. Originalmente decía (BLOQUE TECNOLOGICO)
            ]},
            {"nombre_grupo": "Grupo 2", "tipo_sesion_predominante": "PRACTICA", "docente": "MORA OVIEDO LUIS EDUARDO", "sesiones": [ # Grupo 2 PRACTICA
                {"dia": "Viernes", "inicio": "15:00", "fin": "17:00", "salon": "Aula A302 (BLOQUE TECNOLOGICO)"} # Asumo que es BLOQUE 3
            ]},
            {"nombre_grupo": "Grupo 4", "tipo_sesion_predominante": "PRACTICA", "docente": "MORA OVIEDO LUIS EDUARDO", "sesiones": [
                {"dia": "Viernes", "inicio": "17:00", "fin": "20:00", "salon": "Aula A404 (BLOQUE TECNOLOGICO)"} # 3 horas
            ]}
        ]},
    ]

    for materia_data in materias_data:
        insertar_materia(conn, materia_data["codigo"], materia_data["nombre"], creditos_default)
        
        for grupo_data in materia_data["grupos"]:
            id_grupo = insertar_grupo_materia(conn, materia_data["codigo"], grupo_data["nombre_grupo"], cupos_default)
            if id_grupo:
                for sesion_data in grupo_data["sesiones"]:
                    insertar_sesion_clase(conn, id_grupo,
                                          grupo_data["tipo_sesion_predominante"], # Usar el tipo de sesión del grupo
                                          sesion_data["dia"],
                                          sesion_data["inicio"],
                                          sesion_data["fin"],
                                          grupo_data["docente"],
                                          sesion_data["salon"])
    print("--- Fin de Inserción de Datos Personalizados ---")


def obtener_horarios_materias_filtrados(conn, codigos_materias_seleccionadas, preferencia_turno):
    """
    Genera horarios posibles para las materias seleccionadas, aplicando filtros de turno.
    Esta es una versión que busca grupos no superpuestos para las materias seleccionadas.

    Args:
        conn: Objeto de conexión a la base de datos.
        codigos_materias_seleccionadas (list): Lista de códigos de las materias que el usuario quiere cursar.
        preferencia_turno (str): 'mañana', 'tarde' o 'cualquiera'.

    Returns:
        list: Una lista de diccionarios, donde cada diccionario representa un horario posible.
              Cada horario tiene la estructura:
              {
                  "codigo_materia": [
                      {"id_db_sesion": ..., "tipo": ..., "dia": ..., "hora_inicio": ..., "hora_fin": ..., "docente": ..., "salon": ..., "nombre_grupo": ...},
                      ...
                  ],
                  ...
              }
              Retorna una lista vacía si no hay horarios posibles.
    """
    horarios_encontrados = []
    materias_con_grupos = {}

    # 1. Obtener todos los grupos y sesiones para las materias seleccionadas
    for codigo_materia in codigos_materias_seleccionadas:
        materia_detalles = obtener_materia_con_detalles(conn, codigo_materia)
        if materia_detalles and materia_detalles["grupos_materia"]:
            materias_con_grupos[codigo_materia] = materia_detalles["grupos_materia"]
        else:
            print(f"Advertencia: No se encontraron grupos para la materia {codigo_materia}. No se puede generar un horario completo.")
            return [] # Si una materia no tiene grupos, no podemos generar un horario completo

    # 2. Filtrar grupos por turno y asegurarse de que cada grupo tenga sesiones
    grupos_filtrados_por_materia = {} # {codigo_materia: [grupo_dict1, grupo_dict2, ...]}

    for codigo, grupos in materias_con_grupos.items():
        grupos_filtrados_por_materia[codigo] = []
        for grupo in grupos:
            sesiones_validas_grupo = []
            es_grupo_valido_turno = True
            if not grupo["sesiones"]: # Si un grupo no tiene sesiones, no es válido para el horario
                es_grupo_valido_turno = False
            else:
                for sesion in grupo["sesiones"]:
                    hora_inicio_dt = datetime.strptime(sesion["hora_inicio"], "%H:%M").time()

                    if preferencia_turno == "mañana" and hora_inicio_dt.hour >= 13: # 1 PM
                        es_grupo_valido_turno = False
                        break
                    if preferencia_turno == "tarde" and hora_inicio_dt.hour < 13: # 1 PM
                        es_grupo_valido_turno = False
                        break
                    
                    sesiones_validas_grupo.append(sesion)

            if es_grupo_valido_turno and sesiones_validas_grupo: # Asegurarse de que haya sesiones válidas
                grupo_copia = grupo.copy()
                grupo_copia["sesiones"] = sesiones_validas_grupo
                grupos_filtrados_por_materia[codigo].append(grupo_copia)
    
    # Verificar que cada materia tenga al menos un grupo válido después del filtro de turno
    if any(not v for v in grupos_filtrados_por_materia.values()):
        print("No hay grupos disponibles que cumplan con la preferencia de turno para todas las materias seleccionadas.")
        return []

    # 3. Generar combinaciones de grupos (uno por materia) y verificar superposiciones
    import itertools

    # `grupos_filtrados_por_materia.values()` da una lista de listas de grupos,
    # por ejemplo: [[grupo_A1, grupo_A2], [grupo_B1, grupo_B2, grupo_B3]]
    # `itertools.product` generará combinaciones como (grupo_A1, grupo_B1), (grupo_A1, grupo_B2), etc.
    todas_las_combinaciones_de_grupos = itertools.product(*grupos_filtrados_por_materia.values())

    dias_semana_orden = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    for combinacion_actual_de_grupos in todas_las_combinaciones_de_grupos:
        horario_propuesto_minutos = {} # {(dia, minuto_del_dia): True} para marcar ocupación
        es_valido = True
        
        horario_para_guardar = {} # Para almacenar el formato de salida deseado

        for grupo_seleccionado in combinacion_actual_de_grupos:
            codigo_materia = grupo_seleccionado["codigo_materia_fk"]
            nombre_grupo = grupo_seleccionado["nombre_grupo_original"]

            if codigo_materia not in horario_para_guardar:
                horario_para_guardar[codigo_materia] = []

            for sesion_info in grupo_seleccionado["sesiones"]:
                dia_clase = sesion_info["dia"]
                hora_inicio_str = sesion_info["hora_inicio"]
                hora_fin_str = sesion_info["hora_fin"]

                hi_dt = datetime.strptime(hora_inicio_str, "%H:%M")
                hf_dt = datetime.strptime(hora_fin_str, "%H:%M")
                
                hi_min = hi_dt.hour * 60 + hi_dt.minute
                hf_min = hf_dt.hour * 60 + hf_dt.minute

                # Verificar superposiciones
                for m in range(hi_min, hf_min):
                    if (dia_clase, m) in horario_propuesto_minutos:
                        es_valido = False
                        break
                if not es_valido:
                    break
            
            if not es_valido:
                break
            
            # Si el grupo no superpone, agregamos sus sesiones al horario propuesto para futuras verificaciones
            for sesion_info in grupo_seleccionado["sesiones"]:
                dia_clase = sesion_info["dia"]
                hora_inicio_str = sesion_info["hora_inicio"]
                hora_fin_str = sesion_info["hora_fin"]

                hi_dt = datetime.strptime(hora_inicio_str, "%H:%M")
                hf_dt = datetime.strptime(hora_fin_str, "%H:%M")
                
                hi_min = hi_dt.hour * 60 + hi_dt.minute
                hf_min = hf_dt.hour * 60 + hf_dt.minute
                
                for m in range(hi_min, hf_min):
                    horario_propuesto_minutos[(dia_clase, m)] = True

                # También agregamos la sesión al formato de salida
                sesion_para_guardar = sesion_info.copy()
                sesion_para_guardar["nombre_grupo"] = nombre_grupo # Añadir el nombre del grupo a la sesión
                horario_para_guardar[codigo_materia].append(sesion_para_guardar)
        
        if es_valido:
            # Ordenar las sesiones dentro de cada materia para una mejor presentación
            for codigo_materia, sesiones in horario_para_guardar.items():
                sesiones.sort(key=lambda x: (dias_semana_orden.index(x["dia"]), datetime.strptime(x["hora_inicio"], "%H:%M")))
            horarios_encontrados.append(horario_para_guardar)
            
            # Puedes quitar el 'break' si quieres obtener *todos* los horarios posibles
            # break

    return horarios_encontrados


# --- Bloque de prueba ---
if __name__ == "__main__":
    # Opcional: Eliminar la base de datos para empezar de cero en cada ejecución de prueba.
    # PRECAUCIÓN: Esto borrará todos los datos. Descomentar solo para desarrollo y pruebas.
    if os.path.exists(DATABASE_PATH):
        # pass # Comenta esta línea para no borrar la BD si ya existe
        os.remove(DATABASE_PATH) # Descomenta esta línea para borrar la BD y empezar de cero
        print(f"Base de datos anterior '{DATABASE_PATH}' eliminada para prueba.")

    conn = crear_conexion()

    if conn is not None:
        crear_tablas(conn)

        # Insertar los datos personalizados
        insertar_datos_personalizados(conn)

        # --- Pruebas de las nuevas funciones ---
        print("\n--- Probando nuevas funciones ---")

        # Prueba de actualización de materia
        print("\nActualizando materia '9797' (ADMINISTRACION EDUCATIVA) a 'ADMIN. EDUCATIVA MODIFICADA' con 3 créditos...")
        actualizar_materia(conn, "9797", nuevo_nombre="ADMIN. EDUCATIVA MODIFICADA", nuevos_creditos=3)
        materia_actualizada = obtener_materia_por_codigo(conn, "9797")
        print(f"Materia 9797 después de actualizar: {materia_actualizada}")

        # Prueba de actualización de grupo
        # Necesitamos obtener el ID de un grupo existente
        materia_ejemplo = obtener_materia_con_detalles(conn, "9797")
        if materia_ejemplo and materia_ejemplo["grupos_materia"]:
            id_primer_grupo = materia_ejemplo["grupos_materia"][0]["id_db_grupo"]
            print(f"\nActualizando grupo ID {id_primer_grupo} a 'Grupo A' con 30 cupos...")
            actualizar_grupo_materia(conn, id_primer_grupo, nuevo_nombre_grupo="Grupo A", nuevos_cupos=30)
            grupo_actualizado = obtener_grupo_por_id(conn, id_primer_grupo)
            print(f"Grupo {id_primer_grupo} después de actualizar: {grupo_actualizado}")
        
        # Prueba de actualización de sesión
        # Necesitamos obtener el ID de una sesión existente
        if materia_ejemplo and materia_ejemplo["grupos_materia"] and materia_ejemplo["grupos_materia"][0]["sesiones"]:
            id_primera_sesion = materia_ejemplo["grupos_materia"][0]["sesiones"][0]["id_db_sesion"]
            print(f"\nActualizando sesión ID {id_primera_sesion} a las 14:00 y docente 'Nuevo Docente'...")
            actualizar_sesion_clase(conn, id_primera_sesion, hora_inicio="14:00", docente="Nuevo Docente")
            sesion_actualizada = obtener_sesion_por_id(conn, id_primera_sesion)
            print(f"Sesión {id_primera_sesion} después de actualizar: {sesion_actualizada}")

        # Prueba de eliminación de sesión
        if materia_ejemplo and materia_ejemplo["grupos_materia"] and materia_ejemplo["grupos_materia"][0]["sesiones"]:
             # Obtener una sesión que no sea la que se actualizó para no interferir con la prueba anterior
            if len(materia_ejemplo["grupos_materia"][0]["sesiones"]) > 1:
                id_sesion_a_eliminar = materia_ejemplo["grupos_materia"][0]["sesiones"][1]["id_db_sesion"]
                print(f"\nEliminando sesión ID {id_sesion_a_eliminar}...")
                eliminar_sesion_clase(conn, id_sesion_a_eliminar)
                sesion_eliminada = obtener_sesion_por_id(conn, id_sesion_a_eliminar)
                print(f"Sesión {id_sesion_a_eliminar} después de eliminar: {sesion_eliminada} (debería ser None)")


        # Prueba de eliminación de grupo (esto también eliminará sus sesiones por CASCADE)
        materia_ejemplo_2 = obtener_materia_con_detalles(conn, "9807") # Materia AMBIENTES DE APRENDIZAJE
        if materia_ejemplo_2 and materia_ejemplo_2["grupos_materia"]:
            id_grupo_a_eliminar = materia_ejemplo_2["grupos_materia"][0]["id_db_grupo"]
            print(f"\nEliminando grupo ID {id_grupo_a_eliminar} de la materia 9807...")
            eliminar_grupo_materia(conn, id_grupo_a_eliminar)
            grupo_eliminado = obtener_grupo_por_id(conn, id_grupo_a_eliminar)
            print(f"Grupo {id_grupo_a_eliminar} después de eliminar: {grupo_eliminado} (debería ser None)")
            # Verificar si las sesiones también se fueron
            print("Verificando sesiones del grupo eliminado:")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM SesionesClase WHERE id_grupo_materia_fk = ?", (id_grupo_a_eliminar,))
            sesiones_del_grupo_eliminado = cursor.fetchall()
            print(f"Sesiones asociadas al grupo {id_grupo_a_eliminar}: {sesiones_del_grupo_eliminado} (debería ser vacía)")

        # Prueba de eliminación de materia (esto eliminará grupos y sesiones por CASCADE)
        print("\nEliminando materia '9808' (COMUNICACION Y REDES)...")
        eliminar_materia(conn, "9808")
        materia_eliminada = obtener_materia_por_codigo(conn, "9808")
        print(f"Materia 9808 después de eliminar: {materia_eliminada} (debería ser None)")


        # Consultar datos para verificar después de modificaciones
        print("\n--- Consultando Todas las Materias (Simple) después de modificaciones ---")
        materias_lista = obtener_todas_las_materias_simple(conn)
        if materias_lista:
            for materia in materias_lista:
                print(materia)
        else:
            print("No hay materias en la base de datos después de la eliminación.")

        print("\n--- Generando un horario para materias seleccionadas (ejemplo) ---")
        # Asegúrate de que los códigos de materia existan después de las eliminaciones de prueba
        codigos_para_horario = ["9797", "9788", "9790"] # Materias existentes
        preferencia = "mañana" # "tarde", "cualquiera"

        horarios_posibles = obtener_horarios_materias_filtrados(conn, codigos_para_horario, preferencia)

        if horarios_posibles:
            print(f"\nSe encontraron {len(horarios_posibles)} horarios posibles para el turno de {preferencia}:")
            for i, horario in enumerate(horarios_posibles):
                print(f"\n--- Horario {i+1} ---")
                for codigo_materia, sesiones in horario.items():
                    print(f"  Materia: {codigo_materia}")
                    for sesion in sesiones:
                        print(f"    Grupo: {sesion['nombre_grupo']}, Tipo: {sesion['tipo']}, Día: {sesion['dia']}, Hora: {sesion['hora_inicio']}-{sesion['hora_fin']}, Docente: {sesion['docente']}, Salón: {sesion['salon']}")
        else:
            print("\nNo se encontraron horarios que cumplan con los criterios.")

        conn.close()
        print("\nConexión a la base de datos cerrada.")
    else:
        print("No se pudo establecer una conexión con la base de datos.")
