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
    
    # --- TRATAMENTO DE DATAS ---
    # Converte a coluna para data real e cria uma coluna com o nome do mês
    df['Mês Referência'] = pd.to_datetime(df['Mês Referência'])
    meses_map = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_map)

    # --- SIDEBAR / FILTROS ---
    st.sidebar.markdown("### Filtros Estratégicos")
    
    # Filtro Instituição
    escolha_inst = st.sidebar.selectbox("Instituição", ["Todos", "AMES", "IAV"])
    
    # Filtro Mês (Limitado aos solicitados)
    opcoes_meses = ["Janeiro", "Fevereiro", "Março", "Abril"]
    escolha_mes = st.sidebar.selectbox("Mês de Referência", opcoes_meses)
    
    # Filtro Base
    bases_disponiveis = sorted(df["Base"].unique())
    escolha_base = st.sidebar.selectbox("Base Operacional", ["Todas"] + bases_disponiveis)

    # --- LÓGICA DE FILTRAGEM ---
    # 1. Filtro de Mês
    df_mes = df[df["Mes_Nome"] == escolha_mes]
    
    # 2. Filtro de Instituição (Afeta Mensal e Acumulado)
    if escolha_inst != "Todos":
        df_mes = df_mes[df_mes["Instituição"] == escolha_inst]
        df_total = df[df["Instituição"] == escolha_inst]
    else:
        df_total = df.copy()
        
    # 3. Filtro de Base (Apenas para o Mensal)
    if escolha_base != "Todas":
        df_mes = df_mes[df_mes["Base"] == escolha_base]

    # --- LAYOUT PRINCIPAL ---
    st.title("Sistema de Gestão de Frotas — Inteligência Operacional")
    st.markdown("<br>", unsafe_allow_html=True)

    tab_mensal, tab_anual = st.tabs(["📊 Visão Mensal", "📈 Acumulado Estratégico"])

    # Cores
    AZUL_SOFT = "#81A1C1"
    CINZA_SOFT = "#4C566A"

    with tab_mensal:
        if df_mes.empty:
            st.warning(f"Sem dados para {escolha_mes} com os filtros atuais.")
        else:
            # Métricas
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                draw_metric("Frota Ativa", f"{len(df_mes['Placa'].unique())}")
            with m2:
                draw_metric("KM Rodados", f"{df_mes['Quilometragem'].sum():,.0f}".replace(",", "."))
            with m3:
                custo_m = df_mes['Custo de manutenção'].sum()
                draw_metric("Investimento", f"R$ {custo_m:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            with m4:
                media_km = df_mes['Quilometragem'].mean()
                draw_metric("Média KM/Veículo", f"{media_km:,.0f}".replace(",", "."))

            st.markdown("<br>", unsafe_allow_html=True)

            # Gráficos Top 10
            g1, g2 = st.columns(2)
            with g1:
                st.subheader("Top 10 Quilometragem (Placa)")
                top10_km = df_mes.nlargest(10, 'Quilometragem')
                fig1 = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', color_discrete_sequence=[AZUL_SOFT])
                fig1.update_traces(texttemplate='%{x:,.0f}', textposition='outside')
                fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#AAB"), xaxis=dict(visible=False), yaxis=dict(categoryorder='total ascending'))
                st.plotly_chart(fig1, use_container_width=True)

            with g2:
                st.subheader("Top 10 Maiores Custos (Placa)")
                top10_custo = df_mes.nlargest(10, 'Custo de manutenção')
                fig2 = px.bar(top10_custo, x='Custo de manutenção', y='Placa', orientation='h', color_discrete_sequence=[CINZA_SOFT])
                fig2.update_traces(texttemplate='R$ %{x:,.2f}', textposition='outside')
                fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#AAB"), xaxis=dict(visible=False), yaxis=dict(categoryorder='total ascending'))
                st.plotly_chart(fig2, use_container_width=True)

            with st.expander("🔍 Visualizar Lista Completa da Frota"):
                st.dataframe(df_mes[['Instituição', 'Base', 'Placa', 'Quilometragem', 'Custo de manutenção']].style.format({
                    'Quilometragem': '{:,.0f}', 'Custo de manutenção': 'R$ {:,.2f}'
                }), use_container_width=True)

    with tab_anual:
        st.subheader("Ranking Geral de Bases (Acumulado Jan-Abr)")
        
        # Filtramos o acumulado apenas para os meses desejados
        df_rank = df_total[df_total['Mes_Nome'].isin(opcoes_meses)]
        df_base = df_rank.groupby("Base").agg({"Custo de manutenção": "sum", "Quilometragem": "sum"}).reset_index()
        
        c_anual1, c_anual2 = st.columns(2)
        with c_anual1:
            st.markdown("#### Top 10 Bases por Custo")
            fig3 = px.bar(df_base.nlargest(10, 'Custo de manutenção'), x='Custo de manutenção', y='Base', 
                          orientation='h', color_discrete_sequence=[CINZA_SOFT])
            fig3.update_traces(texttemplate='R$ %{x:,.2f}', textposition='outside')
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#AAB"), xaxis=dict(visible=False), yaxis=dict(categoryorder='total ascending'))
            st.plotly_chart(fig3, use_container_width=True)

        with c_anual2:
            st.markdown("#### Top 10 Bases por Quilometragem")
            fig4 = px.bar(df_base.nlargest(10, 'Quilometragem'), x='Quilometragem', y='Base', 
                          orientation='h', color_discrete_sequence=[AZUL_SOFT])
            fig4.update_traces(texttemplate='%{x:,.0f}', textposition='outside')
            fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#AAB"), xaxis=dict(visible=False), yaxis=dict(categoryorder='total ascending'))
            st.plotly_chart(fig4, use_container_width=True)

except Exception as e:
    st.error(f"Ocorreu um erro: {e}")
