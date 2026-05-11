import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard Gestão de Frotas", layout="wide")

# 2. Estilização CSS (Melhoria UI/UX)
st.markdown("""
    <style>
    .stApp { background-color: #E3F2FD; color: #333333; }
    [data-testid="stSidebar"] { background-color: #BBDEFB; border-right: 1px solid #90CAF9; }
    
    /* Cards de KPI Customizados */
    .metric-container {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #CFD8DC;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .metric-label { color: #546E7A; font-size: 14px; font-weight: 600; text-transform: uppercase; }
    .metric-value { color: #1A237E; font-size: 26px; font-weight: 800; } /* Azul Marinho para contraste */
    .metric-trend { font-size: 14px; font-weight: bold; margin-top: 5px; }
    .trend-up { color: #D32F2F; } /* Vermelho para aumento de custo/km */
    .trend-down { color: #388E3C; } /* Verde para redução */
    
    /* Barra de Progresso do Orçamento */
    .progress-bg { background-color: #eee; border-radius: 10px; width: 100%; height: 10px; margin-top: 10px; }
    .progress-fill { background-color: #F57C00; height: 10px; border-radius: 10px; }

    /* Alinhamento de Títulos */
    h3 { text-align: left !important; color: #1A237E !important; padding-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# Função para formatar moeda/número no padrão BR
def fmt_br(valor, is_moeda=False):
    if is_moeda:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{valor:,.0f}".replace(",", ".")

# Função para desenhar os cards com tendência
def draw_card(label, value, delta=None, is_lower_better=True, progress=None):
    trend_html = ""
    if delta is not None:
        color_class = "trend-down" if (delta <= 0 if is_lower_better else delta >= 0) else "trend-up"
        icon = "↓" if delta <= 0 else "↑"
        trend_html = f'<div class="metric-trend {color_class}">{icon} {abs(delta):.1f}% vs mês ant.</div>'
    
    prog_html = ""
    if progress is not None:
        prog_html = f'<div class="progress-bg"><div class="progress-fill" style="width: {min(progress, 100)}%;"></div></div>'

    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {trend_html}
            {prog_html}
        </div>
    """, unsafe_allow_html=True)

# 3. Carregamento e Tratamento
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("manutencao.xlsx")
        df['Mês Referência'] = pd.to_datetime(df['Mês Referência'])
        meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
                    7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
        df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_pt)
        df['Mes_Num'] = df['Mês Referência'].dt.month
        df['Quilometragem'] = pd.to_numeric(df['Quilometragem'], errors='coerce').fillna(0)
        df['Custo de manutenção'] = pd.to_numeric(df['Custo de manutenção'], errors='coerce').fillna(0)
        df['Ano'] = pd.to_numeric(df.get('Ano', 2026), errors='coerce').fillna(2026).astype(int)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = load_data()
ORCAMENTOS = {"AMES": 987380.00, "IAV": 305434.00}

if not df.empty:
    # 4. Barra Lateral com Espaço para Logo
    # st.sidebar.image("sua_logo.png", width=150) # Descomente quando tiver o arquivo
    st.sidebar.title("📌 Menu de Filtros")
    ano_sel = st.sidebar.selectbox("Ano", options=sorted(df["Ano"].unique(), reverse=True))
    df_ano = df[df["Ano"] == ano_sel]
    
    inst_sel = st.sidebar.multiselect("Instituição", options=sorted(df_ano["Instituição"].unique()), default=sorted(df_ano["Instituição"].unique()))
    mes_sel = st.sidebar.selectbox("Mês Competência", options=df_ano.sort_values("Mes_Num")["Mes_Nome"].unique(), index=len(df_ano["Mes_Nome"].unique())-1)

    # Filtragem
    df_filtrado = df_ano[(df_ano["Instituição"].isin(inst_sel)) & (df_ano["Mes_Nome"] == mes_sel)]
    
    # Cálculo de Tendência (Mês Anterior)
    mes_atual_idx = df_ano[df_ano["Mes_Nome"] == mes_sel]["Mes_Num"].iloc[0]
    df_anterior = df_ano[(df_ano["Instituição"].isin(inst_sel)) & (df_ano["Mes_Num"] == mes_atual_idx - 1)]
    
    def calc_delta(atual, anterior):
        if anterior == 0: return 0
        return ((atual - anterior) / anterior) * 100

    # 5. Dashboard Principal
    st.title("📊 Gestão Estratégica de Frotas")
    
    # Linha de KPIs
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        draw_card("Veículos Ativos", fmt_br(len(df_filtrado["Placa"].unique())))
    
    with k2:
        km_atual = df_filtrado['Quilometragem'].sum()
        km_ant = df_anterior['Quilometragem'].sum()
        draw_card("Quilometragem Mensal", fmt_br(km_atual), delta=calc_delta(km_atual, km_ant), is_lower_better=False)

    with k3:
        custo_atual = df_filtrado['Custo de manutenção'].sum()
        custo_ant = df_anterior['Custo de manutenção'].sum()
        draw_card("Custo de Manutenção", fmt_br(custo_atual, True), delta=calc_delta(custo_atual, custo_ant))

    with k4:
        gasto_acumulado = df_ano[(df_ano["Instituição"].isin(inst_sel)) & (df_ano["Mes_Num"] <= mes_atual_idx)]["Custo de manutenção"].sum()
        orc_total = sum(ORCAMENTOS.get(inst, 0) for inst in inst_sel)
        perc = (gasto_acumulado / orc_total * 100) if orc_total > 0 else 0
        draw_card("Execução Orçamentária", f"{perc:.1f}% consumido", progress=perc)

    st.markdown("<br>", unsafe_allow_html=True)

    # 6. Gráficos de Ranking
    g1, g2 = st.columns(2)

    with g1:
        st.subheader("Ranking de Quilometragem da Frota")
        top10_km = df_filtrado.nlargest(10, 'Quilometragem').sort_values('Quilometragem', ascending=True)
        fig_km = px.bar(top10_km, x='Quilometragem', y='Placa', orientation='h', text='Quilometragem', color_discrete_sequence=['#0288D1'])
        
        # Configuração de Data Viz (Padrão BR e Ocultar Eixos)
        fig_km.update_traces(texttemplate='%{text:,.0f}', textposition='outside', cliponaxis=False)
        fig_km.update_layout(
            separators=',.', # Define padrão brasileiro para o Plotly
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=100, t=20, b=0),
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, top10_km['Quilometragem'].max() * 1.2]),
            yaxis=dict(title="", tickfont=dict(size=12, color='#333'))
        )
        st.plotly_chart(fig_km, use_container_width=True, config={'displayModeBar': False})

    with g2:
        st.subheader("Ranking de Custos de Manutenção")
        top10_custo = df_filtrado.nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
        fig_custo = px.bar(top10_custo, x='Custo de manutenção', y='Placa', orientation='h', text='Custo de manutenção', color_discrete_sequence=['#F57C00'])
        
        # Configuração de Data Viz (Moeda BRL e Ocultar Eixos)
        fig_custo.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside', cliponaxis=False)
        fig_custo.update_layout(
            separators=',.',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=120, t=20, b=0),
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, top10_custo['Custo de manutenção'].max() * 1.3]),
            yaxis=dict(title="", tickfont=dict(size=12, color='#333'))
        )
        st.plotly_chart(fig_custo, use_container_width=True, config={'displayModeBar': False})

    # Tabela detalhada expansível
    with st.expander("📑 Visualizar Base de Dados Detalhada"):
        st.dataframe(df_filtrado.drop(columns=['Mes_Num', 'Ano']), use_container_width=True)
