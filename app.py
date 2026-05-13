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
    .metric-container { background-color: #FFFFFF !important; padding: 20px; border-radius: 12px; border: 1px solid #CFD8DC; box-shadow: 0px 2px 8px rgba(0,0,0,0.05); height: 200px; display: flex; flex-direction: column; margin-bottom: 10px; }
    .metric-label { color: #546E7A !important; font-size: 11px; font-weight: 700; text-transform: uppercase; height: 35px; display: flex; align-items: center; }
    .metric-value { color: #1A237E !important; font-size: 24px; font-weight: 800; height: 40px; display: flex; align-items: center; }
    .metric-subtext { color: #333333 !important; font-size: 13px; font-weight: 500; height: 25px; display: flex; align-items: center; }
    .chart-title { height: 50px; display: flex; align-items: center; font-size: 16px; font-weight: 700; color: #1A237E !important; margin-bottom: 5px; }
    .stTabs [data-baseweb="tab"] { color: #1A237E !important; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

ESTILO_TEXTO = dict(size=13, color='#333333', family="Arial, sans-serif")

def fmt_br(valor, is_moeda=False):
    if is_moeda: return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{valor:,.0f}".replace(",", ".")

@st.cache_data
def load_data(file):
    try:
        df = pd.read_excel(file)
        df['Mês Referência'] = pd.to_datetime(df['Mês Referência'])
        # Mapeamento manual para evitar erro de locale
        meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 
                    7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
        df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_pt)
        df['Mes_Num'] = df['Mês Referência'].dt.month
        
        df['Quilometragem'] = pd.to_numeric(df['Quilometragem'], errors='coerce').fillna(0)
        df['Custo de manutenção'] = pd.to_numeric(df['Custo de manutenção'], errors='coerce').fillna(0)
        df['Custo Combustível'] = pd.to_numeric(df.get('Custo Combustível', 0), errors='coerce').fillna(0)
        df['Custo do Seguro'] = pd.to_numeric(df.get('Custo do Seguro', 0), errors='coerce').fillna(0)
        df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(2026).astype(int)
        
        for col in['Instituição', 'Centro de Custo', 'Base', 'Placa']:
            if col in df.columns: df[col] = df[col].astype(str).str.strip().str.upper().replace('NAN', '')
        return df
    except Exception as e:
        st.error(f"Erro ao processar planilha: {e}"); return pd.DataFrame()

st.sidebar.markdown("### 🏢 GESTÃO DE FROTAS")
uploaded_file = st.sidebar.file_uploader("📥 Carregue a planilha Excel", type=["xlsx", "xls"])

if uploaded_file:
    df = load_data(uploaded_file)
    if not df.empty:
        ano_sel = st.sidebar.selectbox("Ano", sorted(df["Ano"].unique(), reverse=True))
        df_ano = df[df["Ano"] == ano_sel]
        
        inst_sel = st.sidebar.selectbox("Instituição", ["TODAS"] + sorted(df_ano["Instituição"].unique()))
        df_temp = df_ano if inst_sel == "TODAS" else df_ano[df_ano["Instituição"] == inst_sel]
        
        col_cc = 'Centro de Custo' if 'Centro de Custo' in df.columns else 'Base'
        cc_sel = st.sidebar.selectbox("Centro de Custo / Base", ["TODOS"] + sorted(df_temp[col_cc].dropna().unique()))
        df_base = df_temp if cc_sel == "TODOS" else df_temp[df_temp[col_cc] == cc_sel]
        
        mes_sel = st.sidebar.selectbox("Mês Competência", df_ano.sort_values("Mes_Num")["Mes_Nome"].unique())

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📌 Visão Mensal", "📈 Acumulado", "⛽ Combustível", "🛡️ Seguro", "📑 Detalhes"])
        
        with tab4: # ABA SEGURO
            st.markdown(f"### 🛡️ Gestão de Seguros - {ano_sel}")
            df_seg = df_base[df_base["Placa"].str.startswith("SEGURO", na=False)]
            df_seg_mes = df_seg[df_seg["Mes_Nome"] == mes_sel]
            
            st.metric("Total Seguro no Mês", fmt_br(df_seg_mes["Custo do Seguro"].sum(), True))
            
            if not df_seg_mes.empty:
                df_seg_base = df_seg_mes.groupby('Base')['Custo do Seguro'].sum().reset_index().sort_values('Custo do Seguro')
                fig = px.bar(df_seg_base, x='Custo do Seguro', y='Base', orientation='h', text='Custo do Seguro', color='Custo do Seguro', color_continuous_scale='Blues')
                fig.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside')
                fig.update_layout(height=400, coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("Sem dados de seguro para este filtro.")
            
        with tab5: # Detalhes
            st.dataframe(df_base, use_container_width=True)
