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

st.markdown("### 📤 Upload e Gerenciamento de Gestão")

def verificar_arquivo_existe(tipo):
    if not supabase:
        return False
    try:
        nome_procurado = "estoque_fixo.xlsx" if tipo == "estoque" else "vendas_fixo.xlsx"
        for pasta in ["Gestao", "Gestão"]:
            resposta = supabase.storage.from_(BUCKET_NOME).list(pasta)
            if resposta:
                for arquivo in resposta:
                    if arquivo.get("name") == nome_procurado:
                        return True
        return False
    except Exception:
        return False

def apagar_arquivo_supabase(nome_arquivo):
    if not supabase:
        return False
    try:
        for pasta in ["Gestao", "Gestão"]:
            try:
                caminho = f"{pasta}/{nome_arquivo}"
                supabase.storage.from_(BUCKET_NOME).remove([caminho])
            except:
                continue
        return True
    except Exception as e:
        st.error(f"Erro ao apagar: {e}")
        return False

col1, col2 = st.columns(2)

# ==========================================
# COLUNA 1: PLANILHA DE ESTOQUE
# ==========================================
with col1:
    st.markdown("#### Planilha de Estoque")
    arquivo_estoque = st.file_uploader("Envie a nova planilha de estoque", type=["xlsx", "xlsm"], key="up_estoque")
    
    existe_estoque = verificar_arquivo_existe("estoque")
    
    if arquivo_estoque is not None:
        st.success(f"✅ **Novo arquivo pronto para envio:** {arquivo_estoque.name}")
        if st.button("Confirmar Envio (Estoque)", key="btn_est"):
            try:
                bytes_dados = arquivo_estoque.getvalue()
                caminho_no_bucket = "Gestao/estoque_fixo.xlsx"
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
        if existe_estoque:
            st.info("📂 **Arquivo em uso no sistema (Supabase):** `estoque_fixo.xlsx`")
            if st.button("🗑️ Apagar Estoque do Supabase", key="del_est", type="secondary"):
                if apagar_arquivo_supabase("estoque_fixo.xlsx"):
                    st.success("🗑️ Ficheiro de estoque apagado com sucesso do Supabase!")
                    st.rerun()
        else:
            st.warning("⚠️ Nenhum arquivo de estoque encontrado na pasta Gestão.")

# ==========================================
# COLUNA 2: PLANILHA DE VENDAS
# ==========================================
with col2:
    st.markdown("#### Planilha de Vendas")
    arquivo_vendas = st.file_uploader("Envie a nova planilha de vendas", type=["xlsx", "xlsm"], key="up_vendas")
    
    existe_vendas = verificar_arquivo_existe("vendas")
    
    if arquivo_vendas is not None:
        st.success(f"✅ **Novo arquivo pronto para envio:** {arquivo_vendas.name}")
        if st.button("Confirmar Envio (Vendas)", key="btn_vend"):
            try:
                bytes_dados = arquivo_vendas.getvalue()
                caminho_no_bucket = "Gestao/vendas_fixo.xlsx"
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
        if existe_vendas:
            st.info("📂 **Arquivo em uso no sistema (Supabase):** `vendas_fixo.xlsx`")
            if st.button("🗑️ Apagar Vendas do Supabase", key="del_vend", type="secondary"):
                if apagar_arquivo_supabase("vendas_fixo.xlsx"):
                    st.success("🗑️ Ficheiro de vendas apagado com sucesso do Supabase!")
                    st.rerun()
        else:
            st.warning("⚠️ Nenhum arquivo de vendas encontrado na pasta Gestão.")
