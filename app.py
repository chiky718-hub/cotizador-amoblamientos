import streamlit as st
import sqlite3
import pandas as pd
import json
from fpdf import FPDF
import datetime

st.set_page_config(page_title="Cotizador CRM", layout="wide")

if 'carrito' not in st.session_state:
    st.session_state.carrito = []

def obtener_materiales():
    conexion = sqlite3.connect('sistema_noziglia_mvp.db')
    df = pd.read_sql_query("SELECT * FROM materiales", conexion)
    conexion.close()
    return df

# Función para guardar en SQLite
def guardar_en_bd(nombre, apellido, dni, telefono, direccion, costo_mat, margen, precio_final, carrito):
    conexion = sqlite3.connect('sistema_noziglia_mvp.db')
    cursor = conexion.cursor()
    detalles = json.dumps(carrito) # Guarda la lista de materiales como texto compacto
    cursor.execute('''
        INSERT INTO cotizaciones 
        (cliente_nombre, cliente_apellido, dni_cuit, telefono, direccion, costo_materiales, margen_ganancia, precio_final, detalles_json, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Emitido')
    ''', (nombre, apellido, dni, telefono, direccion, costo_mat, margen, precio_final, detalles))
    conexion.commit()
    conexion.close()

# Función para dibujar el PDF
def generar_pdf(nombre, apellido, dni, telefono, direccion, costo_mat, margen, precio_final, carrito):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="PRESUPUESTO OFICIAL", ln=True, align='C')
    pdf.set_font("Arial", size=11)
    fecha = datetime.datetime.now().strftime("%d/%m/%Y")
    pdf.cell(200, 10, txt=f"Fecha: {fecha}", ln=True, align='R')
    
    # Datos del Cliente
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Datos del Cliente:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(200, 8, txt=f"Nombre y Apellido: {nombre} {apellido}", ln=True)
    pdf.cell(200, 8, txt=f"DNI/CUIT: {dni}", ln=True)
    pdf.cell(200, 8, txt=f"Teléfono: {telefono}", ln=True)
    pdf.cell(200, 8, txt=f"Dirección: {direccion}", ln=True)
    pdf.ln(5)
    
    # Detalle del carrito
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Detalle de Materiales:", ln=True)
    pdf.set_font("Arial", size=11)
    for item in carrito:
        texto_item = f"- {item['Cantidad']}x {item['Material']} (P.U: ${item['Precio Unit.']:,.2f}) -> Subtotal: ${item['Subtotal']:,.2f}"
        pdf.cell(200, 8, txt=texto_item, ln=True)
    pdf.ln(5)
    
    # Totales
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Totales:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(200, 8, txt=f"Costo Base: ${costo_mat:,.2f}", ln=True)
    pdf.cell(200, 8, txt=f"Margen Aplicado: ${margen:,.2f}", ln=True)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"PRECIO FINAL: ${precio_final:,.2f}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- DISEÑO DE LA INTERFAZ ---
st.title("📊 Panel de Cotización y Gestión CRM")
st.markdown("---")

df_materiales = obtener_materiales()

# Dividimos la pantalla en dos columnas (Izquierda para cargar datos, Derecha para resultados)
col_izq, col_der = st.columns([1, 2])

with col_izq:
    st.header("👤 1. Datos del Cliente")
    c_nombre = st.text_input("Nombre*")
    c_apellido = st.text_input("Apellido")
    c_dni = st.text_input("DNI o CUIT (Opcional)")
    c_tel = st.text_input("Teléfono")
    c_dir = st.text_input("Dirección")
    
    st.markdown("---")
    st.header("⚙️ 2. Materiales")
    opciones = df_materiales['nombre'].tolist()
    material_seleccionado = st.selectbox("Elegir material:", opciones)
    cantidad = st.number_input("Cantidad:", min_value=1, value=1)

    if st.button("➕ Agregar al presupuesto"):
        precio_unitario = df_materiales[df_materiales['nombre'] == material_seleccionado]['precio_unitario'].values[0]
        subtotal = precio_unitario * cantidad
        item = {
            "Material": material_seleccionado,
            "Cantidad": cantidad,
            "Precio Unit.": precio_unitario,
            "Subtotal": subtotal
        }
        st.session_state.carrito.append(item)
        st.success("¡Agregado!")

with col_der:
    st.header("🛒 3. Resumen del Presupuesto")
    if len(st.session_state.carrito) > 0:
        df_carrito = pd.DataFrame(st.session_state.carrito)
        st.dataframe(df_carrito, use_container_width=True, hide_index=True)
        
        costo_total_material = df_carrito['Subtotal'].sum()
        margen_ganancia = costo_total_material * 0.50
        precio_venta = costo_total_material + margen_ganancia

        c1, c2, c3 = st.columns(3)
        c1.metric("Materiales", f"${costo_total_material:,.2f}")
        c2.metric("Ganancia", f"${margen_ganancia:,.2f}")
        c3.metric("Precio Final", f"${precio_venta:,.2f}")
        
        st.markdown("---")
        st.subheader("💾 Gestión de Datos")
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("💾 Guardar en Base de Datos", type="primary"):
                if c_nombre == "":
                    st.error("⚠️ El Nombre del cliente es obligatorio.")
                else:
                    guardar_en_bd(c_nombre, c_apellido, c_dni, c_tel, c_dir, costo_total_material, margen_ganancia, precio_venta, st.session_state.carrito)
                    st.success("¡Presupuesto guardado!")
        
        with col_btn2:
            pdf_bytes = generar_pdf(c_nombre, c_apellido, c_dni, c_tel, c_dir, costo_total_material, margen_ganancia, precio_venta, st.session_state.carrito)
            st.download_button(
                label="📄 Descargar en PDF",
                data=pdf_bytes,
                file_name=f"Presupuesto_{c_nombre}_{c_apellido}.pdf",
                mime="application/pdf"
            )
        
        with col_btn3:
            if st.button("🗑️ Vaciar todo"):
                st.session_state.carrito = []
                st.rerun()
    else:
        st.info("👈 Cargá los datos del cliente y agregá materiales desde la columna izquierda para ver el resumen.")