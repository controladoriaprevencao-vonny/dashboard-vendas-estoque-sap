import pandas as pd
import streamlit as st

# Configuração da página web com o ícone personalizado
st.set_page_config(
    page_title="Dashboard Executivo - Vonný",
    page_icon="icone.png",
    layout="wide",
)

# Estilo visual ajustado conforme solicitado
st.markdown(
    """
    <style>
    /* Fundo do painel principal (Lado direito) em cinza bem clarinho */
    .main {
        background-color: #F8F9FA !important;
        color: #2C2C2C;
    }
    
    /* Barra lateral em tom rosa claro da marca */
    section[data-testid="stSidebar"] {
        background-color: #FFE6EE !important;
        border-right: 1px solid #F5CCD8;
    }
    
    /* Títulos e cabeçalhos em rosa escuro/magenta */
    h1, h2, h3 {
        color: #C5006B !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 700;
    }
    
    /* Textos gerais do painel */
    p, span, label, div {
        color: #333333;
    }

    /* Botões em rosa bem escuro/magenta */
    .stButton>button {
        width: 100%;
        background-color: #E6007E !important;
        border-radius: 6px;
        height: 48px;
        border: none;
        transition: 0.3s;
    }

    /* Força OBRIGATORIAMENTE o texto dos botões a ficar em BRANCO e NEGRITO */
    .stButton>button p, .stButton>button span, .stButton>button div {
        color: #FFFFFF !important;
        font-weight: bold !important;
        font-size: 15px;
    }
    
    .stButton>button:hover {
        background-color: #C5006B !important;
    }

    .stButton>button:hover p, .stButton>button:hover span {
        color: #FFFFFF !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Inicializa o estado da sessão para navegação e arquivos persistentes
if "perfil_atual" not in st.session_state:
    st.session_state.perfil_atual = "Home"

if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "Home"

if "arquivos_admin_fixos" not in st.session_state:
    st.session_state.arquivos_admin_fixos = {}

if "df_vendas_fixo" not in st.session_state:
    st.session_state.df_vendas_fixo = None

if "df_estoque_fixo" not in st.session_state:
    st.session_state.df_estoque_fixo = None

# ==========================================
# FUNÇÃO DE LEITURA COMPATÍVEL (.XLSX / .XLSM)
# ==========================================
@st.cache_data
def processar_excel(uploaded_file):
    if uploaded_file is None:
        return None
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        return df
    except Exception as e:
        return None

# ==========================================
# BARRA LATERAL (Navegação de Perfis)
# ==========================================
with st.sidebar:
    st.header("✨ Vonný | Painel")
    
    st.markdown("### Selecione o Perfil:")
    if st.button("🏠 Menu Principal"):
        st.session_state.perfil_atual = "Home"
        st.session_state.pagina_atual = "Home"
        st.rerun()
        
    if st.button("🛠️ Visão Administrativa"):
        st.session_state.perfil_atual = "Admin"
        st.rerun()
        
    if st.button("📦 Visão Gestão / Produtos"):
        st.session_state.perfil_atual = "Gerente"
        st.session_state.pagina_atual = "Home"
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Status dos Dados")
    if len(st.session_state.arquivos_admin_fixos) > 0:
        st.success(f"✅ {len(st.session_state.arquivos_admin_fixos)} arquivo(s) carregado(s)")
    else:
        st.warning("⚠️ Nenhum arquivo carregado")

# ==========================================
# 1. HOME / SELEÇÃO DE PERFIL
# ==========================================
if st.session_state.perfil_atual == "Home":
    st.title("✨ Dashboard Executivo - Vonný")
    st.markdown("Bem-vindo ao sistema de relatórios gerenciais. Escolha abaixo qual visão deseja acessar:")
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🛠️ Visão Administrativa")
        st.markdown("Área restrita para upload múltiplo de planilhas (`.xlsx` e `.xlsm`) e fixação de bases.")
        if st.button("Acessar Administrativo ➔", key="btn_admin"):
            st.session_state.perfil_atual = "Admin"
            st.rerun()
            
    with col2:
        st.markdown("### 📦 Visão Gerentes de Produto")
        st.markdown("Área executiva para análise interativa dos relatórios de vendas, estoques e indicadores.")
        if st.button("Acessar Gestão ➔", key="btn_gerente"):
            st.session_state.perfil_atual = "Gerente"
            st.session_state.pagina_atual = "Home"
            st.rerun()

# ==========================================
# 2. VISÃO ADMINISTRATIVA (UPLOAD MÚLTIPLO)
# ==========================================
