import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Gestão de Frotas", layout="wide")

# 2. Estilização CSS (Azul Claro)
st.markdown("""
    <style>
    .stApp { background-color: #E3F2FD; color: #01579B; }
    [data-testid="stSidebar"] { background-color: #BBDEFB; border-right: 1px solid #90CAF9; }
    
    .metric-container {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #90CAF9;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-label { color: #546E7A; font-size: 13px; font-weight: bold; text-transform: uppercase; margin-bottom: 8px; }
    .metric-value { color: #0277BD; font-size: 22px; font-weight: bold; line-height: 1.2; }
    .metric-sub { color: #D32F2F; font-size: 16px; font-weight: bold; margin-top: 5px; }
    
    h1, h2, h3 { color: #01579B !important; }
    
    .stTabs [data-baseweb="tab"] { color: #0277BD; background-color: #E1F5FE; }
    .stTabs [aria-selected="true"] { background-color: #0288D1 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

def draw_metric(label, value, subtext=""):
    sub_html = f'<div class="metric-sub">{subtext}</div>' if subtext else ""
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {sub_html}
        </div>
    """, unsafe_allow_html=True)

# 3. Carregamento e Tratamento
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("manutencao.xlsx")
        df['Mês Referência'] = pd.to_datetime(df['Mês Referência'])
        meses_pt = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
            7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_pt)
        df['Mes_Num'] = df['Mês Referência'].dt.month
        df['Quilometragem'] = pd.to_numeric(df['Quilometragem'], errors='coerce').fillna(0)
        df['Custo de manutenção'] = pd.to_numeric(df['Custo de manutenção'], errors='coerce').fillna(0)
        
        if 'Ano' in df.columns:
            df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(2026).astype(int)
        else:
            df['Ano'] = 2026
        return df
    except Exception as e:
        st.error(f"Erro: {e}")
        return pd.DataFrame()

df = load_data()

# Definição dos Orçamentos Anuais
ORCAMENTOS = {
    "AMES": 987380.00,
    "IAV": 305434.00
}

if not df.empty:
    # 4. Filtros
    st.sidebar.title("🔍 Filtros")
    lista_anos = sorted(df["Ano"].unique(), reverse=True)
    ano_sel = st.sidebar.selectbox("Ano", options=lista_anos)
    
    df_ano = df[df["Ano"] == ano_sel]
    lista_inst = sorted(df_ano["Instituição"].unique())
    inst_sel = st.sidebar.multiselect("Instituição", options=lista_inst, default=lista_inst)
    
    lista_meses_nome = df_ano.sort_values("Mes_Num")["Mes_Nome"].unique()
    mes_sel = st.sidebar.selectbox("Mês", options=lista_meses_nome)
    
    lista_bases = ["Todas"] + list(sorted(df_ano["Base"].unique()))
    base_sel = st.sidebar.selectbox("Base", options=lista_bases)

    # Filtragem Mensal
    df_filtrado = df_ano[(df_ano["Instituição"].isin(inst_sel)) & (df_ano["Mes_Nome"] == mes_sel)]
    if base_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Base"] == base_sel]

    # CÁLCULO DA EXECUÇÃO ORÇAMENTÁRIA (Acumulado)
    mes_num_sel = df_ano[df_ano["Mes_Nome"] == mes_sel]["Mes_Num"].iloc[0]
    
    # Gasto acumulado total de Janeiro até o mês selecionado
    gasto_acumulado_total = df_ano[
        (df_ano["Instituição"].isin(inst_sel)) & 
        (df_ano["Mes_Num"] <= mes_num_sel)
    ]["Custo de manutenção"].sum()
    
    # Orçamento proporcional às instituições selecionadas
    orcamento_total_selecionado = sum(ORCAMENTOS.get(inst, 0) for inst in inst_sel)
    
    percentual_execucao = (gasto_acumulado_total / orcamento_total_selecionado * 100) if orcamento_total_selecionado > 0 else 0

    st.title("📊 Gestão de Frotas")
    st.markdown(f"**Relatório de {mes_sel} de {ano_sel}**")

    # 5. Abas
    tab1, tab2, tab3 = st.tabs(["📌 Visão Mensal", "📈 Evolução Anual", "📑 Dados"])

    with tab1:
        # KPIs
        c1, c2, c3, c4 = st.columns(4)
        km_total_mes = df_filtrado['Quilometragem'].sum()
        custo_mensal = df_filtrado['Custo de manutenção'].sum()

        with c1: 
            draw_metric("Veículos", len(df_filtrado["Placa"].unique()))
        with c2: 
            draw_metric("KM Total no Mês", f"{km_total_mes:,.0f}".replace(",", "."))
        with c3: 
            draw_metric("Custo Manutenção (Mês)", f"R$ {custo_mensal:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with c4: 
            # Mostra o valor em Real e o percentual logo abaixo
            valor_acumulado_str = f"R$ {gasto_acumulado_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            draw_metric("Execução Orçamentária (Ano)", valor_acumulado_str, f"{percentual_execucao:.1f}% consumido")

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráficos de Ranking
        g1, g2 = st.columns(2)
        
        with g1:
            st.subheader("Ranking de Quilometragem da Frota")
            top10_km = df_filtrado.nlargest(10, 'Quilometragem').sort_values('Quilometragem', ascending=True)
            fig_km = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', text='Quilometragem', color_discrete_sequence=['#0288D1'])
            fig_km.update_traces(texttemplate='%{text:,.0f}', textposition='outside', cliponaxis=False)
            fig_km.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#01579B",
                                 margin=dict(r=80), xaxis=dict(range=[0, top10_km['Quilometragem'].max() * 1.2], showticklabels=False, showgrid=False), yaxis=dict(title=""))
            st.plotly_chart(fig_km, use_container_width=True)

        with g2:
            st.subheader("Ranking de Custos de Manutenção da Frota")
            top10_custo = df_filtrado.nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
            fig_custo = px.bar(top10_custo, x='Custo de manutenção', y='Placa', orientation='h', text='Custo de manutenção', color_discrete_sequence=['#D32F2F'])
            fig_custo.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside', cliponaxis=False)
            fig_custo.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#01579B",
                                    margin=dict(r=100), xaxis=dict(range=[0, top10_custo['Custo de manutenção'].max() * 1.3], showticklabels=False, showgrid=False), yaxis=dict(title=""))
            st.plotly_chart(fig_custo, use_container_width=True)

    with tab2:
        st.subheader(f"Evolução Mensal de Custos - {ano_sel}")
        df_acumulado_grafico = df_ano[df_ano["Instituição"].isin(inst_sel)]
        evol_mensal = df_acumulado_grafico.groupby(['Mes_Num', 'Mes_Nome'])['Custo de manutenção'].sum().reset_index().sort_values('Mes_Num')
        
        fig_evol = px.line(evol_mensal, x='Mes_Nome', y='Custo de manutenção', markers=True, text='Custo de manutenção', color_discrete_sequence=['#0288D1'])
        fig_evol.update_traces(texttemplate='R$ %{text:,.2f}', textposition='top center')
        fig_evol.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#01579B", yaxis=dict(title="Valor Gasto (R$)"))
        st.plotly_chart(fig_evol, use_container_width=True)

    with tab3:
        st.subheader("Base de Dados Completa (Filtro Atual)")
        st.dataframe(df_filtrado.drop(columns=['Mes_Num']), use_container_width=True)
else:
    st.info("Aguardando carregamento dos dados...")
