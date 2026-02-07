import os
import pandas as pd

DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "scans.csv")

def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        pd.DataFrame(columns=["timestamp", "label", "confidence", "bin"]).to_csv(CSV_PATH, index=False)

def append_scan(row: dict):
    ensure_storage()
    df = pd.read_csv(CSV_PATH)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)

def load_scans() -> pd.DataFrame:
    ensure_storage()
    return pd.read_csv(CSV_PATH)
