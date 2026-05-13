import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(page_title="Gestão Estratégica de Frotas", layout="wide")

# 2. Estilização CSS
st.markdown("""
    <style>
    .stApp { background-color: #E3F2FD !important; }[data-testid="stAppViewContainer"] { background-color: #E3F2FD !important; }[data-testid="stSidebar"] { background-color: #BBDEFB !important; border-right: 1px solid #90CAF9; }
    h1, h2, h3, p, span, label { color: #1A237E !important; }

    .metric-container {
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #CFD8DC;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
        height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        margin-bottom: 10px;
    }
    .metric-label { color: #546E7A !important; font-size: 11px; font-weight: 700; text-transform: uppercase; height: 35px; display: flex; align-items: center; }
    .metric-value { color: #1A237E !important; font-size: 24px; font-weight: 800; height: 40px; display: flex; align-items: center; }
    .metric-subtext { color: #333333 !important; font-size: 13px; font-weight: 500; height: 25px; display: flex; align-items: center; }
    .trend-container { height: 25px; display: flex; align-items: center; margin-top: 5px; }
    .chart-title { height: 50px; display: flex; align-items: center; font-size: 16px; font-weight: 700; color: #1A237E !important; text-align: left; margin-bottom: 5px; }
    .stTabs [data-baseweb="tab"] { color: #1A237E !important; font-weight: 600; }
    .stTabs[aria-selected="true"] { border-bottom: 3px solid #F57C00 !important; background-color: rgba(255,255,255,0.3) !important; }
    .trend-up { color: #D32F2F !important; font-size: 13px; font-weight: bold; }
    .trend-down { color: #388E3C !important; font-size: 13px; font-weight: bold; }
    .progress-bg { background-color: #E0E0E0; border-radius: 10px; width: 100%; height: 8px; margin-top: 10px; }
    .progress-fill { background-color: #F57C00; height: 8px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

ESTILO_TEXTO = dict(size=13, color='#333333', family="Arial, sans-serif")

def fmt_br(valor, is_moeda=False):
    if is_moeda:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{valor:,.0f}".replace(",", ".")

def draw_card(label, value, subtext="", trend=None, is_lower_better=True, progress=None):
    trend_html = ""
    if trend is not None and trend != 0:
        color = "trend-down" if (trend <= 0 if is_lower_better else trend >= 0) else "trend-up"
        icon = "↓" if trend <= 0 else "↑"
        trend_html = f'<div class="{color}">{icon} {abs(trend):.1f}% vs mês ant.</div>'
    prog_html = f'<div class="progress-bg"><div class="progress-fill" style="width: {min(progress, 100)}%;"></div></div>' if progress is not None else ""
    st.markdown(f'<div class="metric-container"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-subtext">{subtext}</div><div class="trend-container">{trend_html}</div>{prog_html}</div>', unsafe_allow_html=True)

@st.cache_data
def load_data(file):
    try:
        df = pd.read_excel(file)
        df['Mês Referência'] = pd.to_datetime(df['Mês Referência'])
        meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
        df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_pt)
        df['Mes_Num'] = df['Mês Referência'].dt.month
        df['Quilometragem'] = pd.to_numeric(df['Quilometragem'], errors='coerce').fillna(0)
        df['Custo de manutenção'] = pd.to_numeric(df['Custo de manutenção'], errors='coerce').fillna(0)
        df['Custo Combustível'] = pd.to_numeric(df.iloc[:, 3], errors='coerce').fillna(0)
        df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(2026).astype(int) if 'Ano' in df.columns else 2026
        
        if 'Centro de Custo' in df.columns: df['Centro de Custo'] = df['Centro de Custo'].astype(str).str.strip()
        if 'Base' in df.columns: df['Base'] = df['Base'].astype(str).str.strip()
        if 'Instituição' in df.columns: df['Instituição'] = df['Instituição'].astype(str).str.strip()
        if 'Placa' in df.columns:
            df['Placa'] = df['Placa'].astype(str).str.strip().str.upper().replace('NAN', '') 
        return df
    except Exception as e:
        st.error(f"Erro ao processar: {e}")
        return pd.DataFrame()

ORCAMENTOS_MANUT = {"AMES": 987380.00, "IAV": 305434.00}
ORCAMENTOS_COMB = {"AMES": 1000081.06, "IAV": 264450.00}

st.sidebar.markdown("### 🏢 GESTÃO DE FROTAS")
uploaded_file = st.sidebar.file_uploader("📥 Carregue a planilha Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    if not df.empty:
        ano_sel = st.sidebar.selectbox("Ano", options=sorted(df["Ano"].unique(), reverse=True))
        df_ano = df[df["Ano"] == ano_sel]
        
        opcoes_inst = ["TODAS"] + sorted(df_ano["Instituição"].unique())
        inst_sel = st.sidebar.selectbox("Instituição", options=opcoes_inst)
        df_temp_inst = df_ano.copy() if inst_sel == "TODAS" else df_ano[df_ano["Instituição"] == inst_sel]
        inst_ativas = df_ano["Instituição"].unique() if inst_sel == "TODAS" else [inst_sel]
        
        col_cc = 'Centro de Custo' if 'Centro de Custo' in df.columns else 'Base'
        opcoes_cc =["TODOS"] + sorted(df_temp_inst[col_cc].dropna().unique())
        cc_sel = st.sidebar.selectbox("Centro de Custo / Base", options=opcoes_cc)
        df_base = df_temp_inst.copy() if cc_sel == "TODOS" else df_temp_inst[df_temp_inst[col_cc] == cc_sel]
        
        busca_placa = st.sidebar.text_input("🔍 Buscar Placa específica", "").upper().strip()
        lista_meses = df_ano.sort_values("Mes_Num")["Mes_Nome"].unique()
        mes_sel = st.sidebar.selectbox("Mês Competência", options=lista_meses, index=len(lista_meses)-1)

        df_apenas_comb = df_base[df_base["Placa"].str.startswith("COMBUSTÍVEL", na=False)]
        df_apenas_manut = df_base[~df_base["Placa"].str.startswith("COMBUSTÍVEL", na=False)]
        df_filtrado_mes_manut = df_apenas_manut[df_apenas_manut["Mes_Nome"] == mes_sel]
        mes_num_atual = df_ano[df_ano["Mes_Nome"] == mes_sel]["Mes_Num"].iloc[0]
        df_acumulado_ate_mes_manut = df_apenas_manut[df_apenas_manut["Mes_Num"] <= mes_num_atual]
        df_anterior_manut = df_apenas_manut[df_apenas_manut["Mes_Num"] == mes_num_atual - 1]

        tab1, tab2, tab3, tab4 = st.tabs(["📌 Visão Mensal", "📈 Resumo Acumulado", "⛽ Combustível", "📑 Detalhamento"])

        with tab1:
            st.markdown(f"### 📊 Desempenho Mensal Manutenção - {mes_sel}")
            c1, c2, c3, c4 = st.columns(4)
            
            def eh_placa_valida(dff): return dff[(dff["Placa"]!="") & (dff["Placa"].str.len() == 7)]["Placa"].unique()
            
            with c1:
                ativos_m = len(eh_placa_valida(df_filtrado_mes_manut))
                ativos_a = len(eh_placa_valida(df_anterior_manut))
                trend_at = ((ativos_m - ativos_a) / ativos_a * 100) if ativos_a > 0 else 0
                draw_card("VEÍCULOS ATIVOS", fmt_br(ativos_m), trend=trend_at, is_lower_better=False)
            with c2:
                km_m = df_filtrado_mes_manut['Quilometragem'].sum()
                km_a = df_anterior_manut['Quilometragem'].sum()
                draw_card("QUILOMETRAGEM MENSAL", fmt_br(km_m), trend=((km_m-km_a)/km_a*100) if km_a>0 else 0, is_lower_better=False)
            with c3:
                custo_m = df_filtrado_mes_manut['Custo de manutenção'].sum()
                custo_a = df_anterior_manut['Custo de manutenção'].sum()
                num_v = ativos_m if ativos_m > 0 else 1
                draw_card("CUSTO MANUTENÇÃO MENSAL", fmt_br(custo_m, True), f"Média: {fmt_br(custo_m/num_v, True)} /veículo", trend=((custo_m-custo_a)/custo_a*100) if custo_a > 0 else 0)
            with c4:
                orc = sum(ORCAMENTOS_MANUT.get(i, 0) for i in inst_ativas)
                perc = (df_acumulado_ate_mes_manut["Custo de manutenção"].sum() / orc * 100) if orc > 0 else 0
                draw_card("ORÇAMENTO MANUTENÇÃO", fmt_br(df_acumulado_ate_mes_manut["Custo de manutenção"].sum(), True), f"{perc:.1f}% consumido", progress=perc)
        
        # ... (restante das tabs permanece igual)
        with tab4:
            st.dataframe(df_base, use_container_width=True)
    else: st.warning("Dados inválidos.")
else: st.info("Faça o upload do arquivo para começar.")
