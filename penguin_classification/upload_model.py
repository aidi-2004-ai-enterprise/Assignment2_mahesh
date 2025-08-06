from google.cloud import storage
import xgboost as xgb
import os
from dotenv import load_dotenv

load_dotenv()

def upload_model_to_gcs(model_path: str, bucket_name: str, blob_name: str) -> None:
    """
    Upload XGBoost model to Google Cloud Storage.
    
    Args:
        model_path (str): Local path to the model file.
        bucket_name (str): GCS bucket name.
        blob_name (str): Destination blob name in GCS.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(model_path)
    print(f"Model uploaded to gs://{bucket_name}/{blob_name}")

if __name__ == "__main__":
    # Correctly construct the absolute path to the model file
    model_dir = os.path.join(os.path.dirname(__file__), "penguin_app", "data")
    model_path = os.path.join(model_dir, "model.json")
    
    # Load the model from the correct path
    model = xgb.Booster()
    model.load_model(model_path)
    
    # save_model isn't strictly necessary here since the model is already saved,
    # but we'll use the correct path to avoid any confusion.
    model.save_model(model_path)
    
    upload_model_to_gcs(
        model_path=model_path,
        bucket_name=os.getenv("GCS_BUCKET_NAME"),
        blob_name=os.getenv("GCS_BLOB_NAME")
    )
