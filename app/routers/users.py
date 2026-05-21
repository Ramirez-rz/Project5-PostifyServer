from typing import List
import uuid

from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import get_session
from app.models.image import Image
from app.models.post import Post
from app.models.user import User
from app.schemas.image import ImageRead
from app.schemas.post import PostRead
from app.schemas.user import UserRead,UserCreate


router=APIRouter(prefix="/users",tags=["users"])

@router.get('/',response_model=List[UserRead])
async def get_users(session:AsyncSession=Depends(get_session)):
    result= await session.execute(select(User))
    return result.scalars().all()

@router.post('/',response_model=UserRead,status_code=201)
async def create_user(data:UserCreate,session:AsyncSession=Depends(get_session)):
    user = User(**data.model_dump())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@router.get('/{userId}/posts',response_model=List[PostRead])
async def get_post_by_user(userId: uuid.UUID,session:AsyncSession=Depends(get_session)):
    res=await session.execute(select(Post).where(Post.user_id==userId))
    posts=res.scalars().all()
    post_ids=[post.id for post in posts]
    images=[]
    if post_ids:
        image_res=await session.execute(select(Image).where(Image.post_id.in_(post_ids)))
        images=image_res.scalars().all()

    return [
        PostRead(
            id=post.id,
            user_id=post.user_id,
            description=post.description,
            created_at=post.created_at,
            images=[
                ImageRead(**image.model_dump())
                for image in images
                if image.post_id == post.id
            ],
            likes_count=0,
            comments_count=0
        )
        for post in posts
    ]
