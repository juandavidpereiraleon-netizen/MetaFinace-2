# db_postgres.py
# -----------------------------
# PostgreSQL robusto para aplicación de metas, ahorros y salidas
# -----------------------------

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import re
import socket

# -----------------------------
# CONFIGURACIÓN DE CONEXIÓN POSTGRES
# -----------------------------
HOST = "aws-1-us-east-2.pooler.supabase.com"
PORT = "6543"
DATABASE = "postgres"
USER = "postgres.punocfyhkxxkyqsxrmaw"
PASSWORD = "kG4238aIfJ0u6Pkp"

# Forzar solo IPv4
socket.getaddrinfo = lambda host, port, *args, **kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (host, port))]

# -----------------------------
# CONEXIÓN
# -----------------------------
def conectar():
    return psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD,
        port=PORT,
        sslmode="require"
    )

def ejecutar_query(query, params=None, fetch=False):
    conn = conectar()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(query, params or ())
        resultado = cursor.fetchall() if fetch else None
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("❌ Error en query:", e)
        resultado = None
    finally:
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
        "SELECT * FROM usuarios WHERE correo=%s AND contrasena=%s",
        (correo, contrasena),
        fetch=True
    )
    return result[0] if result else None

def obtener_usuarios():
    return ejecutar_query("SELECT * FROM usuarios ORDER BY id", fetch=True)

def obtener_usuario_por_correo(correo):
    result = ejecutar_query("SELECT * FROM usuarios WHERE correo=%s", (correo,), fetch=True)
    return result[0] if result else None

# -----------------------------
# FUNCIONES DE METAS
# -----------------------------
def obtener_metas():
    """Devuelve todas las metas con totales de ahorros y salidas"""
    metas = ejecutar_query("SELECT * FROM metas ORDER BY id", fetch=True)
    if metas:
        for meta in metas:
            meta_id = meta['id']
            meta['total_ahorrado'] = obtener_total_ahorrado(meta_id)
            meta['total_salidas'] = obtener_total_salidas(meta_id)
    return metas or []

def agregar_meta(curso, nombre, fecha, costo):
    ejecutar_query(
        "INSERT INTO metas (curso, nombre, fecha, costo) VALUES (%s, %s, %s, %s)",
        (curso, nombre, fecha, costo)
    )

def actualizar_meta(meta_id, curso, nombre, fecha, costo):
    ejecutar_query(
        "UPDATE metas SET curso=%s, nombre=%s, fecha=%s, costo=%s WHERE id=%s",
        (curso, nombre, fecha, costo, meta_id)
    )

def eliminar_meta(meta_id):
    ejecutar_query("DELETE FROM metas WHERE id=%s", (meta_id,))

def obtener_metas_por_curso(curso, usuario_id=None):
    """Devuelve las metas de un curso específico"""
    metas = ejecutar_query(
        "SELECT * FROM metas WHERE curso=%s ORDER BY id",
        (curso,),
        fetch=True
    )
    # Añadir total_ahorrado y total_salidas por cada meta
    for meta in metas:
        meta_id = meta['id']
        meta['total_ahorrado'] = obtener_total_ahorrado(meta_id, usuario_id)
        meta['total_salidas'] = obtener_total_salidas(meta_id, usuario_id)
    return metas
def obtener_meta_por_id(meta_id):
    meta = ejecutar_query("SELECT * FROM metas WHERE id=%s", (meta_id,), fetch=True)
    if meta:
        meta = meta[0]
        meta['total_ahorrado'] = obtener_total_ahorrado(meta_id)
        meta['total_salidas'] = obtener_total_salidas(meta_id)
        return meta
    return None

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

def obtener_total_ahorrado(meta_id, usuario_id=None):
    if usuario_id:
        result = ejecutar_query(
            "SELECT SUM(cantidad) AS total FROM ahorros WHERE meta_id=%s AND usuario_id=%s",
            (meta_id, usuario_id),
            fetch=True
        )
    else:
        result = ejecutar_query(
            "SELECT SUM(cantidad) AS total FROM ahorros WHERE meta_id=%s",
            (meta_id,),
            fetch=True
        )
    return float(result[0]['total'] or 0) if result else 0

def obtener_total_salidas(meta_id, usuario_id=None):
    if usuario_id:
        result = ejecutar_query(
            "SELECT SUM(cantidad) AS total FROM salidas WHERE meta_id=%s AND usuario_id=%s",
            (meta_id, usuario_id),
            fetch=True
        )
    else:
        result = ejecutar_query(
            "SELECT SUM(cantidad) AS total FROM salidas WHERE meta_id=%s",
            (meta_id,),
            fetch=True
        )
    return float(result[0]['total'] or 0) if result else 0

# -----------------------------
# INIT
# -----------------------------
if __name__ == "__main__":
    crear_tablas()
    print("✅ Base de datos lista con todas las tablas y admin por defecto")
