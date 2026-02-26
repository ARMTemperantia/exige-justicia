import streamlit as st
import pandas as pd
import urllib.parse
import re

# --- 1. CONFIGURACIÓN E INICIO ---
st.set_page_config(page_title="Exige Justicia", page_icon="⚖️", layout="centered")

# --- MODO FANTASMA NIVEL 4: DESTRUCCIÓN DE ENLACES EXTERNOS ---
st.markdown("""
    <style>
    /* 1. Aniquilar el encabezado completo (Avatar, GitHub y Menú) */
    header {visibility: hidden !important; display: none !important;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    
    /* 2. Aniquilar botón de Deploy */
    .stAppDeployButton {display: none !important;}
    
    /* 3. Aniquilar el footer */
    footer {display: none !important;}
    [data-testid="stFooter"] {display: none !important;}
    
    /* 4. MISIL DIRECTO A LOS ENLACES */
    a[href*="github.com/armtemperantia"] {display: none !important; opacity: 0 !important; pointer-events: none !important;}
    a[href*="streamlit.io"] {display: none !important; opacity: 0 !important; pointer-events: none !important;}
    
    /* 5. Cazar la burbuja flotante */
    div[title*="View source"] {display: none !important;}
    div[title*="Hosted on"] {display: none !important;}
    [class*="viewerBadge"] {display: none !important;}
    </style>
    """, unsafe_allow_html=True)
# --------------------------------------------------------------

# --- 2. DICCIONARIO DE CÓDIGOS POSTALES ---
def obtener_estado_por_cp(cp):
    prefijo = cp[:2]
    mapa_estados = {
        '01': 'Ciudad de México', '02': 'Ciudad de México', '03': 'Ciudad de México', '04': 'Ciudad de México',
        '05': 'Ciudad de México', '06': 'Ciudad de México', '07': 'Ciudad de México', '08': 'Ciudad de México',
        '09': 'Ciudad de México', '10': 'Ciudad de México', '11': 'Ciudad de México', '12': 'Ciudad de México',
        '13': 'Ciudad de México', '14': 'Ciudad de México', '15': 'Ciudad de México', '16': 'Ciudad de México',
        '20': 'Aguascalientes', '21': 'Baja California', '22': 'Baja California', '23': 'Baja California Sur',
        '24': 'Campeche', '25': 'Coahuila', '26': 'Coahuila', '27': 'Coahuila', '28': 'Colima',
        '29': 'Chiapas', '30': 'Chiapas', '31': 'Chihuahua', '32': 'Chihuahua', '33': 'Chihuahua',
        '34': 'Durango', '35': 'Durango', '36': 'Guanajuato', '37': 'Guanajuato', '38': 'Guanajuato',
        '39': 'Guerrero', '40': 'Guerrero', '41': 'Guerrero', '42': 'Hidalgo', '43': 'Hidalgo',
        '44': 'Jalisco', '45': 'Jalisco', '46': 'Jalisco', '47': 'Jalisco', '48': 'Jalisco', '49': 'Jalisco',
        '50': 'Estado de México', '51': 'Estado de México', '52': 'Estado de México', '53': 'Estado de México',
        '54': 'Estado de México', '55': 'Estado de México', '56': 'Estado de México', '57': 'Estado de México',
        '58': 'Michoacán', '59': 'Michoacán', '60': 'Michoacán', '61': 'Michoacán', '62': 'Morelos',
        '63': 'Nayarit', '64': 'Nuevo León', '65': 'Nuevo León', '66': 'Nuevo León', '67': 'Nuevo León',
        '68': 'Oaxaca', '69': 'Oaxaca', '70': 'Oaxaca', '71': 'Oaxaca', '72': 'Puebla', '73': 'Puebla',
        '74': 'Puebla', '75': 'Puebla', '76': 'Querétaro', '77': 'Quintana Roo', '78': 'San Luis Potosí',
        '79': 'San Luis Potosí', '80': 'Sinaloa', '81': 'Sinaloa', '82': 'Sinaloa', '83': 'Sonora',
        '84': 'Sonora', '85': 'Sonora', '86': 'Tabasco', '87': 'Tamaulipas', '88': 'Tamaulipas', '89': 'Tamaulipas',
        '90': 'Tlaxcala', '91': 'Veracruz', '92': 'Veracruz', '93': 'Veracruz', '94': 'Veracruz',
        '95': 'Veracruz', '96': 'Veracruz', '97': 'Yucatán', '98': 'Zacatecas', '99': 'Zacatecas'
    }
    return mapa_estados.get(prefijo, None)

# --- 3. MOTOR DE PROTOCOLO Y GÉNERO ---
def formatear_y_obtener_saludo(nombre_crudo, cargo="Senador"):
    nombre_str = str(nombre_crudo).strip()
    if ',' in nombre_str:
        partes = nombre_str.split(',', 1)
        nombre_natural = f"{partes[1].strip()} {partes[0].strip()}".title()
        nombres_reales = partes[1].strip().lower()
    else:
        nombre_natural = nombre_str.title()
        nombres_reales = nombre_str.lower()
        
    palabras = nombres_reales.split()
    primer_nombre = palabras[0] if palabras else ""
    ultimo_nombre = palabras[-1] if palabras else ""
    
    femeninos_fuertes = {
        'carmen', 'rosario', 'guadalupe', 'beatriz', 'dolores', 'consuelo', 'luz', 'paz', 'irene', 'ivonne', 'berenice', 'dulce', 'eunice', 'nayeli', 'xóchitl', 'xochitl', 'citlalli', 'ruth', 'edith', 'margoth', 'simey', 'mayuli', 'lilly', 'sasil', 'marisol', 'raquel', 'isabel', 'leonor', 'ester', 'esther', 'noemí', 'noemi', 'abigail', 'miriam', 'evelyn', 'karem', 'karen', 'sharon', 'belén', 'belen', 'yazmín', 'yazmin', 'jazmín', 'jazmin', 'aylín', 'aylin', 'aidé', 'aide', 'itzel', 'maribel', 'anabell', 'lizeth', 'ivette', 'mely', 'janet', 'janeth', 'rocío', 'rocio', 'socorro', 'concepción', 'asunción', 'pilar', 'soledad', 'inés', 'ines', 'sarahí', 'sarahi', 'areli', 'arelí', 'rubí', 'rubi', 'vianey', 'araceli', 'aracely', 'zaria', 'juana'
    }
    apellidos_con_a = {
        'garcía', 'garcia', 'mora', 'lara', 'nava', 'peña', 'pena', 'ochoa', 'ayala', 'pineda', 'estrada', 'rivera', 'carmona', 'esparza', 'loera', 'mendoza', 'mejía', 'mejia', 'padilla', 'castañeda', 'castaneda', 'quintana', 'arriaga', 'correa', 'guevara', 'tapia', 'valdivia', 'fonseca', 'munguía', 'munguia', 'baeza', 'balderrama', 'cabrera', 'zepeda', 'cepeda', 'figueroa', 'gamboa', 'herrera', 'medina', 'miranda', 'molina', 'nájera', 'najera', 'ojeda', 'pantoja', 'quiroga', 'rocha', 'segovia', 'sosa', 'talavera', 'urquiza', 'varela', 'vega', 'villanueva', 'zavala', 'zaragoza', 'zurita', 'saldaña', 'saldana', 'acosta', 'barrera', 'escalera', 'espinosa', 'espinoza', 'garza', 'guerra', 'hinojosa', 'macías', 'macias', 'mancera', 'ortega', 'ruvalcaba', 'silva', 'téllez', 'tellez'
    }
    
    es_mujer = False
    if any(fem in palabras for fem in femeninos_fuertes):
        es_mujer = True
    elif primer_nombre.endswith('a') and primer_nombre not in apellidos_con_a:
        es_mujer = True
    elif ultimo_nombre.endswith('a') and ultimo_nombre not in apellidos_con_a:
        es_mujer = True
        
    if 'josé' in palabras or 'jose' in palabras: es_mujer = False
    if 'jesús' in palabras or 'jesus' in palabras:
        if 'lucía' not in palabras and 'lucia' not in palabras: es_mujer = False
            
    if cargo == "Senador":
        saludo = "Estimada Senadora" if es_mujer else "Estimado Senador"
        etiqueta = "Senadora" if es_mujer else "Senador"
    else:
        saludo = "Estimada Diputada" if es_mujer else "Estimado Diputado"
        etiqueta = "Diputada" if es_mujer else "Diputado"
        
    return nombre_natural, saludo, etiqueta

# --- 4. GENERADOR DE BOTONES WEBMAIL ---
def generar_botones_webmail(destinatarios, asunto, cuerpo):
    su = urllib.parse.quote(asunto)
    bd = urllib.parse.quote(cuerpo)
    
    gmail = f"https://mail.google.com/mail/?view=cm&fs=1&to={destinatarios}&su={su}&body={bd}"
    outlook_web = f"https://outlook.live.com/mail/0/deeplink/compose?to={destinatarios}&subject={su}&body={bd}"
    yahoo = f"https://compose.mail.yahoo.com/?to={destinatarios}&subject={su}&body={bd}"
    default = f"mailto:{destinatarios}?subject={su}&body={bd}"
    
    html_botones = f"""
    <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; margin-bottom: 20px;">
        <a href="{gmail}" target="_blank" style="text-decoration: none;">
            <button style="background-color: #D44638; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold;">📧 Gmail</button>
        </a>
        <a href="{outlook_web}" target="_blank" style="text-decoration: none;">
            <button style="background-color: #0078D4; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold;">🌐 Outlook</button>
        </a>
        <a href="{yahoo}" target="_blank" style="text-decoration: none;">
            <button style="background-color: #6001D2; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold;">📧 Yahoo</button>
        </a>
        <a href="{default}" style="text-decoration: none;">
            <button style="background-color: #333333; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold;">📱 App de Correo</button>
        </a>
    </div>
    """
    return html_botones

# --- 5. INTERFAZ GRÁFICA PRINCIPAL ---
st.title("✉️ Exige Justicia: Contacta a tus Representantes")
st.markdown("Pide a los Legisladores de tu estado que voten en contra de la Ley de Violencia Vicaria y el Derecho Penal de Autor.")

st.warning("📱 **Aviso para celulares:** Si abriste este enlace desde Facebook, WhatsApp o Twitter, es posible que los botones de correo no funcionen por sus bloqueos de seguridad. Si eso pasa, toca los **3 puntitos (arriba a la derecha) y elige 'Abrir en el navegador (Chrome/Safari)'**, o usa las cajitas grises de cada legislador para copiar el correo y el teléfono manualmente.")
st.markdown("---")

@st.cache_data
def cargar_bases():
    try:
        df_sen = pd.read_csv("senadores_completo.csv")
    except:
        df_sen = pd.DataFrame()
    try:
        df_dip = pd.read_csv("diputados_completo.csv")
    except:
        df_dip = pd.DataFrame()
    return df_sen, df_dip

df_senadores, df_diputados = cargar_bases()

REGEX_NOMBRE = r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]+$"
REGEX_CP = r"^\d{5}$"

# --- 6. FORMULARIO CIUDADANO ---
st.markdown("### 1. Completa tus datos")
st.info("💡 **Instrucciones:** Tu nombre debe contener únicamente letras y espacios. El Código Postal debe ser exactamente de 5 números.")
st.caption("🔒 **Aviso de Privacidad y Seguridad:** Los datos ingresados en este formulario **NO se guardan, NO se rastrean y NO se almacenan** en ninguna base de datos. Únicamente se utilizan de forma temporal en tu propio dispositivo para localizar a tus legisladores y pre-llenar la firma de tu correo (la cual podrás editar libremente en tu aplicación de correo antes de enviarlo).")

with st.form("formulario_contacto"):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Tu Nombre Completo", placeholder="Ej. Juan Pérez García")
    with col2:
        cp = st.text_input("Tu Código Postal", max_chars=5, placeholder="Ej. 54000")
        
    submit_button = st.form_submit_button("Buscar a mis Representantes")

# --- 7. LÓGICA DE PROCESAMIENTO ---
if submit_button:
    nombre = nombre.strip()
    cp = cp.strip()
    errores = False
    
    if not nombre:
        st.error("❌ El campo de Nombre no puede estar vacío.")
        errores = True
    elif not re.fullmatch(REGEX_NOMBRE, nombre):
        st.error("❌ **Error en el Nombre:** Solo se permiten letras, espacios, acentos, diéresis y la letra ñ.")
        errores = True
        
    if not cp:
        st.error("❌ El campo de Código Postal no puede estar vacío.")
        errores = True
    elif not re.fullmatch(REGEX_CP, cp):
        st.error("❌ **Error en el Código Postal:** Debe contener exactamente 5 números.")
        errores = True
        
    if not errores:
        estado_detectado = obtener_estado_por_cp(cp)
        
        if not estado_detectado:
            st.warning("⚠️ No pudimos identificar el estado con ese código postal. Verifica que sea válido.")
        else:
            st.success(f"📍 Detectamos que votas en: **{estado_detectado}**")
            
            # ==========================================
            # SECCIÓN 1: CÁMARA DE SENADORES
            # ==========================================
            st.markdown("---")
            st.header("🏛️ CÁMARA DE SENADORES")
            
            if not df_senadores.empty and 'Estado' in df_senadores.columns:

                # --- FIX: Incluir senadores de Lista Nacional ---
                condicion_estado = df_senadores['Estado'].str.contains(estado_detectado, case=False, na=False)
                condicion_lista_nacional = df_senadores['Estado'].str.contains('Lista Nacional', case=False, na=False)
                senadores_filtrados = df_senadores[condicion_estado | condicion_lista_nacional]
                # ------------------------------------------------

                if senadores_filtrados.empty:
                    st.info(f"No hay senadores registrados para {estado_detectado}.")
                else:
                    # Conteo separado para el subheader
                    sen_estado = senadores_filtrados[~senadores_filtrados['Estado'].str.contains('Lista Nacional', case=False, na=False)]
                    sen_nacionales = senadores_filtrados[senadores_filtrados['Estado'].str.contains('Lista Nacional', case=False, na=False)]

                    correos_senadores = [str(row.get('senator_details_email', '')).strip() for _, row in senadores_filtrados.iterrows() if str(row.get('senator_details_email', '')).strip() and str(row.get('senator_details_email', '')).lower() != 'nan']
                    cadena_correos_sen = ",".join(correos_senadores)
                    
                    if correos_senadores:
                        st.subheader(f"🔥 Envío Masivo ({len(sen_estado)} de {estado_detectado} + {len(sen_nacionales)} Lista Nacional)")
                        asunto_masivo_sen = "Petición ciudadana urgente: Rechazo a la Ley de Violencia Vicaria"
                        cuerpo_masivo_sen = f"Estimados Senadores y Senadoras por el estado de {estado_detectado},\n\nEspero que este mensaje les encuentre muy bien. Me dirijo a ustedes en mi calidad de ciudadano(a) de su estado.\n\nReconociendo su labor en la Cámara Alta y su participación en las comisiones legislativas, les solicito de la manera más respetuosa su intervención conjunta para que NO se apruebe (y se promueva la derogación) de la llamada legislación sobre violencia vicaria.\n\nAprobar una legislación que tipifica delitos de manera asimétrica, excluyendo a los hombres de la posibilidad de denunciar y acceder a la misma protección, nos devuelve a la figura del 'derecho penal de autor', vulnerando la igualdad ante la ley consagrada en nuestra Constitución.\n\nLes solicito que desde el Senado se vote en contra de medidas que comprometan la certidumbre jurídica de nuestro país.\n\nAtentamente,\n{nombre}\nC.P. {cp}"
                        
                        st.markdown("**1. Correos a enviar:** *(Cópialos si quieres enviar el correo manualmente)*")
                        st.code(cadena_correos_sen, language=None)
                        
                        st.markdown("**2. Mensaje sugerido:** *(Cópialo si los botones de abajo fallan)*")
                        st.code(cuerpo_masivo_sen, language=None)
                        
                        st.markdown("**3. Enviar automáticamente:**")
                        st.markdown(generar_botones_webmail(cadena_correos_sen, asunto_masivo_sen, cuerpo_masivo_sen), unsafe_allow_html=True)
                        
                        with st.expander("Ver opciones de contacto individual por Senador"):
                            for _, row in senadores_filtrados.iterrows():
                                sen_nombre_crudo = str(row.get('senator_details_name', ''))
                                nombre_natural, saludo_sen, etiqueta_sen = formatear_y_obtener_saludo(sen_nombre_crudo, "Senador")
                                sen_correo = str(row.get('senator_details_email', '')).strip()
                                sen_comisiones = str(row.get('Comisiones', 'diversas comisiones legislativas'))

                                # Etiqueta de origen del senador
                                es_lista_nacional = 'lista nacional' in str(row.get('Estado', '')).lower()
                                origen_sen = "🌐 Lista Nacional" if es_lista_nacional else f"📍 {estado_detectado}"
                                
                                tiene_correo_sen = bool(sen_correo and sen_correo.lower() != 'nan')
                                pronombre_sen = "Esta" if etiqueta_sen == "Senadora" else "Este"
                                
                                cuerpo_ind_sen = f"{saludo_sen} {nombre_natural},\n\nComo representante por el estado de {estado_detectado} y desde su importante labor como integrante de las comisiones de {sen_comisiones}, me dirijo a usted con profunda preocupación ciudadana.\n\nLe solicito respetuosamente su voto en contra (y la promoción de la derogación) de la legislación sobre violencia vicaria. Esta ley tipifica delitos de manera asimétrica, aplicando un 'derecho penal de autor' que castiga a la persona por su sexo y vulnera la igualdad ante la ley garantizada por nuestra Constitución.\n\nConfío en su compromiso con una justicia equitativa para todos los ciudadanos.\n\nAtentamente,\n{nombre}\nC.P. {cp}"
                                
                                st.markdown(f"**{etiqueta_sen} {nombre_natural}**")
                                st.caption(f"{origen_sen} | 🏛️ Comisiones: {sen_comisiones}")
                                
                                col_email, col_tel = st.columns(2)
                                with col_email:
                                    if tiene_correo_sen:
                                        st.markdown("📧 **Correo electrónico:**")
                                        st.code(sen_correo, language=None)
                                    else:
                                        st.warning(f"⚠️ {pronombre_sen} {etiqueta_sen} no tiene un correo público registrado.")
                                        
                                with col_tel:
                                    detalles_oficina = str(row.get('senator_details_office_details', ''))
                                    busqueda_tel = re.search(r'Tel:\s*([\d\s]+).*?Ext:\s*(.*?)(?=\s*Correo:|$)', detalles_oficina)
                                    if busqueda_tel:
                                        tel_base = busqueda_tel.group(1).strip()
                                        extension = busqueda_tel.group(2).strip()
                                        st.markdown("📞 **Conmutador:**")
                                        st.code(tel_base, language=None)
                                        st.markdown("📟 **Extensión:**")
                                        st.code(extension, language=None)
                                    else:
                                        st.markdown("📞 **Teléfono:**")
                                        st.caption("No disponible")
                                
                                if tiene_correo_sen:
                                    st.markdown("*(Copia este mensaje si los botones de envío fallan)*")
                                    st.code(cuerpo_ind_sen, language=None)
                                    st.markdown(generar_botones_webmail(sen_correo, "Llamado a la Igualdad Constitucional - Violencia Vicaria", cuerpo_ind_sen), unsafe_allow_html=True)
                                
                                st.divider()
            else:
                st.error("Base de datos de Senadores no encontrada.")

            # ==========================================
            # SECCIÓN 2: CÁMARA DE DIPUTADOS
            # ==========================================
            st.markdown("---")
            st.header("🏛️ CÁMARA DE DIPUTADOS")
            
            if not df_diputados.empty and 'Estado' in df_diputados.columns:
                condicion_estado = df_diputados['Estado'].str.contains(estado_detectado, case=False, na=False)
                diputados_filtrados = df_diputados[condicion_estado]
                
                if diputados_filtrados.empty:
                    st.info(f"No hay diputados listados para {estado_detectado}.")
                else:
                    correos_diputados = [str(row.get('Correo', '')).strip() for _, row in diputados_filtrados.iterrows() if str(row.get('Correo', '')).strip() and str(row.get('Correo', '')).lower() != 'nan']
                    cadena_correos_dip = ",".join(correos_diputados)
                    
                    if correos_diputados:
                        st.subheader(f"🚀 Envío Masivo ({len(diputados_filtrados)} Diputados)")
                        asunto_masivo_dip = "Petición ciudadana urgente: Rechazo a la Ley de Violencia Vicaria"
                        cuerpo_masivo_dip = f"Estimados Diputados Federales y Diputadas por el estado de {estado_detectado},\n\nEspero que este mensaje les encuentre muy bien. Me dirijo a ustedes en mi calidad de ciudadano(a) de su estado.\n\nReconociendo su labor legislativa en San Lázaro y su participación en las diversas comisiones, les solicito de la manera más respetuosa su intervención conjunta para que NO se apruebe (y se promueva la derogación) de la llamada legislación sobre violencia vicaria.\n\nAprobar una legislación que tipifica delitos de manera asimétrica, excluyendo a los hombres de la posibilidad de denunciar y acceder a la misma protección, nos devuelve a la figura del 'derecho penal de autor', vulnerando la igualdad ante la ley consagrada en nuestra Constitución.\n\nLes solicito que desde sus curules se vote en contra de medidas que comprometan la certidumbre jurídica de nuestro país.\n\nAtentamente,\n{nombre}\nC.P. {cp}"
                        
                        st.markdown("**1. Correos a enviar:** *(Cópialos si quieres enviar el correo manualmente)*")
                        st.code(cadena_correos_dip, language=None)
                        
                        st.markdown("**2. Mensaje sugerido:** *(Cópialo si los botones de abajo fallan)*")
                        st.code(cuerpo_masivo_dip, language=None)
                        
                        st.markdown("**3. Enviar automáticamente:**")
                        st.markdown(generar_botones_webmail(cadena_correos_dip, asunto_masivo_dip, cuerpo_masivo_dip), unsafe_allow_html=True)
                        
                        with st.expander("Ver opciones de contacto individual por Diputado"):
                            for _, row in diputados_filtrados.iterrows():
                                dip_nombre_crudo = str(row.get('Nombre', ''))
                                nombre_natural, saludo_dip, etiqueta_dip = formatear_y_obtener_saludo(dip_nombre_crudo, "Diputado")
                                dip_partido = str(row.get('Partido', '')).upper()
                                dip_correo = str(row.get('Correo', '')).strip()
                                dip_comisiones = str(row.get('Comisiones', 'diversas comisiones legislativas'))
                                
                                tiene_correo_dip = bool(dip_correo and dip_correo.lower() != 'nan')
                                pronombre_dip = "Esta" if etiqueta_dip == "Diputada" else "Este"
                                
                                cuerpo_ind_dip = f"{saludo_dip} {nombre_natural},\n\nComo representante por el estado de {estado_detectado} y desde su importante labor legislativa como integrante de las comisiones de {dip_comisiones}, me dirijo a usted con profunda preocupación ciudadana.\n\nLe solicito respetuosamente su voto en contra (y la promoción de la derogación) de la legislación sobre violencia vicaria. Esta ley tipifica delitos de manera asimétrica, aplicando un 'derecho penal de autor' que castiga a la persona por su sexo y vulnera la igualdad ante la ley garantizada por el Artículo 4to Constitucional.\n\nConfío en su compromiso con una justicia neutral y equitativa.\n\nAtentamente,\n{nombre}\nC.P. {cp}"
                                
                                st.markdown(f"**{etiqueta_dip} {nombre_natural}** ({dip_partido})")
                                st.caption(f"🏛️ Comisiones: {dip_comisiones}")
                                
                                col_email, col_tel = st.columns(2)
                                with col_email:
                                    if tiene_correo_dip:
                                        st.markdown("📧 **Correo electrónico:**")
                                        st.code(dip_correo, language=None)
                                    else:
                                        st.warning(f"⚠️ {pronombre_dip} {etiqueta_dip} no tiene un correo público registrado.")
                                        
                                with col_tel:
                                    st.markdown("📞 **Conmutador San Lázaro:**")
                                    st.code("55 5036 0000", language=None)
                                    articulo = "de la" if etiqueta_dip == "Diputada" else "del"
                                    st.caption(f"*(Pide que te comuniquen a la oficina {articulo} {etiqueta_dip} {nombre_natural})*")
                                
                                if tiene_correo_dip:
                                    st.markdown("*(Copia este mensaje si los botones de envío fallan)*")
                                    st.code(cuerpo_ind_dip, language=None)
                                    st.markdown(generar_botones_webmail(dip_correo, "Llamado a la Igualdad Constitucional - Violencia Vicaria", cuerpo_ind_dip), unsafe_allow_html=True)
                                    
                                st.divider()
            else:
                st.info("Base de datos de Diputados no encontrada.")
