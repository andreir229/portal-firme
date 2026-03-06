from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd
import os

app = FastAPI()

# Tell FastAPI where your HTML/CSS files are
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load data once at startup (Global) for speed
CSV_PATH = os.path.join("src", "onrc", "od_firme.csv")
df_global = pd.read_csv(CSV_PATH, sep="^", encoding="utf-8", low_memory=False, dtype={'CUI': str}).fillna("")
# Convert CUI to string and strip spaces
df_global['CUI'] = df_global['CUI'].str.strip()

# Load MFinante data
MFINANTE_CSV_PATH_1 = os.path.join("src", "mfinante", "web_bl_bs_sl_an2024.csv")
MFINANTE_TXT_PATH_1 = os.path.join("src", "mfinante", "web_bl_bs_sl_an2024.txt")

MFINANTE_CSV_PATH_2 = os.path.join("src", "mfinante", "web_vs_2024.csv")
MFINANTE_TXT_PATH_2 = os.path.join("src", "mfinante", "web_vs_2024.txt")

# Map variables like 'i1' to their label
mfinante_mapping = {}
try:
    df_mf_labels_1 = pd.read_csv(MFINANTE_CSV_PATH_1, sep=';', header=None, names=["label", "id"], encoding="cp1250").fillna("")
    df_mf_labels_1['id'] = df_mf_labels_1['id'].str.strip().str.lower()
    
    df_mf_labels_2 = pd.read_csv(MFINANTE_CSV_PATH_2, sep=';', header=None, names=["label", "id"], encoding="cp1250").fillna("")
    df_mf_labels_2['id'] = df_mf_labels_2['id'].str.strip().str.lower()
    
    # Combine the mappings (if there are duplicate IDs between the files, the second will overwrite, but they are conceptually distinct groups of metrics anyway, or shared basic ones)
    df_mf_labels = pd.concat([df_mf_labels_1, df_mf_labels_2], ignore_index=True)
    mfinante_mapping = dict(zip(df_mf_labels['id'], df_mf_labels['label']))
except Exception as e:
    print(f"Warning: Could not load mfinante labels: {e}")

try:
    df_mfinante_1 = pd.read_csv(MFINANTE_TXT_PATH_1, sep=",", encoding="cp1250", low_memory=False).fillna("")
    df_mfinante_1['CUI'] = df_mfinante_1['CUI'].astype(str)
    
    df_mfinante_2 = pd.read_csv(MFINANTE_TXT_PATH_2, sep=",", encoding="cp1250", low_memory=False).fillna("")
    df_mfinante_2['CUI'] = df_mfinante_2['CUI'].astype(str)
    
    df_mfinante = pd.concat([df_mfinante_1, df_mfinante_2], ignore_index=True)
except Exception as e:
    print(f"Warning: Could not load mfinante TXT: {e}")
    df_mfinante = pd.DataFrame()

@app.get("/")
def read_index():
    return FileResponse('static/index.html')

@app.get("/search")
def search(q: str):
    # Search in the 'DENUMIRE' column
    results = df_global[df_global['DENUMIRE'].str.contains(q.upper(), na=False)]
    return results.head(20).to_dict(orient="records")

@app.get("/company/{cui}")
def get_company(cui: str):
    # Retrieve company details by CUI (strip whitespace for matching)
    cui_clean = cui.strip()
    if cui_clean.endswith(".0"):
        cui_clean = cui_clean[:-2]
        
    company = df_global[df_global['CUI'] == cui_clean]
    if company.empty:
        raise HTTPException(status_code=404, detail="Company not found")
    
    comp_dict = company.iloc[0].to_dict()
    
    # Attach MFinante financial data if it exists
    if not df_mfinante.empty:
        mf_data = df_mfinante[df_mfinante['CUI'] == cui_clean]
        if not mf_data.empty:
            mf_row = mf_data.iloc[0].to_dict()
            mapped_mf = {}
            for k, v in mf_row.items():
                k_lower = str(k).strip().lower()
                
                # Exclude base IDs since they are already available in company metadata
                if k_lower in ['cui', 'caen']:
                    continue
                    
                if k_lower in mfinante_mapping:
                    label = mfinante_mapping[k_lower]
                    # FastAPI cannot serialize NaN
                    mapped_mf[label] = "" if pd.isna(v) else v
                else:
                    mapped_mf[k] = "" if pd.isna(v) else v
            comp_dict['mfinante'] = mapped_mf

    return comp_dict

@app.get("/details")
def read_details():
    return FileResponse('static/details.html')