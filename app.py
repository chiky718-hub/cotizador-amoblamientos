import streamlit as st
import sqlite3
import pandas as pd
import json
from fpdf import FPDF
import datetime

# --- CONFIGURACIÓN Y CSS ---
st.set_page_config(page_title="Sistema de Gestión Corporativa", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #0b0f19; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 95%; }
    
    div[data-testid="column"] {
        background: linear-gradient(145deg, rgba(17, 24, 39, 0.7), rgba(15, 19, 31, 0.7));
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        color: #64748b; border-bottom: 1px solid transparent; font-weight: 300; letter-spacing: 1.5px; text-transform: uppercase; font-size: 0.8rem;
    }
    .stTabs [aria-selected="true"] { color: #38bdf8; border-bottom: 1px solid #38bdf8; text-shadow: 0 0 8px rgba(56, 189, 248, 0.3); }
    
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea {
        background-color: #0f172a !important; border: 1px solid #1e293b !important; color: #f1f5f9 !important; border-radius: 4px; font-weight: 300; font-size: 0.9rem;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus { border-color: #38bdf8 !important; box-shadow: 0 0 10px rgba(56, 189, 248, 0.15) !important; }
    
    div[data-testid="stButton"] button {
        background-color: transparent; border: 1px solid #38bdf8; color: #38bdf8; border-radius: 4px; font-weight: 300; letter-spacing: 1px; text-transform: uppercase; font-size: 0.75rem; transition: all 0.3s ease;
    }
    div[data-testid="stButton"] button:hover { background-color: rgba(56, 189, 248, 0.05); box-shadow: 0 0 15px rgba(56, 189, 248, 0.2); border-color: #7dd3fc; color: #ffffff; }
    
    h1, h2, h3, h4, h5 { color: #f8fafc !important; font-weight: 200 !important; letter-spacing: 1px; }
    div[data-testid="stMetricValue"] { color: #f1f5f9; font-weight: 200; font-size: 1.8rem; }
    div[data-testid="stMetricLabel"] { color: #94a3b8; font-weight: 300; text-transform: uppercase; letter-spacing: 1px; font-size: 0.7rem; }
    </style>
""", unsafe_allow_html=True)

if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# --- LÓGICA DE BASE DE DATOS ---
def obtener_materiales():
    conexion = sqlite3.connect('sistema_noziglia_mvp.db')
    df = pd.read_sql_query("SELECT * FROM materiales", conexion)
    conexion.close()
    return df

def obtener_historial_presupuestos():
    conexion = sqlite3.connect('sistema_noziglia_mvp.db')
    df = pd.read_sql_query("SELECT id, razon_social, nombre_proyecto, fecha_creacion, precio_final, estado FROM cotizaciones ORDER BY id DESC", conexion)
    conexion.close()
    return df

def obtener_detalle_presupuesto(id_op):
    conexion = sqlite3.connect('sistema_noziglia_mvp.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM cotizaciones WHERE id = ?", (id_op,))
    fila = cursor.fetchone()
    conexion.close()
    return fila

def guardar_en_bd(razon, fantasia, cuit, iva, email, tel, dir, proyecto, c_mat, c_mo, c_log, margen, p_final, carrito):
    conexion = sqlite3.connect('sistema_noziglia_mvp.db')
    cursor = conexion.cursor()
    detalles = json.dumps(carrito)
    cursor.execute('''
        INSERT INTO cotizaciones 
        (razon_social, nombre_fantasia, cuit, condicion_iva, email, telefono, direccion, nombre_proyecto, costo_materiales, costo_mano_obra, costo_logistica, margen_ganancia, precio_final, detalles_json, estado, notas_internas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Borrador Emitido', '')
    ''', (razon, fantasia, cuit, iva, email, tel, dir, proyecto, c_mat, c_mo, c_log, margen, p_final, detalles))
    conexion.commit()
    conexion.close()

def actualizar_crm(id_op, nuevo_estado, nuevas_notas):
    conexion = sqlite3.connect('sistema_noziglia_mvp.db')
    cursor = conexion.cursor()
    cursor.execute("UPDATE cotizaciones SET estado = ?, notas_internas = ? WHERE id = ?", (nuevo_estado, nuevas_notas, id_op))
    conexion.commit()
    conexion.close()

# --- GENERADOR DE PDF CORPORATIVO (DESPIECE OCULTO) ---
def generar_pdf(razon, fantasia, cuit, iva, email, tel, dir, proyecto, c_mat, c_mo, c_log, margen, p_final):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="PRESUPUESTO CORPORATIVO B2B", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Fecha de Emision: {datetime.datetime.now().strftime('%d/%m/%Y')}", ln=True, align='R')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(200, 8, txt="DATOS DEL CLIENTE:", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 6, txt=f"Razon Social: {razon} ({fantasia})", ln=True)
    pdf.cell(200, 6, txt=f"CUIT: {cuit} | Condicion IVA: {iva}", ln=True)
    pdf.cell(200, 6, txt=f"Contacto: {email} | {tel}", ln=True)
    pdf.cell(200, 6, txt=f"Domicilio Comercial: {dir}", ln=True)
    pdf.ln(5)
    
    # Ingeniería protegida: Solo mostramos la descripción del módulo
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(200, 8, txt="DESCRIPCION DE OBRA / EQUIPAMIENTO:", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 6, txt=f"- Modulo a fabricar: {proyecto}", ln=True)
    pdf.cell(200, 6, txt="- Servicio integral: Incluye provisión de materiales, herrajes, armado e instalacion.", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(200, 8, txt="RESUMEN DE INVERSION:", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 6, txt="Costo Estructural y Logistica: Cotizado", ln=True)
    pdf.cell(200, 6, txt="Mano de Obra y Ejecucion: Cotizado", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"PRECIO TOTAL DE INVERSION: ${p_final:,.2f}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ ---
st.markdown("## SISTEMA ERP - NOZIGLIA AMOBLAMIENTOS")
st.markdown("---")
tab1, tab2 = st.tabs(["NUEVA COTIZACIÓN", "CRM Y SEGUIMIENTO"])

with tab1:
    df_materiales = obtener_materiales()
    col_izq, col_der = st.columns([1.2, 2.3], gap="large")

    with col_izq:
        st.markdown("#### PERFIL COMERCIAL (B2B)")
        c_razon = st.text_input("Razón Social*")
        c_fantasia = st.text_input("Nombre de Fantasía")
        
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            c_cuit = st.text_input("CUIT")
        with c_col2:
            c_iva = st.selectbox("Condición IVA", ["Responsable Inscripto", "Monotributo", "Exento", "Consumidor Final"])
            
        c_email = st.text_input("Correo Electrónico Corporativo")
        c_tel = st.text_input("Teléfono de Contacto")
        c_dir = st.text_input("Domicilio de Obra / Instalación")
        c_proyecto = st.text_input("Nombre del Proyecto / Módulo (Ej: Recepción Clínica 3 Metros)*")
        
        st.markdown("<br>#### CATÁLOGO TÉCNICO (DESPIECE INTERNO)", unsafe_allow_html=True)
        opciones = df_materiales['nombre'].tolist()
        material_seleccionado = st.selectbox("Seleccionar Ítem:", opciones)
        cantidad = st.number_input("Cantidad:", min_value=1, value=1)

        if st.button("AGREGAR AL MÓDULO", use_container_width=True):
            precio_unitario = df_materiales[df_materiales['nombre'] == material_seleccionado]['precio_unitario'].values[0]
            st.session_state.carrito.append({
                "Material": material_seleccionado, "Cantidad": cantidad, 
                "Precio Unit.": precio_unitario, "Subtotal": precio_unitario * cantidad
            })
            st.rerun()

    with col_der:
        st.markdown("#### INGENIERÍA DE COSTOS")
        if len(st.session_state.carrito) > 0:
            df_carrito = pd.DataFrame(st.session_state.carrito)
            st.dataframe(df_carrito, use_container_width=True, hide_index=True)
            
            st.markdown("##### Variables de Producción y Logística")
            var_col1, var_col2, var_col3 = st.columns(3)
            with var_col1:
                margen_scrap = st.number_input("% Desperdicio (Scrap)", min_value=0, max_value=30, value=15)
            with var_col2:
                horas_mo = st.number_input("Horas Producción", min_value=0, value=10)
                valor_hora = st.number_input("Valor Hora ($)", min_value=0, value=5000)
            with var_col3:
                costo_flete = st.number_input("Flete / Viáticos ($)", min_value=0, value=25000)

            costo_materiales_neto = df_carrito['Subtotal'].sum()
            costo_materiales_real = costo_materiales_neto * (1 + (margen_scrap / 100))
            costo_mano_obra = horas_mo * valor_hora
            costo_total_directo = costo_materiales_real + costo_mano_obra + costo_flete
            
            margen_comercial = costo_total_directo * 0.50 
            precio_venta = costo_total_directo + margen_comercial

            st.markdown("---")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("MAT. + SCRAP", f"${costo_materiales_real:,.0f}")
            c2.metric("MANO DE OBRA", f"${costo_mano_obra:,.0f}")
            c3.metric("MARGEN (50%)", f"${margen_comercial:,.0f}")
            c4.metric("PRECIO FINAL", f"${precio_venta:,.0f}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            col_b1, col_b2, col_b3 = st.columns(3)
            
            with col_b1:
                if st.button("GUARDAR TRANSACCIÓN", type="primary", use_container_width=True):
                    if c_razon == "" or c_proyecto == "":
                        st.error("Razón Social y Nombre del Proyecto son obligatorios.")
                    else:
                        guardar_en_bd(c_razon, c_fantasia, c_cuit, c_iva, c_email, c_tel, c_dir, c_proyecto, costo_materiales_real, costo_mano_obra, costo_flete, margen_comercial, precio_venta, st.session_state.carrito)
                        st.success("Operación registrada en CRM.")
            
            with col_b2:
                pdf_bytes = generar_pdf(c_razon, c_fantasia, c_cuit, c_iva, c_email, c_tel, c_dir, c_proyecto, costo_materiales_real, costo_mano_obra, costo_flete, margen_comercial, precio_venta)
                st.download_button("EMITIR PDF CORPORATIVO", data=pdf_bytes, file_name=f"Presupuesto_{c_proyecto}.pdf", mime="application/pdf", use_container_width=True)
            
            with col_b3:
                if st.button("PURGAR TABLERO", use_container_width=True):
                    st.session_state.carrito = []
                    st.rerun()
        else:
            empty_html = """
            <div style="text-align: center; padding: 5rem 1rem; border: 1px dashed #1e293b; border-radius: 8px; background: rgba(15, 23, 42, 0.4); margin-top: 1rem;">
                <h2 style="color: #334155; margin-bottom: 0.5rem; font-weight: 200; font-size: 3rem;">◬</h2>
                <p style="color: #64748b; font-weight: 300; letter-spacing: 2px; font-size: 0.85rem; text-transform: uppercase;">Motor de Costos Inactivo</p>
            </div>
            """
            st.markdown(empty_html, unsafe_allow_html=True)

with tab2:
    st.markdown("#### PIPELINE DE VENTAS Y SEGUIMIENTO")
    st.markdown("<p style='color: #64748b; font-size: 0.85rem;'>Seleccione una fila en la tabla para revisar y gestionar el proyecto.</p>", unsafe_allow_html=True)
    
    try:
        df_historial = obtener_historial_presupuestos()
        if not df_historial.empty:
            df_historial.columns = ['Nº Op', 'Razón Social', 'Proyecto', 'Fecha Emisión', 'Monto Total ($)', 'Estado CRM']
            
            seleccion = st.dataframe(
                df_historial, 
                use_container_width=True, 
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            filas_seleccionadas = seleccion.selection.rows
            if filas_seleccionadas:
                indice_fila = filas_seleccionadas[0]
                id_operacion = int(df_historial.iloc[indice_fila]['Nº Op'])
                
                detalle = obtener_detalle_presupuesto(id_operacion)
                if detalle:
                    # Desempaquetado exacto de las 18 columnas de la base final
                    d_id, d_razon, d_fan, d_cuit, d_iva, d_email, d_tel, d_dir, d_proyecto, d_fecha, d_cmat, d_cmo, d_clog, d_marg, d_pfinal, d_json, d_estado, d_notas = detalle
                    materiales_guardados = json.loads(d_json)
                    
                    st.markdown("---")
                    st.markdown(f"#### ⚙️ GESTIÓN DE PROYECTO: {d_proyecto} (OP #{d_id})")
                    
                    col_vp1, col_vp2, col_vp3 = st.columns([1, 1.5, 1])
                    
                    with col_vp1:
                        st.markdown("**Datos del Cliente:**")
                        st.markdown(f"🏢 {d_razon}")
                        st.markdown(f"📞 {d_tel}")
                        st.markdown(f"✉️ {d_email}")
                        st.markdown(f"**Precio Final:** ${d_pfinal:,.2f}")
                        
                        pdf_bytes_historial = generar_pdf(d_razon, d_fan, d_cuit, d_iva, d_email, d_tel, d_dir, d_proyecto, d_cmat, d_cmo, d_clog, d_marg, d_pfinal)
                        st.download_button("📄 REIMPRIMIR PDF", data=pdf_bytes_historial, file_name=f"Presupuesto_{d_proyecto}.pdf", mime="application/pdf", use_container_width=True)

                    with col_vp2:
                        st.markdown("**Auditoría Interna de Costos:**")
                        df_mat_guardados = pd.DataFrame(materiales_guardados)
                        st.dataframe(df_mat_guardados[['Material', 'Cantidad', 'Subtotal']], use_container_width=True, hide_index=True)
                        
                    with col_vp3:
                        st.markdown("**Actualización CRM:**")
                        lista_estados = ["Borrador Emitido", "Enviado al Cliente", "Aprobado (Seña Ingresada)", "En Producción", "Instalado y Saldado"]
                        
                        estado_actual = d_estado if d_estado in lista_estados else "Borrador Emitido"
                        nuevo_estado = st.selectbox("Estado del Pipeline", lista_estados, index=lista_estados.index(estado_actual))
                        
                        nuevas_notas = st.text_area("Notas Internas", value=d_notas if d_notas else "", height=100)
                        
                        if st.button("💾 GUARDAR CAMBIOS CRM", use_container_width=True):
                            actualizar_crm(d_id, nuevo_estado, nuevas_notas)
                            st.rerun()

        else:
            st.info("Directorio vacío. No hay transacciones registradas.")
    except Exception as e:
        st.error(f"Error de conexión con la base de datos: {e}")