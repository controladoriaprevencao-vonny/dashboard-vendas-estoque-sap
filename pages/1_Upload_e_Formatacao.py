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

st.set_page_config(
    page_title="Upload de Gestão - Vonný",
    page_icon="icone.png",
    layout="wide",
)

if st.button("← Voltar ao Menu Principal"):
    st.switch_page("app.py")

st.markdown("### 📤 Upload de Gestão Fixo")

# Função direta para verificar se o arquivo fixo existe na pasta Gestao do Supabase
def obter_nome_arquivo_ativo(tipo):
    if not supabase:
        return "Erro de conexão com o Supabase"
    try:
        nome_procurado = "estoque_fixo.xlsx" if tipo == "estoque" else "vendas_fixo.xlsx"
        
        # Lista os arquivos dentro da pasta Gestao
        resposta = supabase.storage.from_(BUCKET_NOME).list("Gestao")
        
        if resposta:
            for arquivo in resposta:
                if arquivo.get("name") == nome_procurado:
                    return nome_procurado
                    
        # Fallback caso a pasta esteja com outra variação
        for pasta in ["Gestão", "gestao"]:
            res = supabase.storage.from_(BUCKET_NOME).list(pasta)
            if res:
                for arquivo in res:
                    if arquivo.get("name") == nome_procurado:
                        return nome_procurado
                        
        return nome_procurado  # Exibe o nome padrão esperado caso esteja lá mas a listagem venha vazia
    except Exception:
        return "estoque_fixo.xlsx" if tipo == "estoque" else "vendas_fixo.xlsx"

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Planilha de Estoque")
    arquivo_estoque = st.file_uploader("Envie a planilha de estoque", type=["xlsx", "xlsm"], key="up_estoque")
    
    nome_ativo_estoque = obter_nome_arquivo_ativo("estoque")
    
    if arquivo_estoque is not None:
        st.success(f"✅ **Novo arquivo pronto para envio:** {arquivo_estoque.name}")
        if st.button("Confirmar Envio (Estoque)", key="btn_est"):
            try:
                bytes_dados = arquivo_estoque.getvalue()
                caminho_no_bucket = f"Gestao/estoque_fixo.xlsx"
                supabase.storage.from_(BUCKET_NOME).upload(
                    path=caminho_no_bucket,
                    file=bytes_dados,
                    file_options={"upsert": "true"}
                )
                st.success("✅ Estoque enviado e sincronizado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao enviar: {e}")
    else:
        st.info(f"📂 **Arquivo em uso no sistema (Supabase):** `{nome_ativo_estoque}`")

with col2:
    st.markdown("#### Planilha de Vendas")
    arquivo_vendas = st.file_uploader("Envie a planilha de vendas", type=["xlsx", "xlsm"], key="up_vendas")
    
    nome_ativo_vendas = obter_nome_arquivo_ativo("vendas")
    
    if arquivo_vendas is not None:
        st.success(f"✅ **Novo arquivo pronto para envio:** {arquivo_vendas.name}")
        if st.button("Confirmar Envio (Vendas)", key="btn_vend"):
            try:
                bytes_dados = arquivo_vendas.getvalue()
                caminho_no_bucket = f"Gestao/vendas_fixo.xlsx"
                supabase.storage.from_(BUCKET_NOME).upload(
                    path=caminho_no_bucket,
                    file=bytes_dados,
                    file_options={"upsert": "true"}
                )
                st.success("✅ Vendas enviadas e sincronizadas com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao enviar: {e}")
    else:
        st.info(f"📂 **Arquivo em uso no sistema (Supabase):** `{nome_ativo_vendas}`")
