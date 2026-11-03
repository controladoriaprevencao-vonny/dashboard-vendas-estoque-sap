import streamlit as st

# ==========================================
# CONFIGURAÇÃO DE AMBIENTE
# ==========================================
AMBIENTE_STAGING = False  # Mude para True na branch de staging se desejar

# Configuração da página web com o ícone personalizado
st.set_page_config(
    page_title="Dashboard Executivo - Vonný" + (" [STAGING]" if AMBIENTE_STAGING else ""),
    page_icon="icone.png",
    layout="wide",
)

st.markdown(
    """
    <style>
    header[data-testid="stHeader"] { background-color: #E6007E !important; }
    section[data-testid="stSidebar"] { border-right: 1px solid #F5CCD8; }
    h1, h2, h3 { color: #C5006B !important; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 700; }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# BARRA LATERAL (Apenas Logotipo)
# ==========================================
with st.sidebar:
    try:
        st.image("logo_vonny.png", use_container_width=True)
    except:
        st.markdown("<h2 style='color: #E6007E; text-align: center; margin-bottom: 0px;'>VONNÝ</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 11px; color: #666; letter-spacing: 2px;'>COSMÉTICOS</p>", unsafe_allow_html=True)
    
    if AMBIENTE_STAGING:
        st.info("🛠️ **Staging (Testes)**")

# ==========================================
# AVISO CONDICIONAL NO TOPO (SÓ SE FOR STAGING)
# ==========================================
if AMBIENTE_STAGING:
    st.warning("⚠️ **ATENÇÃO: Você está acessando a versão de testes (Staging).**")

# ==========================================
# PÁGINA PRINCIPAL / HOME
# ==========================================
st.title("📊 Dashboard Executivo - Vonný")
st.markdown("Bem-vindo ao sistema de relatórios gerenciais integrados ao SAP e hospedados no Supabase. Escolha abaixo a seção que deseja acessar:")

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📤 Upload")
    st.markdown("Gerenciamento e envio de arquivos para o Supabase.")
    if st.button("Acessar Upload ➔", key="btn_upload", use_container_width=True):
        st.switch_page("pages/1_Upload_e_Formatacao.py")
        
with col2:
    st.markdown("### 📋 Dashboards Estoque")
    st.markdown("Análise inteligente e filtros em cascata do estoque atual.")
    if st.button("Acessar Estoque ➔", key="btn_estoque", use_container_width=True):
        st.switch_page("pages/2_Relatorio_Estoque.py")

with col3:
    st.markdown("### 📈 Dashboards Vendas")
    st.markdown("Relatórios executivos e análise de desempenho de vendas.")
    if st.button("Acessar Vendas ➔", key="btn_vendas", use_container_width=True):
        st.switch_page("pages/3_Relatorio_Vendas.py")
