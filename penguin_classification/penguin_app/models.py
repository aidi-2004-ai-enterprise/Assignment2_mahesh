from pydantic import BaseModel, Field

class PenguinData(BaseModel):
    bill_length_mm: float = Field(..., gt=0, description="Bill length in millimeters")
    bill_depth_mm: float = Field(..., gt=0, description="Bill depth in millimeters")
    flipper_length_mm: float = Field(..., gt=0, description="Flipper length in millimeters")
    body_mass_g: float = Field(..., gt=0, description="Body mass in grams")

    class Config:
        schema_extra = {
            "example": {
                "bill_length_mm": 39.1,
                "bill_depth_mm": 18.7,
                "flipper_length_mm": 181.0,
                "body_mass_g": 3750.0
            }
        }