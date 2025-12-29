from pydantic import BaseModel, Field
from typing import List

class MbtiResponse(BaseModel):
    message: str
