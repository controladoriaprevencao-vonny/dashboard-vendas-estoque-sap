import pandas as pd
import streamlit as st

# Configuração da página web com o ícone personalizado
st.set_page_config(
    page_title="Dashboard Executivo - Vonný",
    page_icon="icone.png",
    layout="wide",
)

# Estilo visual corporativo e limpo
st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    h1, h2, h3 {
        color: #1F4E79;
    }
    .stButton>button {
        width: 100%;
        background-color: #1F4E79;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 50px;
    }
    .stButton>button:hover {
        background-color: #153a5b;
        color: white;
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
    df = pd.read_excel(uploaded_file)
    if "Quantidade faturada" in df.columns and "Preço interno" in df.columns:
        df["Quantidade faturada"] = pd.to_numeric(
            df["Quantidade faturada"], errors="coerce"
        ).fillna(0)
        df["Preço interno"] = pd.to_numeric(
            df["Preço interno"], errors="coerce"
        ).fillna(0)
        df["Valor líquido"] = df["Quantidade faturada"] * df["Preço interno"]
    return df

@st.cache_data
def processar_estoque(uploaded_file):
    if uploaded_file is None:
        return None
    df = pd.read_excel(uploaded_file)
    return df

# ==========================================
# BARRA LATERAL (Navegação de Perfis)
# ==========================================
with st.sidebar:
    st.header("⚙️ Painel de Controle")
    
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
        st.markdown("Área executiva para análise interativa dos relatórios de vendas, estoques e filtros por loja.")
        if st.button("Acessar Gestão ➔", key="btn_gerente"):
            st.session_state.perfil_atual = "Gerente"
            st.session_state.pagina_atual = "Home"
            st.rerun()

# ==========================================
# 2. VISÃO ADMINISTRATIVA (UPLOAD MÚLTIPLO)
# ==========================================
elif st.session_state.perfil_atual == "Admin":
    st.title("🛠️ Painel Administrativo - Upload de Arquivos")
    st.markdown("Selecione ou arraste quantos arquivos precisar de uma só vez. Eles ficarão salvos e fixos na sessão.")

    # Botão único de upload aceitando múltiplos arquivos
    uploaded_files = st.file_uploader(
        "Upload de Arquivos Administrativos",
        type=["xlsx"],
        accept_multiple_files=True,
        key="multi_upload_admin",
        label_visibility="collapsed"
    )

    if uploaded_files:
        for file in uploaded_files:
            # Armazena cada arquivo na sessão usando o nome do arquivo como chave
            st.session_state.arquivos_admin_fixos[file.name] = file
        st.success(f"🎉 {len(uploaded_files)} arquivo(s) processado(s) e fixado(s) com sucesso!")

    st.markdown("---")
    st.subheader("📋 Arquivos Atualmente Fixados na Sessão:")
    if len(st.session_state.arquivos_admin_fixos) > 0:
        for nome_arquivo in st.session_state.arquivos_admin_fixos.keys():
            st.markdown(f"- 📄 **{nome_arquivo}**")
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
    
    # Para as demonstrações das tabelas abaixo, mantemos a compatibilidade
    df_vendas = st.session_state.df_vendas_fixo
    df_estoque = st.session_state.df_estoque_fixo

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
        if df_vendas is not None:
            # Estrutura de vendas padrão
            pass
        else:
            st.warning("⚠️ O arquivo de Vendas não está disponível no momento.")

    elif st.session_state.pagina_atual == "Estoques":
        st.title("📋 Relatório Consolidado de Estoque")
        if df_estoque is not None:
            # Estrutura de estoque padrão
            pass
        else:
            st.warning("⚠️ O arquivo de Estoques não está disponível no momento.")
