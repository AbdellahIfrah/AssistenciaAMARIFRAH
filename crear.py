# # import sqlite3
# # from werkzeug.security import generate_password_hash

# # conn = sqlite3.connect("asistencia.db")
# # cur = conn.cursor()

# # admin_user = ("admin", generate_password_hash("admin123"), "Supervisor", "Supervisor", "admin")

# # cur.execute("""
# # INSERT OR IGNORE INTO usuarios (usuario, password, nombre, cargo, rol)
# # VALUES (?, ?, ?, ?, ?)
# # """, admin_user)

# # conn.commit()
# # conn.close()

# # print("✅ Usuario ADMIN creado")
# import sqlite3
# from werkzeug.security import generate_password_hash

# # Conectar a la base de datos
# conn = sqlite3.connect("asistencia.db")
# cur = conn.cursor()

# # Datos del trabajador (EJEMPLO)
# usuario = "trabajador1"
# password = "1234"          # contraseña que usará el trabajador
# nombre = "Juan Pérez"
# cargo = "Albañil"

# # Encriptar contraseña (MUY IMPORTANTE)
# password_hash = generate_password_hash(password)

# # Insertar en la tabla usuarios
# cur.execute("""
# INSERT INTO usuarios (usuario, password, nombre, cargo)
# VALUES (?, ?, ?, ?)
# """, (usuario, password_hash, nombre, cargo))

# conn.commit()
# conn.close()

# print("✅ Usuario creado correctamente")
# print("Usuario:", usuario)
# print("Contraseña:", password)

