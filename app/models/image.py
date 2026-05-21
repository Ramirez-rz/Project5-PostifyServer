from datetime import datetime
import uuid

from sqlmodel import Field, Relationship, SQLModel

class Image(SQLModel,table=True):
    __tablename__='images'
    url: str
    public_id: str
    post_id: uuid.UUID = Field(foreign_key="posts.id",primary_key=True) 

    post: "Post" = Relationship(back_populates="images")