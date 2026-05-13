import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuração da Página
st.set_page_config(page_title="Gestão Estratégica de Frotas", layout="wide")

# 2. Estilização CSS
st.markdown("""
    <style>
    .stApp { background-color: #E3F2FD !important; }
    [data-testid="stAppViewContainer"] { background-color: #E3F2FD !important; }
    [data-testid="stSidebar"] { background-color: #BBDEFB !important; border-right: 1px solid #90CAF9; }
    h1, h2, h3, p, span, label { color: #1A237E !important; }

    .metric-container {
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #CFD8DC;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 10px;
    }
    
    .metric-label { color: #546E7A !important; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; }
    .metric-value { color: #1A237E !important; font-size: 28px; font-weight: 800; }
    .metric-subtext { color: #333333 !important; font-size: 13px; font-weight: 500; }
    
    .progress-bg { background-color: #E0E0E0; border-radius: 10px; width: 100%; height: 8px; margin-top: 15px; }
    .progress-fill { background-color: #F57C00; height: 8px; border-radius: 10px; }
    
    .chart-title { font-size: 18px; font-weight: 700; color: #1A237E !important; margin: 20px 0 10px 0; }
    </style>
    """, unsafe_allow_html=True)

ESTILO_TEXTO = dict(size=12, color='#333333', family="Arial Black")

def fmt_br(valor, is_moeda=False):
    if is_moeda:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{valor:,.0f}".replace(",", ".")

def draw_card(label, value, subtext="", progress=None):
    prog_html = f'<div class="progress-bg"><div class="progress-fill" style="width: {min(progress, 100) if progress else 0}%;"></div></div>' if progress is not None else ""
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-subtext">{subtext}</div>
            {prog_html}
        </div>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("manutencao.xlsx")
        df.columns = df.columns.str.strip()
        df['Mês Referência'] = pd.to_datetime(df['Mês Referência'])
        meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
        df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_pt)
        df['Mes_Num'] = df['Mês Referência'].dt.month
        
        for col in ['Quilometragem', 'Custo de manutenção', 'Custo de combustível', 'Custo de seguro']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0.0
                
        df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(2026).astype(int)
        df['Placa'] = df['Placa'].astype(str).str.strip().str.upper().replace('NAN', '')
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = load_data()
ORCAMENTOS_SEGURO = {"AMES": 186682.00, "IAV": 15382.00}

if not df.empty:
    # Sidebar
    st.sidebar.markdown("### 🏢 GESTÃO DE FROTAS")
    ano_sel = st.sidebar.selectbox("Ano", options=sorted(df["Ano"].unique(), reverse=True))
    inst_sel = st.sidebar.selectbox("Instituição", options=["TODAS"] + sorted(df["Instituição"].unique()))
    
    # Filtros de Dados
    df_ano = df[df["Ano"] == ano_sel]
    df_inst = df_ano.copy() if inst_sel == "TODAS" else df_ano[df_ano["Instituição"] == inst_sel]
    
    col_cc = 'Base' if 'Base' in df.columns else 'Centro de Custo'
    cc_sel = st.sidebar.selectbox("Centro de Custo / Base", options=["TODOS"] + sorted(df_inst[col_cc].dropna().unique()))
    df_final = df_inst.copy() if cc_sel == "TODOS" else df_inst[df_inst[col_cc] == cc_sel]
    
    mes_sel = st.sidebar.selectbox("Mês Competência", options=df_ano.sort_values("Mes_Num")["Mes_Nome"].unique(), index=0)

    # Abas
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📌 Visão Mensal", "📈 Acumulado", "⛽ Combustível", "🛡️ Seguro", "📑 Detalhes"])

    # --- ABA SEGURO (CORRIGIDA) ---
    with tab4:
        st.markdown(f"### 🛡️ Gestão de Seguro - Ano {ano_sel}")
        
        # 1. Filtro específico para Seguro (Considera o ano todo da instituição selecionada)
        df_seg_anual = df_inst[df_inst["Placa"].str.contains("SEGURO", case=False, na=False)]
        
        # 2. Cálculo da Verba baseada na Instituição Selecionada
        if inst_sel == "TODAS":
            verba_seguro = sum(ORCAMENTOS_SEGURO.values())
        else:
            verba_seguro = ORCAMENTOS_SEGURO.get(inst_sel, 0)
            
        gasto_seguro_total = df_seg_anual["Custo de seguro"].sum()
        perc_seguro = (gasto_seguro_total / verba_seguro * 100) if verba_seguro > 0 else 0
        
        # Card
        c1, _ = st.columns([1, 2])
        with c1:
            draw_card(
                "EXECUÇÃO SEGURO ANUAL", 
                fmt_br(gasto_seguro_total, True), 
                f"Verba: {fmt_br(verba_seguro, True)} ({perc_seguro:.1f}%)", 
                progress=perc_seguro
            )
        
        st.markdown('<div class="chart-title">Ranking de Custos de Seguro por Base</div>', unsafe_allow_html=True)
        
        # 3. Gráfico de Seguro
        seg_base = df_seg_anual.groupby(col_cc)['Custo de seguro'].sum().reset_index()
        seg_base = seg_base[seg_base['Custo de seguro'] > 0].sort_values('Custo de seguro', ascending=True)
        
        if not seg_base.empty:
            fig_seg = px.bar(
                seg_base, 
                x='Custo de seguro', 
                y=col_cc, 
                orientation='h', 
                text='Custo de seguro',
                color='Custo de seguro',
                color_continuous_scale='Blues'
            )
            
            fig_seg.update_traces(
                texttemplate='<b>R$ %{text:,.2f}</b>', 
                textposition='outside',
                cliponaxis=False,
                textfont=dict(size=12, family="Arial Black")
            )
            
            # Ajuste de Layout para não cortar nomes e barras
            fig_seg.update_layout(
                height=max(400, len(seg_base) * 35), # Altura dinâmica
                margin=dict(l=250, r=100, t=20, b=20), # Margem esquerda grande para os nomes das bases
                xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, seg_base['Custo de seguro'].max() * 1.4]),
                yaxis=dict(title="", tickfont=dict(size=11, family="Arial Black")),
                coloraxis_showscale=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_seg, use_container_width=True)
        else:
            st.info("Nenhum dado de seguro encontrado para os filtros aplicados.")

    # (As outras abas permanecem com sua lógica original, apenas garanta que usem df_final e dff_ano corretamente)
    with tab5:
        st.markdown("### 📑 Detalhamento")
        st.dataframe(df_final, use_container_width=True)

else:
    st.warning("Verifique o arquivo manutencao.xlsx")
