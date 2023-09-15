from typing import Any, Optional

from pydantic import BaseModel


class APIResponse(BaseModel):
    message: str
    data: Optional[Any]
