import os
import pandas as pd

DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "scans.csv")
COLUMNS = ["timestamp", "label", "confidence", "bin"]

def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0:
        pd.DataFrame(columns=COLUMNS).to_csv(CSV_PATH, index=False)

def append_scan(row: dict):
    ensure_storage()
    df = pd.read_csv(CSV_PATH)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)

def load_scans() -> pd.DataFrame:
    ensure_storage()
    try:
        df = pd.read_csv(CSV_PATH)
    except pd.errors.EmptyDataError:
        # file exists but is empty/corrupt -> recreate
        pd.DataFrame(columns=COLUMNS).to_csv(CSV_PATH, index=False)
        df = pd.read_csv(CSV_PATH)
    # Ensure required columns exist
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = None
    return df[COLUMNS]

def clear_scans():
    ensure_storage()
    pd.DataFrame(columns=COLUMNS).to_csv(CSV_PATH, index=False)
