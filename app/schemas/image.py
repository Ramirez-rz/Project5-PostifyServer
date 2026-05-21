from datetime import datetime
from typing import TYPE_CHECKING, List
import uuid

from sqlmodel import Field, Relationship, SQLModel

class ImageCreate(SQLModel):
    url: str
    public_id: str
    post_id: uuid.UUID

class ImageRead(SQLModel):
    url: str
    public_id: str
    post_id: uuid.UUID 
