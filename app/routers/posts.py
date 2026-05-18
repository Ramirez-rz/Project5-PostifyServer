from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import get_session
from app.models.post import Post
from app.schemas.post import PostCreate, PostDelete, PostRead, PostUpdate, get_id_Post

router=APIRouter(prefix="/posts",tags=["posts"])

@router.get('/',response_model=List[PostRead])
async def get_posts(session:AsyncSession=Depends(get_session)):
    result=await session.execute(select(Post))
    return result.scalars().all()

@router.post('/', response_model=PostRead,status_code=201)
async def create_post(data: PostCreate,session:AsyncSession =Depends(get_session)):
    post=Post(**data.model_dump())
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post

@router.get('/{post_id}',response_model=get_id_Post)
async def get_post_by_id(post_id:uuid.UUID,session:AsyncSession=Depends(get_session)):
    post=await session.get(Post,post_id)
    if not post:
        raise HTTPException(status_code=404,detail="Post not found")
    return post

@router.put('/{post_id}',response_model=PostRead)
async def update_post(post_id:uuid.UUID,data:PostUpdate,session:AsyncSession=Depends(get_session)):
    post=await session.get(Post,post_id)
    if not post:
        raise HTTPException(status_code=404,detail="Post not found")
    post.description=data.description
    post.user_id=data.user_id
    await session.commit()
    await session.refresh(post)
    return post

@router.delete('/{post_id}',response_model=PostDelete)
async def delete_post(post_id:uuid.UUID,session:AsyncSession=Depends(get_session)):
    post=await session.get(Post,post_id)
    if not post:
        raise HTTPException(status_code=404,detail="Post not found")
    await session.delete(post)
    await session.commit()
    return post
