from typing_extensions import Self
from typing import Optional
from pydantic import BaseModel
import base64

class User(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    photo: Optional[str] = None
    encoding: Optional[str] = None
    phone: Optional[str] = None
    phone2: Optional[str] = None
    
    class Config:
        orm_mode = True

class Result(BaseModel):
    result: str
    message: Optional[str]
    user: Optional[User]
    
