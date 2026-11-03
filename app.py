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

# Inicializa o estado da sessão para navegação
if "perfil_atual" not in st.session_state:
    st.session_state.perfil_atual = "Home"

if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "Home"

# Função para verificar o status geral das pastas no Supabase
def verificar_status_supabase():
    if not supabase:
        return False
    try:
        resp_gestao = supabase.storage.from_(BUCKET_NOME).list("Gestao")
        resp_admin = supabase.storage.from_(BUCKET_NOME).list("Administracao")
        return (resp_gestao is not None and len(resp_gestao) > 0) or (resp_admin is not None and len(resp_admin) > 0)
    except Exception:
        return False

# ==========================================
# BARRA LATERAL (Navegação de Perfis)
# ==========================================
with st.sidebar:
    try:
        st.image("logo_vonny.png", use_container_width=True)
    except:
        st.markdown("<h2 style='color: #E6007E; text-align: center; margin-bottom: 0px;'>VONNÝ</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 11px; color: #666; letter-spacing: 2px;'>COSMÉTICOS</p>", unsafe_allow_html=True)
    
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
    if verificar_status_supabase():
        st.success("✅ Sincronizado com Supabase")
    else:
        st.warning("⚠️ Nenhum arquivo no Supabase")

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
    st.markdown("Bem-vindo ao sistema de relatórios gerenciais integrados ao SAP e hospedados no Supabase. Escolha abaixo qual visão deseja acessar:")
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🛠️ Visão Administrativa")
        st.markdown("Área restrita para visualização e upload de planilhas na pasta **Administração**.")
        if st.button("Acessar Administrativo ➔", key="btn_admin"):
            st.session_state.perfil_atual = "Admin"
            st.rerun()
            
    with col2:
        st.markdown("### 📦 Visão Gerentes de Produto")
        st.markdown("Área executiva para planilhas da pasta **Gestão** (Estoque / Vendas) e análises interativas.")
        if st.button("Acessar Gestão ➔", key="btn_gerente"):
            st.session_state.perfil_atual = "Gerente"
            st.session_state.pagina_atual = "Home"
            st.rerun()

# ==========================================
# 2. VISÃO ADMINISTRATIVA (PASTA ADMINISTRAÇÃO)
# ==========================================
elif st.session_state.perfil_atual == "Admin":
    st.title("🛠️ Painel Administrativo - Arquivos de Parâmetros")
    st.markdown("Estes são os arquivos cadastrais e de parametrização armazenados na pasta **Administração** do Supabase[cite: 10].")

    # Upload opcional para adicionar novos arquivos na pasta Administração
    uploaded_files_admin = st.file_uploader(
        "Enviar novos arquivos para Administração",
        type=["xlsx", "xlsm", "xlsb"],
        accept_multiple_files=True,
        key="multi_upload_admin"
    )

    if uploaded_files_admin and supabase:
        for file in uploaded_files_admin:
            try:
                bytes_dados = file.getvalue()
                caminho_no_bucket = f"Administracao/{file.name}"
                supabase.storage.from_(BUCKET_NOME).upload(
                    path=caminho_no_bucket,
                    file=bytes_dados,
                    file_options={"upsert": "true"}
                )
                st.success(f"🎉 Arquivo **{file.name}** enviado para a pasta Administração com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao enviar {file.name}: {e}")

    st.markdown("---")
    st.subheader("📋 Arquivos Atualmente na Pasta 'Administração' (Supabase):")
    
    if supabase:
        try:
            # Lista especificamente os arquivos da pasta Administração
            resposta_admin = supabase.storage.from_(BUCKET_NOME).list("Administracao")
            
            if resposta_admin:
                for arq in resposta_admin:
                    nome_arquivo = arq.get('name')
                    if nome_arquivo and nome_arquivo != ".emptyFolderPlaceholder":
                        st.markdown(f"- 📄 **{nome_arquivo}**")
            else:
                st.info("Nenhum arquivo encontrado na pasta Administração.")
        except Exception as e:
            st.error(f"Erro ao conectar com o Supabase para listar os arquivos: {e}")
    else:
        st.error("Erro de conexão com o cliente Supabase.")

# ==========================================
# 3. VISÃO DOS GERENTES DE PRODUTO (PASTA GESTAO)
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
        st.markdown("Faça o upload direto dos arquivos da pasta **Gestão** (`estoque_fixo.xlsx` e `vendas_fixo.xlsx`)[cite: 11] ou acesse os módulos abaixo:")

        with st.expander("📂 Fazer Upload Direto para a Pasta Gestão (Supabase)", expanded=True):
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                file_e = st.file_uploader("Planilha de Estoque (`estoque_fixo.xlsx`)", type=["xlsx", "xlsm"], key="up_estoque_gerente")
                if file_e is not None and supabase:
                    try:
                        supabase.storage.from_(BUCKET_NOME).upload(
                            path="Gestao/estoque_fixo.xlsx",
                            file=file_e.getvalue(),
                            file_options={"upsert": "true"}
                        )
                        st.success("✅ Estoque enviado e sincronizado na pasta Gestao!")
                    except Exception as e:
                        st.error(f"Erro: {e}")
            with col_u2:
                file_v = st.file_uploader("Planilha de Vendas (`vendas_fixo.xlsx`)", type=["xlsx", "xlsm"], key="up_vendas_gerente")
                if file_v is not None and supabase:
                    try:
                        supabase.storage.from_(BUCKET_NOME).upload(
                            path="Gestao/vendas_fixo.xlsx",
                            file=file_v.getvalue(),
                            file_options={"upsert": "true"}
                        )
                        st.success("✅ Vendas enviadas e sincronizadas na pasta Gestao!")
                    except Exception as e:
                        st.error(f"Erro: {e}")

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
        st.info("💡 Dica: Acesse a página dedicada de Estoque pelo menu lateral para visualizar os filtros avançados em cascata e ordenação por saldo.")

    elif st.session_state.pagina_atual == "Vendas":
        st.title("📈 Relatório Executivo de Vendas")
        st.info("💡 Dica: Acesse a página dedicada de Vendas pelo menu lateral para visualizar os filtros globais e a análise inteligente de devolução.")
