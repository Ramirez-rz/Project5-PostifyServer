
#update, delete, get_id
from datetime import datetime
from typing import List
import uuid

from sqlmodel import Field, Relationship, SQLModel

class PostCreate(SQLModel):
    description: str
    user_id: uuid.UUID

class PostRead(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    description:str
    created_at:datetime
    likes_count: int=0
    comments_count: int=0

class PostReadDetails(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    description:str
    created_at:datetime 
    likes:List['LikeRead']=[]
    comments:List['CommentRead']=[]


class PostUpdate(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    description:str
    updated_at:datetime 

class PostDelete(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID 

class get_id_Post(SQLModel):
    id: uuid.UUID
    user_id:uuid.UUID
    description:str
    created_at:datetime
    updated_at:datetime 