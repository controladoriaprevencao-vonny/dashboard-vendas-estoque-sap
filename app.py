import io
import pandas as pd
import streamlit as st
from supabase import create_client, Client

# ==========================================
# CONFIGURAÇÃO DE AMBIENTE E SUPABASE
# ==========================================
AMBIENTE_STAGING = False  # Mude para True na branch de staging se desejar

SUPABASE_URL = "https://cfxrcnnuupabepbqascx.supabase.co"
SUPABASE_KEY = "sb_publishable_-Hoz_n3NdCndYmNETF4sDQ_9Bzphw5Q"
BUCKET_NOME = "dados-vonny"

@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        return None

supabase: Client = init_supabase()

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

# Inicializa o estado da sessão para navegação interna
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "Home"

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
    st.warning("⚠️ **ATENÇÃO: Você está a aceder à versão de testes (Staging).**")

# ==========================================
# PÁGINA PRINCIPAL / HOME
# ==========================================
if st.session_state.pagina_atual == "Home":
    st.title("📊 Dashboard Executivo - Vonný")
    st.markdown("Bem-vindo ao sistema de relatórios gerenciais integrados ao SAP e hospedados no Supabase. Escolha abaixo a secção que deseja aceder:")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3 colunas para os três botões principais solicitados
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📤 Upload")
        st.markdown("Gerenciamento e envio de ficheiros para o Supabase.")
        if st.button("Aceder Upload ➔", key="btn_upload", use_container_width=True):
            st.session_state.pagina_atual = "Upload"
            st.rerun()
            
    with col2:
        st.markdown("### 📋 Dashboards Estoque")
        st.markdown("Análise inteligente e filtros em cascata do stock atual.")
        if st.button("Aceder Estoque ➔", key="btn_estoque", use_container_width=True):
            st.session_state.pagina_atual = "Estoque"
            st.rerun()

    with col3:
        st.markdown("### 📈 Dashboards Vendas")
        st.markdown("Relatórios executivos e análise de desempenho de vendas.")
        if st.button("Aceder Vendas ➔", key="btn_vendas", use_container_width=True):
            st.session_state.pagina_atual = "Vendas"
            st.rerun()

# ==========================================
# MÓDULO DE UPLOAD
# ==========================================
elif st.session_state.pagina_atual == "Upload":
    if st.button("← Voltar ao Menu Principal"):
        st.session_state.pagina_atual = "Home"
        st.rerun()
        
    st.title("📤 Painel de Upload de Ficheiros")
    st.markdown("Faça o envio dos ficheiros diretamente para as pastas correspondentes no Supabase.")

    tab1, tab2 = st.tabs(["📁 Pasta Administração", "📁 Pasta Gestão"])

    with tab1:
        st.markdown("### Upload para Administração")
        up_admin = st.file_uploader("Enviar ficheiros de parâmetros", type=["xlsx", "xlsm", "xlsb"], accept_multiple_files=True, key="up_adm")
        if up_admin and supabase:
            for f in up_admin:
                try:
                    supabase.storage.from_(BUCKET_NOME).upload(path=f"Administração/{f.name}", file=f.getvalue(), file_options={"upsert": "true"})
                    st.success(f"Ficheiro **{f.name}** enviado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao enviar {f.name}: {e}")

    with tab2:
        st.markdown("### Upload para Gestão")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            up_est = st.file_uploader("Ficheiro de Stock (`estoque_fixo.xlsx`)", type=["xlsx", "xlsm"], key="up_est_file")
            if up_est and supabase:
                try:
                    supabase.storage.from_(BUCKET_NOME).upload(path="Gestao/estoque_fixo.xlsx", file=up_est.getvalue(), file_options={"upsert": "true"})
                    st.success("Stock atualizado com sucesso!")
                except Exception as e:
                    st.error(f"Erro: {e}")
        with col_g2:
            up_ven = st.file_uploader("Ficheiro de Vendas (`vendas_fixo.xlsx`)", type=["xlsx", "xlsm"], key="up_ven_file")
            if up_ven and supabase:
                try:
                    supabase.storage.from_(BUCKET_NOME).upload(path="Gestao/vendas_fixo.xlsx", file=up_ven.getvalue(), file_options={"upsert": "true"})
                    st.success("Vendas atualizadas com sucesso!")
                except Exception as e:
                    st.error(f"Erro: {e}")

# ==========================================
# MÓDULO DE DASHBOARDS ESTOQUE
# ==========================================
elif st.session_state.pagina_atual == "Estoque":
    if st.button("← Voltar ao Menu Principal"):
        st.session_state.pagina_atual = "Home"
        st.rerun()
        
    st.title("📋 Dashboards Estoque")
    st.info("Módulo de visualização e filtros de stock integrado ao Supabase.")

# ==========================================
# MÓDULO DE DASHBOARDS VENDAS
# ==========================================
elif st.session_state.pagina_atual == "Vendas":
    if st.button("← Voltar ao Menu Principal"):
        st.session_state.pagina_atual = "Home"
        st.rerun()
        
    st.title("📈 Dashboards Vendas")
    st.info("Módulo de visualização e análise de vendas integrado ao Supabase.")
