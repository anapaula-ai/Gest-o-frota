import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Gestão de Frotas", layout="wide")

# 2. CSS Sophisticated Corporate (Estilo Platinum)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    .stApp {
        background-color: #F8FAFC;
        color: #1E293B;
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }

    /* Padronização de Títulos */
    h1, h2, h3 {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #0F172A !important;
        margin-top: 10px !important;
    }

    .main-title {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #0F172A;
        margin-bottom: 25px;
    }

    /* Cards de Métricas */
    .metric-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #F1F5F9;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    .metric-label {
        color: #64748B;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 5px;
    }
    .metric-value {
        color: #0F172A;
        font-size: 24px;
        font-weight: 700;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        font-size: 14px;
        font-weight: 600;
        color: #94A3B8;
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
    
    # Tratamento de Datas
    df['Mês Referência'] = pd.to_datetime(df['Mês Referência'])
    meses_map = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril"}
    df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_map)

    # Sidebar - Filtros
    st.sidebar.markdown("### Filtros Estratégicos")
    escolha_inst = st.sidebar.selectbox("Instituição", ["Todos", "AMES", "IAV"])
    escolha_mes = st.sidebar.selectbox("Mês de Referência", ["Janeiro", "Fevereiro", "Março", "Abril"])
    bases_disponiveis = sorted(df["Base"].unique())
    escolha_base = st.sidebar.selectbox("Base Operacional", ["Todas"] + bases_disponiveis)

    # Lógica de Filtragem
    df_filtrado = df[df["Mes_Nome"] == escolha_mes]
    
    if escolha_inst != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Instituição"] == escolha_inst]
        df_total_ano = df[df["Instituição"] == escolha_inst]
    else:
        df_total_ano = df.copy()
        
    if escolha_base != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Base"] == escolha_base]

    # Layout
    st.markdown('<div class="main-title">Gestão de frotas</div>', unsafe_allow_html=True)
    
    tab_mensal, tab_anual = st.tabs(["Visão Mensal", "Acumulado Estratégico"])

    # Cores Platinum
    AZUL_NAVY = "#1E3A8A"
    CINZA_SLATE = "#334155"

    with tab_mensal:
        # Métricas
        m1, m2, m3 = st.columns(3)
        with m1: draw_metric("Veículos Ativos", f"{len(df_filtrado['Placa'].unique())}")
        with m2: draw_metric("Total KM Rodados", f"{df_filtrado['Quilometragem'].sum():,.0f}".replace(",", "."))
        with m3: draw_metric("Investimento Total", f"R$ {df_filtrado['Custo de manutenção'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.markdown("<br>", unsafe_allow_html=True)

        g1, g2 = st.columns(2)
        
        with g1:
            st.markdown("### Ranking de Quilometragem por Veículo")
            # Ordenação do maior para o menor (Plotly inverte a ordem no gráfico horizontal, por isso ascending=True)
            top10_km = df_filtrado.nlargest(10, 'Quilometragem').sort_values('Quilometragem', ascending=True)
            fig1 = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', color_discrete_sequence=[AZUL_NAVY])
            fig1.update_traces(texttemplate='%{x:,.0f}', textposition='outside', cliponaxis=False)
            fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=100, t=10, b=10),
                              xaxis=dict(visible=False), yaxis=dict(showgrid=False, title="", tickfont=dict(size=12)))
            st.plotly_chart(fig1, use_container_width=True)

        with g2:
            st.markdown("### Ranking de Custos por Veículo")
            top10_custo = df_filtrado.nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
            fig2 = px.bar(top10_custo, x='Custo de manutenção', y='Placa', orientation='h', color_discrete_sequence=[CINZA_SLATE])
            fig2.update_traces(texttemplate='R$ %{x:,.2f}', textposition='outside', cliponaxis=False)
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=130, t=10, b=10),
                              xaxis=dict(visible=False), yaxis=dict(showgrid=False, title="", tickfont=dict(size=12)))
            st.plotly_chart(fig2, use_container_width=True)

    with tab_anual:
        st.markdown("### Ranking Acumulado por Base (Janeiro a Abril)")
        df_base_ranking = df_total_ano[df_total_ano['Mes_Nome'].isin(["Janeiro", "Fevereiro", "Março", "Abril"])]
        df_resumo = df_base_ranking.groupby("Base").agg({"Custo de manutenção": "sum", "Quilometragem": "sum"}).reset_index()
        
        c_anual1, c_anual2 = st.columns(2)
        with c_anual1:
            st.markdown("### Investimento por Base")
            df_plot_c = df_resumo.nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
            fig3 = px.bar(df_plot_c, x='Custo de manutenção', y='Base', orientation='h', color_discrete_sequence=[CINZA_SLATE])
            fig3.update_traces(texttemplate='R$ %{x:,.2f}', textposition='outside', cliponaxis=False)
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=130, t=10, b=10), xaxis=dict(visible=False), yaxis=dict(title=""))
            st.plotly_chart(fig3, use_container_width=True)

        with c_anual2:
            st.markdown("### Rodagem por Base (KM)")
            df_plot_k = df_resumo.nlargest(10, 'Quilometragem').sort_values('Quilometragem', ascending=True)
            fig4 = px.bar(df_plot_k, x='Quilometragem', y='Base', orientation='h', color_discrete_sequence=[AZUL_NAVY])
            fig4.update_traces(texttemplate='%{x:,.0f}', textposition='outside', cliponaxis=False)
            fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=100, t=10, b=10), xaxis=dict(visible=False), yaxis=dict(title=""))
            st.plotly_chart(fig4, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao processar dados: {e}")
