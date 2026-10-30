import streamlit as st

# ==========================================
# CONFIGURAÇÃO DE AMBIENTE E ESTILO VISUAL
# ==========================================
AMBIENTE_STAGING = True

st.set_page_config(
    page_title="Dashboard Executivo - Vonný" + (" [STAGING]" if AMBIENTE_STAGING else ""),
    page_icon="icone.png",
    layout="wide",
)

# Estilização visual customizada (Tema Vonný: Rosa e Cinza Claro)
st.markdown(
    """
    <style>
    /* Cabeçalho superior do Streamlit */
    header[data-testid="stHeader"] {
        background-color: #E6007E !important;
    }
    
    /* Fundo principal da aplicação */
    .main {
        background-color: #EAEAEA !important;
        color: #2C2C2C !important;
    }
    
    /* Fundo da área de conteúdo geral */
    [data-testid="stAppViewContainer"] {
        background-color: #EAEAEA !important;
        color: #2C2C2C !important;
    }
    
    /* Barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #FFE6EE !important;
        border-right: 1px solid #F5CCD8 !important;
    }
    
    /* Títulos */
    h1, h2, h3 {
        color: #C5006B !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 700 !important;
    }
    
    /* Textos gerais */
    p, span, label, div {
        color: #2C2C2C !important;
    }
    
    /* Botões personalizados */
    .stButton>button {
        width: 100%;
        background-color: #555555 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border-radius: 6px;
        height: 48px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #333333 !important;
        color: #FFFFFF !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

if AMBIENTE_STAGING:
    st.warning("⚠️ **ATENÇÃO: Você está acessando a versão de testes (Staging).**")

st.title("📊 Dashboard Executivo - Vonný")
st.markdown("Bem-vindo ao sistema de relatórios gerenciais integrados ao SAP e hospedados no Supabase.")
st.markdown("Utilize o menu lateral esquerdo para navegar entre a **Central de Uploads** e os **Relatórios de Vendas e Estoque**.")

st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📤 Central de Uploads")
    st.markdown("Envie e gerencie as planilhas administrativas, de estoque e de vendas de forma isolada.")

with col2:
    st.markdown("### 📊 Dashboards e Relatórios")
    st.markdown("Consulte os dados consolidados, aplique filtros por loja/material e analise os números.")
