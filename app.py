import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Gestão de Frotas Premium", layout="wide")

# 2. CSS Sophisticated Grey Layout
st.markdown("""
    <style>
    /* Fundo Slate Grey Profissional */
    .stApp {
        background-color: #1A1C23;
        color: #ECEFF4;
        font-size: 13px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111217;
        border-right: 1px solid #2D3139;
    }

    /* Cards de Métricas Estilo Neumorfismo Suave */
    .metric-card {
        background-color: #242731;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333745;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    .metric-label {
        color: #9BA1B0;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 8px;
    }
    .metric-value {
        color: #FFFFFF;
        font-size: 22px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
    }

    /* Tabelas e Dataframes */
    [data-testid="stDataFrame"] {
        border: 1px solid #333745;
        border-radius: 10px;
    }

    /* Títulos e Subtítulos */
    h1 { font-size: 22px !important; font-weight: 700 !important; color: #FFFFFF !important; }
    h2, h3 { font-size: 16px !important; font-weight: 600 !important; color: #D8DEE9 !important; }
    
    /* Customização de Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] {
        color: #7B818E;
        font-size: 13px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: #FFFFFF !important;
        border-bottom: 2px solid #5E81AC !important;
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

    # --- SIDEBAR / FILTROS ---
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3202/3202926.png", width=50) # Ícone sutil
    st.sidebar.markdown("### Filtros Estratégicos")
    
    # Filtro Instituição com opção "Todos"
    opcoes_inst = ["Todos", "AMES", "IAV"]
    escolha_inst = st.sidebar.selectbox("Instituição", opcoes_inst)
    
    # Filtro Mês (Janeiro a Abril)
    meses_disponiveis = ["Janeiro", "Fevereiro", "Março", "Abril"]
    escolha_mes = st.sidebar.selectbox("Mês de Referência", meses_disponiveis)
    
    # Filtro Base (Dinâmico)
    bases_disponiveis = sorted(df["Base"].unique())
    escolha_base = st.sidebar.selectbox("Base Operacional", ["Todas"] + bases_disponiveis)

    # --- LÓGICA DE FILTRAGEM ---
    # Filtrar por Mês
    df_filtrado = df[df["Mês Referência"] == escolha_mes]
    
    # Filtrar por Instituição
    if escolha_inst != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Instituição"] == escolha_inst]
        
    # Filtrar por Base
    if escolha_base != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Base"] == escolha_base]

    # Dados para o Acumulado (Janeiro a Abril)
    df_acumulado = df[df["Mês Referência"].isin(meses_disponiveis)]
    if escolha_inst != "Todos":
        df_acumulado = df_acumulado[df_acumulado["Instituição"] == escolha_inst]

    # --- LAYOUT PRINCIPAL ---
    st.title("Sistema de Gestão de Frotas — Inteligência Operacional")
    st.markdown("<br>", unsafe_allow_html=True)

    tab_mensal, tab_anual = st.tabs(["📊 Visão Mensal", "📈 Acumulado Estratégico"])

    # Cores Padronizadas
    AZUL_SOFT = "#81A1C1"
    CINZA_SOFT = "#4C566A"

    with tab_mensal:
        # Métricas
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            draw_metric("Frota Ativa", f"{len(df_filtrado['Placa'].unique())}")
        with m2:
            draw_metric("KM Rodados", f"{df_filtrado['Quilometragem'].sum():,.0f}".replace(",", "."))
        with m3:
            custo_total = df_filtrado['Custo de manutenção'].sum()
            draw_metric("Investimento", f"R$ {custo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with m4:
            media_km = df_filtrado['Quilometragem'].mean() if not df_filtrado.empty else 0
            draw_metric("Média KM/Veículo", f"{media_km:,.0f}".replace(",", "."))

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráficos Top 10
        g1, g2 = st.columns(2)
        
        with g1:
            st.subheader(f"Top 10 Quilometragem — {escolha_mes}")
            top10_km = df_filtrado.nlargest(10, 'Quilometragem')
            fig1 = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', color_discrete_sequence=[AZUL_SOFT])
            fig1.update_traces(texttemplate='%{x:,.0f}', textposition='outside', hovertemplate='Placa: %{y}<br>KM: %{x:,.0f}')
            fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(size=10, color="#AAB"),
                              xaxis=dict(visible=False), yaxis=dict(categoryorder='total ascending', showgrid=False))
            st.plotly_chart(fig1, use_container_width=True)

        with g2:
            st.subheader(f"Top 10 Maiores Custos — {escolha_mes}")
            top10_custo = df_filtrado.nlargest(10, 'Custo de manutenção')
            fig2 = px.bar(top10_custo, x='Custo de manutenção', y='Placa', orientation='h', color_discrete_sequence=[CINZA_SOFT])
            fig2.update_traces(texttemplate='R$ %{x:,.2f}', textposition='outside')
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(size=10, color="#AAB"),
                              xaxis=dict(visible=False), yaxis=dict(categoryorder='total ascending', showgrid=False))
            st.plotly_chart(fig2, use_container_width=True)

        # --- SEÇÃO NOVA: VISUALIZAR TODA A FROTA ---
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔍 Visualizar Lista Completa da Frota (Filtro Atual)"):
            st.markdown("Use a tabela abaixo para pesquisar placas específicas ou ordenar por qualquer coluna.")
            # Formatando para exibição na tabela
            df_display = df_filtrado[['Instituição', 'Base', 'Placa', 'Quilometragem', 'Custo de manutenção']].copy()
            st.dataframe(df_display.style.format({
                'Quilometragem': '{:,.0f}',
                'Custo de manutenção': 'R$ {:,.2f}'
            }), use_container_width=True, height=300)

    with tab_anual:
        st.subheader("Ranking de Bases (Acumulado Jan-Abr)")
        df_base = df_acumulado.groupby("Base").agg({"Custo de manutenção": "sum", "Quilometragem": "sum"}).reset_index()
        
        c_anual1, c_anual2 = st.columns(2)
        with c_anual1:
            fig3 = px.bar(df_base.nlargest(10, 'Custo de manutenção'), x='Custo de manutenção', y='Base', 
                          orientation='h', title="Custos Acumulados por Base", color_discrete_sequence=[CINZA_SOFT])
            fig3.update_traces(texttemplate='R$ %{x:,.2f}', textposition='outside')
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(size=10), xaxis=dict(visible=False))
            st.plotly_chart(fig3, use_container_width=True)

        with c_anual2:
            fig4 = px.bar(df_base.nlargest(10, 'Quilometragem'), x='Quilometragem', y='Base', 
                          orientation='h', title="KM Acumulada por Base", color_discrete_sequence=[AZUL_SOFT])
            fig4.update_traces(texttemplate='%{x:,.0f}', textposition='outside')
            fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(size=10), xaxis=dict(visible=False))
            st.plotly_chart(fig4, use_container_width=True)

except Exception as e:
    st.error(f"Aguardando arquivo de dados ou erro no processamento: {e}")
