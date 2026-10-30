import pandas as pd
import streamlit as st

# ==========================================
# CONFIGURAÇÃO DE AMBIENTE (CHAVE AUTOMÁTICA)
# Deixe True para Staging (Testes) e mude para False na Main (Produção)
# ==========================================
AMBIENTE_STAGING = True

# Configuração da página web com o ícone personalizado
st.set_page_config(
    page_title="Dashboard Executivo - Vonný" + (" [STAGING]" if AMBIENTE_STAGING else ""),
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

# Inicializa o estado da sessão para garantir persistência ao dar F5
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
# FUNÇÕES DE PROCESSAMENTO
# ==========================================
def processar_vendas(uploaded_file):
    if uploaded_file is None:
        return None
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        if "Quantidade faturada" in df.columns and "Preço interno" in df.columns:
            df["Quantidade faturada"] = pd.to_numeric(df["Quantidade faturada"], errors="coerce").fillna(0)
            df["Preço interno"] = pd.to_numeric(df["Preço interno"], errors="coerce").fillna(0)
            df["Valor líquido"] = df["Quantidade faturada"] * df["Preço interno"]
        return df
    except Exception as e:
        st.error(f"Erro ao processar planilha de vendas: {e}")
        return None

def processar_estoque(uploaded_file):
    if uploaded_file is None:
        return None
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        return df
    except Exception as e:
        st.error(f"Erro ao processar planilha de estoque: {e}")
        return None

# ==========================================
# BARRA LATERAL (Navegação de Perfis)
# ==========================================
with st.sidebar:
    # Exibe a logo oficial no topo da barra lateral
    try:
        st.image("logo_vonny.png", use_container_width=True)
    except:
        st.markdown("<h2 style='color: #E6007E; text-align: center; margin-bottom: 0px;'>VONNÝ</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 11px; color: #666; letter-spacing: 2px;'>COSMÉTICOS</p>", unsafe_allow_html=True)
    
    # Aviso condicional na barra lateral se for Staging
    if AMBIENTE_STAGING:
        st.info("🛠️ **Staging (Testes)**")
        
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
    
    tem_dados = (
        st.session_state.df_vendas_fixo is not None 
        or st.session_state.df_estoque_fixo is not None 
        or len(st.session_state.arquivos_admin_fixos) > 0
    )
    
    if tem_dados:
        st.success("✅ Dados salvos na sessão")
    else:
        st.warning("⚠️ Nenhum arquivo carregado")

# ==========================================
# AVISO CONDICIONAL NO TOPO (SÓ SE FOR STAGING)
# ==========================================
if AMBIENTE_STAGING:
    st.warning("⚠️ **ATENÇÃO: Você está acessando a versão de testes (Staging).** Alterações feitas aqui não afetam o painel oficial em produção.")

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
    st.markdown("Selecione ou arraste quantos arquivos precisar. Eles ficam salvos permanentemente na sessão até que você decida apagá-los pelo botão.")

    uploaded_files = st.file_uploader(
        "Upload de Arquivos Administrativos",
        type=["xlsx", "xlsm"],
        accept_multiple_files=True,
        key="multi_upload_admin"
    )

    # Processa e persiste imediatamente no dicionário de sessão
    if uploaded_files:
        for file in uploaded_files:
            if file.name not in st.session_state.arquivos_admin_fixos:
                df_proc = processar_vendas(file)
                if df_proc is not None:
                    st.session_state.arquivos_admin_fixos[file.name] = df_proc

    st.markdown("---")
    st.subheader("📋 Arquivos Atualmente Salvos na Sessão:")
    if len(st.session_state.arquivos_admin_fixos) > 0:
        for nome_arquivo, df_dados in st.session_state.arquivos_admin_fixos.items():
            qtd_linhas = len(df_dados) if df_dados is not None else 0
            st.markdown(f"- 📄 **{nome_arquivo}** _({qtd_linhas} linhas carregadas)_")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botão Apagar (Visão Admin)
        with st.expander("🗑️ Botão Apagar - Gerenciar Arquivos"):
            st.markdown("Selecione qual arquivo deseja remover da sessão:")
            arquivos_para_apagar = st.multiselect(
                "Escolha os arquivos para apagar:",
                options=list(st.session_state.arquivos_admin_fixos.keys()),
                key="select_apagar_admin"
            )
            
            col_ap1, col_ap2 = st.columns(2)
            with col_ap1:
                if st.button("🗑️ Apagar Selecionados", key="btn_apagar_selecionados_admin"):
                    if arquivos_para_apagar:
                        for arq in arquivos_para_apagar:
                            del st.session_state.arquivos_admin_fixos[arq]
                        st.success("✅ Arquivo(s) selecionado(s) apagado(s) com sucesso!")
                        st.rerun()
                    else:
                        st.warning("Selecione pelo menos um arquivo para apagar.")
            with col_ap2:
                if st.button("🗑️ Apagar Todos os Arquivos", key="btn_apagar_todos_admin"):
                    st.session_state.arquivos_admin_fixos = {}
                    st.success("✅ Todos os arquivos administrativos foram apagados!")
                    st.rerun()
    else:
        st.info("Nenhum arquivo enviado até o momento.")

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
        st.markdown("Faça o upload direto dos arquivos abaixo. Eles ficam salvos na sessão mesmo se você atualizar a página (F5):")

        # Seção de Upload para o Gerente
        with st.expander("📂 Fazer Upload das Planilhas (Estoque e Vendas)", expanded=True):
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                file_e = st.file_uploader("Planilha de Estoque (.xlsx / .xlsm)", type=["xlsx", "xlsm"], key="up_estoque_gerente")
                if file_e is not None:
                    df_e = processar_estoque(file_e)
                    if df_e is not None:
                        st.session_state.df_estoque_fixo = df_e
            with col_u2:
                file_v = st.file_uploader("Planilha de Vendas (.xlsx / .xlsm)", type=["xlsx", "xlsm"], key="up_vendas_gerente")
                if file_v is not None:
                    df_v = processar_vendas(file_v)
                    if df_v is not None:
                        st.session_state.df_vendas_fixo = df_v

        # Exibe status de carregado se já houver dados na sessão
        if st.session_state.df_estoque_fixo is not None:
            st.success("✅ Planilha de Estoque está ativa na sessão.")
        if st.session_state.df_vendas_fixo is not None:
            st.success("✅ Planilha de Vendas está ativa na sessão.")

        # Botão Apagar (Visão Gestão)
        tem_dados_gestao = (st.session_state.df_estoque_fixo is not None) or (st.session_state.df_vendas_fixo is not None)
        if tem_dados_gestao:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("🗑️ Botão Apagar - Gerenciar Planilhas de Gestão"):
                st.markdown("Selecione qual base de dados você deseja remover:")
                opcoes_apagar_gestao = []
                if st.session_state.df_estoque_fixo is not None:
                    opcoes_apagar_gestao.append("Planilha de Estoque")
                if st.session_state.df_vendas_fixo is not None:
                    opcoes_apagar_gestao.append("Planilha de Vendas")
                
                escolhas_apagar = st.multiselect("Selecione o que deseja apagar:", options=opcoes_apagar_gestao, key="select_apagar_gestao")
                
                if st.button("🗑️ Confirmar Exclusão Selecionada", key="btn_confirmar_apagar_gestao"):
                    if escolhas_apagar:
                        if "Planilha de Estoque" in escolhas_apagar:
                            st.session_state.df_estoque_fixo = None
                        if "Planilha de Vendas" in escolhas_apagar:
                            st.session_state.df_vendas_fixo = None
                        st.success("✅ Base(s) selecionada(s) apagada(s) com sucesso!")
                        st.rerun()
                    else:
                        st.warning("Selecione pelo menos uma opção para apagar.")

        st.markdown("<br>", unsafe_allow_html=True)
        col_g1, col_g2 = st.columns(2)

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
