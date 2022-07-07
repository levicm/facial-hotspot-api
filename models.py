from sqlalchemy import Column, Integer, String
from sqlalchemy.types import Date
from database import Base

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80))
    email = Column(String(80), index=True)
    photo = Column(String)
    encoding = Column(String(2400))
    address = Column(String(100))
    phone = Column(String)
    phone2 = Column(String)
    birthday = Column(Date)
    created = Column(Date)
    updated = Column(Date)

