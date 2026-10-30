import pandas as pd
import streamlit as st

# Configuração da página web com o ícone personalizado
st.set_page_config(
    page_title="Dashboard Executivo - Vonný",
    page_icon="icone.png",
    layout="wide",
)

# Estilo visual limpo, com a faixa pink no topo, fundo cinza encorpado e botões em cinza com texto branco e negrito
st.markdown(
    """
    <style>
    /* Faixa pink oficial no topo absoluto da página */
    header[data-testid="stHeader"] {
        background-color: #E6007E !important;
    }
    
    /* Fundo do painel principal (Lado direito) em cinza mais escuro */
    .main {
        background-color: #EAEAEA !important;
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
    
    /* Botões estilizados em cinza elegante */
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
# FUNÇÕES COM CACHE PARA LEITURA RÁPIDA
# ==========================================
@st.cache_data
def processar_vendas(uploaded_file):
    if uploaded_file is None:
        return None
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    if "Quantidade faturada" in df.columns and "Preço interno" in df.columns:
        df["Quantidade faturada"] = pd.to_numeric(df["Quantidade faturada"], errors="coerce").fillna(0)
        df["Preço interno"] = pd.to_numeric(df["Preço interno"], errors="coerce").fillna(0)
        df["Valor líquido"] = df["Quantidade faturada"] * df["Preço interno"]
    return df

@st.cache_data
def processar_estoque(uploaded_file):
    if uploaded_file is None:
        return None
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    return df

# ==========================================
# BARRA LATERAL (Navegação de Perfis)
# ==========================================
with st.sidebar:
    # Exibe a logo oficial no topo da barra lateral (Certifique-se de salvar o arquivo como 'logo_vonny.png' no GitHub)
    try:
        st.image("logo_vonny.png", use_container_width=True)
    except:
        st.markdown("<h2 style='color: #E6007E; text-align: center; margin-bottom: 0px;'>VONNÝ</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 11px; color: #666; letter-spacing: 2px;'>COSMÉTICOS</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### Selecione o Perfil:")
    if st.button("🏠 Menu Principal", key="sb_home"):
        st.session_state.perfil_atual = "Home"
        st.session_state.pagina_atual = "Home"
        st.rerun()
        
    if st.button("🛠️ Visão Administrativa", key="sb_admin"):
        st.session_state.perfil_atual = "Admin"
        st.rerun()
        
    if st.button("📦 Visão Gestão / Produtos", key="sb_gerente"):
        st.session_state.perfil_atual = "Gerente"
        st.session_state.pagina_atual = "Home"
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Status dos Dados")
    if st.session_state.df_vendas_fixo is not None or st.session_state.df_estoque_fixo is not None or len(st.session_state.arquivos_admin_fixos) > 0:
        st.success("✅ Dados carregados na sessão")
    else:
        st.warning("⚠️ Nenhum arquivo carregado")

# ==========================================
# 1. HOME / SELEÇÃO DE PERFIL
# ==========================================
if st.session_state.perfil_atual == "Home":
    st.title("📊 Dashboard Executivo - Vonný")
    st.markdown("Bem-vindo ao sistema de relatórios gerenciais integrados ao SAP. Escolha abaixo qual visão deseja acessar:")
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🛠️ Visão Administrativa")
        st.markdown("Área restrita para upload múltiplo e fixação de planilhas administrativas.")
        if st.button("Acessar Administrativo ➔", key="btn_admin"):
            st.session_state.perfil_atual = "Admin"
            st.rerun()
            
    with col2:
        st.markdown("### 📦 Visão Gerentes de Produto")
        st.markdown("Área executiva para upload individual de planilhas (Estoque / Vendas) e análise interativa.")
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
                "df": processar_vendas(file)
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
    if st.button("🔄 Limpar Todos os Arquivos Fixos", key="btn_limpar_admin"):
        st.session_state.arquivos_admin_fixos = {}
        st.session_state.df_vendas_fixo = None
        st.session_state.df_estoque_fixo = None
        st.cache_data.clear()
        st.rerun()

# ==========================================
# 3. VISÃO DOS GERENTES DE PRODUTO
# ==========================================
elif st.session_state.perfil_atual == "Gerente":
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🧭 Módulos Gerenciais")
        if st.button("📊 Menu Principal Gestão", key="sub_home"):
            st.session_state.pagina_atual = "Home"
            st.rerun()
        if st.button("📋 Módulo de Estoques", key="sub_estoques"):
            st.session_state.pagina_atual = "Estoques"
            st.rerun()
        if st.button("📈 Módulo de Vendas", key="sub_vendas"):
            st.session_state.pagina_atual = "Vendas"
            st.rerun()

    if st.session_state.pagina_atual == "Home":
        st.title("📦 Visão Executiva - Gestão de Produtos")
        st.markdown("Faça o upload direto dos arquivos abaixo (Estoque à esquerda e Vendas à direita) ou selecione o módulo para análise:")

        # Seção de Upload para o Gerente invertida: Estoque primeiro, Vendas depois
        with st.expander("📂 Fazer Upload das Planilhas (Estoque e Vendas)", expanded=True):
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                file_e = st.file_uploader("Planilha de Estoque (.xlsx / .xlsm)", type=["xlsx", "xlsm"], key="up_estoque_gerente")
                if file_e is not None:
                    st.session_state.df_estoque_fixo = processar_estoque(file_e)
                    st.success("✅ Estoque carregado com sucesso!")
            with col_u2:
                file_v = st.file_uploader("Planilha de Vendas (.xlsx / .xlsm)", type=["xlsx", "xlsm"], key="up_vendas_gerente")
                if file_v is not None:
                    st.session_state.df_vendas_fixo = processar_vendas(file_v)
                    st.success("✅ Vendas carregadas com sucesso!")

        st.markdown("<br>", unsafe_allow_html=True)
        col_g1, col_g2 = st.columns(2)

        # Invertido também nos botões da Home da Gestão: Estoque à esquerda, Vendas à direita
        with col_g1:
            st.markdown("### 📋 Módulo de Estoques")
            if st.button("Entrar em Estoques ➔", key="g_estoque"):
                st.session_state.pagina_atual = "Estoques"
                st.rerun()

        with col_g2:
            st.markdown("### 📈 Módulo de Vendas")
            if st.button("Entrar em Vendas ➔", key="g_vendas"):
                st.session_state.pagina_atual = "Vendas"
                st.rerun()

    elif st.session_state.pagina_atual == "Estoques":
        st.title("📋 Relatório Consolidado de Estoque")
        if st.session_state.df_estoque_fixo is not None:
            st.dataframe(st.session_state.df_estoque_fixo, use_container_width=True)
        else:
            st.warning("⚠️ Nenhuma planilha de Estoque carregada. Utilize a seção de upload na página inicial da Gestão.")

    elif st.session_state.pagina_atual == "Vendas":
        st.title("📈 Relatório Executivo de Vendas")
        if st.session_state.df_vendas_fixo is not None:
            st.dataframe(st.session_state.df_vendas_fixo, use_container_width=True)
        else:
            st.warning("⚠️ Nenhuma planilha de Vendas carregada. Utilize a seção de upload na página inicial da Gestão.")
