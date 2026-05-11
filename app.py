import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata

# 1. Configuração da Página
st.set_page_config(page_title="Gestão Estratégica de Frotas", layout="wide")

# 2. Estilização CSS (Layout Looker Studio)
st.markdown("""
    <style>
    .stApp { background-color: #E3F2FD !important; }
    [data-testid="stSidebar"] { background-color: #BBDEFB !important; border-right: 1px solid #90CAF9; }
    h1, h2, h3, p, span, label { color: #1A237E !important; }
    .metric-container {
        background-color: #FFFFFF !important;
        padding: 15px; border-radius: 12px; border: 1px solid #CFD8DC;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05); min-height: 140px;
        display: flex; flex-direction: column; justify-content: center; margin-bottom: 10px;
    }
    .metric-label { color: #546E7A !important; font-size: 10px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px;}
    .metric-value { color: #1A237E !important; font-size: 20px; font-weight: 800; line-height: 1.1; }
    .chart-title { height: 45px; display: flex; align-items: center; font-size: 16px; font-weight: 700; color: #1A237E !important; margin-bottom: 10px; }
    .progress-bg { background-color: #EEEEEE !important; border-radius: 10px; width: 100%; height: 8px !important; margin-top: 8px; overflow: hidden; border: 1px solid #E0E0E0; }
    .progress-fill { background-color: #F57C00 !important; height: 8px !important; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: #1A237E !important; font-weight: 600; }
    .stTabs [aria-selected="true"] { border-bottom: 3px solid #F57C00 !important; }
    </style>
    """, unsafe_allow_html=True)

# Funções de Formatação
def fmt_br(valor, is_moeda=False):
    if is_moeda: return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{valor:,.0f}".replace(",", ".")

def draw_card(label, value, subtext="", progress=None):
    prog_html = f'<div class="progress-bg"><div class="progress-fill" style="width: {min(progress, 100)}%;"></div></div>' if progress is not None else ""
    st.markdown(f"""<div class="metric-container"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div style="color:#333; font-size:11px;">{subtext}</div>{prog_html}</div>""", unsafe_allow_html=True)

def normalizar_coluna(col):
    col = str(col).lower().strip()
    col = unicodedata.normalize('NFKD', col).encode('ascii', 'ignore').decode('utf-8')
    return col

# 3. Carregamento de Dados
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_excel("manutencao.xlsx")
        # Normaliza nomes de colunas (tira acentos, espaços e deixa minúsculo)
        df.columns = [normalizar_coluna(c) for c in df.columns]
        
        # Mapeamento para nomes padrão que o código usa
        mapa = {
            'manutencao': 'custo_manutencao',
            'combustivel': 'custo_combustivel',
            'instituicao': 'instituicao',
            'referencia': 'data'
        }
        # Tenta renomear se encontrar colunas parecidas
        for original in df.columns:
            for chave, novo_nome in mapa.items():
                if chave in original:
                    df = df.rename(columns={original: novo_nome})

        # Conversão numérica
        for c in ['custo_combustivel', 'custo_manutencao', 'km']:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            else:
                df[c] = 0.0

        # Tratamento de Data
        col_data = 'data' if 'data' in df.columns else [c for c in df.columns if 'refer' in c or 'mes' in c][0]
        df['data_dt'] = pd.to_datetime(df[col_data])
        meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
        df['mes_nome'] = df['data_dt'].dt.month.map(meses_pt)
        df['mes_num'] = df['data_dt'].dt.month
        
        if 'ano' not in df.columns: df['ano'] = 2026
        return df
    except Exception as e:
        st.error(f"Erro ao ler Excel. Verifique se as colunas básicas existem. Detalhe: {e}")
        return pd.DataFrame()

df = load_data()

# ORÇAMENTOS FIXOS
ORC_M = {"AMES": 987380.00, "IAV": 305434.00}
ORC_C = {"AMES": 1000081.06, "IAV": 264450.00}

if not df.empty:
    st.sidebar.markdown("### 🏢 GESTÃO DE FROTAS")
    ano_sel = st.sidebar.selectbox("Ano", options=sorted(df["ano"].unique(), reverse=True))
    df_ano = df[df["ano"] == ano_sel]
    
    inst_sel = st.sidebar.multiselect("Instituição", options=sorted(df_ano["instituicao"].unique()), default=sorted(df_ano["instituicao"].unique()))
    lista_meses = df_ano.sort_values("mes_num")["mes_nome"].unique()
    mes_sel = st.sidebar.selectbox("Mês Competência", options=lista_meses, index=0)

    # Filtragem
    df_base_filtrada = df_ano[df_ano["instituicao"].isin(inst_sel)]
    df_mes = df_base_filtrada[df_base_filtrada["mes_nome"] == mes_sel]
    
    num_mes = df_mes["mes_num"].iloc[0] if not df_mes.empty else 1
    df_acum = df_base_filtrada[df_base_filtrada["mes_num"] <= num_mes]
    
    # Separar Veículos Reais
    df_veiculos = df_mes[~df_mes['placa'].str.contains('combust', case=False, na=False)]

    tab1, tab2, tab3 = st.tabs(["📌 Visão Mensal", "📈 Resumo Acumulado", "📑 Detalhamento"])

    with tab1:
        st.markdown(f"### 📊 Desempenho Mensal - {mes_sel}")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        
        with c1: draw_card("Veículos Ativos", fmt_br(len(df_veiculos["placa"].unique())))
        with c2: draw_card("KM Mensal", fmt_br(df_mes['km'].sum()))
        with c3: draw_card("Custo Manutenção", fmt_br(df_mes['custo_manutencao'].sum(), True))
        with c4: draw_card("Custo Combustível", fmt_br(df_mes['custo_combustivel'].sum(), True))
        
        with c5:
            orc_m_total = sum(ORC_M.get(i, 0) for i in inst_sel)
            acum_m = df_acum['custo_manutencao'].sum()
            perc_m = (acum_m / orc_m_total * 100) if orc_m_total > 0 else 0
            draw_card("Exec. Manutenção", fmt_br(acum_m, True), f"{perc_m:.1f}% consumido", progress=perc_m)
        with c6:
            orc_c_total = sum(ORC_C.get(i, 0) for i in inst_sel)
            acum_c = df_acum['custo_combustivel'].sum()
            perc_c = (acum_c / orc_c_total * 100) if orc_c_total > 0 else 0
            draw_card("Exec. Combustível", fmt_br(acum_c, True), f"{perc_c:.1f}% consumido", progress=perc_c)

        st.markdown("<br>", unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1:
            st.markdown('<div class="chart-title">Ranking Quilometragem (Veículos)</div>', unsafe_allow_html=True)
            top_km = df_veiculos.nlargest(10, 'km').sort_values('km', ascending=True)
            fig_km = px.bar(top_km, x='km', y='placa', orientation='h', text='km', color_discrete_sequence=['#0288D1'])
            fig_km.update_layout(height=350, margin=dict(l=0, r=100, t=0, b=0), xaxis=dict(showticklabels=False, showgrid=False, range=[0, top_km['km'].max()*1.3 if not top_km.empty else 1]), yaxis=dict(title=""))
            st.plotly_chart(fig_km, use_container_width=True)
        with g2:
            st.markdown('<div class="chart-title">Ranking Manutenção (Veículos)</div>', unsafe_allow_html=True)
            top_m = df_veiculos.nlargest(10, 'custo_manutencao').sort_values('custo_manutencao', ascending=True)
            fig_m = px.bar(top_m, x='custo_manutencao', y='placa', orientation='h', text='custo_manutencao', color_discrete_sequence=['#F57C00'])
            fig_m.update_traces(texttemplate='R$ %{text:,.2f}')
            fig_m.update_layout(height=350, margin=dict(l=0, r=120, t=0, b=0), xaxis=dict(showticklabels=False, showgrid=False, range=[0, top_m['custo_manutencao'].max()*1.4 if not top_m.empty else 1]), yaxis=dict(title=""))
            st.plotly_chart(fig_m, use_container_width=True)

        st.markdown('<div class="chart-title">Ranking de Bases por Combustível (Mês)</div>', unsafe_allow_html=True)
        base_c = df_mes.groupby('base')['custo_combustivel'].sum().reset_index().nlargest(10, 'custo_combustivel').sort_values('custo_combustivel', ascending=True)
        fig_b = px.bar(base_c, x='custo_combustivel', y='base', orientation='h', text='custo_combustivel', color_discrete_sequence=['#388E3C'])
        fig_b.update_traces(texttemplate='R$ %{text:,.2f}')
        fig_b.update_layout(height=400, margin=dict(l=0, r=150, t=0, b=0), xaxis=dict(showticklabels=False, showgrid=False, range=[0, base_c['custo_combustivel'].max()*1.3 if not base_c.empty else 1]), yaxis=dict(title=""))
        st.plotly_chart(fig_b, use_container_width=True)

    with tab2:
        st.title("📈 Resumo Acumulado")
        evol = df_acum.groupby(['mes_num', 'mes_nome']).agg({'custo_manutencao':'sum', 'custo_combustivel':'sum'}).reset_index().sort_values('mes_num')
        fig_e = px.line(evol, x='mes_nome', y=['custo_manutencao', 'custo_combustivel'], markers=True, color_discrete_map={'custo_manutencao': '#F57C00', 'custo_combustivel': '#388E3C'})
        fig_e.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(title=""), yaxis=dict(title="R$"))
        st.plotly_chart(fig_e, use_container_width=True)

    with tab3:
        st.dataframe(df_mes, use_container_width=True)
