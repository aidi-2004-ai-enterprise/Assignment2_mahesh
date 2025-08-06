from google.cloud import storage
import xgboost as xgb
import os

def load_model_from_gcs(bucket_name: str, blob_name: str) -> xgb.Booster:
    """
    Load XGBoost model from Google Cloud Storage.
    
    Args:
        bucket_name (str): Name of the GCS bucket.
        blob_name (str): Name of the model file in the bucket.
    
    Returns:
        xgb.Booster: Loaded XGBoost model.
    
    Raises:
        Exception: If model loading fails.
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename("model.json")
        model = xgb.Booster()
        model.load_model("model.json")
        return model
    except Exception as e:
        raise Exception(f"Failed to load model from GCS: {str(e)}")