import streamlit as st
import pandas as pd
import urllib.parse
import io 
import random
import smtplib
from email.mime.text import MIMEText

st.set_page_config(page_title="WhatsApp Masivo Universal", page_icon="🚀")

# --- 🔒 SISTEMA DE SEGURIDAD CON EMAIL ---

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'codigo_generado' not in st.session_state:
    st.session_state.codigo_generado = None

if not st.session_state.autenticado:
    st.title("🔒 Acceso Restringido")
    st.write("Para usar este software, necesitas solicitar un código de acceso.")
    
    usuario = st.text_input("Tu Nombre o Empresa:")
    
    if st.button("📩 1. Solicitar Código a Magali"):
        if usuario:
            # Creamos el código secreto de 4 números
            codigo = str(random.randint(1000, 9999))
            st.session_state.codigo_generado = codigo
            
            try:
                # El Cartero saca sus datos de la Caja Fuerte
                remitente = st.secrets["EMAIL_SENDER"]
                password = st.secrets["EMAIL_PASSWORD"]
                destinatario = "magalisaid@hotmail.com" # AQUI TE VA A LLEGAR EL AVISO
                
                
                mensaje_email = f"Hola Magali,\n\nEl usuario '{usuario}' quiere usar tu software.\n\nEl código generado para esta sesión es: {codigo}\n\nPásale este código por WhatsApp para que pueda entrar."
                msg = MIMEText(mensaje_email)
                msg['Subject'] = f"🔑 Nuevo acceso solicitado por {usuario}"
                msg['From'] = remitente
                msg['To'] = destinatario
                
                # El Cartero envía la carta
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(remitente, password)
                server.send_message(msg)
                server.quit()
                
                st.success("✅ ¡Solicitud enviada! Magali recibirá tu código. Por favor, NO CIERRES esta ventana y espera a que te lo pase.")
            except Exception as e:
                st.error("❌ Hubo un error. Avisale a Magali que revise la configuración del correo.")
        else:
            st.warning("⚠️ Por favor, ingresa tu nombre primero.")
            
    if st.session_state.codigo_generado:
        st.write("---")
        codigo_ingresado = st.text_input("🔑 2. Ingresa el código que te pasó Magali:", type="password")
        
        if st.button("Entrar al Software"):
            if codigo_ingresado == st.session_state.codigo_generado:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("❌ Código incorrecto.")
                
    st.stop() # La página se terina aca si no tienen la llave

# --- EL SOFTWARE REAL ---

st.title("🚀 Envíos Masivos por WhatsApp")
st.write("Sube tu lista, escribe tu mensaje personalizado y envía.")

if 'datos' not in st.session_state:
    st.session_state.datos = None

if st.session_state.datos is None:
    archivo_subido = st.file_uploader("Paso 1: Sube tu archivo Excel", type=["xlsx"])
    if archivo_subido is not None:
        df = pd.read_excel(archivo_subido)
        if 'Estado' not in df.columns:
            df['Estado'] = ''
        if 'Enviar' not in df.columns:
            df['Enviar'] = 'Si'
        df['Estado'] = df['Estado'].astype(str)
        st.session_state.datos = df
        st.rerun()

if st.session_state.datos is not None:
    df = st.session_state.datos 
    
    st.write("### 📋 1. Tus Datos:")
    
    # --- NUEVO BOTÓN: POR SI SE EQUIVOCAN DE ARCHIVO ---
    if st.button("❌ Me equivoqué de archivo, quiero subir otro"):
        st.session_state.datos = None
        st.rerun()
        
    st.dataframe(df)
    
    st.write("### ✍️ 2. Escribe tu Mensaje:")
    columnas = df.columns.tolist()
    etiquetas = ", ".join([f"**{{{col}}}**" for col in columnas])
    st.info(f"💡 **Truco:** Puedes usar estas etiquetas en tu mensaje: {etiquetas}")
    
    mensaje_base = st.text_area("Escribe tu mensaje aquí:", "Hola {Nombre}, este es un mensaje de prueba.")
    
    st.write("### 🚀 3. Pendientes de envío:")
    pendientes = 0
    for index, row in df.iterrows():
        enviar = str(row.get('Enviar', '')).strip().lower()
        estado = str(row.get('Estado', '')).strip().lower()
        
        if enviar == 'si' and estado != 'enviado':
            pendientes += 1
            telefono = str(row.get('Telefono', ''))
            nombre_mostrar = str(row.get('Nombre', f'Fila {index+1}'))
            
            if not telefono.startswith('+'):
                telefono = '+' + telefono
                
            mensaje_final = mensaje_base
            for col in columnas:
                etiqueta_buscar = "{" + col + "}"
                if etiqueta_buscar in mensaje_final:
                    mensaje_final = mensaje_final.replace(etiqueta_buscar, str(row[col]))
            
            mensaje_url = urllib.parse.quote(mensaje_final)
            link = f"https://web.whatsapp.com/send?phone={telefono}&text={mensaje_url}"
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.link_button(f"💬 Abrir chat de {nombre_mostrar}", link)
            with col2:
                if st.button(f"✅ Marcar como Enviado", key=f"btn_{index}"):
                    st.session_state.datos.at[index, 'Estado'] = 'Enviado'
                    st.rerun()
                    
    if pendientes == 0:
        st.success("¡No hay mensajes pendientes!")

    st.write("---")
    st.write("### 💾 4. Finalizar:")
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        st.session_state.datos.to_excel(writer, index=False)
    st.download_button(label="📥 Descargar Excel Actualizado", data=buffer.getvalue(), file_name="lista_actualizada.xlsx", mime="application/vnd.ms-excel")

//Para que no se vea la marca de agua de streamlit
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
