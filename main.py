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

# Load MFinante data — list of (year, label_mapping, dataframe) tuples
# This structure allows adding more years later without code changes.
MFINANTE_SOURCES = [
    {
        "year": "2024",
        "csv": os.path.join("src", "mfinante", "web_bl_bs_sl_an2024.csv"),
        "txt": os.path.join("src", "mfinante", "web_bl_bs_sl_an2024.txt"),
    },
    {
        "year": "2024",  # same year, different report type (VS)
        "csv": os.path.join("src", "mfinante", "web_vs_2024.csv"),
        "txt": os.path.join("src", "mfinante", "web_vs_2024.txt"),
    },
]

def load_mfinante_source(source: dict):
    """Load label mapping + data for a single (csv, txt) pair. Returns (mapping_dict, dataframe)."""
    try:
        df_labels = pd.read_csv(source["csv"], sep=';', header=None, names=["label", "id"], encoding="cp1250").fillna("")
        df_labels['id'] = df_labels['id'].str.strip().str.lower()
        mapping = dict(zip(df_labels['id'], df_labels['label']))
    except Exception as e:
        print(f"Warning: Could not load mfinante labels from {source['csv']}: {e}")
        mapping = {}
    try:
        df = pd.read_csv(source["txt"], sep=",", encoding="cp1250", low_memory=False)
        df['CUI'] = df['CUI'].astype(str)
    except Exception as e:
        print(f"Warning: Could not load mfinante data from {source['txt']}: {e}")
        df = pd.DataFrame()
    return mapping, df

# Pre-load all sources at startup
mfinante_loaded = [(s["year"], *load_mfinante_source(s)) for s in MFINANTE_SOURCES]


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
    
    # Build year-keyed financial data: {"2024": {"Label": value, ...}, ...}
    year_data: dict = {}
    for year, mapping, df in mfinante_loaded:
        if df.empty:
            continue
        rows = df[df['CUI'] == cui_clean]
        if rows.empty:
            continue
        row = rows.iloc[0].to_dict()
        year_entry = year_data.setdefault(year, {})
        for k, v in row.items():
            k_lower = str(k).strip().lower()
            if k_lower in ('cui', 'caen'):
                continue
            label = mapping.get(k_lower, k)  # fall back to raw key if not in mapping
            safe_v = "" if (isinstance(v, float) and pd.isna(v)) else v
            year_entry[label] = safe_v

    if year_data:
        comp_dict['mfinante'] = year_data

    return comp_dict

@app.get("/details")
def read_details():
    return FileResponse('static/details.html')