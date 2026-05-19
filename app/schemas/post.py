
#update, delete, get_id
from datetime import datetime
from typing import TYPE_CHECKING, List
import uuid

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.schemas.like import LikeRead
    from app.schemas.comment import CommentRead

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
    user_id: uuid.UUID
    description:str

class PostDelete(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID 

class get_id_Post(SQLModel):
    id: uuid.UUID
    user_id:uuid.UUID
    description:str
    created_at:datetime
    updated_at:datetime 


from app.schemas.like import LikeRead
from app.schemas.comment import CommentRead

PostReadDetails.model_rebuild()
