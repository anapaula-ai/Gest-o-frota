import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Gestão de Frotas AMES/IAV", layout="wide")

# 2. Estilização CSS Black Premium
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #222; }
    .metric-card {
        background-color: #111111;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #333;
        text-align: center;
    }
    .metric-label { color: #888; font-size: 14px; margin-bottom: 5px; text-transform: uppercase; }
    .metric-value { color: #ffffff; font-size: 26px; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { color: #888; }
    .stTabs [aria-selected="true"] { color: #FF0000 !important; border-bottom-color: #FF0000 !important; }
    </style>
    """, unsafe_allow_html=True)

def draw_metric(label, value):
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

# 3. Carregamento de Dados
try:
    df = pd.read_excel("manutencao.xlsx")

    # --- FILTROS SIDEBAR ---
    st.sidebar.header("Filtros de Gestão")
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

    df_ano = df[df["Instituição"].isin(escolha_inst)] # Acumulado ignora o mês, mas respeita a instituição

    st.title("🛡️ Gestão de Frotas (AMES / IAV)")
    st.markdown("---")

    tab_mensal, tab_anual = st.tabs(["📊 Controle Mensal", "📅 Acumulado Anual"])

    # --- ABA MENSAL ---
    with tab_mensal:
        c1, c2, c3 = st.columns(3)
        with c1:
            draw_metric("Veículos na Base", f"{len(df_mes['Placa'].unique())}")
        with c2:
            draw_metric("KM Total Mensal", f"{df_mes['Quilometragem'].sum():,.0f}".replace(",", "."))
        with c3:
            draw_metric("Custo Manutenção", f"R$ {df_mes['Custo de manutenção'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.markdown("<br>", unsafe_allow_html=True)
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.subheader("Top 10 Quilometragem por Placa")
            top10_km_placa = df_mes.nlargest(10, 'Quilometragem')
            fig1 = px.bar(top10_km_placa, x='Quilometragem', y='Placa', orientation='h', 
                          text_auto='.2s', color_discrete_sequence=['#3366FF'])
            fig1.update_traces(textposition='outside', cliponaxis=False)
            fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white",
                              xaxis=dict(showgrid=False), yaxis=dict(categoryorder='total ascending'))
            st.plotly_chart(fig1, use_container_width=True)

        with col_g2:
            st.subheader("Top 10 Custos por Placa")
            top10_custo_placa = df_mes.nlargest(10, 'Custo de manutenção')
            fig2 = px.bar(top10_custo_placa, x='Custo de manutenção', y='Placa', orientation='h', 
                          text_auto='.2s', color_discrete_sequence=['#FF3333'])
            fig2.update_traces(textposition='outside', cliponaxis=False)
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white",
                              xaxis=dict(showgrid=False), yaxis=dict(categoryorder='total ascending'))
            st.plotly_chart(fig2, use_container_width=True)

    # --- ABA ACUMULADO ANUAL ---
    with tab_anual:
        st.subheader("Ranking Geral de Bases (Acumulado Anual)")
        
        c_anual1, c_anual2 = st.columns(2)
        
        # Agrupando por Base para o Acumulado
        df_base_ranking = df_ano.groupby("Base").agg({
            "Custo de manutenção": "sum",
            "Quilometragem": "sum"
        }).reset_index()

        with c_anual1:
            st.markdown("#### 10 Bases com Maior Custo (Anual)")
            top10_base_custo = df_base_ranking.nlargest(10, 'Custo de manutenção')
            fig3 = px.bar(top10_base_custo, x='Custo de manutenção', y='Base', orientation='h',
                          text_auto='.2s', color_discrete_sequence=['#E8C21E']) # Cor Dourada/Premium
            fig3.update_traces(textposition='outside', cliponaxis=False)
            fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white",
                              yaxis=dict(categoryorder='total ascending'))
            st.plotly_chart(fig3, use_container_width=True)

        with c_anual2:
            st.markdown("#### 10 Bases com Maior Rodagem (Anual)")
            top10_base_km = df_base_ranking.nlargest(10, 'Quilometragem')
            fig4 = px.bar(top10_base_km, x='Quilometragem', y='Base', orientation='h',
                          text_auto='.2s', color_discrete_sequence=['#00CC96']) # Cor Verde
            fig4.update_traces(textposition='outside', cliponaxis=False)
            fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white",
                              yaxis=dict(categoryorder='total ascending'))
            st.plotly_chart(fig4, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao processar: {e}")
