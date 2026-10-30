import os
import io
import pandas as pd
import streamlit as st
from supabase import create_client, Client

# ==========================================
# CONFIGURAÇÃO DE AMBIENTE E SUPABASE
# ==========================================
AMBIENTE_STAGING = True

# Credenciais do Supabase fornecidas
SUPABASE_URL = "https://cfxrcnnuupabepbqascx.supabase.co"
SUPABASE_KEY = "sb_publishable_-Hoz_n3NdCndYmNETF4sDQ_9Bzphw5Q"
BUCKET_NOME = "dados-vonny"

@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        return None

supabase: Client = init_supabase()

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

# Inicializa o estado da sessão para navegação
if "perfil_atual" not in st.session_state:
    st.session_state.perfil_atual = "Home"

if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "Home"

# ==========================================
# FUNÇÕES DE PROCESSAMENTO E SUPABASE STORAGE
# ==========================================
def processar_vendas_bytes(file_bytes):
    if file_bytes is None:
        return None
    try:
        df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
        if "Quantidade faturada" in df.columns and "Preço interno" in df.columns:
            df["Quantidade faturada"] = pd.to_numeric(df["Quantidade faturada"], errors="coerce").fillna(0)
            df["Preço interno"] = pd.to_numeric(df["Preço interno"], errors="coerce").fillna(0)
            df["Valor líquido"] = df["Quantidade faturada"] * df["Preço interno"]
        return df
    except Exception as e:
        return None

def processar_estoque_bytes(file_bytes):
    if file_bytes is None:
        return None
    try:
        df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
        return df
    except Exception as e:
        return None

def listar_arquivos_supabase(pasta):
    if not supabase:
        return {}
    arquivos_dict = {}
    try:
        response = supabase.storage.from_(BUCKET_NOME).list(pasta)
        if response:
            for item in response:
                nome_arq = item["name"]
                if nome_arq and nome_arq != ".emptyFolderPlaceholder":
                    caminho_completo = f"{pasta}/{nome_arq}"
                    file_res = supabase.storage.from_(BUCKET_NOME).download(caminho_completo)
                    if file_res:
                        if pasta == "admin":
                            arquivos_dict[nome_arq] = processar_vendas_bytes(file_res)
                        else:
                            if "estoque" in nome_arq:
                                arquivos_dict["estoque"] = processar_estoque_bytes(file_res)
                            elif "vendas" in nome_arq:
                                arquivos_dict["vendas"] = processar_vendas_bytes(file_res)
    except Exception as e:
        pass
    return arquivos_dict

def upload_para_supabase(pasta, nome_arquivo, file_buffer):
    if not supabase:
        return False
    try:
        caminho = f"{pasta}/{nome_arquivo}"
        # Remove se já existir para atualizar
        try:
            supabase.storage.from_(BUCKET_NOME).remove([caminho])
        except:
            pass
        
        supabase.storage.from_(BUCKET_NOME).upload(
            path=caminho,
            file=file_buffer,
            file_options={"content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
        )
        return True
    except Exception as e:
        st.error(f"Erro ao enviar para o Supabase: {e}")
        return False

def deletar_do_supabase(pasta, nomes_arquivos):
    if not supabase:
        return
    try:
         caminhos = [f"{pasta}/{arq}" for arq in nomes_arquivos]
         supabase.storage.from_(BUCKET_NOME).remove(caminhos)
    except Exception as e:
        pass

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
    
    admin_remotos = listar_arquivos_supabase("admin")
    gestao_remotos = listar_arquivos_supabase("gestao")
    
    tem_dados = (len(admin_remotos) > 0) or ("estoque" in gestao_remotos) or ("vendas" in gestao_remotos)
    
    if tem_dados:
        st.success("✅ Dados salvos no Supabase")
    else:
        st.warning("⚠️ Nenhum arquivo na nuvem")

# ==========================================
# AVISO CONDICIONAL NO TOPO
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
    st.markdown("Selecione ou arraste quantos arquivos precisar. Eles são salvos com segurança no Supabase e resistem a qualquer atualização de página (F5).")

    uploaded_files = st.file_uploader(
        "Upload de Arquivos Administrativos",
        type=["xlsx", "xlsm"],
        accept_multiple_files=True,
        key="multi_upload_admin"
    )

    if uploaded_files:
        with st.spinner("Enviando arquivos para o Supabase..."):
            for file in uploaded_files:
                upload_para_supabase("admin", file.name, file.getvalue())
        st.success("🎉 Arquivos enviados e salvos na nuvem com sucesso!")
        st.rerun()

    st.markdown("---")
    st.subheader("📋 Arquivos Atualmente Salvos no Supabase:")
    admin_remotos = listar_arquivos_supabase("admin")
    
    if len(admin_remotos) > 0:
        for nome_arquivo, df_dados in admin_remotos.items():
            qtd_linhas = len(df_dados) if df_dados is not None else 0
            st.markdown(f"- 📄 **{nome_arquivo}** _({qtd_linhas} linhas carregadas)_")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.expander("🗑️ Botão Apagar - Gerenciar Arquivos"):
            st.markdown("Selecione qual arquivo deseja remover permanentemente do Supabase:")
            arquivos_para_apagar = st.multiselect(
                "Escolha os arquivos para apagar:",
                options=list(admin_remotos.keys()),
                key="select_apagar_admin"
            )
            
            col_ap1, col_ap2 = st.columns(2)
            with col_ap1:
                if st.button("🗑️ Apagar Selecionados", key="btn_apagar_selecionados_admin"):
                    if arquivos_para_apagar:
                        deletar_do_supabase("admin", arquivos_para_apagar)
                        st.success("✅ Arquivo(s) selecionado(s) apagado(s) com sucesso!")
                        st.rerun()
                    else:
                        st.warning("Selecione pelo menos um arquivo para apagar.")
            with col_ap2:
                if st.button("🗑️ Apagar Todos os Arquivos", key="btn_apagar_todos_admin"):
                    deletar_do_supabase("admin", list(admin_remotos.keys()))
                    st.success("✅ Todos os arquivos administrativos foram apagados!")
                    st.rerun()
    else:
        st.info("Nenhum arquivo no Supabase no momento.")

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

    gestao_remotos = listar_arquivos_supabase("gestao")
    df_estoque_remoto = gestao_remotos.get("estoque")
    df_vendas_remoto = gestao_remotos.get("vendas")

    if st.session_state.pagina_atual == "Home":
        st.title("📦 Visão Executiva - Gestão de Produtos")
        st.markdown("Faça o upload direto dos arquivos abaixo. Eles ficam salvos no Supabase e não somem ao atualizar a página (F5):")

        with st.expander("📂 Fazer Upload das Planilhas (Estoque e Vendas)", expanded=True):
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                file_e = st.file_uploader("Planilha de Estoque (.xlsx / .xlsm)", type=["xlsx", "xlsm"], key="up_estoque_gerente")
                if file_e is not None:
                    with st.spinner("Enviando estoque para o Supabase..."):
                        upload_para_supabase("gestao", "estoque_fixo.xlsx", file_e.getvalue())
                    st.success("✅ Estoque salvo na nuvem com sucesso!")
                    st.rerun()
            with col_u2:
                file_v = st.file_uploader("Planilha de Vendas (.xlsx / .xlsm)", type=["xlsx", "xlsm"], key="up_vendas_gerente")
                if file_v is not None:
                    with st.spinner("Enviando vendas para o Supabase..."):
                        upload_para_supabase("gestao", "vendas_fixo.xlsx", file_v.getvalue())
                    st.success("✅ Vendas salvas na nuvem com sucesso!")
                    st.rerun()

        if df_estoque_remoto is not None:
            st.success("✅ Planilha de Estoque está ativa e hospedada no Supabase.")
        if df_vendas_remoto is not None:
            st.success("✅ Planilha de Vendas está ativa e hospedada no Supabase.")

        tem_dados_gestao = (df_estoque_remoto is not None) or (df_vendas_remoto is not None)
        if tem_dados_gestao:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("🗑️ Botão Apagar - Gerenciar Planilhas de Gestão"):
                st.markdown("Selecione qual base de dados você deseja remover do Supabase:")
                opcoes_apagar_gestao = []
                if df_estoque_remoto is not None:
                    opcoes_apagar_gestao.append("Planilha de Estoque")
                if df_vendas_remoto is not None:
                    opcoes_apagar_gestao.append("Planilha de Vendas")
                
                escolhas_apagar = st.multiselect("Selecione o que deseja apagar:", options=opcoes_apagar_gestao, key="select_apagar_gestao")
                
                if st.button("🗑️ Confirmar Exclusão Selecionada", key="btn_confirmar_apagar_gestao"):
                    if escolhas_apagar:
                        arquivos_para_remover = []
                        if "Planilha de Estoque" in escolhas_apagar:
                            arquivos_para_remover.append("estoque_fixo.xlsx")
                        if "Planilha de Vendas" in escolhas_apagar:
                            arquivos_para_remover.append("vendas_fixo.xlsx")
                        
                        deletar_do_supabase("gestao", arquivos_para_remover)
                        st.success("✅ Base(s) selecionada(s) apagada(s) do Supabase!")
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
        if df_estoque_remoto is not None:
            st.dataframe(df_estoque_remoto, use_container_width=True)
        else:
            st.warning("⚠️ Nenhuma planilha de Estoque no Supabase. Utilize a seção de upload na página inicial da Gestão.")

    elif st.session_state.pagina_atual == "Vendas":
        st.title("📈 Relatório Executivo de Vendas")
        if df_vendas_remoto is not None:
            st.dataframe(df_vendas_remoto, use_container_width=True)
        else:
            st.warning("⚠️ Nenhuma planilha de Vendas no Supabase. Utilize a seção de upload na página inicial da Gestão.")
