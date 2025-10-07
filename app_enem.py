# ===========================================
# Dashboard ENEM 2024 - Streamlit
# ===========================================
import pandas as pd
import streamlit as st
import plotly.express as px

# ===========================================
# Configurações iniciais
# ===========================================
st.set_page_config(page_title="Dashboard ENEM 2024", layout="wide")

st.title("📊 Dashboard ENEM 2024")
st.markdown("Análise interativa dos microdados do ENEM 2024")

# ===========================================
# Leitura dos dados
# ===========================================
@st.cache_data
def carregar_dados():
    df = pd.read_csv("RESULTADOS_2024.csv", sep=";", encoding="latin1", low_memory=False)
    return df

df = carregar_dados()

# ===========================================
# Seleção de colunas e limpeza básica
# ===========================================
notas_cols = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
df = df.dropna(subset=notas_cols)
df["MEDIA_GERAL"] = df[notas_cols].mean(axis=1)

# ===========================================
# Filtros laterais
# ===========================================
st.sidebar.header("Filtros")
ufs = st.sidebar.multiselect("Selecione o(s) Estado(s):", sorted(df["SG_UF_PROVA"].unique()))
if ufs:
    df = df[df["SG_UF_PROVA"].isin(ufs)]

# ===========================================
# Indicadores principais
# ===========================================
col1, col2, col3 = st.columns(3)

col1.metric("👥 Total de Participantes", f"{len(df):,}")
col2.metric("📈 Média Geral", f"{df['MEDIA_GERAL'].mean():.2f}")
col3.metric("🧾 Média da Redação", f"{df['NU_NOTA_REDACAO'].mean():.2f}")

# ===========================================
# Gráfico 1 - Médias por Estado
# ===========================================
st.subheader("🏙️ Médias por Estado")
media_estado = df.groupby("SG_UF_PROVA")[notas_cols + ["MEDIA_GERAL"]].mean().reset_index()

area = st.selectbox(
    "Selecione a área para análise:",
    ["MEDIA_GERAL"] + notas_cols,
    format_func=lambda x: {
        "MEDIA_GERAL": "Média Geral",
        "NU_NOTA_CN": "Ciências da Natureza",
        "NU_NOTA_CH": "Ciências Humanas",
        "NU_NOTA_LC": "Linguagens e Códigos",
        "NU_NOTA_MT": "Matemática",
        "NU_NOTA_REDACAO": "Redação",
    }[x]
)

fig1 = px.bar(
    media_estado.sort_values(area, ascending=False),
    x="SG_UF_PROVA",
    y=area,
    color=area,
    color_continuous_scale="viridis",
    title=f"Média de {area.replace('NU_NOTA_', '').replace('_', ' ').title()} por Estado",
)
st.plotly_chart(fig1, use_container_width=True)

# ===========================================
# 🗺️ Mapa Interativo do Brasil
# ===========================================
st.subheader("🗺️ Mapa de Médias por Estado (Choropleth)")

# Mapeamento de siglas para nomes completos
mapa_estados = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia",
    "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás",
    "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul", "MG": "Minas Gerais",
    "PA": "Pará", "PB": "Paraíba", "PR": "Paraná", "PE": "Pernambuco", "PI": "Piauí",
    "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul",
    "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo",
    "SE": "Sergipe", "TO": "Tocantins"
}

media_estado["Estado"] = media_estado["SG_UF_PROVA"].map(mapa_estados)

fig_mapa = px.choropleth(
    media_estado,
    geojson="https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson",
    locations="Estado",
    featureidkey="properties.name",
    color=area,
    color_continuous_scale="Viridis",
    title=f"Média de {area.replace('NU_NOTA_', '').replace('_', ' ').title()} por Estado (Mapa)",
)
fig_mapa.update_geos(fitbounds="locations", visible=False)
st.plotly_chart(fig_mapa, use_container_width=True)

# ===========================================
# Gráfico 2 - Distribuição das notas
# ===========================================
st.subheader("📊 Distribuição das Notas")
nota_sel = st.selectbox(
    "Selecione a nota para visualizar a distribuição:",
    notas_cols,
    format_func=lambda x: {
        "NU_NOTA_CN": "Ciências da Natureza",
        "NU_NOTA_CH": "Ciências Humanas",
        "NU_NOTA_LC": "Linguagens e Códigos",
        "NU_NOTA_MT": "Matemática",
        "NU_NOTA_REDACAO": "Redação",
    }[x]
)

fig2 = px.histogram(
    df,
    x=nota_sel,
    nbins=50,
    color_discrete_sequence=["#6a0dad"],
    title=f"Distribuição das Notas de {nota_sel.replace('NU_NOTA_', '').title()}",
)
st.plotly_chart(fig2, use_container_width=True)

# ===========================================
# Gráfico 3 - Correlação entre áreas
# ===========================================
st.subheader("🔗 Correlação entre as Áreas de Conhecimento")
corr = df[notas_cols].corr().round(2)
fig3 = px.imshow(
    corr,
    text_auto=True,
    color_continuous_scale="RdBu_r",
    title="Matriz de Correlação das Notas",
)
st.plotly_chart(fig3, use_container_width=True)

# ===========================================
# Gráfico 4 - Ranking dos Estados
# ===========================================
st.subheader("🏅 Ranking dos Estados por Média Geral")
ranking = media_estado.sort_values("MEDIA_GERAL", ascending=False).head(10)
fig4 = px.bar(
    ranking,
    x="SG_UF_PROVA",
    y="MEDIA_GERAL",
    color="MEDIA_GERAL",
    text="MEDIA_GERAL",
    color_continuous_scale="teal",
    title="Top 10 Estados com Maiores Médias Gerais",
)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.caption("Desenvolvido por Saint Raymundo de Almeida Melo | Dados ENEM 2024")