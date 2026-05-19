
from datetime import datetime
import uuid
from typing import List

from sqlmodel import Field, Relationship, SQLModel

class User(SQLModel, table=True):
    __tablename__="users"

    id: uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    username:str=Field(unique=True,index=True)
    name:str
    lastname:str
    email:str=Field(unique=True,index=True)
    password:str
    created_at:datetime=Field(default_factory=datetime.utcnow)

    posts: list["Post"] = Relationship(back_populates="user")
    likes: List['Like'] = Relationship(back_populates="user")
    comments: List['Comment'] = Relationship(back_populates="user")