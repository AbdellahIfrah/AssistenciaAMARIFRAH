# =========================
# IMPORTACIONES
# =========================
from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# =========================
# CONFIGURACIÓN
# =========================
app = Flask(__name__)
app.secret_key = "CLAVE_SUPER_SECRETA"  # cámbiala
DATABASE = "asistencia.db"

# =========================
# CONEXIÓN BD
# =========================
def conectar_db():
    return sqlite3.connect(DATABASE)

# =========================
# CREAR TABLAS
# =========================
def crear_tablas():
    conn = conectar_db()
    cur = conn.cursor()

    # cur.execute("""
    # CREATE TABLE IF NOT EXISTS usuarios (
    #     id INTEGER PRIMARY KEY AUTOINCREMENT,
    #     usuario TEXT UNIQUE,
    #     password TEXT,
    #     nombre TEXT,
    #     cargo TEXT
    # )
    # """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        password TEXT,
        nombre TEXT,
        cargo TEXT,
        rol TEXT DEFAULT 'trabajador'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS asistencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        fecha TEXT,
        hora_entrada TEXT,
        hora_salida TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )
    """)

    conn.commit()
    conn.close()

# =========================
# LOGIN
# =========================
@app.route("/", methods=["GET", "POST"])
def login():
    mensaje = ""

    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        conn = conectar_db()
        cur = conn.cursor()

        # cur.execute("SELECT id, password FROM usuarios WHERE usuario=?", (usuario,))
        cur.execute("SELECT id, password, rol FROM usuarios WHERE usuario=?", (usuario,))

        dato = cur.fetchone()
        conn.close()
        if dato and check_password_hash(dato[1], password):
            session["usuario_id"] = dato[0]
            session["rol"] = dato[2]  # guardamos rol en la sesión
            if dato[2] == "admin":
                return redirect("/admin")
            else:
                return redirect("/asistencia")
        else:
            mensaje = "❌ Usuario o contraseña incorrectos"

    return render_template("login.html", mensaje=mensaje)

# =========================
# ASISTENCIA
# =========================
# @app.route("/asistencia", methods=["GET", "POST"])
# def asistencia():
#     if "usuario_id" not in session:
#         return redirect("/")

#     mensaje = ""
#     usuario_id = session["usuario_id"]

#     if request.method == "POST":
#         accion = request.form["accion"]
#         hoy = datetime.now().strftime("%Y-%m-%d")
#         ahora = datetime.now().strftime("%H:%M:%S")

#         conn = conectar_db()
#         cur = conn.cursor()

#         if accion == "entrada":
#             cur.execute("""
#                 SELECT id FROM asistencia
#                 WHERE usuario_id=? AND fecha=?
#             """, (usuario_id, hoy))

#             if cur.fetchone():
#                 mensaje = "⚠️ Ya marcaste entrada"
#             else:
#                 cur.execute("""
#                     INSERT INTO asistencia
#                     (usuario_id, fecha, hora_entrada)
#                     VALUES (?, ?, ?)
#                 """, (usuario_id, hoy, ahora))
#                 conn.commit()
#                 mensaje = "✅ Entrada registrada"

#         if accion == "salida":
#             cur.execute("""
#                 SELECT id, hora_salida FROM asistencia
#                 WHERE usuario_id=? AND fecha=?
#             """, (usuario_id, hoy))

#             fila = cur.fetchone()
#             if not fila:
#                 mensaje = "❌ No tienes entrada"
#             elif fila[1]:
#                 mensaje = "⚠️ Ya marcaste salida"
#             else:
#                 cur.execute("""
#                     UPDATE asistencia
#                     SET hora_salida=?
#                     WHERE id=?
#                 """, (ahora, fila[0]))
#                 conn.commit()
#                 mensaje = "✅ Salida registrada"

#         conn.close()

#     return render_template("asistencia.html", mensaje=mensaje)


# =========================
# ASISTENCIA (mejorada)
# =========================
@app.route("/asistencia", methods=["GET", "POST"])
def asistencia():
    if "usuario_id" not in session:
        return redirect("/")

    mensaje = ""
    usuario_id = session["usuario_id"]
    hoy = datetime.now().strftime("%Y-%m-%d")
    ahora = datetime.now().strftime("%H:%M:%S")

    conn = conectar_db()
    cur = conn.cursor()

    if request.method == "POST":
        accion = request.form["accion"]

        # Obtener el último registro de asistencia del día
        cur.execute("""
            SELECT id, hora_entrada, hora_salida
            FROM asistencia
            WHERE usuario_id=? AND fecha=?
            ORDER BY id DESC
            LIMIT 1
        """, (usuario_id, hoy))
        fila = cur.fetchone()

        if accion == "entrada":
            if fila and not fila[2]:
                mensaje = "⚠️ Primero debes marcar salida antes de nueva entrada"
            else:
                cur.execute("""
                    INSERT INTO asistencia (usuario_id, fecha, hora_entrada)
                    VALUES (?, ?, ?)
                """, (usuario_id, hoy, ahora))
                conn.commit()
                mensaje = "✅ Entrada registrada"

        elif accion == "salida":
            if not fila:
                mensaje = "❌ No hay entrada para marcar salida"
            elif fila[2]:
                mensaje = "⚠️ Ya marcaste salida"
            else:
                cur.execute("""
                    UPDATE asistencia
                    SET hora_salida=?
                    WHERE id=?
                """, (ahora, fila[0]))
                conn.commit()
                mensaje = "✅ Salida registrada"

    conn.close()
    return render_template("asistencia.html", mensaje=mensaje)


# @app.route("/admin/asistencia", methods=["GET", "POST"])
# def admin_asistencia():
#     if "usuario_id" not in session or session.get("rol") != "admin":
#         return "❌ Acceso denegado"

#     fecha_inicio = request.form.get("fecha_inicio")
#     fecha_fin = request.form.get("fecha_fin")

#     conn = conectar_db()
#     cur = conn.cursor()

#     # query = """
#     #     SELECT u.usuario, u.nombre, a.fecha, a.hora_entrada, a.hora_salida
#     #     FROM asistencia a
#     #     JOIN usuarios u ON a.usuario_id = u.id
#     # """
#     query = """
#     SELECT a.id, u.usuario, u.nombre, a.fecha, a.hora_entrada, a.hora_salida,
#            CASE 
#                WHEN a.hora_entrada IS NOT NULL AND a.hora_salida IS NOT NULL 
#                THEN ROUND((julianday('2000-01-01 ' || a.hora_salida) - julianday('2000-01-01 ' || a.hora_entrada)) * 24, 2)
#                ELSE 0
#            END AS horas
#     FROM asistencia a
#     JOIN usuarios u ON a.usuario_id = u.id
# """

#     params = []

#     if fecha_inicio and fecha_fin:
#         query += " WHERE a.fecha BETWEEN ? AND ?"
#         params = [fecha_inicio, fecha_fin]

#     query += " ORDER BY u.nombre, a.fecha"
#     cur.execute(query, params)
#     datos = cur.fetchall()
#     conn.close()

#     # Calcular horas trabajadas por registro
#     registros = []
#     total_por_trabajador = {}
#     for fila in datos:
#         usuario, nombre, fecha, entrada, salida = fila
#         if entrada and salida:
#             fmt = "%H:%M:%S"
#             h_entrada = datetime.strptime(entrada, fmt)
#             h_salida = datetime.strptime(salida, fmt)
#             horas = (h_salida - h_entrada).seconds / 3600  # horas decimales
#         else:
#             horas = 0
#         registros.append((usuario, nombre, fecha, entrada, salida, round(horas,2)))
#         total_por_trabajador[usuario] = total_por_trabajador.get(usuario, 0) + horas

#     return render_template("asistencia_admin.html", registros=registros,
#                            total_por_trabajador=total_por_trabajador,
#                            fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)


@app.route("/admin/asistencia", methods=["GET", "POST"])
def admin_asistencia():
    if "usuario_id" not in session or session.get("rol") != "admin":
        return "❌ Acceso denegado"

    fecha_inicio = request.form.get("fecha_inicio")
    fecha_fin = request.form.get("fecha_fin")

    conn = conectar_db()
    cur = conn.cursor()

    # Query que trae id, usuario, nombre, fecha, entrada, salida y calcula horas
    query = """
        SELECT a.id, u.usuario, u.nombre, a.fecha, a.hora_entrada, a.hora_salida,
               CASE 
                   WHEN a.hora_entrada IS NOT NULL AND a.hora_salida IS NOT NULL 
                   THEN ROUND((julianday('2000-01-01 ' || a.hora_salida) - julianday('2000-01-01 ' || a.hora_entrada)) * 24, 2)
                   ELSE 0
               END AS horas
        FROM asistencia a
        JOIN usuarios u ON a.usuario_id = u.id
    """
    params = []

    # Filtro por fecha si se envía
    if fecha_inicio and fecha_fin:
        query += " WHERE a.fecha BETWEEN ? AND ?"
        params = [fecha_inicio, fecha_fin]

    query += " ORDER BY u.nombre, a.fecha"

    cur.execute(query, params)
    datos = cur.fetchall()
    conn.close()

    # Preparar registros y calcular total de horas por trabajador
    registros = []
    total_por_trabajador = {}

    for fila in datos:
        # Desempaquetar correctamente todas las columnas
        id_registro, usuario, nombre, fecha, entrada, salida, horas = fila

        # Agregar a lista de registros para la plantilla
        registros.append((id_registro, usuario, nombre, fecha, entrada, salida, horas))

        # Sumar horas al total por trabajador
        total_por_trabajador[usuario] = total_por_trabajador.get(usuario, 0) + horas

    # Renderizar plantilla profesional con sidebar y botón de editar
    return render_template(
        "asistencia_admin.html",
        registros=registros,
        total_por_trabajador=total_por_trabajador,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )


@app.route("/admin/editar_asistencia/<int:asistencia_id>", methods=["GET", "POST"])
def editar_asistencia(asistencia_id):
    if "usuario_id" not in session or session.get("rol") != "admin":
        return "❌ Acceso denegado"

    conn = conectar_db()
    cur = conn.cursor()
    mensaje = ""

    if request.method == "POST":
        fecha = request.form["fecha"]
        entrada = request.form["hora_entrada"]
        salida = request.form["hora_salida"]

        cur.execute("""
            UPDATE asistencia
            SET fecha=?, hora_entrada=?, hora_salida=?
            WHERE id=?
        """, (fecha, entrada, salida, asistencia_id))
        conn.commit()
        mensaje = "✅ Registro actualizado"

    # Obtener datos de la asistencia
    cur.execute("""
        SELECT a.id, u.usuario, u.nombre, a.fecha, a.hora_entrada, a.hora_salida
        FROM asistencia a
        JOIN usuarios u ON a.usuario_id = u.id
        WHERE a.id=?
    """, (asistencia_id,))
    fila = cur.fetchone()
    conn.close()

    return render_template("editar_asistencia.html", asistencia=fila, mensaje=mensaje)




# =========================
# ADMINISTRADOR
# =========================






# @app.route("/admin", methods=["GET", "POST"])
# def admin():
#     if "usuario_id" not in session or session.get("rol") != "admin":
#         return "❌ Acceso denegado"

#     mensaje = ""
#     conn = conectar_db()
#     cur = conn.cursor()

#     # Crear trabajador desde el panel
#     if request.method == "POST":
#         usuario = request.form["usuario"]
#         password = request.form["password"]
#         nombre = request.form["nombre"]
#         cargo = request.form["cargo"]

#         try:
#             cur.execute("""
#                 INSERT INTO usuarios (usuario, password, nombre, cargo, rol)
#                 VALUES (?, ?, ?, ?, 'trabajador')
#             """, (usuario, generate_password_hash(password), nombre, cargo))
#             conn.commit()
#             mensaje = "✅ Trabajador creado"
#         except sqlite3.IntegrityError:
#             mensaje = "❌ Usuario ya existe"

#     # Obtener lista de trabajadores
#     cur.execute("SELECT id, usuario, nombre, cargo FROM usuarios WHERE rol='trabajador'")
#     trabajadores = cur.fetchall()
#     conn.close()

#     return render_template("admin.html", mensaje=mensaje, trabajadores=trabajadores)





# ==================== ADMIN: PANEL PRINCIPAL ====================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "usuario_id" not in session or session.get("rol") != "admin":
        return "❌ Acceso denegado"

    mensaje = ""
    conn = conectar_db()
    cur = conn.cursor()

    # CREAR NUEVO TRABAJADOR
    if request.method == "POST" and request.form.get("accion") == "crear":
        usuario = request.form["usuario"]
        password = request.form["password"]
        nombre = request.form["nombre"]
        cargo = request.form["cargo"]

        try:
            cur.execute("""
                INSERT INTO usuarios (usuario, password, nombre, cargo, rol)
                VALUES (?, ?, ?, ?, 'trabajador')
            """, (usuario, generate_password_hash(password), nombre, cargo))
            conn.commit()
            mensaje = "✅ Trabajador creado"
        except sqlite3.IntegrityError:
            mensaje = "❌ Usuario ya existe"

    # ELIMINAR TRABAJADOR
    if request.method == "POST" and request.form.get("accion") == "eliminar":
        usuario_id = request.form["usuario_id"]
        cur.execute("DELETE FROM usuarios WHERE id=?", (usuario_id,))
        conn.commit()
        mensaje = "✅ Trabajador eliminado"

    # EDITAR TRABAJADOR
    if request.method == "POST" and request.form.get("accion") == "editar":
        usuario_id = request.form["usuario_id"]
        nombre = request.form["nombre"]
        cargo = request.form["cargo"]
        cur.execute("""
            UPDATE usuarios SET nombre=?, cargo=? WHERE id=?
        """, (nombre, cargo, usuario_id))
        conn.commit()
        mensaje = "✅ Trabajador editado"

    # LISTA DE TRABAJADORES
    cur.execute("SELECT id, usuario, nombre, cargo FROM usuarios WHERE rol='trabajador'")
    trabajadores = cur.fetchall()
    conn.close()
    return render_template("admin.html", mensaje=mensaje, trabajadores=trabajadores)



# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# =========================
# INICIO
# =========================
# if __name__ == "__main__":
#     crear_tablas()
#     app.run(host="0.0.0.0", port=5000, debug=True)
if __name__ == "__main__":
    crear_tablas()
    app.run(host="0.0.0.0", port=5000)
