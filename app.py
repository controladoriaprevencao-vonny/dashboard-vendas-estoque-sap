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

if AMBIENTE_STAGING:
    st.warning("⚠️ **ATENÇÃO: Você está acessando a versão de testes (Staging).**")

st.title("📊 Dashboard Executivo - Vonný")
st.markdown("Bem-vindo ao sistema de relatórios gerenciais integrados ao SAP e hospedados no Supabase.")
st.markdown("Utilize os botões abaixo ou o menu lateral esquerdo para acessar rapidamente cada módulo do sistema:")

st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📤 Central de Uploads")
    st.markdown("Envie e gerencie as planilhas administrativas, de estoque e de vendas de forma isolada.")
    if st.button("Ir para Central de Uploads ➔", key="btn_upload"):
        st.switch_page("pages/1_📤_Upload_e_Formatacao.py")

with col2:
    st.markdown("### 📊 Dashboards e Relatórios")
    st.markdown("Consulte os dados consolidados, filtre por loja, material, grupo e depósito.")
    if st.button("Ver Relatório de Vendas ➔", key="btn_vendas"):
        st.switch_page("pages/2_📈_Relatorio_Vendas.py")
    if st.button("Ver Relatório de Estoque ➔", key="btn_estoque"):
        st.switch_page("pages/3_📦_Relatorio_Estoque.py")
