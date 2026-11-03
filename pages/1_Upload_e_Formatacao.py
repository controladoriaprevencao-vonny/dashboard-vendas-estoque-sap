import io
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

st.title("📤 Central de Upload e Formatação")
st.markdown("Faça o upload dos arquivos oficiais. Eles serão salvos no Supabase e sincronizados com todas as páginas e ambientes (`main` e `staging`).")

# Exemplo de upload para o arquivo de vendas
arquivo_upload = st.file_uploader("Enviar Planilha de Vendas (vendas_fixo.xlsx)", type=["xlsx", "xlsm"])

if arquivo_upload is not None:
    if st.button("Enviar para o Supabase"):
        if not supabase:
            st.error("Erro ao conectar com o Supabase.")
        else:
            try:
                # O arquivo é lido em bytes e enviado para a pasta 'Gestao/' no bucket
                bytes_dados = arquivo_upload.getvalue()
                caminho_no_bucket = "Gestao/vendas_fixo.xlsx"
                
                # Realiza o upload (fazendo upsert para substituir se já existir)
                supabase.storage.from_(BUCKET_NOME).upload(
                    path=caminho_no_bucket,
                    file=bytes_dados,
                    file_options={"upsert": "true"}
                )
                st.success("✅ Arquivo enviado e sincronizado com sucesso no Supabase!")
            except Exception as e:
                st.error(f"Erro ao enviar o arquivo: {e}")
