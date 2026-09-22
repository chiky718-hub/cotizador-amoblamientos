import sqlite3

def inicializar_base_datos():
    conexion = sqlite3.connect('sistema_noziglia_mvp.db')
    cursor = conexion.cursor()

    # Tabla 1: Materiales (Se mantiene igual)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS materiales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_sku TEXT UNIQUE,
        nombre TEXT NOT NULL,
        categoria TEXT NOT NULL,
        unidad TEXT NOT NULL,
        precio_unitario REAL NOT NULL
    )
    ''')

    # Tabla 2: Cotizaciones (AMPLIADA CON DATOS DEL CLIENTE)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cotizaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_nombre TEXT NOT NULL,
        cliente_apellido TEXT,
        dni_cuit TEXT,
        telefono TEXT,
        direccion TEXT,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        costo_materiales REAL NOT NULL,
        margen_ganancia REAL NOT NULL,
        precio_final REAL NOT NULL,
        detalles_json TEXT NOT NULL,
        estado TEXT NOT NULL
    )
    ''')

    materiales_demo = [
        ('MEL-BLA-18', 'Placa Melamina Blanca 18mm (Faplac)', 'Maderas', 'Unidad', 45000.00),
        ('MEL-NOG-18', 'Placa Melamina Nogal Terracota 18mm', 'Maderas', 'Unidad', 58000.00),
        ('TAP-BLA-22', 'Tapacanto ABS Blanco 22mm', 'Terminaciones', 'ml', 450.00),
        ('BIS-CS-01', 'Bisagra Cazoleta Cierre Suave 35mm', 'Herrajes', 'Unidad', 1200.00),
        ('GUA-TEL-45', 'Guía Telescópica 45cm', 'Herrajes', 'Par', 3500.00),
        ('PER-ALU-MAN', 'Perfil Aluminio Manija tipo J', 'Perfilería', 'ml', 4200.00)
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO materiales (codigo_sku, nombre, categoria, unidad, precio_unitario)
    VALUES (?, ?, ?, ?, ?)
    ''', materiales_demo)

    conexion.commit()
    conexion.close()
    print("Base de datos actualizada con perfil de clientes creada con éxito.")

if __name__ == '__main__':
    inicializar_base_datos()