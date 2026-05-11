import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Gestão de Frotas", layout="wide")

# 2. Estilização CSS (Design Corporativo)
st.markdown("""
    <style>
    .stApp { background-color: #E3F2FD; color: #01579B; }
    [data-testid="stSidebar"] { background-color: #BBDEFB; border-right: 1px solid #90CAF9; }
    
    /* Estilo dos Cards */
    .metric-container {
        background-color: #FFFFFF;
        padding: 35px; /* Padding interno aumentado */
        border-radius: 15px;
        border: 1px solid #CFD8DC;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.03); /* Sombra muito leve */
        min-height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-label { 
        color: #546E7A; 
        font-size: 15px; 
        font-weight: bold; 
        text-transform: none; /* Mantém como digitado */
        margin-bottom: 10px;
    }
    .metric-value { 
        color: #0277BD; 
        font-size: 28px; 
        font-weight: 900; 
        line-height: 1.1;
    }
    .metric-sub { 
        color: #E65100; /* Laranja para o destaque do consumo */
        font-size: 15px; 
        font-weight: 600; 
        margin-top: 8px; 
    }
    
    /* Títulos e Espaçamento */
    h1, h2, h3 { color: #01579B !important; margin-bottom: 5px !important; }
    
    /* Ajuste de Abas */
    .stTabs [data-baseweb="tab"] { color: #0277BD; background-color: #E1F5FE; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #0288D1 !important; color: white !important; }
    
    /* Diminuir espaço entre elementos do Streamlit */
    .block-container { padding-top: 2rem; }
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

# Orçamentos
ORCAMENTOS = {"AMES": 987380.00, "IAV": 305434.00}

if not df.empty:
    # 4. Filtros
    st.sidebar.title("🔍 Filtros de Gestão")
    ano_sel = st.sidebar.selectbox("Ano", options=sorted(df["Ano"].unique(), reverse=True))
    df_ano = df[df["Ano"] == ano_sel]
    
    inst_sel = st.sidebar.multiselect("Instituição", options=sorted(df_ano["Instituição"].unique()), default=sorted(df_ano["Instituição"].unique()))
    mes_sel = st.sidebar.selectbox("Mês", options=df_ano.sort_values("Mes_Num")["Mes_Nome"].unique())
    base_sel = st.sidebar.selectbox("Base", options=["Todas"] + list(sorted(df_ano["Base"].unique())))

    # Lógica de Filtros
    df_filtrado = df_ano[(df_ano["Instituição"].isin(inst_sel)) & (df_ano["Mes_Nome"] == mes_sel)]
    if base_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Base"] == base_sel]

    # Cálculo Execução (Acumulado)
    mes_num_sel = df_ano[df_ano["Mes_Nome"] == mes_sel]["Mes_Num"].iloc[0]
    gasto_acumulado = df_ano[(df_ano["Instituição"].isin(inst_sel)) & (df_ano["Mes_Num"] <= mes_num_sel)]["Custo de manutenção"].sum()
    orcamento_total = sum(ORCAMENTOS.get(inst, 0) for inst in inst_sel)
    perc_exec = (gasto_acumulado / orcamento_total * 100) if orcamento_total > 0 else 0

    st.title("📊 Gestão de Frotas")
    st.markdown(f"**Competência: {mes_sel} / {ano_sel}**")

    tab1, tab2, tab3 = st.tabs(["📌 Mensal", "📈 Evolução Anual", "📑 Base de Dados"])

    with tab1:
        # Linha de KPIs
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            draw_metric("Veículos Ativos", len(df_filtrado["Placa"].unique()))
        with c2:
            draw_metric("Quilometragem mensal", f"{df_filtrado['Quilometragem'].sum():,.0f}".replace(",", "."))
        with c3:
            custo_m = df_filtrado['Custo de manutenção'].sum()
            draw_metric("Custo de Manutenção mensal", f"R$ {custo_m:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with c4:
            valor_ac = f"R$ {gasto_acumulado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            draw_metric("Execução Orçamentária anual", valor_ac, f"{perc_exec:.1f}% do orçamento consumido".replace(".", ","))

        # Espaço reduzido entre KPIs e Gráficos
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # Gráficos
        g1, g2 = st.columns(2)
        
        with g1:
            st.subheader("Ranking de Quilometragem da Frota")
            top10_km = df_filtrado.nlargest(10, 'Quilometragem').sort_values('Quilometragem', ascending=True)
            fig_km = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', text='Quilometragem', color_discrete_sequence=['#0288D1'])
            fig_km.update_traces(texttemplate='%{text:,.0f}', textposition='outside', cliponaxis=False)
            fig_km.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#01579B",
                margin=dict(l=0, r=80, t=30, b=0), # Alinhamento à esquerda
                xaxis=dict(range=[0, top10_km['Quilometragem'].max() * 1.2], showticklabels=False, showgrid=False),
                yaxis=dict(title="")
            )
            st.plotly_chart(fig_km, use_container_width=True)

        with g2:
            st.subheader("Ranking de Custos de Manutenção da Frota")
            top10_custo = df_filtrado.nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
            fig_custo = px.bar(top10_custo, x='Custo de manutenção', y='Placa', orientation='h', text='Custo de manutenção', color_discrete_sequence=['#F57C00']) # Laranja Corporativo
            fig_custo.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside', cliponaxis=False)
            fig_custo.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#01579B",
                margin=dict(l=0, r=100, t=30, b=0), # Alinhamento à esquerda
                xaxis=dict(range=[0, top10_custo['Custo de manutenção'].max() * 1.3], showticklabels=False, showgrid=False),
                yaxis=dict(title="")
            )
            st.plotly_chart(fig_custo, use_container_width=True)

    with tab2:
        st.subheader(f"Evolução Mensal de Custos - {ano_sel}")
        df_acumulado_grafico = df_ano[df_ano["Instituição"].isin(inst_sel)]
        evol_mensal = df_acumulado_grafico.groupby(['Mes_Num', 'Mes_Nome'])['Custo de manutenção'].sum().reset_index().sort_values('Mes_Num')
        fig_evol = px.line(evol_mensal, x='Mes_Nome', y='Custo de manutenção', markers=True, text='Custo de manutenção', color_discrete_sequence=['#0288D1'])
        fig_evol.update_traces(texttemplate='R$ %{text:,.2f}', textposition='top center')
        fig_evol.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#01579B", margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_evol, use_container_width=True)

    with tab3:
        st.subheader("Base de Dados Completa")
        st.dataframe(df_filtrado.drop(columns=['Mes_Num']), use_container_width=True)
else:
    st.info("Aguardando o arquivo 'manutencao.xlsx' no repositório.")
