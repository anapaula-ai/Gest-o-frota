import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Gestão de Frotas Premium", layout="wide")

# 2. Estilização CSS (Black Premium)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: white; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #333; }
    
    /* Cards de Métricas */
    .metric-container {
        background-color: #111111;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333333;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    .metric-label { color: #888888; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { color: #ffffff; font-size: 26px; font-weight: bold; margin-top: 5px; }
    
    /* Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        color: #888; 
        background-color: #0a0a0a; 
        border-radius: 5px 5px 0 0;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { color: #FF4B4B !important; border-bottom: 2px solid #FF4B4B !important; }
    </style>
    """, unsafe_allow_html=True)

def draw_metric(label, value):
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)

# 3. Carregamento e Tratamento de Dados
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("manutencao.xlsx")
        
        # Converter colunas para numérico
        df['Quilometragem'] = pd.to_numeric(df['Quilometragem'], errors='coerce').fillna(0)
        df['Custo de manutenção'] = pd.to_numeric(df['Custo de manutenção'], errors='coerce').fillna(0)
        
        # Ordem dos meses
        meses_map = {
            'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4, 'Maio': 5, 'Junho': 6,
            'Julho': 7, 'Agosto': 8, 'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
        }
        df['Mes_Num'] = df['Mês Referência'].map(meses_map)
        
        # Trata a coluna Ano que você adicionou
        if 'Ano' in df.columns:
            df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(2026).astype(int)
        else:
            df['Ano'] = 2026
            
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 4. Filtros na Barra Lateral
    st.sidebar.title("💎 Filtros de Gestão")
    
    lista_anos = sorted(df["Ano"].unique(), reverse=True)
    ano_sel = st.sidebar.selectbox("Ano", options=lista_anos)
    
    # Filtra o DF apenas pelo ano para alimentar os outros filtros
    df_ano_base = df[df["Ano"] == ano_sel]
    
    lista_instituicao = sorted(df_ano_base["Instituição"].unique())
    inst_sel = st.sidebar.multiselect("Instituição", options=lista_instituicao, default=lista_instituicao)
    
    lista_meses = df_ano_base["Mês Referência"].unique()
    mes_sel = st.sidebar.selectbox("Mês de Referência", options=lista_meses)
    
    lista_bases = ["Todas"] + list(sorted(df_ano_base["Base"].unique()))
    base_sel = st.sidebar.selectbox("Base Operacional", options=lista_bases)

    # Aplicação final dos Filtros para os Gráficos
    df_filtrado = df_ano_base[(df_ano_base["Instituição"].isin(inst_sel)) & (df_ano_base["Mês Referência"] == mes_sel)]
    if base_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Base"] == base_sel]

    # 5. Título Principal
    st.title("📊 Dashboard Gestão de Frotas")
    st.markdown(f"**Análise de {mes_sel} / {ano_sel}**")
    st.markdown("---")

    # 6. Organização por Abas
    tab1, tab2, tab3 = st.tabs(["📌 Mensal", "📈 Acumulado Anual", "📑 Base de Dados"])

    with tab1:
        m1, m2, m3, m4 = st.columns(4)
        
        veiculos_total = len(df_filtrado["Placa"].unique())
        km_total = df_filtrado['Quilometragem'].sum()
        custo_total = df_filtrado['Custo de manutenção'].sum()
        custo_km = custo_total / km_total if km_total > 0 else 0

        with m1: draw_metric("Veículos Ativos", veiculos_total)
        with m2: draw_metric("KM Rodados", f"{km_total:,.0f}".replace(",", "."))
        with m3: draw_metric("Investimento", f"R$ {custo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with m4: draw_metric("Custo por KM", f"R$ {custo_km:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.markdown("<br>", unsafe_allow_html=True)

        g1, g2 = st.columns(2)
        with g1:
            st.subheader("Top 10 KM por Placa")
            top10_km = df_filtrado.nlargest(10, 'Quilometragem').sort_values('Quilometragem', ascending=True)
            fig_km = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', text_auto='.2s', color_discrete_sequence=['#4B4BFF'])
            fig_km.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=450)
            st.plotly_chart(fig_km, use_container_width=True)

        with g2:
            st.subheader("Top 10 Custos por Placa")
            top10_custo = df_filtrado.nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
            fig_custo = px.bar(top10_custo, x='Custo de manutenção', y='Placa', orientation='h', text_auto='.2s', color_discrete_sequence=['#FF4B4B'])
            fig_custo.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=450)
            st.plotly_chart(fig_custo, use_container_width=True)

    with tab2:
        st.subheader(f"Tendência e Distribuição - Ano {ano_sel}")
        df_ano_acumulado = df[(df["Ano"] == ano_sel) & (df["Instituição"].isin(inst_sel))]
        
        evolucao_mensal = df_ano_acumulado.groupby(['Mes_Num', 'Mês Referência'])['Custo de manutenção'].sum().reset_index().sort_values('Mes_Num')
        fig_evol = px.line(evolucao_mensal, x='Mês Referência', y='Custo de manutenção', markers=True, color_discrete_sequence=['#FF4B4B'])
        fig_evol.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_evol, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            custo_base = df_ano_acumulado.groupby("Base")["Custo de manutenção"].sum().reset_index()
            fig_pie = px.pie(custo_base, values='Custo de manutenção', names='Base', hole=.4, template="plotly_dark")
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            st.dataframe(evolucao_mensal[['Mês Referência', 'Custo de manutenção']].style.format({"Custo de manutenção": "R$ {:,.2f}"}), use_container_width=True)

    with tab3:
        st.subheader("Visualização dos Dados")
        st.dataframe(df_filtrado, use_container_width=True)
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar em CSV", data=csv, file_name=f"frota_{mes_sel}.csv", mime="text/csv")

else:
    st.warning("⚠️ Aguardando dados do arquivo 'manutencao.xlsx'.")
