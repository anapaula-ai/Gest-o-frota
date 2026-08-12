import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # Adicionado para o gráfico de rosca
import time  # Adicionado para forçar atualização do cache do Google
import re

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="Logística", layout="wide")

# ==========================================
# 2. TELA DE LOGIN E SEGURANÇA
# ==========================================
# A senha agora é puxada de forma segura das configurações (secrets)
try:
    SENHA_ACESSO = st.secrets["senha_acesso"]
except KeyError:
    st.error("⚠️ Erro de configuração: A senha não foi encontrada nos secrets.")
    st.info("Lembre-se de criar o arquivo `.streamlit/secrets.toml` localmente ou configurar nos Secrets do painel Streamlit Cloud.")
    st.stop()

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

# Estilo global (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #E3F2FD !important; }
    [data-testid="stAppViewContainer"] { background-color: #E3F2FD !important; }
    [data-testid="stSidebar"] { background-color: #BBDEFB !important; border-right: 1px solid #90CAF9; }
    h1, h2, h3, p, span, label { color: #1A237E !important; }

    .metric-container {
        position: relative;
        overflow: hidden;
        background: linear-gradient(180deg, #FFFFFF 0%, #FCFDFF 100%) !important;
        padding: 21px 20px 18px 20px;
        border-radius: 14px;
        border: 1px solid #D7E0EA;
        box-shadow: 0 5px 16px rgba(26, 35, 126, 0.07);
        min-height: 185px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        margin-bottom: 10px;
    }

    .metric-container::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: #1A237E;
    }

    .metric-label {
        color: #60758A !important;
        font-size: 11.5px;
        letter-spacing: .28px;
        font-weight: 750;
        text-transform: uppercase;
        min-height: 34px;
        display: flex;
        align-items: center;
    }

    .metric-value {
        color: #14206F !important;
        font-size: 23px;
        font-weight: 750;
        min-height: 39px;
        display: flex;
        align-items: center;
        letter-spacing: -.25px;
    }

    .metric-subtext {
        color: #455A64 !important;
        font-size: 13px;
        font-weight: 500;
        min-height: 31px;
        display: block;
        line-height: 1.45;
        margin-top: 7px;
        padding-top: 8px;
        border-top: 1px solid #EEF2F6;
    }

    .trend-container {
        min-height: 18px;
        display: flex;
        align-items: center;
        margin-top: 4px;
    }

    .radar-card {
        background: #FFFFFF;
        border: 1px solid #DCE4EC;
        border-left: 4px solid #1A237E;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
        box-shadow: 0 3px 10px rgba(26, 35, 126, 0.05);
        color: #263238 !important;
        font-size: 14.5px;
        line-height: 1.5;
    }
    .radar-card.warning { border-left-color: #F57C00; }
    .radar-card.critical { border-left-color: #D32F2F; }
    .radar-card.ok { border-left-color: #2E7D32; }
    .chart-title { height: 50px; display: flex; align-items: center; font-size: 18px; font-weight: 700; color: #1A237E !important; text-align: left; margin-bottom: 5px; }

    /* ==========================================
       ESTILO DAS ABAS (TABS COMO BOTÕES PROPORCIONAIS)
       ========================================== */
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
    div[data-testid="stTabs"] [data-baseweb="tab-border"] {
        display: none !important;
    }

    div[data-testid="stTabs"] [role="tablist"] {
        display: flex !important;
        flex-wrap: wrap !important;
        justify-content: center !important;
        gap: 12px !important;
        padding-bottom: 15px !important;
    }

    div[data-testid="stTabs"] [role="tab"] {
        flex: 1 1 calc(20% - 12px) !important;
        min-width: 140px !important;
        background-color: #FFFFFF !important; 
        border: 1px solid #CFD8DC !important; 
        border-radius: 8px !important; 
        padding: 10px 8px !important; 
        margin: 0 !important;
        min-height: 48px !important;
        height: auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
    }

    div[data-testid="stTabs"] [role="tab"] p {
        color: #1A237E !important; 
        font-weight: 700 !important; 
        font-size: 14px !important;
        margin: 0 !important;
        white-space: normal !important;
        text-align: center !important;
        line-height: 1.2 !important;
    }

    div[data-testid="stTabs"] [role="tab"]:hover {
        background-color: #F0F4F8 !important;
        border-color: #90CAF9 !important;
        transform: translateY(-2px);
    }

    div[data-testid="stTabs"] [role="tab"][aria-selected="true"] { 
        background-color: #1A237E !important; 
        border-color: #1A237E !important; 
        box-shadow: 0px 4px 10px rgba(26, 35, 126, 0.2) !important;
    }

    div[data-testid="stTabs"] [role="tab"][aria-selected="true"] p { 
        color: #FFFFFF !important; 
    }
    /* ========================================== */

    .trend-up { color: #D32F2F !important; font-size: 13px; font-weight: bold; }
    .trend-down { color: #388E3C !important; font-size: 13px; font-weight: bold; }
    .progress-bg { background-color: #E0E0E0; border-radius: 10px; width: 100%; height: 8px; margin-top: 10px; }
    .progress-fill { height: 8px; border-radius: 10px; }
    .bg-normal { background-color: #F57C00; } 
    .bg-alert { background-color: #D32F2F !important; } 
    
    .raiox-container { display: flex; flex-wrap: wrap; background-color: #FFFFFF !important; padding: 20px; border-radius: 12px; border: 1px solid #CFD8DC; box-shadow: 0px 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px; gap: 10px; }
    .raiox-item { flex: 1; min-width: 130px; text-align: center; border-right: 1px solid #E0E0E0; }
    .raiox-item:last-child { border-right: none; }
    .raiox-label { color: #546E7A !important; font-size: 12px; font-weight: 700; text-transform: uppercase; }
    .raiox-value { color: #1A237E !important; font-size: 20px; font-weight: 800; margin-top: 5px; }
    
    .stDownloadButton button { background-color: #F57C00 !important; color: white !important; font-weight: 600 !important; border-radius: 8px !important; }
    .stDownloadButton button:hover { background-color: #E65100 !important; }
    
    .inst-card{background:#fff;border:1px solid #DCE4EC;border-radius:12px;padding:14px 16px;margin:8px 0;box-shadow:0 3px 10px rgba(26,35,126,.04)}
    .inst-name{color:#14206F;font-size:15px;font-weight:800;margin-bottom:9px}
    .inst-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}
    .inst-lbl{color:#78909C;font-size:9px;font-weight:800;text-transform:uppercase}
    .inst-val{color:#263238;font-size:13px;font-weight:750;margin-top:2px}
    .inst-progress{height:5px;background:#EDF1F5;border-radius:10px;margin-top:10px;overflow:hidden}.inst-progress div{height:100%;background:#1A237E}
    .exec-list{background:#fff;border:1px solid #DCE4EC;border-radius:12px;overflow:hidden;box-shadow:0 3px 10px rgba(26,35,126,.04)}
    .exec-row{display:grid;grid-template-columns:minmax(170px,2.1fr) .72fr 1fr 1.15fr .9fr;align-items:center;gap:10px;padding:10px 12px;border-bottom:1px solid #EEF2F6}
    .exec-row:last-child{border-bottom:none}.exec-row:hover{background:#FAFCFF}
    .exec-name{color:#263238;font-size:11.5px;font-weight:750}.exec-muted{color:#607D8B;font-size:10.5px;text-align:right}
    .exec-money{color:#14206F;font-size:11.5px;font-weight:750;text-align:right}.exec-badge{justify-self:end;background:#F2F5FA;color:#14206F;border:1px solid #E0E6EF;border-radius:999px;padding:4px 7px;font-size:10px;font-weight:750}
    .exec-inst{color:#607D8B;font-size:8.5px;font-weight:800;margin-left:5px;background:#F3F6F9;border-radius:999px;padding:2px 5px}
    .odonto-list .exec-row{grid-template-columns:minmax(210px,2.3fr) .55fr .75fr 1fr 1fr 1.05fr .8fr}

    .rx-list{
        background:#FFFFFF;
        border:1px solid #DCE4EC;
        border-radius:12px;
        overflow:hidden;
        box-shadow:0 3px 10px rgba(26,35,126,.04);
    }
    .rx-header{
        display:grid;
        grid-template-columns:minmax(190px,2.15fr) .75fr 1fr 1.2fr .9fr;
        align-items:center;
        gap:10px;
        padding:10px 14px 8px 14px;
        background:#F9FBFD;
        border-bottom:1px solid #E7EDF3;
        color:#607D8B !important;
        font-size:11px;
        font-weight:800;
        text-transform:uppercase;
        letter-spacing:.35px;
    }
    .rx-row{
        display:grid;
        grid-template-columns:minmax(190px,2.15fr) .75fr 1fr 1.2fr .9fr;
        align-items:center;
        gap:10px;
        padding:12px 14px;
        border-bottom:1px solid #EEF2F6;
    }
    .rx-row:last-child{border-bottom:none}
    .rx-row:hover{background:#FAFCFF}
    .rx-name{color:#17206A !important;font-size:13.5px;font-weight:800}
    .rx-ativos{color:#2E7D32 !important;font-size:12.5px;font-weight:800;text-align:right;white-space:nowrap}
    .rx-km{color:#1976D2 !important;font-size:12.5px;font-weight:800;text-align:right;white-space:nowrap}
    .rx-money{color:#14206F !important;font-size:12.5px;font-weight:800;text-align:right;white-space:nowrap}
    .rx-badge{justify-self:end;background:#F2F5FA;color:#14206F !important;border:1px solid #E0E6EF;border-radius:999px;padding:5px 9px;font-size:12px;font-weight:800;white-space:nowrap}
    .rx-inst{color:#607D8B !important;font-size:8.5px;font-weight:800;margin-left:5px;background:#F3F6F9;border-radius:999px;padding:2px 5px}

    .odonto-summary{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;margin:4px 0 14px 0}
    .odonto-kpi{background:#FFFFFF;border:1px solid #DCE4EC;border-radius:11px;padding:12px 10px;box-shadow:0 3px 10px rgba(26,35,126,.04);min-height:86px}
    .odonto-kpi-label{color:#60758A !important;font-size:12px;font-weight:800;text-transform:uppercase;line-height:1.25;min-height:28px}
    .odonto-kpi-value{color:#14206F !important;font-size:22px;font-weight:800;margin-top:7px;white-space:nowrap}
    .odonto-kpi-sub{color:#607D8B !important;font-size:11.5px;margin-top:4px}
    @media (max-width: 1100px){.odonto-summary{grid-template-columns:repeat(3,minmax(0,1fr));}}



    .manut-attention{
        background:#FFFFFF;border:1px solid #DCE4EC;border-left:4px solid #F57C00;
        border-radius:10px;padding:14px 16px;margin-bottom:9px;
        box-shadow:0 3px 10px rgba(26,35,126,.04);
        color:#263238 !important;font-size:14.5px;line-height:1.55;
    }

    .vs-alta { color:#D32F2F !important; font-weight:800 !important; }
    .vs-baixa { color:#2E7D32 !important; font-weight:800 !important; }
    .vs-neutro { color:#607D8B !important; font-weight:800 !important; }


    .manut-attention b { font-size:15px !important; }

</style>
""", unsafe_allow_html=True)

if not st.session_state["autenticado"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div style="background-color: white; padding: 40px; border-radius: 15px; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); text-align: center;">
            <h2 style="color: #1A237E; margin-bottom: 5px;">🏢 LOGÍSTICA</h2>
            <p style="color: #546E7A; margin-bottom: 30px;">Acesso Restrito</p>
        """, unsafe_allow_html=True)
        
        senha_digitada = st.text_input("🔑 Digite a senha para acessar:", type="password")
        
        if st.button("Desbloquear Painel", use_container_width=True):
            if senha_digitada == SENHA_ACESSO:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Senha incorreta. Tente novamente.")
                
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.sidebar.markdown("### 🏢 LOGÍSTICA")
    if st.sidebar.button("🔒 Sair / Bloquear App"):
        st.session_state["autenticado"] = False
        st.rerun()
    
    st.sidebar.markdown("---")

    ESTILO_TEXTO = dict(size=13, color='#333333', family="Arial, sans-serif")

    def fmt_br(valor, is_moeda=False):
        if is_moeda:
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{valor:,.0f}".replace(",", ".")

    def get_ativos(df):
        excluir_pattern = "COMBUS|SEGUR|FINANC|CONSÓRC|RASTR|LOGIST|MANUT|MENSAL|TAXA"
        return df[
            (~df["Placa"].astype(str).str.contains(excluir_pattern, case=False, na=True)) &
            (df["Placa"].astype(str).str.strip() != "") & 
            (df["Placa"].astype(str).str.upper() != "NAN") &
            (df["Placa"].astype(str).str.strip() != "0")
        ]["Placa"].unique()

    def draw_card(label, value, subtext="", trend=None, is_lower_better=True, progress=None, progress_text="", extra_class=""):
        trend_html = ""
        if trend is not None and trend != 0:
            color = "trend-down" if (trend <= 0 if is_lower_better else trend >= 0) else "trend-up"
            icon = "↓" if trend <= 0 else "↑"
            trend_html = f'<div class="{color}">{icon} {abs(trend):.1f}% vs mês ant.</div>'
        
        prog_html = ""
        if progress is not None:
            prog_color = "bg-alert" if progress > 100 else "bg-normal"
            prog_html = f'<div class="progress-bg"><div class="progress-fill {prog_color}" style="width: {min(progress, 100)}%;"></div></div><div style="font-size: 13px; color: #455A64; margin-top: 6px; font-weight: 500;">{progress_text}</div>'
        
        html_card = f"""
    <div class="metric-container {extra_class}">
    <div class="metric-label">{label}</div>
    <div class="metric-value">{value}</div>
    <div class="metric-subtext">{subtext}</div>
    <div class="trend-container">{trend_html}</div>
    {prog_html}
    </div>
    """
        st.markdown(html_card, unsafe_allow_html=True)

    def to_float(serie):
        def clean_val(x):
            try:
                if pd.isna(x): return 0.0
                if isinstance(x, (int, float)): return float(x)
                x = str(x).upper().replace('R$', '').replace(' ', '').strip()
                if x == '': return 0.0
                
                if '.' in x and ',' in x:
                    if x.rfind(',') > x.rfind('.'):
                        x = x.replace('.', '').replace(',', '.')
                    else:
                        x = x.replace(',', '')
                elif ',' in x:
                    x = x.replace(',', '.')
                    
                return float(x)
            except:
                return 0.0
        return serie.apply(clean_val)

    @st.cache_data(ttl=60) 
    def load_ipva_data():
        try:
            url_ipva_base = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVMBTwRCrEvDUddWeUaIIpdSiA27cuPhHeArqAa_I3b_E8Fa_43lKg5hhSh2StAQddZQIXFFlM-zn-/pub?gid=398571100&single=true&output=csv"
            url_ipva = f"{url_ipva_base}&t={int(time.time())}"
            
            df_ipva = pd.read_csv(url_ipva, decimal=',', sep=',')
            
            if 'Ipva estimado' in df_ipva.columns:
                df_ipva['Ipva estimado'] = to_float(df_ipva['Ipva estimado'])
                
            return df_ipva
            
        except Exception as e:
            st.error(f"Erro ao carregar dados de IPVA: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=60) 
    def load_top_km_data():
        try:
            url_top_km_base = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVMBTwRCrEvDUddWeUaIIpdSiA27cuPhHeArqAa_I3b_E8Fa_43lKg5hhSh2StAQddZQIXFFlM-zn-/pub?gid=2146713884&single=true&output=csv"
            
            if "COLE_O_LINK" in url_top_km_base:
                return pd.DataFrame() 
            
            url_top_km = f"{url_top_km_base}&t={int(time.time())}"
            df_top = pd.read_csv(url_top_km, decimal=',', sep=',', thousands='.')
            return df_top
            
        except Exception as e:
            st.error(f"Erro ao carregar dados do Top KM: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=60) 
    def load_data():
        try:
            url_base = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVMBTwRCrEvDUddWeUaIIpdSiA27cuPhHeArqAa_I3b_E8Fa_43lKg5hhSh2StAQddZQIXFFlM-zn-/pub?output=csv"
            url_planilha = f"{url_base}&t={int(time.time())}" 
            
            if ".csv" in url_planilha.lower() or "output=csv" in url_planilha.lower():
                df = pd.read_csv(url_planilha, decimal=',', thousands='.')
            else:
                df = pd.read_excel(url_planilha)
            
            if 'Mês Referência' in df.columns:
                datas_cruas = df['Mês Referência'].astype(str)
            else:
                datas_cruas = pd.Series('2026-01-01', index=df.index)

            datas_str = datas_cruas.str.strip().str.split(' ').str[0].str.split('T').str[0]
            
            formatos = ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y', '%m/%d/%Y']
            d1 = pd.Series(pd.NaT, index=datas_str.index)
            
            for fmt in formatos:
                mask = d1.isna()
                if mask.any():
                    d1.loc[mask] = pd.to_datetime(datas_str[mask], format=fmt, errors='coerce')
            
            mask = d1.isna()
            if mask.any():
                d1.loc[mask] = pd.to_datetime(datas_str[mask], errors='coerce', dayfirst=True)
            
            df['Mês Referência'] = d1
            
            meses_pt = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 
                        7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}
            df['Mes_Nome'] = df['Mês Referência'].dt.month.map(meses_pt)
            df['Mes_Num'] = df['Mês Referência'].dt.month
            
            df['Ano'] = pd.to_datetime(df['Mês Referência'], errors='coerce').dt.year.fillna(2026).astype(int)
            
            df['Quilometragem'] = to_float(df['Quilometragem'])
            df['Custo de manutenção'] = to_float(df['Custo de manutenção'])
            df['Custo de seguro'] = to_float(df.get('Custo de seguro', 0))
            df['Custo de Rastreador'] = to_float(df.get('Custo de Rastreador', 0))
            
            if 'Custo de combustível' in df.columns:
                df['Custo Combustível'] = to_float(df['Custo de combustível'])
            else:
                df['Custo Combustível'] = to_float(df.iloc[:, 3])
            
            if 'Centro de Custo' in df.columns: df['Centro de Custo'] = df['Centro de Custo'].astype(str).str.strip()
            if 'Base' in df.columns: df['Base'] = df['Base'].astype(str).str.strip()
            if 'Instituição' in df.columns: df['Instituição'] = df['Instituição'].astype(str).str.strip()
            
            if 'Modelo' in df.columns: 
                df['Modelo'] = df['Modelo'].astype(str).str.strip().replace(['0', '0.0', 'nan', 'NAN', 'None'], '-')
            else:
                df['Modelo'] = '-'
                
            if 'Motorista' in df.columns: 
                df['Motorista'] = df['Motorista'].astype(str).str.strip().replace(['0', '0.0', 'nan', 'NAN', 'None'], '-')
            else:
                df['Motorista'] = '-'
            
            if 'Placa' in df.columns: 
                df['Placa'] = df['Placa'].astype(str).str.strip().str.upper()
                df['Placa'] = df['Placa'].replace(['NAN', 'NONE'], '')
            
            return df
        except Exception as e:
            st.error(f"Erro ao carregar dados. Verifique se o link está correto: {e}")
            return pd.DataFrame()

    df = load_data()

    # VERBAS (Definidas apenas para 2026)
    ORCAMENTOS_MANUT_2026 = {"AMES": 987380.00, "IAV": 305434.00}
    ORCAMENTOS_COMB_2026 = {"AMES": 1000081.06, "IAV": 264450.00}
    ORCAMENTOS_SEGURO_2026 = {"AMES": 186682.00, "IAV": 115461.00}
    ORCAMENTOS_RASTREADOR_2026 = {"AMES": 0.00, "IAV": 10194.00} 

    if not df.empty:
        ano_sel = st.sidebar.selectbox("Ano", options=sorted(df["Ano"].unique(), reverse=True))
        df_ano = df[df["Ano"] == ano_sel]
        opcoes_inst =["TODAS"] + sorted(df_ano["Instituição"].unique())
        inst_sel = st.sidebar.selectbox("Instituição", options=opcoes_inst)
        
        if inst_sel == "TODAS":
            df_temp_inst = df_ano.copy()
            inst_ativas = df_ano["Instituição"].unique()
        else:
            df_temp_inst = df_ano[df_ano["Instituição"] == inst_sel]
            inst_ativas = [inst_sel]
        
        col_cc = 'Centro de Custo' if 'Centro de Custo' in df.columns else 'Base'
        opcoes_cc = ["TODOS"] + sorted(df_temp_inst[col_cc].dropna().unique())
        cc_sel = st.sidebar.selectbox("Centro de Custo / Base", options=opcoes_cc)
        
        df_base_completa = df_temp_inst.copy() if cc_sel == "TODOS" else df_temp_inst[df_temp_inst[col_cc] == cc_sel]
        
        pattern_digitais = "VEÍCUL|VEICUL|ALUGAD|MOTO|KOMBI|TRICICLO|REBOQUE|SPRINTER|ÔNIBUS|ONIBUS|MICRO"
        
        mask_reais = ~df_base_completa["Placa"].astype(str).str.contains(pattern_digitais, case=False, na=True)
        df_base = df_base_completa[mask_reais]

        placas_disponiveis = get_ativos(df_base)
        opcoes_placas = [""] + sorted(placas_disponiveis)
        
        busca_placa = st.sidebar.selectbox(
            "🔍 Buscar Placa específica", 
            options=opcoes_placas, 
            index=0,
            help="Clique e comece a digitar a placa para pesquisar"
        ).upper().strip()
        
        df_meses_validos = df_ano.dropna(subset=['Mes_Num', 'Mes_Nome']).copy()
        
        if df_meses_validos.empty:
            lista_meses = ["Nenhum Mês"]
        else:
            df_meses_unicos = df_meses_validos[['Mes_Num', 'Mes_Nome']].drop_duplicates().sort_values('Mes_Num')
            lista_meses = df_meses_unicos['Mes_Nome'].tolist()
            
        mes_sel = st.sidebar.selectbox("Mês Competência", options=lista_meses, index=len(lista_meses)-1)

        df_apenas_comb = df_base[df_base["Placa"].str.startswith("COMBUSTÍVEL", na=False)]
        df_apenas_manut = df_base[~df_base["Placa"].str.startswith("COMBUSTÍVEL", na=False)]

        try:
            mes_num_atual = df_ano[df_ano["Mes_Nome"] == mes_sel]["Mes_Num"].iloc[0]
        except:
            mes_num_atual = 1

        df_filtrado_mes_manut = df_apenas_manut[df_apenas_manut["Mes_Nome"] == mes_sel]
        df_acumulado_ate_mes_manut = df_apenas_manut[df_apenas_manut["Mes_Num"] <= mes_num_atual]
        df_anterior_manut = df_apenas_manut[df_apenas_manut["Mes_Num"] == mes_num_atual - 1]

        df_comb_mes = df_apenas_comb[df_apenas_comb["Mes_Nome"] == mes_sel]
        df_comb_acum = df_apenas_comb[df_apenas_comb["Mes_Num"] <= mes_num_atual]
        df_comb_anterior = df_apenas_comb[df_apenas_comb["Mes_Num"] == mes_num_atual - 1]

        # ==========================================================
        # CONJUNTO DE ABAS - OTIMIZADO PARA 8 OPÇÕES
        # ==========================================================
        tab_ceo, tab_manut, tab_comb, tab_seg, tab_raiox, tab_km, tab_frota, tab_detalhes = st.tabs([
            "🌐 Visão Executiva",
            "🔧 Manutenção", 
            "⛽ Combustível", 
            "🛡️ Seguro/Rastreadores", 
            "📍 Raio-X da Base", 
            "🛣️ Gestão de Quilometragem", 
            "📋 Frota, IPVA & Doc", 
            "📑 Detalhamento"
        ])

        with tab_ceo:
            # ==========================================================
            # VISÃO EXECUTIVA 2.0 — GESTÃO, ORÇAMENTO E RASTREABILIDADE
            # ==========================================================
            st.markdown(f"### 🌎 Painel Executivo de Logística | {ano_sel}")

            if inst_sel == "AMES":
                nome_unidade = "Base Social"
                titulo_ranking_unidades = "📍 Bases Sociais | Maior Custo Acumulado"
                titulo_raiox_unidades = "🔎 Raio-X das Bases Sociais"
                contexto_inst = "AMES · Apoio à atuação missionária"
            elif inst_sel == "IAV":
                nome_unidade = "Centro de Custo"
                titulo_ranking_unidades = "🏢 Centros de Custo | Maior Custo Acumulado"
                titulo_raiox_unidades = "🔎 Raio-X dos Centros de Custo"
                contexto_inst = "IAV · Estrutura, projetos e serviços"
            else:
                nome_unidade = "Unidade"
                titulo_ranking_unidades = "📊 Unidades | Maior Custo Acumulado"
                titulo_raiox_unidades = "🔎 Raio-X das Unidades"
                contexto_inst = "AMES + IAV · Visão consolidada"

            st.caption(f"{contexto_inst} · Acumulado até {mes_sel}/{ano_sel}")

            # ---------- Regras centrais de classificação ----------
            # Cadastro/composição da frota: serve para identificar os ativos,
            # modelos, motoristas e vínculos. NÃO entra nos custos.
            cadastro_pattern = r"^(VEÍCUL|VEICUL|ALUGAD|MOTO|KOMBI|TRICICLO|REBOQUE|SPRINTER|ÔNIBUS|ONIBUS|MICRO)"

            def limpar_unidade(valor):
                texto = str(valor).strip()
                # Ignora o código do ERP entre parênteses e padroniza espaços.
                texto = re.sub(r"\s*\(\d+\)\s*$", "", texto).strip()
                texto = re.sub(r"\s+", " ", texto)
                texto = re.sub(r"\s*-\s*", " - ", texto)
                # Correções conhecidas de nomenclatura.
                texto = texto.replace("RDB7G83", "RBD7G83")
                texto = texto.replace("LOGISTICA", "LOGÍSTICA")
                return texto.strip()

            # Base financeira: exclui somente o cadastro auxiliar da frota.
            # Permanecem placas físicas + placas digitais de custo.
            mask_cadastro_exec = df_base_completa["Placa"].astype(str).str.contains(
                cadastro_pattern, case=False, na=False, regex=True
            )
            df_fin_exec = df_base_completa[~mask_cadastro_exec].copy()
            df_fin_exec = df_fin_exec[df_fin_exec["Mes_Num"] <= mes_num_atual].copy()
            df_fin_exec["Unidade_Gestao"] = df_fin_exec[col_cc].apply(limpar_unidade)
            df_fin_exec["Custo_Total"] = (
                df_fin_exec["Custo de manutenção"]
                + df_fin_exec["Custo Combustível"]
                + df_fin_exec["Custo de seguro"]
                + df_fin_exec["Custo de Rastreador"]
            )

            # Frota atual: usa o cadastro auxiliar, pega o último vínculo conhecido
            # de cada placa física no ano e só então aplica o filtro da unidade.
            mask_cadastro_frota = df_temp_inst["Placa"].astype(str).str.contains(
                cadastro_pattern, case=False, na=False, regex=True
            )
            df_frota_atual = df_temp_inst[mask_cadastro_frota].copy()
            if not df_frota_atual.empty:
                df_frota_atual["Placa_Fisica"] = df_frota_atual["Placa"].astype(str).str.upper().str.extract(r"([A-Z0-9]{7})\s*$", expand=False)
                df_frota_atual["Placa_Fisica"] = df_frota_atual["Placa_Fisica"].fillna(df_frota_atual["Placa"].astype(str))
                df_frota_atual = df_frota_atual.sort_values("Mes_Num").drop_duplicates(subset=["Placa_Fisica"], keep="last")
                df_frota_atual["Unidade_Gestao"] = df_frota_atual[col_cc].apply(limpar_unidade)
                if cc_sel != "TODOS":
                    unidade_sel_limpa = limpar_unidade(cc_sel)
                    df_frota_atual = df_frota_atual[df_frota_atual["Unidade_Gestao"] == unidade_sel_limpa]

            # ---------- Indicadores executivos ----------
            gasto_manut_acum = df_fin_exec["Custo de manutenção"].sum()
            gasto_comb_acum = df_fin_exec["Custo Combustível"].sum()
            gasto_seguro_acum = df_fin_exec["Custo de seguro"].sum()
            gasto_rastreador_acum = df_fin_exec["Custo de Rastreador"].sum()
            custo_total_global = df_fin_exec["Custo_Total"].sum()
            km_total_global = df_fin_exec["Quilometragem"].sum()
            qtd_frota = df_frota_atual["Placa_Fisica"].nunique() if not df_frota_atual.empty else 0

            orc_manut = sum(ORCAMENTOS_MANUT_2026.get(inst, 0) for inst in inst_ativas)
            orc_comb = sum(ORCAMENTOS_COMB_2026.get(inst, 0) for inst in inst_ativas)
            orc_seg = sum(ORCAMENTOS_SEGURO_2026.get(inst, 0) for inst in inst_ativas)
            orc_rast = sum(ORCAMENTOS_RASTREADOR_2026.get(inst, 0) for inst in inst_ativas)
            orcamento_total_global = orc_manut + orc_comb + orc_seg + orc_rast

            saldo_global = orcamento_total_global - custo_total_global
            perc_global = (custo_total_global / orcamento_total_global * 100) if orcamento_total_global > 0 else 0
            cpk_global = custo_total_global / km_total_global if km_total_global > 0 else 0
            projecao_anual = (custo_total_global / mes_num_atual) * 12 if mes_num_atual > 0 else 0
            diferenca_proj = orcamento_total_global - projecao_anual

            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                draw_card(
                    "💰 CUSTO ACUMULADO",
                    fmt_br(custo_total_global, True),
                    f"Até {mes_sel}/{ano_sel}"
                )
            with c2:
                if ano_sel == 2026 and orcamento_total_global > 0:
                    draw_card(
                        "🎯 EXECUÇÃO ORÇAMENTÁRIA",
                        f"{perc_global:.1f}%",
                        f"Orçamento: <b>{fmt_br(orcamento_total_global, True)}</b>",
                        progress=perc_global,
                        progress_text=f"Saldo: {fmt_br(saldo_global, True)}"
                    )
                else:
                    draw_card("🎯 EXECUÇÃO ORÇAMENTÁRIA", "—", "Orçamento não cadastrado para o ano")
            with c3:
                if ano_sel == 2026 and orcamento_total_global > 0:
                    if projecao_anual <= orcamento_total_global:
                        texto_proj = f"🟢 {fmt_br(diferenca_proj, True)} abaixo do orçamento"
                    else:
                        texto_proj = f"🔴 {fmt_br(abs(diferenca_proj), True)} acima do orçamento"
                    draw_card(
                        "📈 PREVISÃO DE GASTO ATÉ DEZ/26",
                        fmt_br(projecao_anual, True),
                        texto_proj
                    )
                else:
                    draw_card("📈 PREVISÃO DE GASTO ATÉ DEZ", fmt_br(projecao_anual, True), "Mantida a média atual de gastos")
            with c4:
                draw_card(
                    "🛣️ KM ACUMULADOS",
                    fmt_br(km_total_global),
                    f"CPK global: <b>{fmt_br(cpk_global, True)}/km</b>",
                    is_lower_better=False
                )
            with c5:
                draw_card(
                    "🚙 ATIVOS CADASTRADOS",
                    fmt_br(qtd_frota),
                    "Ativos no último vínculo conhecido do ano",
                    is_lower_better=False
                )

            st.markdown("<hr style='margin-top: 5px; margin-bottom: 18px'>", unsafe_allow_html=True)

            # ---------- Leitura financeira executiva ----------
            col_recursos, col_orcado = st.columns([1, 1.45])

            with col_recursos:
                st.markdown('<div class="chart-title">💰 Composição dos Custos</div>', unsafe_allow_html=True)
                df_composicao = pd.DataFrame({
                    "Categoria": ["Manutenção", "Combustível", "Seguro", "Rastreador"],
                    "Valor": [gasto_manut_acum, gasto_comb_acum, gasto_seguro_acum, gasto_rastreador_acum]
                })
                df_composicao = df_composicao[df_composicao["Valor"] > 0]
                if not df_composicao.empty:
                    fig_comp = px.pie(
                        df_composicao, names="Categoria", values="Valor", color="Categoria",
                        color_discrete_map={
                            "Manutenção": "#F57C00", "Combustível": "#0288D1",
                            "Seguro": "#1A237E", "Rastreador": "#81D4FA"
                        }, hole=0
                    )
                    fig_comp.update_traces(
                        textposition="inside", textinfo="percent+label", textfont=dict(size=14),
                        hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>",
                        marker=dict(line=dict(color="#FFFFFF", width=2))
                    )
                    fig_comp.update_layout(
                        height=360, separators=",.", paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=5, r=5, t=5, b=30),
                        showlegend=True,
                        legend=dict(orientation="h", yanchor="top", y=-0.05, xanchor="center", x=0.5, font=dict(size=12))
                    )
                    st.plotly_chart(fig_comp, use_container_width=True, config={"displayModeBar": False})
                else:
                    st.info("Sem custos para exibir nesta seleção.")

            with col_orcado:
                st.markdown('<div class="chart-title">🎯 Real x Orçado por Categoria</div>', unsafe_allow_html=True)
                if ano_sel == 2026:
                    df_orcado = pd.DataFrame({
                        "Categoria": ["Manutenção", "Combustível", "Seguro", "Rastreador"],
                        "Real acumulado": [gasto_manut_acum, gasto_comb_acum, gasto_seguro_acum, gasto_rastreador_acum],
                        "Orçamento anual": [orc_manut, orc_comb, orc_seg, orc_rast]
                    })
                    df_orcado["Execução"] = df_orcado.apply(
                        lambda r: (r["Real acumulado"] / r["Orçamento anual"] * 100) if r["Orçamento anual"] > 0 else 0,
                        axis=1
                    )
                    df_orcado_long = df_orcado.melt(
                        id_vars=["Categoria", "Execução"],
                        value_vars=["Real acumulado", "Orçamento anual"],
                        var_name="Referência", value_name="Valor"
                    )
                    fig_orcado = px.bar(
                        df_orcado_long, x="Categoria", y="Valor", color="Referência", barmode="group",
                        text="Valor", custom_data=["Execução"],
                        color_discrete_map={"Real acumulado": "#F57C00", "Orçamento anual": "#1A237E"}
                    )
                    fig_orcado.update_traces(
                        texttemplate='<b>R$ %{text:,.0f}</b>', textposition='outside', cliponaxis=False,
                        hovertemplate='<b>%{x}</b><br>%{fullData.name}: R$ %{y:,.2f}<br>Execução: %{customdata[0]:.1f}%<extra></extra>'
                    )
                    max_orcado = df_orcado_long["Valor"].max() if not df_orcado_long.empty else 1
                    fig_orcado.update_layout(
                        height=360, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=5, r=10, t=5, b=20),
                        yaxis=dict(title="", showticklabels=False, showgrid=True, gridcolor="#E6ECF2", range=[0, max_orcado * 1.22]),
                        xaxis=dict(title="", tickfont=dict(size=12)),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title="", font=dict(size=12))
                    )
                    st.plotly_chart(fig_orcado, use_container_width=True, config={"displayModeBar": False})
                    execucao_resumo = " · ".join(
                        f'{r["Categoria"]}: {r["Execução"]:.1f}%' if r["Orçamento anual"] > 0 else f'{r["Categoria"]}: sem orçamento'
                        for _, r in df_orcado.iterrows()
                    )
                    st.caption(f"Execução do orçamento anual · {execucao_resumo}")
                else:
                    st.info("Comparativo Real x Orçado disponível para 2026, ano com orçamento cadastrado.")

            st.markdown('<div class="chart-title">🚨 Radar de Atenção</div>', unsafe_allow_html=True)
            alertas = []
            if ano_sel == 2026 and orcamento_total_global > 0:
                perc_tempo = (mes_num_atual / 12) * 100
                if projecao_anual > orcamento_total_global:
                    alertas.append(f"⚠️ **Projeção acima do orçamento:** excesso estimado de {fmt_br(abs(diferenca_proj), True)}.")
                elif perc_global > perc_tempo + 10:
                    alertas.append(f"⚠️ **Ritmo de consumo elevado:** {perc_global:.1f}% do orçamento utilizado com {perc_tempo:.1f}% do ano transcorrido.")

                exec_categorias = [
                    ("Manutenção", gasto_manut_acum, orc_manut),
                    ("Combustível", gasto_comb_acum, orc_comb),
                    ("Seguro", gasto_seguro_acum, orc_seg),
                    ("Rastreador", gasto_rastreador_acum, orc_rast)
                ]
                exec_validas = [(cat, real / orc * 100) for cat, real, orc in exec_categorias if orc > 0]
                if exec_validas:
                    cat_crit, perc_crit = max(exec_validas, key=lambda x: x[1])
                    if perc_crit > perc_tempo + 10:
                        alertas.append(f"🎯 **{cat_crit}** · Maior pressão orçamentária: {perc_crit:.1f}% do orçamento anual já executado.")

            mask_placa_fisica = df_fin_exec["Placa"].astype(str).str.fullmatch(r"[A-Z0-9]{7}", case=False, na=False)
            df_placas_exec = df_fin_exec[mask_placa_fisica].copy()
            if not df_placas_exec.empty and df_placas_exec["Custo de manutenção"].sum() > 0:
                resumo_placa = df_placas_exec.groupby("Placa", as_index=False).agg({
                    "Custo de manutenção": "sum", "Custo_Total": "sum", "Quilometragem": "sum"
                }).sort_values("Custo de manutenção", ascending=False)
                placa_crit = resumo_placa.iloc[0]["Placa"]
                valor_crit = resumo_placa.iloc[0]["Custo de manutenção"]
                custo_total_crit = resumo_placa.iloc[0]["Custo_Total"]
                km_crit = resumo_placa.iloc[0]["Quilometragem"]
                cpk_crit = custo_total_crit / km_crit if km_crit > 0 else 0
                unidade_crit = ""
                if not df_frota_atual.empty:
                    vinculo = df_frota_atual[df_frota_atual["Placa_Fisica"].astype(str).str.upper() == str(placa_crit).upper()]
                    if not vinculo.empty:
                        unidade_crit = str(vinculo.iloc[-1]["Unidade_Gestao"])
                titulo_crit = unidade_crit if "ODONTOVAN" in unidade_crit.upper() else placa_crit
                alertas.append(
                    f"🔧 **{titulo_crit}** · Maior manutenção acumulada: {fmt_br(valor_crit, True)} · Custo/KM: {fmt_br(cpk_crit, True)}"
                )

            if alertas:
                radar_cols = st.columns(2)
                for idx, alerta in enumerate(alertas[:4]):
                    classe = "critical" if ("acima do orçamento" in alerta.lower() or "ritmo de consumo elevado" in alerta.lower()) else "warning"
                    with radar_cols[idx % 2]:
                        st.markdown(f'<div class="radar-card {classe}">{alerta.replace("**", "")}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="radar-card ok">✅ Nenhum alerta financeiro crítico identificado para a seleção atual.</div>', unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)

            # ---------- Ranking de Bases Sociais / Centros de Custo ----------
            df_unidades = df_fin_exec.groupby(["Instituição", "Unidade_Gestao"], as_index=False).agg({
                "Custo de manutenção": "sum",
                "Custo Combustível": "sum",
                "Custo de seguro": "sum",
                "Custo de Rastreador": "sum",
                "Custo_Total": "sum",
                "Quilometragem": "sum"
            })

            if not df_frota_atual.empty:
                frota_unid = df_frota_atual.groupby(["Instituição", "Unidade_Gestao"])["Placa_Fisica"].nunique().reset_index(name="Ativos")
                df_unidades = pd.merge(df_unidades, frota_unid, on=["Instituição", "Unidade_Gestao"], how="left")
            else:
                df_unidades["Ativos"] = 0

            df_unidades["Ativos"] = df_unidades["Ativos"].fillna(0).astype(int)
            df_unidades["Custo/KM"] = df_unidades.apply(
                lambda r: r["Custo_Total"] / r["Quilometragem"] if r["Quilometragem"] > 0 else 0, axis=1
            )

            col_rank, col_top = st.columns([1.25, 1])
            with col_rank:
                st.markdown(f'<div class="chart-title">{titulo_ranking_unidades}</div>', unsafe_allow_html=True)
                top_unidades = df_unidades[df_unidades["Custo_Total"] > 0].nlargest(8, "Custo_Total").sort_values("Custo_Total")
                if not top_unidades.empty:
                    fig_unid = px.bar(
                        top_unidades,
                        x="Custo_Total", y="Unidade_Gestao", orientation="h",
                        text="Custo_Total", color="Instituição",
                        color_discrete_map={"AMES": "#0288D1", "IAV": "#F57C00"}
                    )
                    fig_unid.update_traces(texttemplate='<b>R$ %{text:,.0f}</b>', textposition='outside', cliponaxis=False)
                    fig_unid.update_layout(
                        height=390, separators=',.',
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=10, r=90, t=5, b=10),
                        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                        yaxis=dict(title="", automargin=True, tickfont=dict(size=13)),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title="", font=dict(size=12))
                    )
                    st.plotly_chart(fig_unid, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.info("Sem custos para exibir nesta seleção.")

            with col_top:
                st.markdown(f'<div class="chart-title">{titulo_raiox_unidades}</div>', unsafe_allow_html=True)
                tabela_unid = df_unidades[df_unidades["Custo_Total"] > 0].nlargest(8, "Custo_Total")[
                    ["Instituição", "Unidade_Gestao", "Ativos", "Quilometragem", "Custo_Total", "Custo/KM"]
                ].rename(columns={"Unidade_Gestao": nome_unidade})
                if not tabela_unid.empty:
                    linhas = []
                    mostrar_inst = inst_sel == "TODAS"
                    for _, r in tabela_unid.iterrows():
                        tag = f'<span class="rx-inst">{r["Instituição"]}</span>' if mostrar_inst else ""
                        linhas.append(
                            f'<div class="rx-row">'
                            f'<div class="rx-name">{r[nome_unidade]}{tag}</div>'
                            f'<div class="rx-ativos">{int(r["Ativos"])} ativos</div>'
                            f'<div class="rx-km">{fmt_br(r["Quilometragem"])} km</div>'
                            f'<div class="rx-money">{fmt_br(r["Custo_Total"], True)}</div>'
                            f'<div class="rx-badge">{fmt_br(r["Custo/KM"], True)}/km</div>'
                            f'</div>'
                        )

                    cabecalho_rx = (
                        '<div class="rx-header">'
                        f'<div>{nome_unidade}</div>'
                        '<div style="text-align:right">Ativos</div>'
                        '<div style="text-align:right">KM</div>'
                        '<div style="text-align:right">Custo Total</div>'
                        '<div style="text-align:right">Custo/KM</div>'
                        '</div>'
                    )

                    st.markdown(
                        '<div class="rx-list">' + cabecalho_rx + "".join(linhas) + '</div>',
                        unsafe_allow_html=True
                    )

            # ---------- Destaque específico: Odontovans ----------
            df_odonto = df_unidades[
                df_unidades["Unidade_Gestao"].astype(str).str.contains("ODONTOVAN", case=False, na=False)
                & ~df_unidades["Unidade_Gestao"].astype(str).str.contains("CAFARNAUM", case=False, na=False)
            ].copy()
            if not df_odonto.empty:
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown('<div class="chart-title">🦷 Odontovans | Painel Executivo</div>', unsafe_allow_html=True)

                od_custo = df_odonto["Custo_Total"].sum()
                od_manut = df_odonto["Custo de manutenção"].sum()
                od_comb = df_odonto["Custo Combustível"].sum()
                od_km = df_odonto["Quilometragem"].sum()
                od_cpk = od_custo / od_km if od_km > 0 else 0

                df_iav_ref = df_ano[df_ano["Instituição"] == "IAV"].copy()
                mask_cadastro_iav = df_iav_ref["Placa"].astype(str).str.contains(
                    cadastro_pattern, case=False, na=False, regex=True
                )
                df_iav_ref = df_iav_ref[~mask_cadastro_iav].copy()
                df_iav_ref = df_iav_ref[df_iav_ref["Mes_Num"] <= mes_num_atual].copy()
                custo_iav_ref = (
                    df_iav_ref["Custo de manutenção"].sum() + df_iav_ref["Custo Combustível"].sum()
                    + df_iav_ref["Custo de seguro"].sum() + df_iav_ref["Custo de Rastreador"].sum()
                )
                od_part_iav = (od_custo / custo_iav_ref * 100) if custo_iav_ref > 0 else 0

                resumo_od_html = (
                    '<div class="odonto-summary">'
                    + f'<div class="odonto-kpi"><div class="odonto-kpi-label">Custo total</div><div class="odonto-kpi-value">{fmt_br(od_custo, True)}</div><div class="odonto-kpi-sub">Acumulado até {mes_sel}</div></div>'
                    + f'<div class="odonto-kpi"><div class="odonto-kpi-label">Manutenção</div><div class="odonto-kpi-value">{fmt_br(od_manut, True)}</div><div class="odonto-kpi-sub">Custo acumulado</div></div>'
                    + f'<div class="odonto-kpi"><div class="odonto-kpi-label">Combustível</div><div class="odonto-kpi-value">{fmt_br(od_comb, True)}</div><div class="odonto-kpi-sub">Custo acumulado</div></div>'
                    + f'<div class="odonto-kpi"><div class="odonto-kpi-label">KM acumulados</div><div class="odonto-kpi-value">{fmt_br(od_km)}</div><div class="odonto-kpi-sub">Quilometragem total</div></div>'
                    + f'<div class="odonto-kpi"><div class="odonto-kpi-label">Participação no IAV</div><div class="odonto-kpi-value">{od_part_iav:.1f}%</div><div class="odonto-kpi-sub">Do custo total do IAV</div></div>'
                    + '</div>'
                )
                st.markdown(resumo_od_html, unsafe_allow_html=True)

                tabela_odonto = df_odonto[[
                    "Instituição", "Unidade_Gestao", "Ativos", "Quilometragem",
                    "Custo de manutenção", "Custo Combustível", "Custo_Total", "Custo/KM"
                ]].sort_values("Custo_Total", ascending=False).rename(columns={
                    "Unidade_Gestao": "Odontovan", "Quilometragem": "KM"
                })

                col_od_graf, col_od_tabela = st.columns([1, 1.4])
                with col_od_graf:
                    st.markdown('<div class="chart-title">📊 Custo Total por Odontovan</div>', unsafe_allow_html=True)
                    graf_od = tabela_odonto[tabela_odonto["Custo_Total"] > 0].sort_values("Custo_Total")
                    if not graf_od.empty:
                        fig_od = px.bar(
                            graf_od, x="Custo_Total", y="Odontovan", orientation="h",
                            text="Custo_Total", color_discrete_sequence=["#F57C00"]
                        )
                        fig_od.update_traces(texttemplate='<b>R$ %{text:,.0f}</b>', textposition='outside', cliponaxis=False)
                        max_od = graf_od["Custo_Total"].max() if not graf_od.empty else 1
                        fig_od.update_layout(
                            height=max(300, 54 * len(graf_od) + 90), separators=',.',
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=5, r=95, t=5, b=10),
                            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, max_od * 1.32]),
                            yaxis=dict(title="", automargin=True, tickfont=dict(size=12)), showlegend=False
                        )
                        st.plotly_chart(fig_od, use_container_width=True, config={"displayModeBar": False})

                with col_od_tabela:
                    st.markdown('<div class="chart-title">🔎 Comparativo Operacional</div>', unsafe_allow_html=True)
                    linhas_od = []
                    mostrar_inst_od = inst_sel == "TODAS"
                    for _, r in tabela_odonto.iterrows():
                        tag = f'<span class="rx-inst">{r["Instituição"]}</span>' if mostrar_inst_od else ""
                        linhas_od.append(
                            f'<div class="rx-row">'
                            f'<div class="rx-name">{r["Odontovan"]}{tag}</div>'
                            f'<div class="rx-ativos">{int(r["Ativos"])} ativos</div>'
                            f'<div class="rx-km">{fmt_br(r["KM"])} km</div>'
                            f'<div class="rx-money">{fmt_br(r["Custo_Total"], True)}</div>'
                            f'<div class="rx-badge">{fmt_br(r["Custo/KM"], True)}/km</div>'
                            f'</div>'
                        )
                    cabecalho_od = (
                        '<div class="rx-header"><div>Odontovan</div>'
                        '<div style="text-align:right">Ativos</div><div style="text-align:right">KM</div>'
                        '<div style="text-align:right">Custo Total</div><div style="text-align:right">Custo/KM</div></div>'
                    )
                    st.markdown('<div class="rx-list">' + cabecalho_od + "".join(linhas_od) + '</div>', unsafe_allow_html=True)

        with tab_manut:
            # ================= VISÃO MENSAL =================
            st.markdown(f"### 📊 Desempenho Mensal | {mes_sel}/{ano_sel}")

            km_m = df_filtrado_mes_manut['Quilometragem'].sum()
            km_a = df_anterior_manut['Quilometragem'].sum()
            trend_km = ((km_m-km_a)/km_a*100) if km_a > 0 else 0

            custo_m = df_filtrado_mes_manut['Custo de manutenção'].sum()
            custo_a = df_anterior_manut['Custo de manutenção'].sum()
            trend_c = ((custo_m-custo_a)/custo_a*100) if custo_a > 0 else 0

            mask_fisica_mes = df_filtrado_mes_manut["Placa"].astype(str).str.fullmatch(
                r"[A-Z0-9]{7}", case=False, na=False
            )
            df_veiculos_manut_mes = df_filtrado_mes_manut[
                mask_fisica_mes & (df_filtrado_mes_manut["Custo de manutenção"] > 0)
            ].copy()
            veiculos_manut_mes = df_veiculos_manut_mes["Placa"].nunique()
            custo_medio_atendido = custo_m / veiculos_manut_mes if veiculos_manut_mes > 0 else 0

            gasto_manut_acum_aba = df_acumulado_ate_mes_manut["Custo de manutenção"].sum()
            orc_manut_aba = sum(ORCAMENTOS_MANUT_2026.get(inst, 0) for inst in inst_ativas) if ano_sel == 2026 else 0
            perc_manut_aba = (gasto_manut_acum_aba / orc_manut_aba * 100) if orc_manut_aba > 0 else 0

            m1, m2, m3, m4, m5 = st.columns(5)
            with m1:
                if custo_a > 0:
                    if trend_c > 0:
                        classe_vs = "vs-alta"
                        icone_vs = "▲"
                    elif trend_c < 0:
                        classe_vs = "vs-baixa"
                        icone_vs = "▼"
                    else:
                        classe_vs = "vs-neutro"
                        icone_vs = "●"

                    texto_vs = (
                        f'Vs mês anterior: '
                        f'<span class="{classe_vs}">'
                        f'{icone_vs} {abs(trend_c):.1f}%</span>'
                    )
                else:
                    texto_vs = "Vs mês anterior: sem base de comparação"

                draw_card("🔧 CUSTO NO MÊS", fmt_br(custo_m, True), texto_vs)
            with m2:
                draw_card("💰 CUSTO ACUMULADO", fmt_br(gasto_manut_acum_aba, True), f"Até {mes_sel}/{ano_sel}")
            with m3:
                draw_card("🚙 VEÍCULOS ATENDIDOS", fmt_br(veiculos_manut_mes), "Com manutenção lançada no mês", is_lower_better=False)
            with m4:
                draw_card("📊 MÉDIA POR VEÍCULO", fmt_br(custo_medio_atendido, True), "Entre veículos atendidos no mês")
            with m5:
                if ano_sel == 2026 and orc_manut_aba > 0:
                    draw_card(
                        "🎯 ORÇAMENTO CONSUMIDO", f"{perc_manut_aba:.1f}%",
                        f"Orçamento anual: <b>{fmt_br(orc_manut_aba, True)}</b>",
                        progress=perc_manut_aba,
                        progress_text=f"Saldo: {fmt_br(orc_manut_aba-gasto_manut_acum_aba, True)}"
                    )
                else:
                    draw_card("🎯 ORÇAMENTO CONSUMIDO", "—", "Orçamento não cadastrado para o ano")

            if busca_placa:
                st.markdown("---")
                st.markdown(f"#### 🔍 Raio-X do Veículo: {busca_placa}")
                
                df_veiculo = df_base[df_base["Placa"] == busca_placa].sort_values("Mes_Num")
                
                if not df_veiculo.empty:
                    v_gasto_total = df_veiculo['Custo de manutenção'].sum()
                    v_km_total = df_veiculo['Quilometragem'].sum()
                    v_custo_km = v_gasto_total / v_km_total if v_km_total > 0 else 0
                    v_base = df_veiculo['Base'].iloc[-1]
                    
                    st.markdown(f"""
                    <div class="raiox-container">
                        <div class="raiox-item">
                            <div class="raiox-label">📍 Base atual</div>
                            <div class="raiox-value" style="font-size: 16px;">{v_base}</div>
                        </div>
                        <div class="raiox-item">
                            <div class="raiox-label">💰 Gasto Total Ano</div>
                            <div class="raiox-value" style="font-size: 16px;">{fmt_br(v_gasto_total, True)}</div>
                        </div>
                        <div class="raiox-item">
                            <div class="raiox-label">🛣️ KM Total Ano</div>
                            <div class="raiox-value" style="font-size: 16px;">{fmt_br(v_km_total)}</div>
                        </div>
                        <div class="raiox-item">
                            <div class="raiox-label">📊 Custo por KM</div>
                            <div class="raiox-value" style="font-size: 16px;">{fmt_br(v_custo_km, True)}/km</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    fig_raiox = px.line(df_veiculo, x='Mes_Nome', y='Custo de manutenção', markers=True, title="Histórico de Gastos (Manutenção)")
                    fig_raiox.update_traces(line_color='#0288D1', marker=dict(size=10, color='#1A237E'))
                    fig_raiox.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=30, b=0))
                    st.plotly_chart(fig_raiox, use_container_width=True)
                else:
                    st.warning("Nenhum dado financeiro ou de KM encontrado para esta Placa no período.")
                st.markdown("---")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            g1, g2 = st.columns(2)
            
            mask_veiculos_reais = (
                (~df_filtrado_mes_manut["Placa"].astype(str).str.contains("COMBUS|SEGUR|FINANC|CONSÓRC|RASTR|LOGIST|MANUT|MENSAL|TAXA", case=False, na=True)) &
                (df_filtrado_mes_manut["Placa"].astype(str).str.strip() != "") &
                (df_filtrado_mes_manut["Placa"].astype(str).str.upper() != "NAN") &
                (df_filtrado_mes_manut["Placa"].astype(str).str.strip() != "0")
            )
            df_top10 = df_filtrado_mes_manut[mask_veiculos_reais]

            with g1:
                st.markdown('<div class="chart-title">Top 10 veículos | Maior Quilometragem no Mês</div>', unsafe_allow_html=True)
                top10_km = df_top10[df_top10['Quilometragem'] > 0].nlargest(10, 'Quilometragem').sort_values('Quilometragem', ascending=True)
                
                if not top10_km.empty:
                    top10_km['Placa_Base'] = "<b>" + top10_km['Placa'] + "</b><br><span style='font-size:9.5px; color:#888888; font-weight:normal;'>" + top10_km['Base'] + "</span>"
                    fig_km = px.bar(top10_km, x='Quilometragem', y='Placa_Base', orientation='h', text='Quilometragem', color_discrete_sequence=['#0288D1'])
                    fig_km.update_traces(texttemplate='<b>%{text:,.0f}</b>', textposition='outside', textfont=ESTILO_TEXTO, cliponaxis=False)
                    max_km = top10_km['Quilometragem'].max() if not top10_km.empty else 1
                    fig_km.update_layout(height=450, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(r=150, l=10, t=10, b=10), xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, max_km * 1.4]), yaxis=dict(automargin=True, tickfont=dict(size=13, color='#333333', family="Arial, sans-serif"), title=""))
                    st.plotly_chart(fig_km, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.info("Nenhum dado para exibir neste mês.")
                
            with g2:
                st.markdown('<div class="chart-title">Top 10 veículos | Maior Custo de Manutenção no Mês</div>', unsafe_allow_html=True)
                top10_custo = df_top10[df_top10['Custo de manutenção'] > 0].nlargest(10, 'Custo de manutenção').sort_values('Custo de manutenção', ascending=True)
                
                if not top10_custo.empty and top10_custo['Custo de manutenção'].sum() > 0:
                    top10_custo['Placa_Base'] = "<b>" + top10_custo['Placa'] + "</b><br><span style='font-size:9.5px; color:#888888; font-weight:normal;'>" + top10_custo['Base'] + "</span>"
                    fig_custo = px.bar(top10_custo, x='Custo de manutenção', y='Placa_Base', orientation='h', text='Custo de manutenção', color_discrete_sequence=['#F57C00'])
                    fig_custo.update_traces(texttemplate='<b>R$ %{text:,.2f}</b>', textposition='outside', textfont=ESTILO_TEXTO, cliponaxis=False)
                    max_c = top10_custo['Custo de manutenção'].max() if not top10_custo.empty else 1
                    fig_custo.update_layout(height=450, separators=',.', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(r=150, l=10, t=10, b=10), xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, max_c * 1.4]), yaxis=dict(automargin=True, tickfont=dict(size=13, color='#333333', family="Arial, sans-serif"), title=""))
                    st.plotly_chart(fig_custo, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.info("Nenhum custo lançado neste mês.")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div class="chart-title">⚠️ Veículos em Atenção | Acumulado</div>',
                unsafe_allow_html=True
            )
            st.caption(
                "Critério gerencial: veículos que apresentam pelo menos 2 sinais de atenção entre "
                "custo acumulado acima da média, custo de manutenção por KM acima da média e recorrência de manutenção."
            )

            mask_fisica_acum = df_acumulado_ate_mes_manut["Placa"].astype(str).str.fullmatch(
                r"[A-Z0-9]{7}", case=False, na=False
            )
            df_atencao_base = df_acumulado_ate_mes_manut[mask_fisica_acum].copy()

            if not df_atencao_base.empty:
                resumo_atencao = df_atencao_base.groupby("Placa", as_index=False).agg({
                    "Custo de manutenção": "sum",
                    "Quilometragem": "sum"
                })

                meses_manut = (
                    df_atencao_base[df_atencao_base["Custo de manutenção"] > 0]
                    .groupby("Placa")["Mes_Num"]
                    .nunique()
                    .reset_index(name="Meses com Manutenção")
                )

                resumo_atencao = resumo_atencao.merge(
                    meses_manut, on="Placa", how="left"
                )
                resumo_atencao["Meses com Manutenção"] = (
                    resumo_atencao["Meses com Manutenção"].fillna(0).astype(int)
                )

                resumo_atencao = resumo_atencao[
                    resumo_atencao["Custo de manutenção"] > 0
                ].copy()

                resumo_atencao["Custo/KM Manut."] = resumo_atencao.apply(
                    lambda r: (
                        r["Custo de manutenção"] / r["Quilometragem"]
                        if r["Quilometragem"] > 0 else 0
                    ),
                    axis=1
                )

                media_custo_frota = (
                    resumo_atencao["Custo de manutenção"].mean()
                    if not resumo_atencao.empty else 0
                )

                positivos_cpk = resumo_atencao[
                    resumo_atencao["Custo/KM Manut."] > 0
                ]
                media_cpk_frota = (
                    positivos_cpk["Custo/KM Manut."].mean()
                    if not positivos_cpk.empty else 0
                )

                # Recorrência: manutenção registrada em 2 ou mais competências.
                resumo_atencao["Sinal_Custo"] = (
                    resumo_atencao["Custo de manutenção"] > media_custo_frota
                )
                resumo_atencao["Sinal_CPK"] = (
                    (resumo_atencao["Custo/KM Manut."] > media_cpk_frota)
                    & (resumo_atencao["Quilometragem"] > 0)
                )
                resumo_atencao["Sinal_Recorrencia"] = (
                    resumo_atencao["Meses com Manutenção"] >= 2
                )

                resumo_atencao["Qtd_Sinais"] = (
                    resumo_atencao[
                        ["Sinal_Custo", "Sinal_CPK", "Sinal_Recorrencia"]
                    ].sum(axis=1)
                )

                criticos = (
                    resumo_atencao[resumo_atencao["Qtd_Sinais"] >= 2]
                    .sort_values(
                        ["Qtd_Sinais", "Custo de manutenção"],
                        ascending=[False, False]
                    )
                    .head(5)
                )

                if not criticos.empty:
                    for _, r in criticos.iterrows():
                        motivos = []
                        if r["Sinal_Custo"]:
                            motivos.append("custo acima da média")
                        if r["Sinal_CPK"]:
                            motivos.append("custo/KM acima da média")
                        if r["Sinal_Recorrencia"]:
                            motivos.append(
                                f'{int(r["Meses com Manutenção"])} meses com manutenção'
                            )

                        motivos_txt = " · ".join(motivos)

                        st.markdown(
                            f'<div class="manut-attention">'
                            f'<b>{r["Placa"]}</b> · '
                            f'Manutenção: <b>{fmt_br(r["Custo de manutenção"], True)}</b> · '
                            f'KM: {fmt_br(r["Quilometragem"])} · '
                            f'Custo manut./KM: <b>{fmt_br(r["Custo/KM Manut."], True)}/km</b><br>'
                            f'<span style="font-size:13px;color:#607D8B;">'
                            f'Motivos: {motivos_txt}</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                else:
                    st.success(
                        "Nenhum veículo apresenta pelo menos 2 sinais de atenção na seleção atual."
                    )
            else:
                st.info("Sem dados suficientes para análise de veículos em atenção.")

            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("---")

            # ================= VISÃO ACUMULADA =================
            st.markdown(f"### 📈 Desempenho Acumulado | {ano_sel}")
            
            ca1, ca2, ca3 = st.columns(3)
            with ca1:
                if ano_sel == 2026:
                    orc_total_manut = sum(ORCAMENTOS_MANUT_2026.get(inst, 0) for inst in inst_ativas)
                    saldo_manut = orc_total_manut - gasto_manut_acum
                    perc_manut = (gasto_manut_acum / orc_total_manut * 100) if orc_total_manut > 0 else 0
                    sub_manut = f"Orçamento Anual: <b>{fmt_br(orc_total_manut, True)}</b>"
                    prog_text_manut = f"{perc_manut:.1f}% &middot; Saldo {fmt_br(saldo_manut, True)}"
                    draw_card("EXECUÇÃO MANUT. (ACUMULADO)", fmt_br(gasto_manut_acum, True), sub_manut, progress=perc_manut, progress_text=prog_text_manut)
                else:
                    sub_manut = "Orçamento Anual: <b>A definir</b>"
                    draw_card("CUSTO DE MANUT. (ACUMULADO)", fmt_br(gasto_manut_acum, True), sub_manut)
                
            with ca2:
                km_acumulado = df_acumulado_ate_mes_manut['Quilometragem'].sum()
                sub_km = f"Total rodado em {ano_sel} até {mes_sel}"
                draw_card("QUILOMETRAGEM ACUMULADA", fmt_br(km_acumulado), subtext=sub_km, is_lower_better=False)
            
            st.markdown("---")
            
            st.markdown(
                f'<div class="chart-title">Evolução Mensal do Custo de Manutenção | {ano_sel}</div>',
                unsafe_allow_html=True
            )

            evol_inst = (
                df_acumulado_ate_mes_manut
                .groupby(['Mes_Num', 'Mes_Nome', 'Instituição'])['Custo de manutenção']
                .sum().reset_index().sort_values('Mes_Num')
            )

            evol_total = (
                df_acumulado_ate_mes_manut
                .groupby(['Mes_Num', 'Mes_Nome'])['Custo de manutenção']
                .sum().reset_index().sort_values('Mes_Num')
            )

            if not evol_inst.empty and not evol_total.empty:
                media_mensal = evol_total['Custo de manutenção'].mean()

                # Mantém a separação AMES/IAV quando ambas estiverem selecionadas,
                # mas em linha para enfatizar a evolução temporal.
                fig_evol = px.line(
                    evol_inst,
                    x='Mes_Nome',
                    y='Custo de manutenção',
                    color='Instituição',
                    markers=True,
                    text='Custo de manutenção',
                    color_discrete_map={"AMES": "#0288D1", "IAV": "#F57C00"}
                )

                fig_evol.update_traces(
                    texttemplate='<b>R$ %{text:,.0f}</b>',
                    textposition='top center',
                    textfont=dict(size=11),
                    line=dict(width=3),
                    marker=dict(size=8)
                )

                fig_evol.add_hline(
                    y=media_mensal,
                    line_dash='dash',
                    line_color='#78909C',
                    line_width=1.5,
                    annotation_text=f"Média mensal total: {fmt_br(media_mensal, True)}",
                    annotation_position='bottom right',
                    annotation_font=dict(size=11, color='#546E7A')
                )

                max_c_evol = max(
                    evol_inst['Custo de manutenção'].max(),
                    media_mensal
                ) if not evol_inst.empty else 1

                fig_evol.update_layout(
                    height=430,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(r=20, l=10, t=35, b=10),
                    yaxis=dict(
                        title="Custo no Mês (R$)",
                        showgrid=True,
                        gridcolor='#E0E0E0',
                        range=[0, max_c_evol * 1.30]
                    ),
                    xaxis=dict(title=""),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        title=""
                    ),
                    separators=',.'
                )
                st.plotly_chart(fig_evol, use_container_width=True, config={'displayModeBar': False})

                # Variação consolidada do último mês contra o mês anterior.
                if len(evol_total) >= 2:
                    atual = float(evol_total.iloc[-1]['Custo de manutenção'])
                    anterior = float(evol_total.iloc[-2]['Custo de manutenção'])
                    mes_atual = str(evol_total.iloc[-1]['Mes_Nome'])
                    mes_anterior = str(evol_total.iloc[-2]['Mes_Nome'])

                    if anterior > 0:
                        variacao_ev = ((atual - anterior) / anterior) * 100

                        if variacao_ev > 0:
                            classe_ev, icone_ev = "vs-alta", "▲"
                        elif variacao_ev < 0:
                            classe_ev, icone_ev = "vs-baixa", "▼"
                        else:
                            classe_ev, icone_ev = "vs-neutro", "●"

                        st.markdown(
                            f'<div style="font-size:12.5px;color:#455A64;margin-top:-8px;">'
                            f'{mes_atual} vs {mes_anterior}: '
                            f'<span class="{classe_ev}">{icone_ev} {abs(variacao_ev):.1f}%</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
            else:
                st.info("Sem dados mensais de manutenção para a seleção atual.")

            st.markdown("---")
            if inst_sel == "AMES":
                rotulo_unid_manut = "Bases Sociais"
            elif inst_sel == "IAV":
                rotulo_unid_manut = "Centros de Custo"
            else:
                rotulo_unid_manut = "Bases / Centros de Custo"

            st.markdown(
                f'<div class="chart-title">Top 10 {rotulo_unid_manut} | Maior Custo de Manutenção Acumulado</div>',
                unsafe_allow_html=True
            )
            st.caption(
                f"Acumulado até {mes_sel}/{ano_sel} · % representa a participação no custo total de manutenção."
            )

            df_rank_acum = df_acumulado_ate_mes_manut.copy()
            df_rank_acum["Unidade_Ranking"] = df_rank_acum[col_cc].apply(limpar_unidade)

            custo_total_manut_rank = df_rank_acum["Custo de manutenção"].sum()

            custo_base_acum = (
                df_rank_acum
                .groupby("Unidade_Ranking", as_index=False)["Custo de manutenção"]
                .sum()
            )
            custo_base_acum = custo_base_acum[
                custo_base_acum["Custo de manutenção"] > 0
            ].copy()

            if not custo_base_acum.empty and custo_total_manut_rank > 0:
                custo_base_acum["Participação"] = (
                    custo_base_acum["Custo de manutenção"] / custo_total_manut_rank * 100
                )

                custo_base_acum = (
                    custo_base_acum
                    .nlargest(10, "Custo de manutenção")
                    .sort_values("Custo de manutenção", ascending=True)
                )

                # Rótulo único e compacto: valor principal + participação.
                custo_base_acum["Rotulo_Profissional"] = custo_base_acum.apply(
                    lambda r: (
                        f'{fmt_br(r["Custo de manutenção"], True)}'
                        f'  |  {r["Participação"]:.1f}% do total'
                    ),
                    axis=1
                )

                fig_base_acum = go.Figure()
                fig_base_acum.add_trace(go.Bar(
                    x=custo_base_acum["Custo de manutenção"],
                    y=custo_base_acum["Unidade_Ranking"],
                    orientation="h",
                    marker_color="#F57C00",
                    text=custo_base_acum["Rotulo_Profissional"],
                    textposition="outside",
                    textfont=dict(size=14, color="#37474F"),
                    cliponaxis=False,
                    customdata=custo_base_acum["Participação"],
                    hovertemplate=(
                        "<b>%{y}</b><br>"
                        "Manutenção acumulada: R$ %{x:,.2f}<br>"
                        "Participação no total: %{customdata:.1f}%"
                        "<extra></extra>"
                    ),
                    showlegend=False
                ))

                max_cb = custo_base_acum["Custo de manutenção"].max()
                fig_base_acum.update_layout(
                    height=470,
                    separators=",.",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(r=165, l=10, t=10, b=10),
                    showlegend=False,
                    xaxis=dict(
                        showticklabels=False,
                        showgrid=False,
                        zeroline=False,
                        range=[0, max_cb * 1.52]
                    ),
                    yaxis=dict(
                        title="",
                        automargin=True,
                        tickfont=dict(size=12.5, color="#333333", family="Arial, sans-serif")
                    )
                )

                st.plotly_chart(
                    fig_base_acum,
                    use_container_width=True,
                    config={"displayModeBar": False}
                )
            else:
                st.info("Sem custo de manutenção acumulado para exibir nesta seleção.")

        with tab_comb:
            st.markdown(f"### ⛽ Desempenho de Combustível | {mes_sel}/{ano_sel}")

            # Combustível é controlado financeiramente pelas placas digitais.
            df_comb = df_base[df_base["Placa"].astype(str).str.contains("COMBUST", case=False, na=False)].copy()
            df_comb_mes = df_comb[df_comb["Mes_Num"] == mes_num_atual].copy()
            df_comb_acum = df_comb[df_comb["Mes_Num"] <= mes_num_atual].copy()
            df_comb_ant = df_comb[df_comb["Mes_Num"] == (mes_num_atual - 1)].copy() if mes_num_atual > 1 else df_comb.iloc[0:0].copy()

            # Unidade de gestão usada nos rankings de combustível.
            # Criada logo no início para estar disponível em todos os blocos.
            df_comb_mes["Unidade_Comb"] = df_comb_mes[col_cc].apply(limpar_unidade)
            df_comb_acum["Unidade_Comb"] = df_comb_acum[col_cc].apply(limpar_unidade)
            if not df_comb_ant.empty:
                df_comb_ant["Unidade_Comb"] = df_comb_ant[col_cc].apply(limpar_unidade)

            custo_comb_mes = df_comb_mes["Custo de combustível"].sum()
            custo_comb_ant = df_comb_ant["Custo de combustível"].sum()
            custo_comb_acum = df_comb_acum["Custo de combustível"].sum()
            var_comb = ((custo_comb_mes - custo_comb_ant) / custo_comb_ant * 100) if custo_comb_ant > 0 else 0

            df_comb_mes["Unidade_Comb"] = df_comb_mes[col_cc].apply(limpar_unidade)
            unidades_gasto_mes = df_comb_mes.loc[
                df_comb_mes["Custo de combustível"] > 0, "Unidade_Comb"
            ].nunique()

            orc_comb_aba = sum(
                ORCAMENTOS_COMB_2026.get(inst, 0) for inst in inst_ativas
            ) if ano_sel == 2026 else 0
            perc_comb_aba = (custo_comb_acum / orc_comb_aba * 100) if orc_comb_aba > 0 else 0

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if custo_comb_ant > 0:
                    if var_comb > 0:
                        classe_comb, icone_comb = "vs-alta", "▲"
                    elif var_comb < 0:
                        classe_comb, icone_comb = "vs-baixa", "▼"
                    else:
                        classe_comb, icone_comb = "vs-neutro", "●"
                    sub_comb = (
                        f'Vs mês anterior: <span class="{classe_comb}">'
                        f'{icone_comb} {abs(var_comb):.1f}%</span>'
                    )
                else:
                    sub_comb = "Vs mês anterior: sem base de comparação"
                draw_card("⛽ CUSTO NO MÊS", fmt_br(custo_comb_mes, True), sub_comb)

            with c2:
                draw_card(
                    "💰 CUSTO ACUMULADO",
                    fmt_br(custo_comb_acum, True),
                    f"Até {mes_sel}/{ano_sel}"
                )

            with c3:
                draw_card(
                    "📍 UNIDADES COM GASTO",
                    fmt_br(unidades_gasto_mes),
                    "Bases/Centros de Custo no mês",
                    is_lower_better=False
                )

            with c4:
                if ano_sel == 2026 and orc_comb_aba > 0:
                    draw_card(
                        "🎯 ORÇAMENTO CONSUMIDO",
                        f"{perc_comb_aba:.1f}%",
                        f"Orçamento anual: <b>{fmt_br(orc_comb_aba, True)}</b>",
                        progress=perc_comb_aba,
                        progress_text=f"Saldo: {fmt_br(orc_comb_aba-custo_comb_acum, True)}"
                    )
                else:
                    draw_card(
                        "🎯 ORÇAMENTO CONSUMIDO",
                        "—",
                        "Orçamento não cadastrado para o ano"
                    )

            st.markdown("<br>", unsafe_allow_html=True)

            if inst_sel == "AMES":
                rotulo_comb = "Bases Sociais"
            elif inst_sel == "IAV":
                rotulo_comb = "Centros de Custo"
            else:
                rotulo_comb = "Bases / Centros de Custo"

            g1, g2 = st.columns(2)

            with g1:
                st.markdown(
                    f'<div class="chart-title">Top 10 {rotulo_comb} | Maior Custo de Combustível no Mês</div>',
                    unsafe_allow_html=True
                )
                st.caption(f"Competência: {mes_sel}/{ano_sel} · ranking do custo de combustível no mês.")
                rank_mes = (
                    df_comb_mes.groupby("Unidade_Comb", as_index=False)["Custo de combustível"]
                    .sum()
                )
                rank_mes = rank_mes[rank_mes["Custo de combustível"] > 0].nlargest(
                    10, "Custo de combustível"
                ).sort_values("Custo de combustível", ascending=True)

                if not rank_mes.empty:
                    fig_cm = px.bar(
                        rank_mes,
                        x="Custo de combustível",
                        y="Unidade_Comb",
                        orientation="h",
                        text="Custo de combustível",
                        color_discrete_sequence=["#0288D1"]
                    )
                    fig_cm.update_traces(
                        texttemplate="<b>R$ %{text:,.2f}</b>",
                        textposition="outside",
                        textfont=dict(size=12.5, color="#263238"),
                        cliponaxis=False
                    )
                    max_cm = rank_mes["Custo de combustível"].max()
                    fig_cm.update_layout(
                        height=455, separators=",.",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(r=115, l=10, t=10, b=10),
                        showlegend=False,
                        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, max_cm*1.38]),
                        yaxis=dict(title="", automargin=True, tickfont=dict(size=11.5))
                    )
                    st.plotly_chart(fig_cm, use_container_width=True, config={"displayModeBar": False})
                else:
                    st.info("Sem custo de combustível no mês para esta seleção.")

            with g2:
                st.markdown(
                    f'<div class="chart-title">Top 10 {rotulo_comb} | Maior Custo de Combustível Acumulado</div>',
                    unsafe_allow_html=True
                )
                st.caption(
                    f"Acumulado até {mes_sel}/{ano_sel} · % representa a participação no custo total de combustível."
                )
                rank_ac = (
                    df_comb_acum.groupby("Unidade_Comb", as_index=False)["Custo de combustível"]
                    .sum()
                )
                rank_ac = rank_ac[rank_ac["Custo de combustível"] > 0].copy()
                total_rank_ac = rank_ac["Custo de combustível"].sum()

                if not rank_ac.empty and total_rank_ac > 0:
                    rank_ac["Participação"] = rank_ac["Custo de combustível"] / total_rank_ac * 100
                    rank_ac = rank_ac.nlargest(10, "Custo de combustível").sort_values(
                        "Custo de combustível", ascending=True
                    )
                    rank_ac["Rotulo"] = rank_ac.apply(
                        lambda r: f'{fmt_br(r["Custo de combustível"], True)}  |  {r["Participação"]:.1f}% do total',
                        axis=1
                    )
                    fig_ca = go.Figure(go.Bar(
                        x=rank_ac["Custo de combustível"],
                        y=rank_ac["Unidade_Comb"],
                        orientation="h",
                        marker_color="#0288D1",
                        text=rank_ac["Rotulo"],
                        textposition="outside",
                        textfont=dict(size=12.5, color="#37474F"),
                        cliponaxis=False,
                        customdata=rank_ac["Participação"],
                        hovertemplate=(
                            "<b>%{y}</b><br>Custo acumulado: R$ %{x:,.2f}<br>"
                            "Participação: %{customdata:.1f}%<extra></extra>"
                        )
                    ))
                    max_ca = rank_ac["Custo de combustível"].max()
                    fig_ca.update_layout(
                        height=455, separators=",.",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(r=165, l=10, t=10, b=10),
                        showlegend=False,
                        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, max_ca*1.62]),
                        yaxis=dict(title="", automargin=True, tickfont=dict(size=11.5))
                    )
                    st.plotly_chart(fig_ca, use_container_width=True, config={"displayModeBar": False})
                else:
                    st.info("Sem custo acumulado de combustível para esta seleção.")

            st.markdown("---")
            st.markdown(
                f'<div class="chart-title">Evolução Mensal do Custo de Combustível | {ano_sel}</div>',
                unsafe_allow_html=True
            )

            evol_comb_inst = (
                df_comb_acum.groupby(["Mes_Num", "Mes_Nome", "Instituição"])["Custo de combustível"]
                .sum().reset_index().sort_values("Mes_Num")
            )
            evol_comb_total = (
                df_comb_acum.groupby(["Mes_Num", "Mes_Nome"])["Custo de combustível"]
                .sum().reset_index().sort_values("Mes_Num")
            )

            if not evol_comb_inst.empty and not evol_comb_total.empty:
                media_comb = evol_comb_total["Custo de combustível"].mean()

                fig_ec = px.line(
                    evol_comb_inst,
                    x="Mes_Nome",
                    y="Custo de combustível",
                    color="Instituição",
                    markers=True,
                    text="Custo de combustível",
                    color_discrete_map={"AMES": "#0288D1", "IAV": "#F57C00"}
                )
                fig_ec.update_traces(
                    texttemplate="<b>R$ %{text:,.0f}</b>",
                    textposition="top center",
                    textfont=dict(size=11),
                    line=dict(width=3),
                    marker=dict(size=8)
                )
                fig_ec.add_hline(
                    y=media_comb,
                    line_dash="dash",
                    line_color="#78909C",
                    line_width=1.5,
                    annotation_text=f"Média mensal total: {fmt_br(media_comb, True)}",
                    annotation_position="bottom right",
                    annotation_font=dict(size=11, color="#546E7A")
                )
                max_ec = max(evol_comb_inst["Custo de combustível"].max(), media_comb)
                fig_ec.update_layout(
                    height=430, separators=",.",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(r=20, l=10, t=35, b=10),
                    yaxis=dict(
                        title="Custo no Mês (R$)",
                        showgrid=True,
                        gridcolor="#E0E0E0",
                        range=[0, max_ec*1.30]
                    ),
                    xaxis=dict(title=""),
                    legend=dict(
                        orientation="h", yanchor="bottom", y=1.02,
                        xanchor="right", x=1, title=""
                    )
                )
                st.plotly_chart(fig_ec, use_container_width=True, config={"displayModeBar": False})

                if len(evol_comb_total) >= 2:
                    atual = float(evol_comb_total.iloc[-1]["Custo de combustível"])
                    anterior = float(evol_comb_total.iloc[-2]["Custo de combustível"])
                    nome_atual = str(evol_comb_total.iloc[-1]["Mes_Nome"])
                    nome_ant = str(evol_comb_total.iloc[-2]["Mes_Nome"])

                    if anterior > 0:
                        var_ec = (atual-anterior)/anterior*100
                        if var_ec > 0:
                            classe_ec, icone_ec = "vs-alta", "▲"
                        elif var_ec < 0:
                            classe_ec, icone_ec = "vs-baixa", "▼"
                        else:
                            classe_ec, icone_ec = "vs-neutro", "●"

                        st.markdown(
                            f'<div style="font-size:12.5px;color:#455A64;margin-top:-8px;">'
                            f'{nome_atual} vs {nome_ant}: '
                            f'<span class="{classe_ec}">{icone_ec} {abs(var_ec):.1f}%</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
            else:
                st.info("Sem dados mensais de combustível para a seleção atual.")

        with tab_seg:
            st.markdown(f"### 🛡️ Seguro/Rastreadores | {ano_sel}")
            df_fixos_acum = df_base[df_base["Mes_Num"] <= mes_num_atual]
            
            gasto_seguro = df_fixos_acum["Custo de seguro"].sum()
            gasto_rastreador = df_fixos_acum["Custo de Rastreador"].sum()
            
            cf1, cf2 = st.columns(2)
            
            with cf1:
                if ano_sel == 2026:
                    orc_seguro = sum(ORCAMENTOS_SEGURO_2026.get(inst, 0) for inst in inst_ativas)
                    saldo_seguro = orc_seguro - gasto_seguro
                    perc_seguro = (gasto_seguro / orc_seguro * 100) if orc_seguro > 0 else 0
                    sub_seguro = f"Orçamento Anual: <b>{fmt_br(orc_seguro, True)}</b>"
                    prog_text_seguro = f"{perc_seguro:.1f}% &middot; Saldo {fmt_br(saldo_seguro, True)}"
                    draw_card("EXECUÇÃO SEGURO DE VEÍCULOS", fmt_br(gasto_seguro, True), sub_seguro, progress=perc_seguro, progress_text=prog_text_seguro)
                else:
                    sub_seguro = "Orçamento Anual: <b>A definir</b>"
                    draw_card("CUSTO COM SEGURO", fmt_br(gasto_seguro, True), sub_seguro)

            with cf2:
                if ano_sel == 2026:
                    orc_rastreador = sum(ORCAMENTOS_RASTREADOR_2026.get(inst, 0) for inst in inst_ativas)
                    saldo_rastreador = orc_rastreador - gasto_rastreador
                    perc_rastreador = (gasto_rastreador / orc_rastreador * 100) if orc_rastreador > 0 else 0
                    sub_rastreador = f"Orçamento Anual: <b>{fmt_br(orc_rastreador, True)}</b>"
                    prog_text_rastreador = f"{perc_rastreador:.1f}% &middot; Saldo {fmt_br(saldo_rastreador, True)}"
                    draw_card("EXECUÇÃO RASTREADOR", fmt_br(gasto_rastreador, True), sub_rastreador, progress=perc_rastreador, progress_text=prog_text_rastreador)
                else:
                    sub_rastreador = "Orçamento Anual: <b>A definir</b>"
                    draw_card("CUSTO COM RASTREADOR", fmt_br(gasto_rastreador, True), sub_rastreador)
                
            st.markdown("---")
            st.markdown('<div class="chart-title">Evolução Mensal de Seguro e Rastreadores</div>', unsafe_allow_html=True)
            
            evol_fixos = df_fixos_acum.groupby(['Mes_Nome', 'Mes_Num'])[['Custo de seguro', 'Custo de Rastreador']].sum().reset_index().sort_values('Mes_Num')
            evol_fixos_melted = evol_fixos.melt(id_vars=['Mes_Nome', 'Mes_Num'], 
                                                value_vars=['Custo de seguro', 'Custo de Rastreador'], 
                                                var_name='Tipo Despesa', 
                                                value_name='Custo')
            
            evol_fixos_melted['Tipo Despesa'] = evol_fixos_melted['Tipo Despesa'].map({'Custo de seguro': 'Seguro', 'Custo de Rastreador': 'Rastreador'})
            
            if evol_fixos_melted['Custo'].sum() > 0:
                fig_fixos = px.bar(evol_fixos_melted, x='Mes_Nome', y='Custo', color='Tipo Despesa', barmode='group', color_discrete_map={"Seguro": "#1A237E", "Rastreador": "#0288D1"})
                
                max_f = evol_fixos_melted['Custo'].max()
                fig_fixos.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                        yaxis=dict(title="Custo (R$)", showgrid=True, gridcolor='#E0E0E0', range=[0, max_f * 1.3]), xaxis_title="",
                                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=""),
                                        separators=',.')
                
                fig_fixos.update_traces(texttemplate='<b>R$ %{y:,.2f}</b>', textposition='outside', textfont=ESTILO_TEXTO)
                st.plotly_chart(fig_fixos, use_container_width=True)
            else:
                st.info("Nenhum custo de Seguro ou Rastreador lançado nestes meses.")

        with tab_raiox:
            # Nomenclatura institucional
            if inst_sel == "AMES":
                rotulo_rx = "Base Social"
            elif inst_sel == "IAV":
                rotulo_rx = "Centro de Custo"
            else:
                rotulo_rx = "Unidade"

            st.markdown(f"### 📍 Raio-X da {rotulo_rx} | {mes_sel}/{ano_sel}")

            unidades_rx = sorted(df_base[col_cc].dropna().unique())
            base_raiox = st.selectbox(
                f"🔍 Selecione a {rotulo_rx} para análise detalhada:",
                unidades_rx
            )

            if base_raiox:
                df_rx_base = df_base[df_base[col_cc] == base_raiox].copy()
                df_rx_mes = df_rx_base[df_rx_base["Mes_Num"] == mes_num_atual].copy()
                df_rx_acum = df_rx_base[df_rx_base["Mes_Num"] <= mes_num_atual].copy()

                # Mês anterior para comparação
                df_rx_ant = (
                    df_rx_base[df_rx_base["Mes_Num"] == (mes_num_atual - 1)].copy()
                    if mes_num_atual > 1 else df_rx_base.iloc[0:0].copy()
                )

                km_mes = df_rx_mes["Quilometragem"].sum()
                km_acum = df_rx_acum["Quilometragem"].sum()

                manut_mes = df_rx_mes["Custo de manutenção"].sum()
                manut_acum = df_rx_acum["Custo de manutenção"].sum()
                manut_ant = df_rx_ant["Custo de manutenção"].sum()

                comb_mes = df_rx_mes["Custo Combustível"].sum()
                comb_acum = df_rx_acum["Custo Combustível"].sum()
                comb_ant = df_rx_ant["Custo Combustível"].sum()

                total_mes = manut_mes + comb_mes
                total_acum = manut_acum + comb_acum
                total_ant = manut_ant + comb_ant

                def variacao_rx(atual, anterior):
                    if anterior <= 0:
                        return "Sem base de comparação"
                    v = ((atual - anterior) / anterior) * 100
                    if v > 0:
                        return f'<span class="vs-alta">▲ {abs(v):.1f}%</span> vs mês anterior'
                    elif v < 0:
                        return f'<span class="vs-baixa">▼ {abs(v):.1f}%</span> vs mês anterior'
                    return '<span class="vs-neutro">● 0,0%</span> vs mês anterior'

                # Apenas placas físicas no inventário da unidade
                mask_fisica_rx = df_rx_acum["Placa"].astype(str).str.fullmatch(
                    r"[A-Z0-9]{7}", case=False, na=False
                )
                qtd_veiculos_base = df_rx_acum.loc[mask_fisica_rx, "Placa"].nunique()

                st.markdown(
                    f'<div style="font-size:14px;color:#455A64;margin:4px 0 14px 0;">'
                    f'<b>{base_raiox}</b> · Resumo mensal para acompanhamento de Manutenção e Combustível'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # Resumo mensal orientado ao missionário
                r1, r2, r3 = st.columns(3)
                with r1:
                    draw_card(
                        "🔧 MANUTENÇÃO NO MÊS",
                        fmt_br(manut_mes, True),
                        variacao_rx(manut_mes, manut_ant)
                    )
                with r2:
                    draw_card(
                        "⛽ COMBUSTÍVEL NO MÊS",
                        fmt_br(comb_mes, True),
                        variacao_rx(comb_mes, comb_ant)
                    )
                with r3:
                    draw_card(
                        "💰 TOTAL ACOMPANHADO",
                        fmt_br(total_mes, True),
                        variacao_rx(total_mes, total_ant)
                    )

                st.markdown("<br>", unsafe_allow_html=True)

                r4, r5, r6 = st.columns(3)
                with r4:
                    draw_card(
                        "🚘 VEÍCULOS DA UNIDADE",
                        fmt_br(qtd_veiculos_base),
                        "Placas físicas vinculadas",
                        is_lower_better=False
                    )
                with r5:
                    draw_card(
                        "🛣️ KM RODADO NO MÊS",
                        fmt_br(km_mes),
                        f"Acumulado: <b>{fmt_br(km_acum)}</b>",
                        is_lower_better=False
                    )
                with r6:
                    draw_card(
                        "📅 TOTAL ACUMULADO",
                        fmt_br(total_acum, True),
                        f"Manut.: <b>{fmt_br(manut_acum, True)}</b> · Comb.: <b>{fmt_br(comb_acum, True)}</b>"
                    )

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    '<div class="chart-title">📊 Composição do Gasto Acompanhado | Mês</div>',
                    unsafe_allow_html=True
                )

                comp_rx = pd.DataFrame({
                    "Categoria": ["Manutenção", "Combustível"],
                    "Valor": [manut_mes, comb_mes]
                })
                comp_rx = comp_rx[comp_rx["Valor"] > 0]

                if not comp_rx.empty:
                    fig_comp_rx = px.pie(
                        comp_rx,
                        names="Categoria",
                        values="Valor",
                        hole=0.58,
                        color="Categoria",
                        color_discrete_map={"Manutenção": "#F57C00", "Combustível": "#0288D1"}
                    )
                    fig_comp_rx.update_traces(
                        textposition="outside",
                        textinfo="label+percent",
                        textfont=dict(size=13),
                        hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>"
                    )
                    fig_comp_rx.add_annotation(
                        text=f"<b>{fmt_br(total_mes, True)}</b><br>Total do mês",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(size=14, color="#263238")
                    )
                    fig_comp_rx.update_layout(
                        height=330,
                        margin=dict(l=20, r=20, t=10, b=10),
                        showlegend=False,
                        paper_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_comp_rx, use_container_width=True, config={"displayModeBar": False})
                else:
                    st.info("Sem gastos de manutenção ou combustível no mês selecionado.")

                st.markdown("---")
                st.markdown(f"#### 📋 Detalhamento da {rotulo_rx} | {base_raiox}")
                st.caption(
                    f"Histórico de janeiro até {mes_sel}/{ano_sel}, organizado em duas leituras: "
                    "evolução mensal da unidade e detalhamento das placas."
                )

                meses_rx = (
                    df_rx_acum[["Mes_Num", "Mes_Nome"]]
                    .dropna()
                    .drop_duplicates()
                    .sort_values("Mes_Num")
                )
                meses_ordem_rx = meses_rx["Mes_Nome"].tolist()

                # ============================================================
                # 1) RESUMO MENSAL DA UNIDADE
                # ============================================================
                resumo_mensal_rx = []

                for _, linha_mes in meses_rx.iterrows():
                    num_m = linha_mes["Mes_Num"]
                    nome_m = linha_mes["Mes_Nome"]
                    df_m = df_rx_acum[df_rx_acum["Mes_Num"] == num_m]

                    mask_fisica_m = df_m["Placa"].astype(str).str.fullmatch(
                        r"[A-Z0-9]{7}", case=False, na=False
                    )
                    km_m = df_m.loc[mask_fisica_m, "Quilometragem"].sum()
                    manut_m = df_m["Custo de manutenção"].sum()
                    comb_m = df_m["Custo Combustível"].sum()
                    total_m = manut_m + comb_m

                    resumo_mensal_rx.append({
                        "Mês": nome_m,
                        "KM Total": km_m,
                        "Manutenção": manut_m,
                        "Combustível": comb_m,
                        "Total do Mês": total_m
                    })

                df_resumo_mensal_rx = pd.DataFrame(resumo_mensal_rx)

                # Variação do total em relação ao mês anterior.
                # Redução de gasto = verde; aumento de gasto = vermelho.
                if not df_resumo_mensal_rx.empty:
                    variacoes = []
                    anterior = None
                    for valor in df_resumo_mensal_rx["Total do Mês"]:
                        if anterior is None or anterior <= 0:
                            variacoes.append("—")
                        else:
                            v = ((valor - anterior) / anterior) * 100
                            sinal = "▲" if v > 0 else ("▼" if v < 0 else "●")
                            variacoes.append(f"{sinal} {abs(v):.1f}%")
                        anterior = valor
                    df_resumo_mensal_rx["Vs mês anterior"] = variacoes

                st.markdown("##### 1. Evolução Mensal da Unidade")

                def cor_variacao_rx(valor):
                    valor_txt = str(valor).strip()
                    if valor_txt.startswith("▲"):
                        return "color:#C62828;font-weight:700;"
                    if valor_txt.startswith("▼"):
                        return "color:#2E7D32;font-weight:700;"
                    return "color:#607D8B;font-weight:600;"

                resumo_mensal_styled = df_resumo_mensal_rx.style.map(
                    cor_variacao_rx,
                    subset=["Vs mês anterior"]
                )

                st.dataframe(
                    resumo_mensal_styled,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Mês": st.column_config.TextColumn("Mês", width="small"),
                        "KM Total": st.column_config.NumberColumn("KM Total", format="%.0f"),
                        "Manutenção": st.column_config.NumberColumn("Manutenção", format="R$ %.2f"),
                        "Combustível": st.column_config.NumberColumn("Combustível", format="R$ %.2f"),
                        "Total do Mês": st.column_config.NumberColumn("Total do Mês", format="R$ %.2f"),
                        "Vs mês anterior": st.column_config.TextColumn("Vs mês anterior", width="small")
                    }
                )

                st.markdown("<br>", unsafe_allow_html=True)

                # ============================================================
                # 2) DETALHAMENTO DAS PLACAS
                # ============================================================
                st.markdown("##### 2. Detalhamento dos Veículos")
                st.caption(
                    "KM e manutenção são apresentados por placa. O combustível permanece no resumo da unidade, "
                    "pois não é rateado individualmente entre os veículos."
                )

                df_veic_acum_rx = df_rx_acum[
                    df_rx_acum["Placa"].astype(str).str.fullmatch(
                        r"[A-Z0-9]{7}", case=False, na=False
                    )
                ].copy()

                placas_rx = sorted(df_veic_acum_rx["Placa"].dropna().unique())
                df_placas_rx = pd.DataFrame({"Placa": placas_rx})

                for m in meses_ordem_rx:
                    df_m_veic = df_veic_acum_rx[
                        df_veic_acum_rx["Mes_Nome"] == m
                    ]

                    km_dict = (
                        df_m_veic.groupby("Placa")["Quilometragem"]
                        .sum()
                        .to_dict()
                    )
                    manut_dict = (
                        df_m_veic.groupby("Placa")["Custo de manutenção"]
                        .sum()
                        .to_dict()
                    )

                    df_placas_rx[f"KM | {m}"] = (
                        df_placas_rx["Placa"].map(km_dict).fillna(0)
                    )
                    df_placas_rx[f"Manutenção | {m}"] = (
                        df_placas_rx["Placa"].map(manut_dict).fillna(0)
                    )

                cols_km_rx = [f"KM | {m}" for m in meses_ordem_rx]
                cols_manut_rx = [f"Manutenção | {m}" for m in meses_ordem_rx]

                df_placas_rx["KM Total"] = (
                    df_placas_rx[cols_km_rx].sum(axis=1)
                    if cols_km_rx else 0
                )
                df_placas_rx["Manutenção Total"] = (
                    df_placas_rx[cols_manut_rx].sum(axis=1)
                    if cols_manut_rx else 0
                )

                # Ordena por maior manutenção acumulada para facilitar a leitura.
                if not df_placas_rx.empty:
                    df_placas_rx = df_placas_rx.sort_values(
                        "Manutenção Total", ascending=False
                    )

                config_placas_rx = {
                    "Placa": st.column_config.TextColumn("Placa", width="medium")
                }
                for m in meses_ordem_rx:
                    config_placas_rx[f"KM | {m}"] = st.column_config.NumberColumn(
                        f"KM | {m}", format="%.0f"
                    )
                    config_placas_rx[f"Manutenção | {m}"] = st.column_config.NumberColumn(
                        f"Manutenção | {m}", format="R$ %.2f"
                    )

                config_placas_rx["KM Total"] = st.column_config.NumberColumn(
                    "KM Total", format="%.0f"
                )
                config_placas_rx["Manutenção Total"] = st.column_config.NumberColumn(
                    "Manutenção Total", format="R$ %.2f"
                )

                st.dataframe(
                    df_placas_rx,
                    use_container_width=True,
                    hide_index=True,
                    column_config=config_placas_rx
                )

                # ============================================================
                # DOWNLOAD ÚNICO: duas seções no mesmo CSV
                # ============================================================
                linhas_csv = []
                linhas_csv.append(f"RESUMO MENSAL DA UNIDADE - {base_raiox}")
                linhas_csv.append(
                    df_resumo_mensal_rx.to_csv(
                        index=False, sep=";", decimal=","
                    ).strip()
                )
                linhas_csv.append("")
                linhas_csv.append(f"DETALHAMENTO DOS VEÍCULOS - {base_raiox}")
                linhas_csv.append(
                    df_placas_rx.to_csv(
                        index=False, sep=";", decimal=","
                    ).strip()
                )

                csv_missionario = "\n".join(linhas_csv).encode("utf-8-sig")

                st.download_button(
                    label="📥 Baixar Relatório Completo",
                    data=csv_missionario,
                    file_name=(
                        f"Relatorio_Detalhamento_{str(base_raiox).replace(' ', '_')}_"
                        f"Ate_{mes_sel}_{ano_sel}.csv"
                    ),
                    mime="text/csv",
                    use_container_width=False,
                    key="btn_rx_missionario"
                )

                st.caption(
                    "Seguro e rastreador não entram neste resumo, pois são despesas fixas administradas internamente."
                )

        with tab_km:
            # ================= TOP 15 KM =================
            st.markdown(f"### 🚗 Top 15 Veículos | Maior Quilometragem")
            st.markdown("Análise dos veículos mais rodados da frota")
            
            df_top_km = load_top_km_data()
            
            if df_top_km.empty:
                st.warning("⚠️ Os dados do Top KM ainda não puderam ser carregados. Verifique se há informações preenchidas na aba da planilha.")
            else:
                col_placa = 'Placa' if 'Placa' in df_top_km.columns else df_top_km.columns[0]
                
                col_km = None
                for col in df_top_km.columns:
                    if 'KM' in col.upper() or 'QUILOMETRAGEM' in col.upper():
                        col_km = col
                        break
                
                if not col_km and len(df_top_km.columns) > 1:
                    col_km = df_top_km.columns[1]
                
                if col_placa and col_km:
                    df_top_km[col_km] = to_float(df_top_km[col_km])
                    
                    if df_top_km[col_km].max() > 0 and df_top_km[col_km].max() < 3000:
                        df_top_km[col_km] = df_top_km[col_km] * 1000
                    
                    top15 = df_top_km.nlargest(15, col_km).sort_values(col_km, ascending=True)
                    
                    c_grafico, c_tabela = st.columns([2, 1.2])
                    
                    with c_grafico:
                        st.markdown('<div class="chart-title">Ranking dos 15 veículos Mais Rodados</div>', unsafe_allow_html=True)
                        
                        def formatar_k(x):
                            if x >= 1000:
                                return f"{x/1000:.0f}K"
                            return f"{x:,.0f}".replace(',', '.')
                        
                        top15['KM_Formatado'] = top15[col_km].apply(formatar_k)
                        
                        # APLICADO O DEGRADÊ DE VERMELHO ABAIXO
                        fig_top15 = px.bar(
                            top15, 
                            x=col_km, 
                            y=col_placa, 
                            orientation='h', 
                            text='KM_Formatado', 
                            color=col_km,  # Mapeia a cor para o valor da Quilometragem
                            color_continuous_scale='Reds'  # Aplica o degradê do mais claro ao mais escuro
                        )
                        
                        fig_top15.update_traces(
                            texttemplate='<b>%{text}</b>', 
                            textposition='outside', 
                            textfont=ESTILO_TEXTO, 
                            cliponaxis=False
                        )
                        max_km = top15[col_km].max() if not top15.empty else 1
                        
                        fig_top15.update_layout(
                            height=550, 
                            paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)', 
                            margin=dict(r=60, l=10, t=10, b=10), 
                            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[0, max_km * 1.20]), 
                            yaxis=dict(automargin=True, tickfont=dict(size=13, color='#333333', family="Arial, sans-serif"), title=""),
                            coloraxis_showscale=False  # Oculta a barrinha lateral do degradê para ficar mais limpo
                        )
                        st.plotly_chart(fig_top15, use_container_width=True, config={'displayModeBar': False})
                    
                    with c_tabela:
                        st.markdown('<div class="chart-title">Tabela de Dados</div>', unsafe_allow_html=True)
                        tabela_top15 = df_top_km.nlargest(15, col_km).sort_values(col_km, ascending=False)
                        st.dataframe(
                            tabela_top15, 
                            use_container_width=True, 
                            hide_index=True,
                            column_config={col_km: st.column_config.NumberColumn("Quilometragem", format="%d")}
                        )
                else:
                    st.error("Não foi possível identificar as colunas de 'Placa' e 'KM' na sua nova planilha Top Km. Verifique os títulos das colunas.")

            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("---")

            # ================= MAPA DE QUILOMETRAGEM =================
            st.markdown(f"### 🛣️ Mapa de Quilometragem | {ano_sel}")
            st.markdown("Visão em matriz da quilometragem rodada por veículo e por base, com totais consolidados ao longo dos meses.")
            
            padrao_exclusao_km = "COMBUS|SEGUR|FINANC|CONSÓRC|RASTR|LOGIST|MANUT|MENSAL|TAXA|VEÍCUL|VEICUL|ALUGAD|MOTO|KOMBI|TRICICLO|REBOQUE|SPRINTER|ÔNIBUS|ONIBUS|MICRO"
            
            mask_km = (
                (~df_base_completa["Placa"].astype(str).str.contains(padrao_exclusao_km, case=False, na=True)) &
                (df_base_completa["Placa"].astype(str).str.strip() != "") &
                (df_base_completa["Placa"].astype(str).str.upper() != "NAN") &
                (df_base_completa["Placa"].astype(str).str.strip() != "0")
            )
            df_km_matrix = df_base_completa[mask_km]
            
            if not df_km_matrix.empty:
                pt_km = pd.pivot_table(
                    df_km_matrix,
                    values='Quilometragem',
                    index=['Instituição', col_cc, 'Placa'],
                    columns='Mes_Num',
                    aggfunc='sum',
                    fill_value=0
                ).reset_index()
                
                meses_map = {1: 'JAN', 2: 'FEV', 3: 'MAR', 4: 'ABR', 5: 'MAI', 6: 'JUN', 
                             7: 'JUL', 8: 'AGO', 9: 'SET', 10: 'OUT', 11: 'NOV', 12: 'DEZ'}
                
                meses_presentes = sorted([c for c in pt_km.columns if isinstance(c, int)])
                nomes_meses_presentes = [meses_map.get(m, str(m)) for m in meses_presentes]
                
                renames = {m: meses_map.get(m, str(m)) for m in meses_presentes}
                pt_km.rename(columns=renames, inplace=True)
                
                pt_km['TOTAL'] = pt_km[nomes_meses_presentes].sum(axis=1)
                pt_km = pt_km.sort_values(['Instituição', col_cc, 'Placa'])
                
                linhas_subtotal = []
                for inst in pt_km['Instituição'].unique():
                    df_inst = pt_km[pt_km['Instituição'] == inst]
                    for base in df_inst[col_cc].unique():
                        df_b = df_inst[df_inst[col_cc] == base]
                        
                        for _, row in df_b.iterrows():
                            linhas_subtotal.append(row.to_dict())
                        
                        subtotal_dict = {'Instituição': inst, col_cc: base, 'Placa': 'Subtotal'}
                        for mes in nomes_meses_presentes:
                            subtotal_dict[mes] = df_b[mes].sum()
                        subtotal_dict['TOTAL'] = df_b['TOTAL'].sum()
                        linhas_subtotal.append(subtotal_dict)
                    
                    total_inst_dict = {'Instituição': inst, col_cc: '', 'Placa': f'TOTAL {inst}'}
                    for mes in nomes_meses_presentes:
                        total_inst_dict[mes] = df_inst[mes].sum()
                    total_inst_dict['TOTAL'] = df_inst['TOTAL'].sum()
                    linhas_subtotal.append(total_inst_dict)
                
                total_geral_dict = {'Instituição': '', col_cc: '', 'Placa': 'TOTAL GERAL'}
                for mes in nomes_meses_presentes:
                    total_geral_dict[mes] = pt_km[mes].sum()
                total_geral_dict['TOTAL'] = pt_km['TOTAL'].sum()
                linhas_subtotal.append(total_geral_dict)
                
                df_km_subtotals = pd.DataFrame(linhas_subtotal)
                
                def highlight_subtotals(row):
                    placa = str(row['Placa']).upper()
                    if 'SUBTOTAL' in placa:
                        return ['background-color: #E3F2FD; font-weight: bold; color: #1A237E'] * len(row)
                    elif 'TOTAL' in placa:
                        return ['background-color: #1A237E; color: white; font-weight: bold'] * len(row)
                    return [''] * len(row)
                
                def format_br_int(val):
                    try: return f"{int(val):,.0f}".replace(",", ".")
                    except: return "0"
                
                format_dict = {c: format_br_int for c in nomes_meses_presentes + ['TOTAL']}
                df_styled = df_km_subtotals.style.apply(highlight_subtotals, axis=1).format(format_dict)
                
                col_btn_km1, col_btn_km2 = st.columns([2, 1])
                with col_btn_km2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    csv_km = df_km_subtotals.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
                    st.download_button(
                        label="📥 Baixar Mapa de KM em Excel/CSV",
                        data=csv_km,
                        file_name=f"Mapa_Quilometragem_Completo_{inst_sel}_{ano_sel}.csv",
                        mime="text/csv",
                        key="btn_download_km"
                    )
                
                st.dataframe(df_styled, use_container_width=True, height=600, hide_index=True)
                
            else:
                st.warning("Nenhum dado de quilometragem encontrado para esta seleção.")

        with tab_frota:
            # ================= RELAÇÃO DA FROTA =================
            st.markdown(f"### 📋 Relação da Frota | {ano_sel}")
            st.markdown("Lista atualizada da frota genérica vinculada às bases, segmentada por categoria em uma única planilha.")
            
            pattern_digitais = "VEÍCUL|VEICUL|ALUGAD|MOTO|KOMBI|TRICICLO|REBOQUE|SPRINTER|ÔNIBUS|ONIBUS|MICRO"
            mask_frota_aba = df_base_completa["Placa"].astype(str).str.contains(pattern_digitais, case=False, na=False)
            
            df_frota = df_base_completa[mask_frota_aba].copy()
            
            if not df_frota.empty:
                df_frota_unica = df_frota.sort_values("Mes_Num", ascending=False).drop_duplicates(subset=["Placa"])
                
                def classificar_frota(placa):
                    texto = str(placa).upper()
                    if 'ALUGAD' in texto: return 'Alugados'
                    elif 'MOTO' in texto: return 'Moto'
                    elif 'TRICICLO' in texto: return 'Triciclo'
                    elif 'REBOQUE' in texto: return 'Reboque'
                    elif 'SPRINTER' in texto: return 'Sprinter'
                    elif 'ÔNIBUS' in texto or 'ONIBUS' in texto or 'MICRO' in texto: return 'Ônibus/Micro'
                    elif 'KOMBI' in texto: return 'Kombi'
                    else: return 'Veículos Próprios'
                    
                df_frota_unica['Categoria'] = df_frota_unica['Placa'].apply(classificar_frota)
                
                ordem_cat = {"Veículos Próprios": 1, "Alugados": 2, "Moto": 3, "Triciclo": 4, "Reboque": 5, "Sprinter": 6, "Kombi": 7, "Ônibus/Micro": 8}
                df_frota_unica['Ordem_Cat'] = df_frota_unica['Categoria'].map(lambda x: ordem_cat.get(x, 99))
                
                df_frota_unica = df_frota_unica.sort_values(['Instituição', 'Ordem_Cat', col_cc, 'Placa'])
                
                linhas_segmentadas = []
                for inst in df_frota_unica['Instituição'].unique():
                    df_i = df_frota_unica[df_frota_unica['Instituição'] == inst]
                    
                    for cat in df_i['Categoria'].unique():
                        linhas_segmentadas.append({
                            'Placa': f"🔸 {str(cat).upper()}",
                            'Instituição': inst,
                            col_cc: "",
                            'Modelo': "",
                            'Motorista': ""
                        })
                        
                        df_cat = df_i[df_i['Categoria'] == cat]
                        for _, row in df_cat.iterrows():
                            linhas_segmentadas.append({
                                'Placa': row['Placa'],
                                'Instituição': row['Instituição'],
                                col_cc: row.get(col_cc, ""),
                                'Modelo': row.get('Modelo', ""),
                                'Motorista': row.get('Motorista', "")
                            })
                            
                df_apresentacao = pd.DataFrame(linhas_segmentadas)
                
                def highlight_category(row):
                    placa_val = str(row['Placa'])
                    if placa_val.startswith('🔸'):
                        return ['background-color: #1A237E; color: white; font-weight: bold'] * len(row)
                    return [''] * len(row)
                
                df_styled = df_apresentacao.style.apply(highlight_category, axis=1)
                
                csv_relacao = df_apresentacao.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
                st.download_button(
                    label="📥 Baixar Relação da Frota Segmentada (Excel/CSV)",
                    data=csv_relacao,
                    file_name=f"Relacao_Frota_Segmentada_{inst_sel}_{ano_sel}.csv",
                    mime="text/csv",
                    key="btn_download_relacao"
                )
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.dataframe(df_styled, use_container_width=True, hide_index=True)
                st.info(f"Total de registros na frota (excluindo cabeçalhos): **{len(df_frota_unica)}**")
            else:
                st.warning("Nenhum veículo encontrado para exibir nesta aba.")

            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("---")

            # ================= VEÍCULOS & IPVA =================
            st.markdown(f"### 📅 Estimativas de IPVA e Dados de Veículos")
            st.markdown("Base de consulta atualizada automaticamente via Google Sheets.")
            
            df_ipva = load_ipva_data()
            
            if "Aviso" in df_ipva.columns:
                st.warning(df_ipva["Aviso"].iloc[0])
            elif not df_ipva.empty:
                
                col_filtros1, col_filtros2 = st.columns(2)
                with col_filtros1:
                    if 'Instituição' in df_ipva.columns:
                        inst_ipva = st.selectbox("Filtrar por Instituição:", ["TODAS"] + sorted(df_ipva['Instituição'].dropna().unique()), key='ipva_inst')
                    else:
                        inst_ipva = "TODAS"
                        
                with col_filtros2:
                    if 'Ano base' in df_ipva.columns:
                        ano_ipva = st.selectbox("Filtrar por Ano Base (IPVA):", ["TODOS"] + sorted(df_ipva['Ano base'].dropna().unique(), reverse=True), key='ipva_ano')
                    else:
                        ano_ipva = "TODOS"
                
                df_ipva_filtrado = df_ipva.copy()
                if inst_ipva != "TODAS":
                    df_ipva_filtrado = df_ipva_filtrado[df_ipva_filtrado['Instituição'] == inst_ipva]
                if ano_ipva != "TODOS":
                    df_ipva_filtrado = df_ipva_filtrado[df_ipva_filtrado['Ano base'] == ano_ipva]
                
                config_cols_ipva = {}
                if 'Ipva estimado' in df_ipva_filtrado.columns:
                    config_cols_ipva['Ipva estimado'] = st.column_config.NumberColumn("Ipva estimado", format="R$ %.2f")
                if 'Ano base' in df_ipva_filtrado.columns:
                    config_cols_ipva['Ano base'] = st.column_config.NumberColumn("Ano base", format="%d")
                if 'Ano do veículo' in df_ipva_filtrado.columns:
                    config_cols_ipva['Ano do veículo'] = st.column_config.NumberColumn("Ano do veículo", format="%d")
                
                total_ipva = df_ipva_filtrado['Ipva estimado'].sum() if 'Ipva estimado' in df_ipva_filtrado.columns else 0
                st.markdown(f"**Total de veículos listados:** {len(df_ipva_filtrado)} | **Valor Total Estimado:** {fmt_br(total_ipva, True)}")
                
                col_btn, col_esp = st.columns([1, 2])
                with col_btn:
                    csv_ipva = df_ipva_filtrado.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
                    st.download_button(
                        label="📥 Baixar Tabela Filtrada de IPVA",
                        data=csv_ipva,
                        file_name=f"Base_IPVA_Frota_{inst_ipva}_{ano_ipva}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.dataframe(df_ipva_filtrado, use_container_width=True, hide_index=True, column_config=config_cols_ipva)
            else:
                st.warning("Nenhum dado de IPVA encontrado ou erro de carregamento.")

        with tab_detalhes:
            st.markdown("### 📑 Detalhamento dos Dados")
            
            df_download = df_base_completa.drop(columns=['Mes_Num'], errors='ignore')
            
            csv_data = df_download.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')
            st.download_button(
                label="📥 Baixar Relatório Completo (Excel/CSV)",
                data=csv_data,
                file_name=f"Relatorio_Frotas_{inst_sel}_{mes_sel}_{ano_sel}.csv",
                mime="text/csv"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            colunas_moeda = [c for c in ['Custo de manutenção', 'Custo Combustível', 'Custo de seguro', 'Custo de Rastreador'] if c in df_download.columns]
            config_cols = {col: st.column_config.NumberColumn(col, format="R$ %.2f") for col in colunas_moeda}
            
            if 'Quilometragem' in df_download.columns:
                config_cols['Quilometragem'] = st.column_config.NumberColumn('Quilometragem', format="%.0f")
                
            st.dataframe(df_download, use_container_width=True, hide_index=True, column_config=config_cols)

    else:
        st.warning("Verifique o link do arquivo da planilha online ou certifique-se de que os dados foram publicados.")
