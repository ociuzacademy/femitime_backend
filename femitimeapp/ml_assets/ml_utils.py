import os
import pickle
import re
import fitz  # PyMuPDF
import pandas as pd
from django.conf import settings

# =======================================================
# ML ASSETS PATH
# =======================================================
ML_PATH = os.path.join(settings.BASE_DIR, "femitimeapp", "ml_assets")


# =======================================================
# SAFE PICKLE LOADER
# =======================================================
def load_pickle(filename):
    path = os.path.join(ML_PATH, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Missing ML file: {path}")
    with open(path, "rb") as f:
        return pickle.load(f)


# =======================================================
# LOAD NEW MODEL FILES (NO PULSE RATE)
# =======================================================
model = load_pickle("best_model1.pkl")
scaler = load_pickle("scaler1.pkl")
pcod_label_encoder = load_pickle("pcod_label_encoder1.pkl")


# =======================================================
# ENCODERS / MAPPERS
# =======================================================
def encode_blood_group(bg):
    mapping = {
        "A+": 0, "A-": 1,
        "B+": 2, "B-": 3,
        "AB+": 4, "AB-": 5,
        "O+": 6, "O-": 7
    }
    return mapping.get(str(bg).upper().strip(), 0)


def map_fast_food(val):
    return {
        "Never": 0,
        "Rarely": 1,
        "Often": 2,
        "Daily": 3
    }.get(val, 0)


def map_cycle(val):
    return {
        "Regular": 0,
        "Irregular": 1
    }.get(val, 0)


def map_severity(val):
    return {
        "None": 0,
        "Mild": 1,
        "Moderate": 2,
        "Severe": 3
    }.get(val, 0)


# =======================================================
# PDF MEDICAL VALUE EXTRACTION (NO NaN GUARANTEE)
# =======================================================
def extract_medical_values(pdf_path):
    doc = fitz.open(pdf_path)
    text = "".join(page.get_text() for page in doc)

    fields = {
        "TSH": 0,
        "VitaminD": 0,
        "Glucose": 0,
        "LH": 0,
        "FSH": 0,
        "Prolactin": 0,
        "Testosterone": 0,
        "Hemoglobin": 0
    }

    for key in fields:
        pattern = r"Vitamin\s*D" if key == "VitaminD" else key
        match = re.search(
            rf"{pattern}\s*[:\-]?\s*([0-9.]+)",
            text,
            re.IGNORECASE
        )
        if match:
            fields[key] = float(match.group(1))

    return fields


# =======================================================
# FINAL DATAFRAME (MUST MATCH TRAINING ORDER)
# =======================================================
def prepare_final_df(user_input, pdf_values):
    columns = [
        "Age", "Weight", "Height", "BMI",
        "Fast_Food_Consumption", "Blood_Group",
        "Cycle_Regularity",
        "Hair_Growth", "Acne", "Mood_Swings", "Skin_Darkening",
        "TSH", "VitaminD", "LH", "FSH",
        "Prolactin", "Testosterone", "Hemoglobin"
    ]

    data = {}
    for col in columns:
        data[col] = user_input.get(col, pdf_values.get(col, 0))

    # absolutely no NaN allowed
    return pd.DataFrame([data]).fillna(0)
