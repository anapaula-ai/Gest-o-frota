import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Gestão de Frotas", layout="wide")

# 2. Estilização CSS (Layout Black Premium)
st.markdown("""
    <style>
    /* Fundo principal */
    .stApp {
        background-color: #000000;
        color: white;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #333;
    }

    /* Cards de Métricas */
    .metric-container {
        background-color: #111111;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333333;
        text-align: center;
    }
    .metric-label {
        color: #888888;
        font-size: 14px;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .metric-value {
        color: #ffffff;
        font-size: 28px;
        font-weight: bold;
    }

    /* Ajuste de abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #555555;
    }
    .stTabs [aria-selected="true"] {
        color: #FF4B4B !important;
        border-bottom-color: #FF4B4B !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Função para criar os cards
def draw_metric(label, value):
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)

# 3. Carregamento de Dados
@st.cache_data
def load_data():
    # Certifique-se que o arquivo manutenção.xlsx está na mesma pasta no GitHub
    df = pd.read_excel("manutencao.xlsx")
    return df

try:
    df = load_data()

    # 4. Filtros na Barra Lateral
    st.sidebar.title("Filtros")
    
    instituicao = st.sidebar.multiselect("Instituição", options=df["Instituição"].unique(), default=df["Instituição"].unique())
    mes = st.sidebar.selectbox("Mês Referência", options=df["Mês Referência"].unique())
    base = st.sidebar.selectbox("Base", options=["Todas"] + list(df["Base"].unique()))

    # Aplicação dos Filtros
    df_filtrado = df[(df["Instituição"].isin(instituicao)) & (df["Mês Referência"] == mes)]
    if base != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Base"] == base]

    # 5. Título Principal
    st.title("📊 Gestão de Frotas")
    st.markdown("---")

    # 6. Abas
    tab1, tab2 = st.tabs(["Mensal", "Acumulado"])

    with tab1:
        # Métricas Principais
        c1, c2, c3 = st.columns(3)
        with c1:
            draw_metric("Veículos", len(df_filtrado["Placa"].unique()))
        with c2:
            km_total = f"{df_filtrado['Quilometragem'].sum():,.0f}".replace(",", ".")
            draw_metric("KM Total", km_total)
        with c3:
            custo_total = f"R$ {df_filtrado['Custo de manutenção'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            draw_metric("Custo Total", custo_total)

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráficos Mensais
        g1, g2 = st.columns(2)

        with g1:
            st.subheader("Top 10 KM por Placa")
            top10_km = df_filtrado.nlargest(10, 'Quilometragem')
            fig_km = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', color_discrete_sequence=['#4B4BFF'])
            fig_km.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=400)
            st.plotly_chart(fig_km, use_container_width=True)

        with g2:
            st.subheader("Top 10 Custos por Placa")
            top10_custo = df_filtrado.nlargest(10, 'Custo de manutenção')
            fig_custo = px.bar(top10_custo, x='Custo de manutenção', y='Placa', orientation='h', color_discrete_sequence=['#FF4B4B'])
            fig_custo.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=400)
            st.plotly_chart(fig_custo, use_container_width=True)

    with tab2:
        st.subheader("Visão Acumulada Anual")
        # Filtro apenas por instituição no acumulado
        df_acumulado = df[df["Instituição"].isin(instituicao)]
        
        custo_anual = df_acumulado.groupby("Base")["Custo de manutenção"].sum().reset_index()
        fig_anual = px.pie(custo_anual, values='Custo de manutenção', names='Base', hole=.4, template="plotly_dark")
        fig_anual.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_anual, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.info("Verifique se o arquivo 'manutencao.xlsx' está no repositório do GitHub.")
