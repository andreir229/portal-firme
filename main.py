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
df_global = pd.read_csv(CSV_PATH, sep="^", encoding="utf-8", low_memory=False).fillna("")

@app.get("/")
def read_index():
    return FileResponse('static/index.html')

@app.get("/search")
def search(q: str):
    # Search in the 'DENUMIRE' column
    results = df_global[df_global['DENUMIRE'].str.contains(q.upper(), na=False)]
    return results.head(20).to_dict(orient="records")