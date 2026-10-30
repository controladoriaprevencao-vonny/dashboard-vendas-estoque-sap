import streamlit as st

AMBIENTE_STAGING = True

st.set_page_config(
    page_title="Dashboard Executivo - Vonný" + (" [STAGING]" if AMBIENTE_STAGING else ""),
    page_icon="icone.png",
    layout="wide",
)

st.markdown(
    """
    <style>
    header[data-testid="stHeader"] { background-color: #E6007E !important; }
    h1, h2, h3 { color: #C5006B !important; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 700; }
    </style>
""",
    unsafe_allow_html=True,
)

if AMBIENTE_STAGING:
    st.warning("⚠️ **ATENÇÃO: Você está acessando a versão de testes (Staging).**")

st.title("📊 Dashboard Executivo - Vonný")
st.markdown("Bem-vindo ao sistema de relatórios gerenciais integrados ao SAP e hospedados no Supabase.")
st.markdown("Como o menu lateral está oculto, utilize os links diretos abaixo para acessar os módulos:")

st.markdown("<br>", unsafe_allow_html=True)

# Usando st.page_link com os nomes atuais exatos dos arquivos
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📤 Central de Uploads")
    st.page_link("pages/1_Upload_e_Formatacao.py", label="Abrir Central de Uploads ➔", use_container_width=True)

with col2:
    st.markdown("### 📊 Relatórios e Ativos")
    st.page_link("pages/2_Relatorio_Vendas.py", label="Abrir Relatório de Vendas ➔", use_container_width=True)
    st.page_link("pages/3_Relatorio_Estoque.py", label="Abrir Relatório de Estoque ➔", use_container_width=True)
    st.page_link("pages/4_Imagens_e_Ativos.py", label="Abrir Imagens e Ativos ➔", use_container_width=True)
