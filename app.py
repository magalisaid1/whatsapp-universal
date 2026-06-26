import streamlit as st
import pandas as pd
import urllib.parse
import io 
import random
import smtplib
from email.mime.text import MIMEText

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="WhatsApp Universal", page_icon="✈️", layout="wide")

# 2. INYECCIÓN DE CSS
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background-color: #F4F5F7 !important;
    }

    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, label {
        color: #1E293B !important;
    }

    div[data-baseweb="input"] > div, 
    div[data-baseweb="textarea"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }
    
    div[data-baseweb="input"] input, 
    div[data-baseweb="textarea"] textarea {
        color: #1E293B !important;
        background-color: transparent !important;
        caret-color: #1E293B !important; 
    }

    div[data-testid="stButton"] > button {
        background-color: #25D366 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        width: 100%;
        transition: all 0.3s ease;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #128C7E !important;
        box-shadow: 0 4px 6px rgba(37, 211, 102, 0.2);
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
        border: none !important;
    }
    
    h1, h2, h3 {
        color: #1E293B;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔒 PANTALLA DE LOGIN ---

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'codigo_generado' not in st.session_state:
    st.session_state.codigo_generado = None

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.write("")
        st.write("")
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center; color: #25D366;'>✈️</h1>", unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center;'>WhatsApp Universal</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray;'>Envíos Masivos WhatsApp</p>", unsafe_allow_html=True)
            st.write("---")
            
            usuario = st.text_input("Tu Nombre o Empresa", placeholder="Ej. Magui")
            
            if st.button("📩 Solicitar Código de Acceso"):
                if usuario:
                    codigo = str(random.randint(1000, 9999))
                    st.session_state.codigo_generado = codigo
                    try:
                        remitente = st.secrets["EMAIL_SENDER"]
                        password = st.secrets["EMAIL_PASSWORD"]
                        destinatario = "magalisaid@hotmail.com" 
                        
                        mensaje_email = f"Hola Magali,\n\nEl usuario '{usuario}' quiere usar tu software.\n\nCódigo: {codigo}"
                        msg = MIMEText(mensaje_email)
                        msg['Subject'] = f"🔑 Acceso: {usuario}"
                        msg['From'] = remitente
                        msg['To'] = destinatario
                        
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(remitente, password)
                        server.send_message(msg)
                        server.quit()
                        st.success("✅ Código enviado a Magali.")
                    except Exception as e:
                        st.error("Error de correo. Código de emergencia: " + codigo)
                else:
                    st.warning("Ingresa tu nombre.")
            
            st.write("")
            codigo_ingresado = st.text_input("🔑 Código de Acceso", type="password", placeholder="Ingresa tu código")
            
            if st.button("Entrar al Software"):
                if codigo_ingresado == st.session_state.codigo_generado or codigo_ingresado == "MAGUI2024":
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("❌ Código incorrecto.")
            
            st.markdown("<p style='text-align: center; color: #CBD5E1; font-size: 12px; margin-top: 20px;'>Sistema de uso exclusivo para empresas autorizadas</p>", unsafe_allow_html=True)
    st.stop()

# --- 🚀 PANTALLA PRINCIPAL (DASHBOARD) ---

col_logo, col_logout = st.columns([4, 1])
with col_logo:
    st.markdown("### ✈️ WhatsApp Universal <span style='color:gray; font-size:16px; font-weight:normal;'>| Panel de Envíos Masivos</span>", unsafe_allow_html=True)
with col_logout:
    if st.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.datos = None
        st.rerun()

st.write("")

if 'datos' not in st.session_state:
    st.session_state.datos = None

# LA SOLUCIÓN: Inicializamos la memoria única de la caja de texto
if 'txt_area' not in st.session_state:
    st.session_state.txt_area = ""

if st.session_state.datos is None:
    with st.container(border=True):
        st.markdown("#### 📄 Cargar Datos desde Excel")
        archivo_subido = st.file_uploader("Arrastra y suelta tu archivo Excel", type=["xlsx", "xls"])
        if archivo_subido is not None:
            df = pd.read_excel(archivo_subido)
            if 'Estado' not in df.columns:
                df['Estado'] = 'Pendiente'
            if 'Enviar' not in df.columns:
                df['Enviar'] = 'Si'
            df['Estado'] = df['Estado'].astype(str)
            st.session_state.datos = df
            st.rerun()
else:
    df = st.session_state.datos
    
    total_contactos = len(df)
    enviados = len(df[df['Estado'].str.lower() == 'enviado'])
    pendientes = total_contactos - enviados

    m1, m2, m3 = st.columns(3)
    with m1:
        with st.container(border=True):
            st.metric("Total Contactos 👥", total_contactos)
    with m2:
        with st.container(border=True):
            st.metric("Pendientes 💬", pendientes)
    with m3:
        with st.container(border=True):
            st.metric("Enviados ✅", enviados)

    with st.container(border=True):
        st.markdown("#### 📊 Vista Previa de Datos")
        st.session_state.datos = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    with st.container(border=True):
        st.markdown("#### ✍️ Creador de Mensajes")
        st.markdown("<p style='color:gray; font-size:14px;'>Haz clic en las variables para insertarlas en tu mensaje</p>", unsafe_allow_html=True)
        
        columnas = df.columns.tolist()
        
        cols_vars = st.columns(len(columnas))
        for i, col in enumerate(columnas):
            if cols_vars[i].button(f"{{{col}}}", key=f"var_{col}"):
                # Agregamos el texto directamente a la memoria única
                st.session_state.txt_area += f" {{{col}}}"
                st.rerun()
        
        # La caja de texto ahora solo usa su 'key' para recordar todo
        mensaje_base = st.text_area("Escribe tu mensaje aquí...", height=100, key="txt_area")
        
        if len(df) > 0:
            primer_fila = df.iloc[0]
            mensaje_preview = mensaje_base
            for col in columnas:
                etiqueta = "{" + col + "}"
                if etiqueta in mensaje_preview:
                    mensaje_preview = mensaje_preview.replace(etiqueta, str(primer_fila[col]))
            
            st.markdown("<p style='color:gray; font-size:12px; margin-bottom:0;'>VISTA PREVIA (con primer contacto):</p>", unsafe_allow_html=True)
            st.info(mensaje_preview)

    with st.container(border=True):
        st.markdown("#### 🚀 Panel de Envíos - Contactos Pendientes")
        st.markdown("<p style='color:gray; font-size:14px;'>Envía mensajes uno por uno de forma controlada</p>", unsafe_allow_html=True)
        
        hay_pendientes = False
        for index, row in df.iterrows():
            enviar = str(row.get('Enviar', '')).strip().lower()
            estado = str(row.get('Estado', '')).strip().lower()
            
            if enviar == 'si' and estado != 'enviado':
                hay_pendientes = True
                telefono = str(row.get('Telefono', ''))
                nombre_mostrar = str(row.get('Nombre', f'Fila {index+1}'))
                
                if not telefono.startswith('+'):
                    telefono = '+' + telefono
                    
                mensaje_final = mensaje_base
                for col in columnas:
                    etiqueta = "{" + col + "}"
                    if etiqueta in mensaje_final:
                        mensaje_final = mensaje_final.replace(etiqueta, str(row[col]))
                
                mensaje_url = urllib.parse.quote(mensaje_final)
                link = f"https://web.whatsapp.com/send?phone={telefono}&text={mensaje_url}"
                
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 1.5, 1.5])
                    with c1:
                        st.markdown(f"<h5 style='margin-top: 10px;'>📇 {nombre_mostrar} <span style='color:gray; font-size:14px;'>({telefono})</span></h5>", unsafe_allow_html=True)
                    with c2:
                        st.link_button("💬 Abrir Chat", link, use_container_width=True)
                    with c3:
                        if st.button("✅ Marcar Enviado", key=f"btn_{index}", use_container_width=True):
                            st.session_state.datos.at[index, 'Estado'] = 'Enviado'
                            st.rerun()
                            
        if not hay_pendientes:
            st.success("🎉 ¡Excelente trabajo! No hay mensajes pendientes por enviar.")

    st.write("")
    col_down1, col_down2, col_down3 = st.columns([1, 2, 1])
    with col_down2:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            st.session_state.datos.to_excel(writer, index=False)
        st.download_button(
            label="📥 Descargar Excel Actualizado con Estados",
            data=buffer.getvalue(),
            file_name="envios_actualizados.xlsx",
            mime="application/vnd.ms-excel",
            use_container_width=True
        )
