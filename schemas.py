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
    
    class Config:
        orm_mode = True

    def get_photo_image(self):
        return base64.b64decode(self.photo.replace('data:image/jpeg;base64,', ''))

    def get_image_file_path(self):
        return './images/' + str(self.id) + ';' + self.name + '.jpg'