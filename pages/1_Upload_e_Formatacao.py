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

# Função blindada para buscar os arquivos ativos na pasta de Gestão do Supabase
def obter_nome_arquivo_ativo(tipo):
    if not supabase:
        return "Erro de conexão com o Supabase"
    try:
        resposta = None
        # Varredura inteligente para lidar com variações de acentuação (Gestao / Gestão)
        raiz = supabase.storage.from_(BUCKET_NOME).list("")
        if raiz:
            for item in raiz:
                nome_item = item.get("name", "")
                if "gestao" in nome_item.lower():
                    resposta = supabase.storage.from_(BUCKET_NOME).list(nome_item)
                    break
        
        # Fallback direto se a raiz não retornar
        if not resposta:
            for p in ["Gestao", "Gestão"]:
                try:
                    resposta = supabase.storage.from_(BUCKET_NOME).list(p)
                    if resposta:
                        break
                except:
                    continue

        if not resposta:
            return "Nenhum arquivo encontrado"
            
        for arquivo in resposta:
            nome_arq = arquivo.get("name", "").lower()
            if tipo == "estoque" and ("estoque" in nome_arq or "02_nome_depositos" in nome_arq or "padrao" in nome_arq):
                return arquivo.get("name")
            elif tipo == "vendas" and ("venda" in nome_arq or "faturado" in nome_arq or "produt" in nome_arq):
                return arquivo.get("name")
                
        if len(resposta) > 0:
            for arq in resposta:
                nome_arq = arq.get("name", "")
                if nome_arq and nome_arq != ".emptyFolderPlaceholder":
                    return nome_arq
                    
        return "Nenhum arquivo ativo"
    except Exception as e:
        return "Arquivo ativo no Supabase"

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
                caminho_no_bucket = f"Gestao/{arquivo_estoque.name}"
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
                caminho_no_bucket = f"Gestao/{arquivo_vendas.name}"
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
