from pydantic import BaseModel, ConfigDict
from datetime import datetime


class FileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_name: str
    generated_name: str
    content_type: str
    size: int
    created_at: datetime
