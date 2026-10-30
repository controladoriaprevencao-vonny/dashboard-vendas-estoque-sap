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
    </style>
""",
    unsafe_allow_html=True,
)

if AMBIENTE_STAGING:
    st.warning("⚠️ **ATENÇÃO: Você está acessando a versão de testes (Staging).**")

st.title("📊 Dashboard Executivo - Vonný")
st.markdown("Bem-vindo ao sistema de relatórios gerenciais integrados ao SAP e hospedados no Supabase.")

# Criando as abas profissionais do sistema
tab_home, tab_upload, tab_vendas, tab_estoque, tab_ativos = st.tabs([
    "🏠 Início", 
    "📤 Central de Uploads", 
    "📈 Relatório de Vendas", 
    "📦 Relatório de Estoque", 
    "🎨 Imagens e Ativos"
])

with tab_home:
    st.markdown("### Bem-vindo ao Painel Principal")
    st.markdown("Utilize as abas acima para navegar instantaneamente entre os módulos do sistema sem nenhum risco de erro de carregamento.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("📤 **Central de Uploads:** Envie e gerencie planilhas administrativas, de estoque e vendas.")
    with col2:
        st.info("📊 **Relatórios:** Consulte dados consolidados e aplique filtros por loja e material.")

with tab_upload:
    st.header("📤 Central de Uploads e Formatação")
    st.write("Insira aqui o código do seu arquivo `1_Upload_e_Formatacao.py`")
    # Cole aqui o código correspondente à sua página de uploads

with tab_vendas:
    st.header("📈 Relatório de Vendas")
    st.write("Insira aqui o código do seu arquivo `2_Relatorio_Vendas.py`")
    # Cole aqui o código correspondente à sua página de vendas

with tab_estoque:
    st.header("📦 Relatório de Estoque")
    st.write("Insira aqui o código do seu arquivo `3_Relatorio_Estoque.py`")
    # Cole aqui o código correspondente à sua página de estoque

with tab_ativos:
    st.header("🎨 Imagens e Ativos")
    st.write("Insira aqui o código do seu arquivo `4_Imagens_e_Ativos.py`")
    # Cole aqui o código correspondente à sua página de ativos
