from pydantic import BaseModel
from datetime import date


class UserShema(BaseModel):
    name: str
    password: str
    
class StuffShema(BaseModel):
    id: int
    name: str
    phone: str    
    birthday: date
    depart: str
    post: str
    room: str
    email: str
    other_info: str | None = None
    
class PostAddShema(BaseModel):
    name: str