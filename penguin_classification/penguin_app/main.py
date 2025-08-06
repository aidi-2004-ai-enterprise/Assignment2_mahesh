# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from enum import Enum
import pandas as pd
import os
import joblib
import logging

logging.basicConfig(level=logging.INFO)

# Enums for API input validation
class Island(str, Enum):
    Torgersen = "Torgersen"
    Biscoe = "Biscoe"
    Dream = "Dream"

class Sex(str, Enum):
    male = "male"
    female = "female"

class PenguinFeatures(BaseModel):
    # Added Field(..., gt=0) for numerical validation
    bill_length_mm: float = Field(..., gt=0, description="Bill length in millimeters (must be positive)")
    bill_depth_mm: float = Field(..., gt=0, description="Bill depth in millimeters (must be positive)")
    flipper_length_mm: float = Field(..., gt=0, description="Flipper length in millimeters (must be positive)")
    body_mass_g: float = Field(..., gt=0, description="Body mass in grams (must be positive)")
    sex: Sex
    island: Island

# Corrected paths to load model, encoder, and columns
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# This is the key change. We now check the environment
# to determine the correct path. This works for both local and Docker.
if os.path.exists(os.path.join(BASE_DIR, "..", "app", "data")):
    DATA_DIR = os.path.join(BASE_DIR, "..", "app", "data")
else:
    DATA_DIR = os.path.join(BASE_DIR, "..", "data")

MODEL_PATH = os.path.join(DATA_DIR, "model.pkl")
ENCODER_PATH = os.path.join(DATA_DIR, "label_encoder.pkl")
COLUMNS_PATH = os.path.join(DATA_DIR, "columns.pkl")

try:
    model = joblib.load(MODEL_PATH)
    label_encoder = joblib.load(ENCODER_PATH)
    columns = joblib.load(COLUMNS_PATH)
    logging.info("Model and necessary files loaded successfully.")
except FileNotFoundError as e:
    logging.error(f"Failed to load model files: {e}")
    raise RuntimeError("Application startup failed. Model files not found.")

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Penguin Predictor Active!"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(features: PenguinFeatures):
    logging.info(f"Received input: {features}")
    
    input_data = features.dict()
    input_df = pd.DataFrame([input_data])

    input_df["sex"] = input_df["sex"].str.lower()
    input_df["island"] = input_df["island"].str.capitalize()

    input_df = pd.get_dummies(input_df, columns=["sex", "island"], drop_first=False)

    input_df = input_df.reindex(columns=columns, fill_value=0)

    try:
        prediction = model.predict(input_df)[0]
        species = label_encoder.inverse_transform([int(prediction)])[0]
        logging.info(f"Prediction successful: {species}")
        return {"prediction": species}
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        raise HTTPException(status_code=400, detail="Prediction failed. Please check input values.")
