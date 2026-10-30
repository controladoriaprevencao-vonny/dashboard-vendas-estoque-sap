import pandas as pd
import streamlit as st

# Configuração da página web com o ícone personalizado
st.set_page_config(
    page_title="Dashboard Executivo - Vonný",
    page_icon="icone.png",
    layout="wide",
)

# Estilo visual limpo, elegante e alinhado com a marca Vonný
st.markdown(
    """
    <style>
    /* Faixa pink oficial no topo absoluto da página */
    header[data-testid="stHeader"] {
        background-color: #E6007E !important;
    }
    
    /* Fundo do painel principal (Lado direito) em cinza claro sofisticado */
    .main {
        background-color: #F4F4F6 !important;
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

    /* Botões estilizados com padrão limpo e elegante */
    .stButton>button {
        width: 100%;
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
        border: 1px solid #D5CBD0 !important;
        border-radius: 6px;
        height: 48px;
        font-weight: 600;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #E6007E !important;
        color: #FFFFFF !important;
        border-color: #E6007E !important;
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
    # Exibição segura do logo (se o arquivo logo.png estiver na pasta)
    try:
        st.image("logo.png", use_column_width=True)
    except Exception:
        st.markdown("<h2 style='color: #E6007E; text-align: center;'>VONNÝ</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 12px; color: #666;'>COSMÉTICOS</p>", unsafe_allow_html=True)
    
    st.markdown("---")
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
elif st.session_state.perfil_atual == "Admin":
    st.title("🛠️ Painel Administrativo - Upload de Arquivos")
    st.markdown("Selecione ou arraste quantos arquivos precisar de uma só vez (formatos `.xlsx` e `.xlsm`). Eles ficarão salvos e fixos na sessão.")

    uploaded_files = st.file_uploader(
        "Upload de Arquivos Administrativos",
        type=["xlsx", "xlsm"],
        accept_multiple_files=True,
        key="multi_upload_admin",
        label_visibility="collapsed"
    )

    if uploaded_files:
        for file in uploaded_files:
            st.session_state.arquivos_admin_fixos[file.name] = {
                "objeto": file,
                "df": processar_excel(file)
            }
        st.success(f"🎉 {len(uploaded_files)} arquivo(s) processado(s) e fixado(s) com sucesso!")

    st.markdown("---")
    st.subheader("📋 Arquivos Atualmente Fixados na Sessão:")
    if len(st.session_state.arquivos_admin_fixos) > 0:
        for nome_arquivo, dados in st.session_state.arquivos_admin_fixos.items():
            qtd_linhas = len(dados["df"]) if dados["df"] is not None else 0
            st.markdown(f"- 📄 **{nome_arquivo}** _({qtd_linhas} linhas carregadas)_")
    else:
        st.info("Nenhum arquivo enviado até o momento.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Limpar Todos os Arquivos Fixos"):
        st.session_state.arquivos_admin_fixos = {}
        st.cache_data.clear()
        st.rerun()

# ==========================================
# 3. VISÃO DOS GERENTES DE PRODUTO
# ==========================================
elif st.session_state.perfil_atual == "Gerente":
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🧭 Módulos Gerenciais")
        if st.button("📊 Menu Principal Gestão"):
            st.session_state.pagina_atual = "Home"
            st.rerun()
        if st.button("📈 Módulo de Vendas"):
            st.session_state.pagina_atual = "Vendas"
            st.rerun()
        if st.button("📋 Módulo de Estoques"):
            st.session_state.pagina_atual = "Estoques"
            st.rerun()

    if st.session_state.pagina_atual == "Home":
        st.title("📦 Visão Executiva - Gestão de Produtos")
        st.markdown("Selecione abaixo o módulo que deseja analisar:")

        st.markdown("<br>", unsafe_allow_html=True)
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown("### 📈 Módulo de Vendas")
            if st.button("Entrar em Vendas ➔", key="g_vendas"):
                st.session_state.pagina_atual = "Vendas"
                st.rerun()

        with col_g2:
            st.markdown("### 📋 Módulo de Estoques")
            if st.button("Entrar em Estoques ➔", key="g_estoque"):
                st.session_state.pagina_atual = "Estoques"
                st.rerun()

    elif st.session_state.pagina_atual == "Vendas":
        st.title("📈 Relatório Executivo de Vendas")
        st.info("💡 Módulo aguardando definição de cruzamento com os arquivos administrativos.")

    elif st.session_state.pagina_atual == "Estoques":
        st.title("📋 Relatório Consolidado de Estoque")
        st.info("💡 Módulo aguardando definição de cruzamento com os arquivos administrativos.")
