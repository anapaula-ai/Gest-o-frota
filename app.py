import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Gestão de Frotas", layout="wide")

# 2. Estilização CSS: Fundo Cinza, Letras Menores e Elegância
st.markdown("""
    <style>
    /* Fundo Cinza Escuro Elegante */
    .stApp {
        background-color: #1E1E1E;
        color: #D3D3D3;
        font-size: 14px; /* Letras menores globalmente */
    }
    
    /* Sidebar Cinza mais fechado */
    [data-testid="stSidebar"] {
        background-color: #161616;
        border-right: 1px solid #333;
    }

    /* Cards de Métricas em Cinza Grafite */
    .metric-card {
        background-color: #262626;
        padding: 12px;
        border-radius: 6px;
        border: 1px solid #444;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-label {
        color: #AAAAAA;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        color: #FFFFFF;
        font-size: 20px;
        font-weight: bold;
    }

    /* Ajuste das Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        color: #888;
        font-size: 13px;
        padding: 5px 15px;
    }
    .stTabs [aria-selected="true"] {
        color: #FFFFFF !important;
        border-bottom-color: #555555 !important;
    }

    /* Reduzir títulos de seções */
    h1 { font-size: 24px !important; }
    h2, h3 { font-size: 18px !important; color: #CCCCCC !important; }
    </style>
    """, unsafe_allow_html=True)

def draw_metric(label, value):
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

# 3. Carregamento de Dados
try:
    df = pd.read_excel("manutencao.xlsx")

    # Filtros
    st.sidebar.markdown("### Filtros")
    lista_inst = df["Instituição"].unique()
    escolha_inst = st.sidebar.multiselect("Instituição", options=lista_inst, default=lista_inst)
    
    lista_meses = df["Mês Referência"].unique()
    escolha_mes = st.sidebar.selectbox("Mês Referência", options=lista_meses)
    
    lista_bases = sorted(df["Base"].unique())
    escolha_base = st.sidebar.selectbox("Base", options=["Todas"] + lista_bases)

    # Lógica de Filtragem
    df_mes = df[(df["Instituição"].isin(escolha_inst)) & (df["Mês Referência"] == escolha_mes)]
    if escolha_base != "Todas":
        df_mes = df_mes[df_mes["Base"] == escolha_base]

    df_ano = df[df["Instituição"].isin(escolha_inst)]

    st.title("Gestão de Frotas — AMES / IAV")
    
    tab_mensal, tab_anual = st.tabs(["Controle Mensal", "Acumulado Anual"])

    # Paleta de Cores Padronizada (Cinza Azulado e Azul Soft)
    COR_KM = "#5A7D9A" 
    COR_CUSTO = "#8E8E8E"

    with tab_mensal:
        c1, c2, c3 = st.columns(3)
        with c1:
            draw_metric("Veículos", f"{len(df_mes['Placa'].unique())}")
        with c2:
            km_val = df_mes['Quilometragem'].sum()
            draw_metric("KM Total", f"{km_val:,.0f}".replace(",", "."))
        with c3:
            custo_val = df_mes['Custo de manutenção'].sum()
            draw_metric("Custo Total", f"R$ {custo_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.markdown("<br>", unsafe_allow_html=True)
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.subheader("Top 10 KM por Placa")
            top10_km = df_mes.nlargest(10, 'Quilometragem')
            # texttemplate='%{x}' exibe o valor inteiro sem abreviação
            fig1 = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', 
                          color_discrete_sequence=[COR_KM])
            fig1.update_traces(texttemplate='%{x:,.0f}', textposition='outside', cliponaxis=False)
            fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#AAA", size=10),
                              xaxis=dict(showgrid=False, visible=False), yaxis=dict(categoryorder='total ascending'))
            st.plotly_chart(fig1, use_container_width=True)

        with col_g2:
            st.subheader("Top 10 Custos por Placa")
            top10_custo = df_mes.nlargest(10, 'Custo de manutenção')
            fig2 = px.bar(top10_custo, x='Custo de manutenção', y='Placa', orientation='h', 
                          color_discrete_sequence=[COR_CUSTO])
            # Formatação para R$ inteiro
            fig2.update_traces(texttemplate='R$ %{x:,.2f}', textposition='outside', cliponaxis=False)
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#AAA", size=10),
                              xaxis=dict(showgrid=False, visible=False), yaxis=dict(categoryorder='total ascending'))
            st.plotly_chart(fig2, use_container_width=True)

    with tab_anual:
        df_base_ranking = df_ano.groupby("Base").agg({"Custo de manutenção": "sum", "Quilometragem": "sum"}).reset_index()
        
        c_anual1, c_anual2 = st.columns(2)
        with c_anual1:
            st.subheader("Top 10 Bases — Custo Acumulado")
            top10_base_custo = df_base_ranking.nlargest(10, 'Custo de manutenção')
            fig3 = px.bar(top10_base_custo, x='Custo de manutenção', y='Base', orientation='h', color_discrete_sequence=[COR_CUSTO])
            fig3.update_traces(texttemplate='R$ %{x:,.2f}', textposition='outside')
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#AAA", size=10),
                              xaxis=dict(visible=False), yaxis=dict(categoryorder='total ascending'))
            st.plotly_chart(fig3, use_container_width=True)

        with c_anual2:
            st.subheader("Top 10 Bases — KM Acumulado")
            top10_base_km = df_base_ranking.nlargest(10, 'Quilometragem')
            fig4 = px.bar(top10_base_km, x='Quilometragem', y='Base', orientation='h', color_discrete_sequence=[COR_KM])
            fig4.update_traces(texttemplate='%{x:,.0f}', textposition='outside')
            fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#AAA", size=10),
                              xaxis=dict(visible=False), yaxis=dict(categoryorder='total ascending'))
            st.plotly_chart(fig4, use_container_width=True)

except Exception as e:
    st.error(f"Erro: {e}")
