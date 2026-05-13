from datetime import datetime
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

class PostUpdate(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    new_description:str
    created_at:datetime 