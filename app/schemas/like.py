
#update, delete, get_id
from datetime import datetime
import uuid

from sqlmodel import Field, Relationship, SQLModel


class LikeCreate(SQLModel):
    user_id: uuid.UUID
    post_id: uuid.UUID

class LikeRead(SQLModel):
    user_id: uuid.UUID
    post_id: uuid.UUID
    created_at:datetime 