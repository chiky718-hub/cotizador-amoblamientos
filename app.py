import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Cotizador B2B", layout="wide")

# --- NUEVO: CREAR LA MEMORIA (CARRITO) ---
# Si no existe el carrito, lo creamos vacío
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

def obtener_materiales():
    conexion = sqlite3.connect('sistema_noziglia_mvp.db')
    df = pd.read_sql_query("SELECT * FROM materiales", conexion)
    conexion.close()
    return df

st.title("📊 Panel de Cotización Dinámica")
st.markdown("---")

df_materiales = obtener_materiales()

st.sidebar.header("⚙️ Armar Presupuesto")
cliente = st.sidebar.text_input("Nombre del Cliente")

st.sidebar.subheader("Agregar Materiales")
opciones = df_materiales['nombre'].tolist()
material_seleccionado = st.sidebar.selectbox("Elegir material:", opciones)
cantidad = st.sidebar.number_input("Cantidad:", min_value=1, value=1)

# --- NUEVO: BOTÓN PARA AGREGAR AL CARRITO ---
if st.sidebar.button("➕ Agregar al presupuesto"):
    precio_unitario = df_materiales[df_materiales['nombre'] == material_seleccionado]['precio_unitario'].values[0]
    subtotal = precio_unitario * cantidad
    
    # Guardamos los datos del material en la memoria
    item = {
        "Material": material_seleccionado,
        "Cantidad": cantidad,
        "Precio Unit.": precio_unitario,
        "Subtotal": subtotal
    }
    st.session_state.carrito.append(item)
    st.sidebar.success(f"¡Agregado!")

# --- NUEVO: MOSTRAR EL CARRITO Y CALCULAR TOTALES ---
# Si hay cosas en el carrito, mostramos los totales
if len(st.session_state.carrito) > 0:
    st.markdown(f"### Presupuesto actual para: **{cliente if cliente else 'Sin nombre'}**")
    
    # Convertimos la memoria en una tabla visual
    df_carrito = pd.DataFrame(st.session_state.carrito)
    st.dataframe(df_carrito, use_container_width=True, hide_index=True)
    
    # Calculamos sumando toda la columna 'Subtotal'
    costo_total_material = df_carrito['Subtotal'].sum()
    margen_ganancia = costo_total_material * 0.50  # 50% de ganancia
    precio_venta = costo_total_material + margen_ganancia

    col1, col2, col3 = st.columns(3)
    col1.metric("Costo de Materiales (Suma total)", f"${costo_total_material:,.2f}")
    col2.metric("Margen de Ganancia", f"${margen_ganancia:,.2f}", "50%")
    col3.metric("Precio Final Sugerido", f"${precio_venta:,.2f}", "A cobrar")
    
    # Botón para limpiar todo y empezar de cero
    if st.button("🗑️ Vaciar presupuesto"):
        st.session_state.carrito = []
        st.rerun()
else:
    st.info("👈 Seleccioná materiales en el menú de la izquierda y hacé clic en 'Agregar al presupuesto' para empezar.")