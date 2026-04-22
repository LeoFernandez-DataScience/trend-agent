import streamlit as st
import pandas as pd
import json
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# CONFIG
SPREADSHEET_ID = "1tEPoR0oMNAm_L8abIXLfpvTtL1trfXua1392lJMdyjc"
RANGE = "Trends!A1:Z1000"


def load_data():
    # 🔥 Lê credenciais do Streamlit Secrets (em vez de arquivo local)
    creds_dict = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])

    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )

    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE
    ).execute()

    values = result.get("values", [])

    if not values:
        return pd.DataFrame()

    df = pd.DataFrame(values[1:], columns=values[0])

    return df


# APP
st.set_page_config(page_title="Radar de Trends", layout="wide")

st.title("📊 Radar de Trends")

df = load_data()

if df.empty:
    st.warning("Sem dados ainda")
else:
    st.success(f"{len(df)} vídeos encontrados")

    # 🔹 Renomear colunas para ficar mais claro
    df = df.rename(columns={
        "Score": "Score (Potencial)",
        "Stage": "Status da Trend"
    })

    # 🔹 BLOCO EXPLICATIVO
    st.markdown("### 🧠 Como interpretar os dados")

    st.info("""
**Score (Potencial)**  
Representa o potencial da trend com base em:
- Engajamento (curtidas + comentários)
- Compartilhamentos
- Volume de visualizações

Quanto maior o score, maior a chance de ser uma trend relevante.

**Status da Trend**  
Indica o momento da trend:

- 🟢 **EM_ALTA** → tendência forte, já validada (bom para copiar/adaptar)
- 🟡 **EM_ASCENSÃO** → tendência crescendo (ótimo timing para entrar)
- 🔴 **INÍCIO** → tendência nova, ainda incerta (alto risco, alta oportunidade)
""")

    # 🔹 TABELA
    st.dataframe(df, use_container_width=True)
