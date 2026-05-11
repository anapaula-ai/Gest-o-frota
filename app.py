import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Gestão de Frotas", layout="wide")

# 2. Estilização CSS (Layout Azul Claro)
st.markdown("""
    <style>
    /* Fundo Principal */
    .stApp {
        background-color: #E3F2FD;
        color: #01579B;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #BBDEFB;
        border-right: 1px solid #90CAF9;
    }

    /* Cards de Métricas */
    .metric-container {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #90CAF9;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .metric-label {
        color: #546E7A;
        font-size: 14px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .metric-value {
        color: #0277BD;
        font-size: 28px;
        font-weight: bold;
    }

    /* Títulos e Textos */
    h1, h2, h3, p {
        color: #01579B !important;
    }

    /* Ajuste de abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #0277BD;
        background-color: #E1F5FE;
        border-radius: 5px 5px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0288D1 !important;
        color: white !important;
    }
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
        
        # Garantir que Mês Referência seja string ou data
        df['Mês Referência'] = pd.to_datetime(df['Mês Referência'])
        
        # Criar coluna com Nome do Mês em Português
        meses_pt = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
            7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_pt)
        df['Mes_Num'] = df['Mês Referência'].dt.month
        
        # Converter colunas numéricas
        df['Quilometragem'] = pd.to_numeric(df['Quilometragem'], errors='coerce').fillna(0)
        df['Custo de manutenção'] = pd.to_numeric(df['Custo de manutenção'], errors='coerce').fillna(0)
        
        # Trata coluna Ano
        if 'Ano' in df.columns:
            df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(2026).astype(int)
        else:
            df['Ano'] = 2026
            
        return df
    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 4. Filtros na Barra Lateral
    st.sidebar.title("🔍 Filtros")
    
    lista_anos = sorted(df["Ano"].unique(), reverse=True)
    ano_sel = st.sidebar.selectbox("Ano", options=lista_anos)
    
    df_ano = df[df["Ano"] == ano_sel]
    
    lista_inst = sorted(df_ano["Instituição"].unique())
    inst_sel = st.sidebar.multiselect("Instituição", options=lista_inst, default=lista_inst)
    
    # Filtro de Mês pelo Nome
    lista_meses_nome = df_ano.sort_values("Mes_Num")["Mes_Nome"].unique()
    mes_sel = st.sidebar.selectbox("Mês", options=lista_meses_nome)
    
    lista_bases = ["Todas"] + list(sorted(df_ano["Base"].unique()))
    base_sel = st.sidebar.selectbox("Base", options=lista_bases)

    # Filtragem Final
    df_filtrado = df_ano[(df_ano["Instituição"].isin(inst_sel)) & (df_ano["Mes_Nome"] == mes_sel)]
    if base_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Base"] == base_sel]

    st.title("📊 Gestão de Frotas")
    st.markdown(f"**Relatório de {mes_sel} de {ano_sel}**")

    # 5. Abas
    tab1, tab2, tab3 = st.tabs(["📌 Visão Mensal", "📈 Evolução Anual", "📑 Dados"])

    with tab1:
        # Métricas
        c1, c2, c3, c4 = st.columns(4)
        km_total = df_filtrado['Quilometragem'].sum()
        custo_total = df_filtrado['Custo de manutenção'].sum()
        custo_km = custo_total / km_total if km_total > 0 else 0

        with c1: draw_metric("Veículos", len(df_filtrado["Placa"].unique()))
        with c2: draw_metric("KM Total", f"{km_total:,.0f}".replace(",", "."))
        with c3: draw_metric("Custo Total", f"R$ {custo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with c4: draw_metric("R$ por KM", f"R$ {custo_km:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.markdown("<br>", unsafe_allow_html=True)

        g1, g2 = st.columns(2)
        with g1:
            st.subheader("Top 10 KM por Placa")
            top10_km = df_filtrado.nlargest(10, 'Quilometragem').sort_values('Quilometragem', ascending=True)
            fig_km = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', 
                            text='Quilometragem', color_discrete_sequence=['#0288D1'])
            fig_km.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
            fig_km.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#01579B")
            st.plotly_chart(fig_km, use_container_width=True)

        with g2:
            st.subheader("Top 10 Custos por Placa")
            top10_custo = df_filtrado.nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
            fig_custo = px.bar(top10_custo, x='Custo de manutenção', y='Placa', orientation='h', 
                               text='Custo de manutenção', color_discrete_sequence=['#D32F2F'])
            fig_custo.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside')
            fig_custo.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#01579B")
            st.plotly_chart(fig_custo, use_container_width=True)

    with tab2:
        st.subheader(f"Evolução dos Custos - {ano_sel}")
        df_acumulado = df_ano[df_ano["Instituição"].isin(inst_sel)]
        evol_mensal = df_acumulado.groupby(['Mes_Num', 'Mes_Nome'])['Custo de manutenção'].sum().reset_index().sort_values('Mes_Num')
        
        fig_evol = px.line(evol_mensal, x='Mes_Nome', y='Custo de manutenção', markers=True, 
                           text='Custo de manutenção', color_discrete_sequence=['#0288D1'])
        fig_evol.update_traces(texttemplate='R$ %{text:,.2f}', textposition='top center')
        fig_evol.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#01579B", yaxis_title="Custo Total")
        st.plotly_chart(fig_evol, use_container_width=True)

    with tab3:
        st.subheader("Base de Dados Completa")
        st.dataframe(df_filtrado.drop(columns=['Mes_Num']), use_container_width=True)

else:
    st.info("Carregue o arquivo 'manutencao.xlsx' para visualizar os dados.")
