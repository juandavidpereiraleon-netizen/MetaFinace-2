# db_postgres_app.py
# -----------------------------
# Adaptación de DB SQLite a PostgreSQL (Supabase)
# -----------------------------

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import re

# -----------------------------
# CONFIGURACIÓN DE CONEXIÓN POSTGRES
# -----------------------------
HOST = "db.punocfyhkxxkyqsxrmaw.supabase.co"
DATABASE = "postgres"
USER = "postgres"
PASSWORD = "kG4238aIfJ0u6Pkp"
PORT = "5432"

def conectar():
    conn = psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD,
        port=PORT,
        sslmode="require"
    )
    return conn

def ejecutar_query(query, params=None, fetch=False):
    conn = conectar()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(query, params or ())
    if fetch:
        resultado = cursor.fetchall()
    else:
        resultado = None
    conn.commit()
    cursor.close()
    conn.close()
    return resultado

# -----------------------------
# CREACIÓN DE TABLAS
# -----------------------------
def crear_tablas():
    # Usuarios
    ejecutar_query("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            padre TEXT,
            estudiante TEXT,
            curso TEXT,
            promocion TEXT,
            correo TEXT UNIQUE,
            contrasena TEXT,
            tipo_usuario TEXT DEFAULT 'user'
        )
    """)

    # Metas
    ejecutar_query("""
        CREATE TABLE IF NOT EXISTS metas (
            id SERIAL PRIMARY KEY,
            curso TEXT,
            nombre TEXT,
            fecha TEXT,
            costo REAL
        )
    """)

    # Ahorros
    ejecutar_query("""
        CREATE TABLE IF NOT EXISTS ahorros (
            id SERIAL PRIMARY KEY,
            meta_id INTEGER REFERENCES metas(id) ON DELETE CASCADE,
            usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            cantidad REAL,
            fecha TEXT
        )
    """)

    # Salidas
    ejecutar_query("""
        CREATE TABLE IF NOT EXISTS salidas (
            id SERIAL PRIMARY KEY,
            meta_id INTEGER REFERENCES metas(id) ON DELETE CASCADE,
            usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            cantidad REAL,
            fecha TEXT
        )
    """)

    # Aportes
    ejecutar_query("""
        CREATE TABLE IF NOT EXISTS aportes (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            curso TEXT,
            cantidad REAL,
            fecha TEXT,
            hora TEXT
        )
    """)

    # Ascensos
    ejecutar_query("""
        CREATE TABLE IF NOT EXISTS ascensos (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            curso_anterior TEXT,
            curso_nuevo TEXT,
            fecha TEXT
        )
    """)

    # Admin por defecto
    ejecutar_query("""
        INSERT INTO usuarios (padre, estudiante, curso, promocion, correo, contrasena, tipo_usuario)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (correo) DO NOTHING
    """, ("-", "-", "-", "-", "juan.david.pereira.leon@gmail.com", "7719", "admin"))

# -----------------------------
# FUNCIONES DE USUARIOS
# -----------------------------
def registrar_usuario(padre, estudiante, curso, promocion, correo, contrasena):
    patron = r"^[a-zA-Z0-9._%+-]+@(gmail\.com|hotmail\.com|outlook\.com|yahoo\.com|ngc\.edu\.co)$"
    if not re.match(patron, correo):
        print("❌ Correo inválido o dominio no permitido.")
        return False
    try:
        ejecutar_query("""
            INSERT INTO usuarios (padre, estudiante, curso, promocion, correo, contrasena, tipo_usuario)
            VALUES (%s, %s, %s, %s, %s, %s, 'user')
        """, (padre, estudiante, curso, promocion, correo, contrasena))
        return True
    except Exception as e:
        print("❌ Error registrando usuario:", e)
        return False

def validar_login(correo, contrasena):
    result = ejecutar_query(
        "SELECT * FROM usuarios WHERE correo = %s AND contrasena = %s",
        (correo, contrasena),
        fetch=True
    )
    return result[0] if result else None

def obtener_usuarios():
    return ejecutar_query("SELECT * FROM usuarios;", fetch=True)

def obtener_usuario_por_correo(correo):
    result = ejecutar_query("SELECT * FROM usuarios WHERE correo = %s", (correo,), fetch=True)
    return result[0] if result else None

# -----------------------------
# FUNCIONES DE METAS
# -----------------------------
def agregar_meta(curso, nombre, fecha, costo):
    ejecutar_query(
        "INSERT INTO metas (curso, nombre, fecha, costo) VALUES (%s, %s, %s, %s)",
        (curso, nombre, fecha, costo)
    )

def obtener_metas():
    return ejecutar_query("SELECT * FROM metas;", fetch=True)

# -----------------------------
# AHORROS Y SALIDAS
# -----------------------------
def registrar_ahorro(meta_id, usuario_id, cantidad):
    fecha = datetime.now().strftime("%d/%m/%Y")
    ejecutar_query(
        "INSERT INTO ahorros (meta_id, usuario_id, cantidad, fecha) VALUES (%s, %s, %s, %s)",
        (meta_id, usuario_id, cantidad, fecha)
    )

def registrar_salida(meta_id, usuario_id, cantidad):
    fecha = datetime.now().strftime("%d/%m/%Y")
    ejecutar_query(
        "INSERT INTO salidas (meta_id, usuario_id, cantidad, fecha) VALUES (%s, %s, %s, %s)",
        (meta_id, usuario_id, cantidad, fecha)
    )

# -----------------------------
# APORTES
# -----------------------------
def registrar_aporte(usuario_id, curso, cantidad):
    ahora = datetime.now()
    fecha = ahora.strftime("%d/%m/%Y")
    hora = ahora.strftime("%H:%M:%S")
    ejecutar_query(
        "INSERT INTO aportes (usuario_id, curso, cantidad, fecha, hora) VALUES (%s, %s, %s, %s, %s)",
        (usuario_id, curso, cantidad, fecha, hora)
    )

# -----------------------------
# ASCENSOS
# -----------------------------
def registrar_ascenso(usuario_id, curso_anterior, curso_nuevo):
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ejecutar_query(
        "INSERT INTO ascensos (usuario_id, curso_anterior, curso_nuevo, fecha) VALUES (%s, %s, %s, %s)",
        (usuario_id, curso_anterior, curso_nuevo, fecha)
    )
    ejecutar_query("UPDATE usuarios SET curso = %s WHERE id = %s", (curso_nuevo, usuario_id))

# -----------------------------
# INIT
# -----------------------------
if __name__ == "__main__":
    crear_tablas()
    print("✅ Tablas creadas y admin por defecto listo en PostgreSQL (Supabase).")
