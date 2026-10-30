import os
import io
import unicodedata
import pandas as pd
import streamlit as st
from supabase import create_client, Client

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

st.title("📤 Central de Upload e Formatação de Dados")
st.markdown("Faça o envio dos seus arquivos. O sistema remove acentos e espaços automaticamente antes de enviar para o Supabase.")

def limpar_nome_arquivo(nome):
    nfkd_form = unicodedata.normalize('NFKD', nome)
    texto_sem_acento = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return texto_sem_acento.replace(" ", "_")

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

def deletar_do_supabase(pasta, nomes_arquivos):
    if not supabase:
        return
    try:
        caminhos = [f"{pasta}/{arq}" for arq in nomes_arquivos]
        supabase.storage.from_(BUCKET_NOME).remove(caminhos)
        st.cache_data.clear()
    except Exception:
        pass

tab1, tab2 = st.tabs(["🛠️ Área Administrativa", "📦 Gestão (Estoque / Vendas)"])

with tab1:
    st.subheader("Upload Múltiplo Administrativo")
    uploaded_files = st.file_uploader("Arraste os arquivos administrativos", type=["xlsx", "xlsm"], accept_multiple_files=True, key="up_admin")
    if uploaded_files:
        with st.spinner("Enviando para o Supabase..."):
            for file in uploaded_files:
                sucesso, msg = upload_para_supabase("admin", file.name, file.getvalue())
                if sucesso:
                    st.success(f"✅ '{file.name}' enviado com sucesso!")
                else:
                    st.error(f"❌ Erro em '{file.name}': {msg}")
    
    st.markdown("---")
    st.subheader("Arquivos na Nuvem (Admin):")
    admin_list = listar_nomes_arquivos_supabase("admin")
    if admin_list:
        for f in admin_list:
            st.write(f"- {f}")
        if st.button("🗑️ Apagar Arquivos Selecionados (Admin)", key="del_adm"):
            apagar = st.multiselect("Escolha para apagar", options=admin_list, key="sel_del_adm")
            if apagar:
                deletar_do_supabase("admin", apagar)
                st.success("Apagado com sucesso!")
                st.rerun()
    else:
        st.info("Nenhum arquivo encontrado.")

with tab2:
    st.subheader("Upload de Gestão Fixo")
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        file_e = st.file_uploader("Planilha de Estoque", type=["xlsx", "xlsm"], key="up_est")
        if file_e is not None:
            sucesso, msg = upload_para_supabase("gestao", "estoque_fixo.xlsx", file_e.getvalue())
            if sucesso:
                st.success("✅ Estoque salvo na nuvem!")
            else:
                st.error(f"❌ Erro: {msg}")
    with col_u2:
        file_v = st.file_uploader("Planilha de Vendas", type=["xlsx", "xlsm"], key="up_ven")
        if file_v is not None:
            sucesso, msg = upload_para_supabase("gestao", "vendas_fixo.xlsx", file_v.getvalue())
            if sucesso:
                st.success("✅ Vendas salvas na nuvem!")
            else:
                st.error(f"❌ Erro: {msg}")
