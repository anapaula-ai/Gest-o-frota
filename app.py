import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Gestão de Frotas Premium", layout="wide")

# 2. CSS Sophisticated Grey Layout
st.markdown("""
    <style>
    .stApp { background-color: #1A1C23; color: #ECEFF4; font-size: 13px; }
    [data-testid="stSidebar"] { background-color: #111217; border-right: 1px solid #2D3139; }
    .metric-card {
        background-color: #242731; padding: 15px; border-radius: 10px;
        border: 1px solid #333745; text-align: center;
    }
    .metric-label { color: #9BA1B0; font-size: 11px; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 8px; }
    .metric-value { color: #FFFFFF; font-size: 22px; font-weight: 600; }
    h1 { font-size: 22px !important; color: #FFFFFF !important; }
    h2, h3 { font-size: 16px !important; color: #D8DEE9 !important; }
    .stTabs [aria-selected="true"] { color: #FFFFFF !important; border-bottom: 2px solid #5E81AC !important; }
    </style>
    """, unsafe_allow_html=True)

def draw_metric(label, value):
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

# 3. Processamento de Dados
try:
    df = pd.read_excel("manutencao.xlsx")
    
    # --- LIMPEZA DE DADOS (Para evitar erro de meses) ---
    # Garantimos que a coluna de mês seja tratada como string e sem espaços
    df["Mês Referência"] = df["Mês Referência"].astype(str).str.strip()

    # --- SIDEBAR / FILTROS ---
    st.sidebar.markdown("### Filtros Estratégicos")
    
    # Filtro Instituição
    opcoes_inst = ["Todos", "AMES", "IAV"]
    escolha_inst = st.sidebar.selectbox("Instituição", opcoes_inst)
    
    # Filtro Mês - CAPTURANDO DINAMICAMENTE DO EXCEL PARA NÃO DAR ERRO
    meses_no_excel = sorted(df["Mês Referência"].unique())
    escolha_mes = st.sidebar.selectbox("Mês de Referência", meses_no_excel)
    
    # Filtro Base
    bases_disponiveis = sorted(df["Base"].unique())
    escolha_base = st.sidebar.selectbox("Base Operacional", ["Todas"] + bases_disponiveis)

    # --- LÓGICA DE FILTRAGEM ---
    # 1. Filtro de Mês (Sempre aplicado)
    df_filtrado = df[df["Mês Referência"] == escolha_mes]
    
    # 2. Filtro de Instituição
    if escolha_inst != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Instituição"] == escolha_inst]
        
    # 3. Filtro de Base
    if escolha_base != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Base"] == escolha_base]

    # --- LAYOUT PRINCIPAL ---
    st.title("Sistema de Gestão de Frotas — Inteligência Operacional")
    st.markdown("<br>", unsafe_allow_html=True)

    if df_filtrado.empty:
        st.warning(f"⚠️ Não foram encontrados dados para o mês {escolha_mes} com os filtros selecionados.")
    else:
        tab_mensal, tab_anual = st.tabs(["📊 Visão Mensal", "📈 Acumulado Estratégico"])

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
                media_km = df_filtrado['Quilometragem'].mean()
                draw_metric("Média KM/Veículo", f"{media_km:,.0f}".replace(",", "."))

            st.markdown("<br>", unsafe_allow_html=True)

            # Gráficos Top 10
            g1, g2 = st.columns(2)
            with g1:
                st.subheader("Top 10 Quilometragem")
                top10_km = df_filtrado.nlargest(10, 'Quilometragem')
                fig1 = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', color_discrete_sequence=['#81A1C1'])
                fig1.update_traces(texttemplate='%{x:,.0f}', textposition='outside')
                fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#AAB"), xaxis=dict(visible=False), yaxis=dict(categoryorder='total ascending'))
                st.plotly_chart(fig1, use_container_width=True)

            with g2:
                st.subheader("Top 10 Maiores Custos")
                top10_custo = df_filtrado.nlargest(10, 'Custo de manutenção')
                fig2 = px.bar(top10_custo, x='Custo de manutenção', y='Placa', orientation='h', color_discrete_sequence=['#4C566A'])
                fig2.update_traces(texttemplate='R$ %{x:,.2f}', textposition='outside')
                fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#AAB"), xaxis=dict(visible=False), yaxis=dict(categoryorder='total ascending'))
                st.plotly_chart(fig2, use_container_width=True)

            # Seção Frota Completa
            with st.expander("🔍 Visualizar Lista Completa da Frota"):
                st.dataframe(df_filtrado[['Instituição', 'Base', 'Placa', 'Quilometragem', 'Custo de manutenção']].style.format({
                    'Quilometragem': '{:,.0f}', 'Custo de manutenção': 'R$ {:,.2f}'
                }), use_container_width=True)

        with tab_anual:
            # Acumulado considerando todos os meses carregados
            st.subheader("Ranking de Bases (Acumulado)")
            df_base = df.groupby("Base").agg({"Custo de manutenção": "sum", "Quilometragem": "sum"}).reset_index()
            # ... (resto do código de gráficos do acumulado)

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
