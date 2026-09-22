import sqlite3

def inicializar_base_datos():
    # Conectar a la base de datos (se creará automáticamente si no existe)
    conexion = sqlite3.connect('sistema_noziglia_mvp.db')
    cursor = conexion.cursor()

    # 1. Crear tabla de Materiales
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

    # 2. Crear tabla de Cotizaciones
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cotizaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_nombre TEXT NOT NULL,
        proyecto_desc TEXT,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        costo_materiales REAL NOT NULL,
        margen_ganancia REAL NOT NULL,
        precio_final REAL NOT NULL,
        estado TEXT NOT NULL
    )
    ''')

    # 3. Insertar datos ficticios (Muestra de catálogo comercial para el prototipo)
    materiales_demo = [
        ('MEL-BLA-18', 'Placa Melamina Blanca 18mm (Faplac)', 'Maderas', 'Unidad', 45000.00),
        ('MEL-NOG-18', 'Placa Melamina Nogal Terracota 18mm', 'Maderas', 'Unidad', 58000.00),
        ('TAP-BLA-22', 'Tapacanto ABS Blanco 22mm', 'Terminaciones', 'ml', 450.00),
        ('BIS-CS-01', 'Bisagra Cazoleta Cierre Suave 35mm', 'Herrajes', 'Unidad', 1200.00),
        ('GUA-TEL-45', 'Guía Telescópica 45cm', 'Herrajes', 'Par', 3500.00),
        ('PER-ALU-MAN', 'Perfil Aluminio Manija tipo J', 'Perfilería', 'ml', 4200.00)
    ]

    # Usamos IGNORE para que no duplique si corrés el script dos veces
    cursor.executemany('''
    INSERT OR IGNORE INTO materiales (codigo_sku, nombre, categoria, unidad, precio_unitario)
    VALUES (?, ?, ?, ?, ?)
    ''', materiales_demo)

    # Confirmar cambios y cerrar conexión
    conexion.commit()
    conexion.close()
    
    print("Base de datos 'sistema_noziglia_mvp.db' creada y poblada con éxito.")

if __name__ == '__main__':
    inicializar_base_datos()