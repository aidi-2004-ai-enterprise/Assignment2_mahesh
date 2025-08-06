import pytest
import numpy as np
import os
import joblib
import pandas as pd

def test_model_prediction():
    """Test the loaded model with known data after preprocessing."""
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    model_path = os.path.join(project_root, "app", "data", "model.pkl")
    label_encoder_path = os.path.join(project_root, "app", "data", "label_encoder.pkl")
    columns_path = os.path.join(project_root, "app", "data", "columns.pkl")

    try:
        model = joblib.load(model_path)
        label_encoder = joblib.load(label_encoder_path)
        loaded_columns = joblib.load(columns_path)
    except FileNotFoundError as e:
        pytest.fail(f"Required model files not found: {e}. Ensure 'model.pkl', 'label_encoder.pkl', and 'columns.pkl' are in 'app/data/'.")

    sample_raw_data = {
        'bill_length_mm': 39.1,
        'bill_depth_mm': 18.7,
        'flipper_length_mm': 181.0,
        'body_mass_g': 3750.0,
        'sex': 'male',
        'island': 'Torgersen'
    }

    input_df = pd.DataFrame([sample_raw_data])
    
    input_df["sex"] = input_df["sex"].str.lower()
    input_df["island"] = input_df["island"].str.capitalize()

    input_df = pd.get_dummies(input_df, columns=["sex", "island"], drop_first=False)
    
    input_df = input_df.reindex(columns=loaded_columns, fill_value=0)

    prediction_numerical = model.predict(input_df)[0]
    
    predicted_species = label_encoder.inverse_transform([int(prediction_numerical)])[0]

    assert predicted_species in ['Adelie', 'Chinstrap', 'Gentoo']