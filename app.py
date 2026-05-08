import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Gestão de Frotas — Dashboard Executivo", layout="wide")

# 2. CSS Platinum Corporate (Mais claro, elegante e padronizado)
st.markdown("""
    <style>
    /* Fundo Cinza Platina Suave */
    .stApp {
        background-color: #F8F9FB;
        color: #1E293B;
        font-family: 'Inter', sans-serif;
    }
    
    /* Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }

    /* Padronização de Títulos (Todos com o mesmo tamanho) */
    h1, h2, h3 {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: #0F172A !important;
        margin-bottom: 15px !important;
    }

    /* Cards de Métricas Brancos com Sombra Sutil */
    .metric-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .metric-label {
        color: #64748B;
        font-size: 12px;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .metric-value {
        color: #1E293B;
        font-size: 24px;
        font-weight: 700;
    }

    /* Ajuste das Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        color: #64748B;
        font-size: 14px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: #2563EB !important;
        border-bottom: 2px solid #2563EB !important;
    }

    /* Letras Menores na Tabela */
    [data-testid="stDataFrame"] { font-size: 12px; }
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
    
    # Tratamento de Datas
    df['Mês Referência'] = pd.to_datetime(df['Mês Referência'])
    meses_map = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril"}
    df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_map)

    # Filtros Sidebar
    st.sidebar.markdown("### Parâmetros de Filtro")
    escolha_inst = st.sidebar.selectbox("Instituição", ["Todos", "AMES", "IAV"])
    escolha_mes = st.sidebar.selectbox("Mês de Referência", ["Janeiro", "Fevereiro", "Março", "Abril"])
    bases_disponiveis = sorted(df["Base"].unique())
    escolha_base = st.sidebar.selectbox("Base Operacional", ["Todas"] + bases_disponiveis)

    # Lógica de Filtragem
    df_mes = df[df["Mes_Nome"] == escolha_mes]
    if escolha_inst != "Todos":
        df_mes = df_mes[df_mes["Instituição"] == escolha_inst]
        df_total = df[df["Instituição"] == escolha_inst]
    else:
        df_total = df.copy()
        
    if escolha_base != "Todas":
        df_mes = df_mes[df_mes["Base"] == escolha_base]

    # Layout Principal
    st.markdown("### Dashboard de Gestão de Frotas — Controle de Ativos")
    
    tab_mensal, tab_anual = st.tabs(["Visão Mensal", "Acumulado Estratégico"])

    # Cores Corporativas (Azul Marinho e Cinza Slate)
    COR_PRIMARIA = "#1E40AF" 
    COR_SECUNDARIA = "#475569"

    with tab_mensal:
        # Métricas Padronizadas
        m1, m2, m3, m4 = st.columns(4)
        with m1: draw_metric("Frota Ativa", f"{len(df_mes['Placa'].unique())}")
        with m2: draw_metric("KM Rodados", f"{df_mes['Quilometragem'].sum():,.0f}".replace(",", "."))
        with m3: draw_metric("Investimento", f"R$ {df_mes['Custo de manutenção'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with m4: draw_metric("Média KM/Veículo", f"{df_mes['Quilometragem'].mean():,.0f}".replace(",", "."))

        st.markdown("<br>", unsafe_allow_html=True)

        g1, g2 = st.columns(2)
        
        # Ajuste crucial: 'margin' no update_layout para não cortar números
        with g1:
            st.markdown("### Top 10 Quilometragem por Placa")
            top10_km = df_mes.nlargest(10, 'Quilometragem')
            fig1 = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', color_discrete_sequence=[COR_PRIMARIA])
            fig1.update_traces(texttemplate='%{x:,.0f}', textposition='outside', cliponaxis=False)
            fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(size=11),
                              xaxis=dict(visible=False), yaxis=dict(categoryorder='total ascending', showgrid=False),
                              margin=dict(l=20, r=100, t=20, b=20)) # Margem direita aumentada
            st.plotly_chart(fig1, use_container_width=True)

        with g2:
            st.markdown("### Top 10 Maiores Custos por Placa")
            top10_custo = df_mes.nlargest(10, 'Custo de manutenção')
            fig2 = px.bar(top10_custo, x='Custo de manutenção', y='Placa', orientation='h', color_discrete_sequence=[COR_SECUNDARIA])
            fig2.update_traces(texttemplate='R$ %{x:,.2f}', textposition='outside', cliponaxis=False)
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(size=11),
                              xaxis=dict(visible=False), yaxis=dict(categoryorder='total ascending', showgrid=False),
                              margin=dict(l=20, r=120, t=20, b=20)) # Margem direita aumentada para o R$
            st.plotly_chart(fig2, use_container_width=True)

        with st.expander("🔍 Visualizar Lista Completa da Frota"):
            st.dataframe(df_mes[['Instituição', 'Base', 'Placa', 'Quilometragem', 'Custo de manutenção']].style.format({
                'Quilometragem': '{:,.0f}', 'Custo de manutenção': 'R$ {:,.2f}'
            }), use_container_width=True)

    with tab_anual:
        st.markdown("### Ranking Acumulado por Base (Janeiro a Abril)")
        df_rank = df_total[df_total['Mes_Nome'].isin(["Janeiro", "Fevereiro", "Março", "Abril"])]
        df_base = df_rank.groupby("Base").agg({"Custo de manutenção": "sum", "Quilometragem": "sum"}).reset_index()
        
        c_anual1, c_anual2 = st.columns(2)
        with c_anual1:
            st.markdown("### Top 10 Bases por Custo")
            fig3 = px.bar(df_base.nlargest(10, 'Custo de manutenção'), x='Custo de manutenção', y='Base', 
                          orientation='h', color_discrete_sequence=[COR_SECUNDARIA])
            fig3.update_traces(texttemplate='R$ %{x:,.2f}', textposition='outside', cliponaxis=False)
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=120, t=20, b=20), xaxis=dict(visible=False))
            st.plotly_chart(fig3, use_container_width=True)

        with c_anual2:
            st.markdown("### Top 10 Bases por Quilometragem")
            fig4 = px.bar(df_base.nlargest(10, 'Quilometragem'), x='Quilometragem', y='Base', 
                          orientation='h', color_discrete_sequence=[COR_PRIMARIA])
            fig4.update_traces(texttemplate='%{x:,.0f}', textposition='outside', cliponaxis=False)
            fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=100, t=20, b=20), xaxis=dict(visible=False))
            st.plotly_chart(fig4, use_container_width=True)

except Exception as e:
    st.error(f"Erro no processamento: {e}")
