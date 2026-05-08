import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. Configuração da Página
st.set_page_config(page_title="Gestão de Frotas", layout="wide")

# 2. CSS Sophisticated Corporate Layout
st.markdown("""
    <style>
    /* Importando fonte Inter para um ar mais moderno */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    .stApp {
        background-color: #F8FAFC;
        color: #1E293B;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar minimalista */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }

    /* Padronização absoluta de Títulos */
    h1, h2, h3, .stMarkdown h3 {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #0F172A !important;
        letter-spacing: -0.02em;
        margin-top: 10px !important;
    }

    /* Título Principal maior e elegante */
    .main-title {
        font-size: 28px !important;
        font-weight: 800 !important;
        color: #0F172A;
        margin-bottom: 20px;
    }

    /* Cards de Métricas Estilo Executivo */
    .metric-card {
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #F1F5F9;
        text-align: left;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
    }
    .metric-label {
        color: #64748B;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .metric-value {
        color: #0F172A;
        font-size: 28px;
        font-weight: 700;
    }

    /* Tabs Padronizadas */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        font-size: 15px;
        font-weight: 600;
        color: #94A3B8;
        padding-bottom: 8px;
    }
    .stTabs [aria-selected="true"] {
        color: #0F172A !important;
        border-bottom: 3px solid #0F172A !important;
    }
    </style>
    """, unsafe_allow_html=True)

def draw_metric(label, value):
    st.markdown(f'''
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
    ''', unsafe_allow_html=True)

# 3. Processamento de Dados
try:
    df = pd.read_excel("manutencao.xlsx")
    
    # Tratamento de Datas e Mês
    df['Mês Referência'] = pd.to_datetime(df['Mês Referência'])
    meses_map = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril"}
    df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_map)

    # Sidebar - Filtros
    st.sidebar.markdown("<br><h3>Filtros Estratégicos</h3>", unsafe_allow_html=True)
    escolha_inst = st.sidebar.selectbox("Instituição", ["Todos", "AMES", "IAV"])
    escolha_mes = st.sidebar.selectbox("Mês de Referência", ["Janeiro", "Fevereiro", "Março", "Abril"])
    bases_disponiveis = sorted(df["Base"].unique())
    escolha_base = st.sidebar.selectbox("Base Operacional", ["Todas"] + bases_disponiveis)

    # Lógica de Filtragem
    df_filtrado_mensal = df[df["Mes_Nome"] == escolha_mes]
    
    if escolha_inst != "Todos":
        df_filtrado_mensal = df_filtrado_mensal[df_filtrado_mensal["Instituição"] == escolha_inst]
        df_total_ano = df[df["Instituição"] == escolha_inst]
    else:
        df_total_ano = df.copy()
        
    if escolha_base != "Todas":
        df_filtrado_mensal = df_filtrado_mensal[df_filtrado_mensal["Base"] == escolha_base]

    # Layout Principal
    st.markdown('<div class="main-title">Gestão de frotas</div>', unsafe_allow_html=True)
    
    tab_mensal, tab_anual = st.tabs(["Visão Mensal", "Acumulado Estratégico"])

    # Cores Executivas: Azul Marinho Sóbrio e Cinza Grafite
    COR_KM = "#1E3A8A"   # Navy Blue
    COR_CUSTO = "#334155" # Slate 700

    with tab_mensal:
        # Métricas (Apenas 3 conforme solicitado)
        m1, m2, m3 = st.columns(3)
        with m1: draw_metric("Veículos Ativos", f"{len(df_filtrado_mensal['Placa'].unique())}")
        with m2: draw_metric("Total KM Rodados", f"{df_filtrado_mensal['Quilometragem'].sum():,.0f}".replace(",", "."))
        with m3: draw_metric("Investimento Total", f"R$ {df_filtrado_mensal['Custo de manutenção'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.markdown("<br><br>", unsafe_allow_html=True)

        g1, g2 = st.columns(2)
        
        with g1:
            st.markdown("### Ranking de Quilometragem por Veículo")
            # Ordenação do maior para o menor
            top10_km = df_filtrado_mensal.nlargest(10, 'Quilometragem').sort_values('Quilometragem', ascending=True)
            fig1 = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', color_discrete_sequence=[COR_KM])
            fig1.update_traces(texttemplate='%{x:,.0f}', textposition='outside', cliponaxis=False, textfont=dict(size=11, fontweight='bold'))
            fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=100, t=10, b=10),
                              xaxis=dict(visible=False), yaxis=dict(showgrid=False, title=""))
            st.plotly_chart(fig1, use_container_width=True)

        with g2:
            st.markdown("### Ranking de Custos por Veículo")
            # Ordenação do maior para o menor
            top10_custo = df_filtrado_mensal.nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
            fig2 = px.bar(top10_custo, x='Custo de manutenção', y='Placa', orientation='h', color_discrete_sequence=[COR_CUSTO])
            fig2.update_traces(texttemplate='R$ %{x:,.2f}', textposition='outside', cliponaxis=False, textfont=dict(size=11, fontweight='bold'))
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=120, t=10, b=10),
                              xaxis=dict(visible=False), yaxis=dict(showgrid=False, title=""))
            st.plotly_chart(fig2, use_container_width=True)

        with st.expander("🔍 Detalhamento Completo da Frota"):
            st.dataframe(df_filtrado_mensal[['Instituição', 'Base', 'Placa', 'Quilometragem', 'Custo de manutenção']]
                         .sort_values('Custo de manutenção', ascending=False)
                         .style.format({'Quilometragem': '{:,.0f}', 'Custo de manutenção': 'R$ {:,.2f}'}), use_container_width=True)

    with tab_anual:
        st.markdown("### Ranking Acumulado por Base (Janeiro a Abril)")
        # Agrupamento e Ordenação
        df_base = df_total_ano[df_total_ano['Mes_Nome'].isin(["Janeiro", "Fevereiro", "Março", "Abril"])]
        df_ranking_base = df_base.groupby("Base").agg({"Custo de manutenção": "sum", "Quilometragem": "sum"}).reset_index()
        
        c_anual1, c_anual2 = st.columns(2)
        with c_anual1:
            st.markdown("### Top Bases por Investimento")
            df_base_custo = df_ranking_base.nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
            fig3 = px.bar(df_base_custo, x='Custo de manutenção', y='Base', orientation='h', color_discrete_sequence=[COR_CUSTO])
            fig3.update_traces(texttemplate='R$ %{x:,.2f}', textposition='outside', cliponaxis=False, textfont=dict(fontweight='bold'))
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=120, t=10, b=10), xaxis=dict(visible=False), yaxis=dict(title=""))
            st.plotly_chart(fig3, use_container_width=True)

        with c_anual2:
            st.markdown("### Top Bases por Rodagem (KM)")
            df_base_km = df_ranking_base.nlargest(10, 'Quilometragem').sort_values('Quilometragem', ascending=True)
            fig4 = px.bar(df_base_km, x='Quilometragem', y='Base', orientation='h', color_discrete_sequence=[COR_KM])
            fig4.update_traces(texttemplate='%{x:,.0f}', textposition='outside', cliponaxis=False, textfont=dict(fontweight='bold'))
            fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=100, t=10, b=10), xaxis=dict(visible=False), yaxis=dict(title=""))
            st.plotly_chart(fig4, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao processar dados: {e}")
