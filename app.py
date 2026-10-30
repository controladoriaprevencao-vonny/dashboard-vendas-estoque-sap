import os
import io
import unicodedata
import pandas as pd
import streamlit as st
from supabase import create_client, Client

# ==========================================
# CONFIGURAÇÃO DE AMBIENTE E SUPABASE
# ==========================================
AMBIENTE_STAGING = True

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

st.set_page_config(
    page_title="Dashboard Executivo - Vonný" + (" [STAGING]" if AMBIENTE_STAGING else ""),
    page_icon="icone.png",
    layout="wide",
)

# Estilização Adaptável (Preserva Temas Claro e Escuro)
st.markdown(
    """
    <style>
    header[data-testid="stHeader"] { background-color: #E6007E !important; }
    section[data-testid="stSidebar"] { border-right: 1px solid #F5CCD8; }
    h1, h2, h3 { color: #C5006B !important; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 700; }
    .stButton>button {
        width: 100%; background-color: #555555 !important; color: #FFFFFF !important;
        font-weight: bold !important; border-radius: 6px; height: 48px; border: none; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #333333 !important; color: #FFFFFF !important; }
    </style>
""",
    unsafe_allow_html=True,
)

if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "Home"

# ==========================================
# FUNÇÕES DE TRATAMENTO E SUPABASE
# ==========================================
def limpar_nome_arquivo(nome):
    nfkd_form = unicodedata.normalize('NFKD', nome)
    texto_sem_acento = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return texto_sem_acento.replace(" ", "_")

def processar_vendas_consolidado(file_bytes):
    if file_bytes is None:
        return None
    try:
        df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
        
        if "Quantidade faturada" in df.columns:
            df["Quantidade faturada"] = pd.to_numeric(df["Quantidade faturada"], errors="coerce").fillna(0)
        if "Preço interno" in df.columns:
            df["Preço interno"] = pd.to_numeric(df["Preço interno"], errors="coerce").fillna(0)
            
        if "Quantidade faturada" in df.columns and "Preço interno" in df.columns:
            df["Valor líquido"] = df["Quantidade faturada"] * df["Preço interno"]
        
        if "Divisão" in df.columns and "Material" in df.columns:
            colunas_agrupamento = ["Divisão", "Material"]
            colunas_soma = ["Quantidade faturada"]
            if "Valor líquido" in df.columns:
                colunas_soma.append("Valor líquido")
            if "Subtotal 1" in df.columns:
                df["Subtotal 1"] = pd.to_numeric(df["Subtotal 1"], errors="coerce").fillna(0)
                colunas_soma.append("Subtotal 1")

            agg_dict = {col: "sum" for col in colunas_soma}
            
            if "Denominação de item" in df.columns:
                agg_dict["Denominação de item"] = "first"
            if "Grupo de mercadorias" in df.columns:
                agg_dict["Grupo de mercadorias"] = "first"
            if "Data fixação preço" in df.columns:
                agg_dict["Data fixação preço"] = "first"

            df = df.groupby(colunas_agrupamento, as_index=False).agg(agg_dict)
            
        return df
    except Exception:
        return None

@st.cache_data(ttl=300)
def listar_nomes_arquivos_supabase(pasta):
    if not supabase:
        return []
    try:
        response = supabase.storage.from_(BUCKET_NOME).list(pasta)
        if response:
            return [item.get("name") for item in response if item.get("name") and item.get("name") != ".emptyFolderPlaceholder"]
    except Exception:
        pass
    return []

@st.cache_data(ttl=300)
def baixar_arquivo_supabase(pasta, nome_arquivo):
    if not supabase:
        return None
    try:
        caminho = f"{pasta}/{nome_arquivo}"
        file_res = supabase.storage.from_(BUCKET_NOME).download(caminho)
        if file_res:
            if "vendas" in nome_arquivo.lower() or pasta == "admin":
                return processar_vendas_consolidado(file_res)
            else:
                return pd.read_excel(io.BytesIO(file_res), engine="openpyxl")
    except Exception:
        return None

def upload_para_supabase(pasta, nome_arquivo, file_buffer):
    if not supabase:
        return False, "Cliente Supabase não inicializado."
    try:
        nome_tratado = limpar_nome_arquivo(nome_arquivo)
        caminho = f"{pasta}/{nome_tratado}"
        try:
            supabase.storage.from_(BUCKET_NOME).remove([caminho])
        except Exception:
            pass
        
        supabase.storage.from_(BUCKET_NOME).upload(
            path=caminho,
            file=file_buffer,
            file_options={"content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "upsert": "true"}
        )
        st.cache_data.clear()
        return True, ""
    except Exception as e:
        return False, str(e)

def deletar_do_supabase(pasta, nomes_arquivos):
    if not supabase:
        return
    try:
        caminhos = [f"{pasta}/{arq}" for arq in nomes_arquivos]
        supabase.storage.from_(BUCKET_NOME).remove(caminhos)
        st.cache_data.clear()
    except Exception:
        pass

# ==========================================
# BARRA LATERAL (Navegação Global)
# ==========================================
with st.sidebar:
    try:
        st.image("logo_vonny.png", use_container_width=True)
    except Exception:
        st.markdown("<h2 style='color: #E6007E; text-align: center; margin-bottom: 0px;'>VONNÝ</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 11px; color: #666; letter-spacing: 2px;'>COSMÉTICOS</p>", unsafe_allow_html=True)
    
    if AMBIENTE_STAGING:
        st.info("🛠️ **Staging (Testes)**")
        
    st.markdown("---")
    st.markdown("### 🧭 Menu de Navegação")
    
    if st.button("🏠 Início / Home", key="nav_home"):
        st.session_state.pagina_atual = "Home"
        st.rerun()
        
    st.markdown("---")
    st.markdown("### 📤 Central de Uploads")
    if st.button("🛠️ Upload Administrativo", key="nav_up_admin"):
        st.session_state.pagina_atual = "Upload_Admin"
        st.rerun()
    if st.button("📦 Upload de Gestão (Estoque/Vendas)", key="nav_up_gestao"):
        st.session_state.pagina_atual = "Upload_Gestao"
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Dashboards e Relatórios")
    if st.button("📋 Relatório Consolidado de Estoque", key="nav_rel_estoque"):
        st.session_state.pagina_atual = "Relatorio_Estoque"
        st.rerun()
    if st.button("📈 Relatório Executivo de Vendas", key="nav_rel_vendas"):
        st.session_state.pagina_atual = "Relatorio_Vendas"
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Status")
    st.success("✅ Conectado ao Supabase")

if AMBIENTE_STAGING:
    st.warning("⚠️ **ATENÇÃO: Você está acessando a versão de testes (Staging).**")

# ==========================================
# 1. PÁGINA INICIAL (HOME)
# ==========================================
if st.session_state.pagina_atual == "Home":
    st.title("📊 Dashboard Executivo - Vonný")
    st.markdown("Bem-vindo ao sistema de relatórios gerenciais integrados ao SAP. Utilize os botões abaixo para acessar rapidamente a área desejada:")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Áreas de Upload (Envio de Dados)")
        st.markdown("Faça o envio e gerenciamento de arquivos em nuvem de forma separada.")
        if st.button("Ir para Upload Administrativo ➔", key="btn_h_up_admin"):
            st.session_state.pagina_atual = "Upload_Admin"
            st.rerun()
        if st.button("Ir para Upload de Gestão ➔", key="btn_h_up_gestao"):
            st.session_state.pagina_atual = "Upload_Gestao"
            st.rerun()

    with col2:
        st.markdown("### 📊 Áreas de Visualização (Dashboards)")
        st.markdown("Consulte relatórios consolidados, utilize filtros e analise os dados.")
        if st.button("Ver Relatório de Estoques ➔", key="btn_h_rel_est"):
            st.session_state.pagina_atual = "Relatorio_Estoque"
            st.rerun()
        if st.button("Ver Relatório de Vendas ➔", key="btn_h_rel_ven"):
            st.session_state.pagina_atual = "Relatorio_Vendas"
            st.rerun()

# ==========================================
# 2. UPLOAD ADMINISTRATIVO (Exclusivo para envio)
# ==========================================
elif st.session_state.pagina_atual == "Upload_Admin":
    st.title("🛠️ Central de Upload - Administrativo")
    st.markdown("Esta área é dedicada exclusivamente ao envio e remoção de arquivos administrativos.")

    uploaded_files = st.file_uploader(
        "Arraste ou selecione os arquivos administrativos",
        type=["xlsx", "xlsm"],
        accept_multiple_files=True,
        key="multi_upload_admin"
    )

    if uploaded_files:
        with st.spinner("Enviando arquivos automaticamente para o Supabase..."):
            erros_encontrados = []
            for file in uploaded_files:
                sucesso, erro_msg = upload_para_supabase("admin", file.name, file.getvalue())
                if not sucesso:
                    erros_encontrados.append((file.name, erro_msg))
            
            if erros_encontrados:
                for nome_arq, msg in erros_encontrados:
                    st.error(f"❌ Erro ao enviar '{nome_arq}': {msg}")
            else:
                st.success("🎉 Arquivos enviados e salvos na nuvem com sucesso!")
                st.rerun()

    st.markdown("---")
    st.subheader("📋 Arquivos Atualmente Armazenados na Nuvem:")
    
    lista_arquivos = listar_nomes_arquivos_supabase("admin")
    
    if len(lista_arquivos) > 0:
        for nome_arquivo in lista_arquivos:
            st.markdown(f"- 📄 **{nome_arquivo}**")
        
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🗑️ Gerenciar / Apagar Arquivos"):
            arquivos_para_apagar = st.multiselect(
                "Escolha os arquivos que deseja excluir permanentemente:",
                options=lista_arquivos,
                key="select_apagar_admin"
            )
            col_ap1, col_ap2 = st.columns(2)
            with col_ap1:
                if st.button("🗑️ Apagar Selecionados", key="btn_apagar_selecionados_admin"):
                    if arquivos_para_apagar:
                        deletar_do_supabase("admin", arquivos_para_apagar)
                        st.success("✅ Arquivo(s) apagado(s)!")
                        st.rerun()
                    else:
                        st.warning("Selecione pelo menos um arquivo.")
            with col_ap2:
                if st.button("🗑️ Apagar Todos", key="btn_apagar_todos_admin"):
                    deletar_do_supabase("admin", lista_arquivos)
                    st.success("✅ Todos apagados!")
                    st.rerun()
    else:
        st.info("Nenhum arquivo administrativo na nuvem no momento.")

# ==========================================
# 3. UPLOAD DE GESTÃO (Exclusivo para envio)
# ==========================================
elif st.session_state.pagina_atual == "Upload_Gestao":
    st.title("📦 Central de Upload - Gestão (Estoque / Vendas)")
    st.markdown("Faça o envio individual das planilhas de controle gerencial sem misturar com as telas de relatórios.")

    with st.expander("📂 Painel de Envio de Planilhas Fiscais/Gerenciais", expanded=True):
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            st.markdown("### Planilha de Estoque")
            file_e = st.file_uploader("Enviar arquivo de Estoque (.xlsx / .xlsm)", type=["xlsx", "xlsm"], key="up_estoque_gerente")
            if file_e is not None:
                with st.spinner("Enviando estoque automaticamente..."):
                    sucesso, erro_msg = upload_para_supabase("gestao", "estoque_fixo.xlsx", file_e.getvalue())
                    if sucesso:
                        st.success("✅ Estoque salvo na nuvem!")
                        st.rerun()
                    else:
                        st.error(f"❌ Erro: {erro_msg}")
        with col_u2:
            st.markdown("### Planilha de Vendas")
            file_v = st.file_uploader("Enviar arquivo de Vendas (.xlsx / .xlsm)", type=["xlsx", "xlsm"], key="up_vendas_gerente")
            if file_v is not None:
                with st.spinner("Enviando vendas automaticamente..."):
                    sucesso, erro_msg = upload_para_supabase("gestao", "vendas_fixo.xlsx", file_v.getvalue())
                    if sucesso:
                        st.success("✅ Vendas salvas na nuvem!")
                        st.rerun()
                    else:
                        st.error(f"❌ Erro: {erro_msg}")

    st.markdown("---")
    st.subheader("📋 Status das Bases de Gestão na Nuvem:")
    lista_gestao = listar_nomes_arquivos_supabase("gestao")
    
    tem_estoque = "estoque_fixo.xlsx" in lista_gestao
    tem_vendas = "vendas_fixo.xlsx" in lista_gestao

    if tem_estoque:
        st.success("✅ Planilha de Estoque está ativa no Supabase.")
    else:
        st.warning("⚠️ Nenhuma planilha de Estoque enviada.")

    if tem_vendas:
        st.success("✅ Planilha de Vendas está ativa no Supabase.")
    else:
        st.warning("⚠️ Nenhuma planilha de Vendas enviada.")

    if len(lista_gestao) > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🗑️ Gerenciar / Apagar Planilhas de Gestão"):
            escolhas_apagar = st.multiselect("Selecione o que deseja apagar:", options=lista_gestao, key="select_apagar_gestao")
            if st.button("🗑️ Confirmar Exclusão de Gestão", key="btn_confirmar_apagar_gestao"):
                if escolhas_apagar:
                    deletar_do_supabase("gestao", escolhas_apagar)
                    st.success("✅ Base(s) apagada(s)!")
                    st.rerun()

# ==========================================
# 4. RELATÓRIO DE ESTOQUE (Exclusivo para Visualização e Filtros)
# ==========================================
elif st.session_state.pagina_atual == "Relatorio_Estoque":
    st.title("📋 Relatório Consolidado de Estoque")
    st.markdown("Área limpa dedicada exclusivamente à análise e filtros do estoque atual.")
    
    lista_gestao = listar_nomes_arquivos_supabase("gestao")
    if "estoque_fixo.xlsx" in lista_gestao:
        with st.spinner("Baixando e processando estoque da nuvem..."):
            df_estoque = baixar_arquivo_supabase("gestao", "estoque_fixo.xlsx")
        if df_estoque is not None:
            st.markdown("### 🔍 Filtros Interativos")
            f_col1, f_col2 = st.columns(2)
            
            df_filtrado_est = df_estoque.copy()
            
            if "Divisão" in df_estoque.columns:
                lojas_est = sorted(df_estoque["Divisão"].dropna().astype(str).unique())
                with f_col1:
                    loja_escolhida_est = st.multiselect("Filtrar por Loja (Divisão)", options=lojas_est, key="filtro_loja_est")
                if loja_escolhida_est:
                    df_filtrado_est = df_filtrado_est[df_filtrado_est["Divisão"].astype(str).isin(loja_escolhida_est)]
            
            if "Material" in df_estoque.columns:
                materiais_est = sorted(df_estoque["Material"].dropna().astype(str).unique())
                with f_col2:
                    material_escolhido_est = st.multiselect("Filtrar por Material", options=materiais_est, key="filtro_mat_est")
                if material_escolhido_est:
                    df_filtrado_est = df_filtrado_est[df_filtrado_est["Material"].astype(str).isin(material_escolhido_est)]

            st.markdown(f"**Total de linhas exibidas:** {len(df_filtrado_est)}")
            st.markdown("<br>", unsafe_allow_html=True)
            st.dataframe(df_filtrado_est, use_container_width=True)
        else:
            st.error("Erro ao ler o arquivo de estoque.")
    else:
        st.warning("⚠️ Nenhuma planilha de Estoque encontrada no Supabase. Vá até a **Central de Upload de Gestão** para enviar uma.")

# ==========================================
# 5. RELATÓRIO DE VENDAS (Exclusivo para Visualização, Consolidação e Filtros)
# ==========================================
elif st.session_state.pagina_atual == "Relatorio_Vendas":
    st.title("📈 Relatório Executivo de Vendas")
    st.markdown("Visualização consolidada de vendas por Loja e Material, equipada com filtros avançados e métricas financeiras.")
    
    lista_gestao = listar_nomes_arquivos_supabase("gestao")
    if "vendas_fixo.xlsx" in lista_gestao:
        with st.spinner("Baixando e processando vendas da nuvem..."):
            df_vendas = baixar_arquivo_supabase("gestao", "vendas_fixo.xlsx")
        if df_vendas is not None:
            st.markdown("### 🔍 Filtros Interativos")
            f1, f2, f3 = st.columns(3)
            
            df_filtrado = df_vendas.copy()
            
            if "Divisão" in df_vendas.columns:
                lojas = sorted(df_vendas["Divisão"].dropna().astype(str).unique())
                with f1:
                    loja_selecionada = st.multiselect("Filtrar por Loja (Divisão)", options=lojas, key="filtro_loja_vendas")
                if loja_selecionada:
                    df_filtrado = df_filtrado[df_filtrado["Divisão"].astype(str).isin(loja_selecionada)]
            
            if "Material" in df_vendas.columns:
                materiais = sorted(df_vendas["Material"].dropna().astype(str).unique())
                with f2:
                    material_selecionado = st.multiselect("Filtrar por Material", options=materiais, key="filtro_material_vendas")
                if material_selecionado:
                    df_filtrado = df_filtrado[df_filtrado["Material"].astype(str).isin(material_selecionado)]

            if "Grupo de mercadorias" in df_vendas.columns:
                grupos = sorted(df_vendas["Grupo de mercadorias"].dropna().astype(str).unique())
                with f3:
                    grupo_selecionado = st.multiselect("Filtrar por Grupo de Mercadorias", options=grupos, key="filtro_grupo_vendas")
                if grupo_selecionado:
                    df_filtrado = df_filtrado[df_filtrado["Grupo de mercadorias"].astype(str).isin(grupo_selecionado)]

            st.markdown("<br>", unsafe_allow_html=True)
            m1, m2 = st.columns(2)
            with m1:
                total_qtd = df_filtrado["Quantidade faturada"].sum() if "Quantidade faturada" in df_filtrado.columns else 0
                st.metric("📦 Quantidade Total Faturada (Filtrado)", f"{total_qtd:,.0f}")
            with m2:
                total_val = df_filtrado["Valor líquido"].sum() if "Valor líquido" in df_filtrado.columns else 0
                st.metric("💰 Valor Líquido Total (Filtrado)", f"R$ {total_val:,.2f}")

            st.markdown("<br>", unsafe_allow_html=True)
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.error("Erro ao ler o arquivo de vendas.")
    else:
        st.warning("⚠️ Nenhuma planilha de Vendas encontrada no Supabase. Vá até a **Central de Upload de Gestão** para enviar uma.")
