from typing import List
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import get_session
from app.models.comment import Comment
from app.models.image import Image
from app.models.like import Like
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentRead
from app.schemas.image import ImageRead
from app.schemas.like import LikeCreate, LikeRead
from app.schemas.post import PostCreate, PostDelete, PostRead, PostReadDetails, PostUpdate, get_id_Post
from app.services.cloudinary_service import cloudinary_service

router=APIRouter(prefix="/posts",tags=["posts"])

@router.get('/',response_model=List[PostRead])
async def get_posts(session:AsyncSession=Depends(get_session)):
    result=await session.execute(select(Post))
    posts=result.scalars().all()
    post_ids=[post.id for post in posts]
    images=[]
    if post_ids:
        image_result=await session.execute(select(Image).where(Image.post_id.in_(post_ids)))
        images=image_result.scalars().all()

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

@router.post('/', response_model=PostRead,status_code=201)
async def create_post(
    user_id:str=Form(...),
    description: str=Form(...),
    files:List[UploadFile]=File(default=[]),
    session:AsyncSession=Depends(get_session)):

    user=await session.get(User,user_id)
    if not user:
        raise HTTPException(status_code=404,detail="User not found")

    try:
        post = Post(description=description,user_id=user_id)
        session.add(post)
        await session.flush()

        images=[]
        if files and files[0].filename:
            for file in files:
                cloud_res= await cloudinary_service.upload_image(
                    file,
                    folder=f"postify/posts/{post.id}"
                )

                image = Image(
                    url=cloud_res["url"],
                    public_id=cloud_res['public_id'],
                    post_id=post.id
                )

                session.add(image)
                images.append(image)
            
        await session.commit()
        await session.refresh(post)
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return PostRead(
        id= post.id,
        user_id= post.user_id,
        description= post.description,
        created_at= post.created_at,
        images=[ImageRead(**img.model_dump()) for img in images],
        likes_count= 0,
        comments_count= 0
    )

@router.get('/{post_id}',response_model=PostReadDetails)
async def get_post_by_id(post_id:uuid.UUID,session:AsyncSession=Depends(get_session)):
    result=await session.execute(select(Post).where(Post.id==post_id))
    post=result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404,detail="Post not found")    
    
    like_result = await session.execute(select(Like).where(Like.post_id==post_id))
    likes=like_result.scalars().all()
    comments_result=await session.execute(select(Comment).where(Comment.post_id==post_id))
    comments=comments_result.scalars().all()
    return PostReadDetails(
        id=post_id,
        user_id=post.user_id,
        description= post.description,
        created_at=post.created_at,
        likes=[LikeRead(**like.model_dump()) for like in likes],
        comments=[CommentRead(**comment.model_dump()) for comment in comments]
    )


@router.get('/{post_id}/simple',response_model=get_id_Post)
async def get_post_by_id_simple(post_id:uuid.UUID,session:AsyncSession=Depends(get_session)):
    post=await session.get(Post,post_id)
    if not post:
        raise HTTPException(status_code=404,detail="Post not found")
    return post

@router.put('/{post_id}',response_model=PostRead)
async def update_post(post_id:uuid.UUID,data:PostUpdate,session:AsyncSession=Depends(get_session)):
    post=await session.get(Post,post_id)
    if not post:
        raise HTTPException(status_code=404,detail="Post not found")
    user=await session.get(User,data.user_id)
    if not user:
        raise HTTPException(status_code=404,detail="User not found")

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

    deleted_post=PostDelete(id=post.id,user_id=post.user_id)
    images=await session.execute(select(Image).where(Image.post_id==post_id))
    likes=await session.execute(select(Like).where(Like.post_id==post_id))
    comments=await session.execute(select(Comment).where(Comment.post_id==post_id))

    for image in images.scalars().all():
        await session.delete(image)
    for like in likes.scalars().all():
        await session.delete(like)
    for comment in comments.scalars().all():
        await session.delete(comment)

    await session.delete(post)
    await session.commit()
    return deleted_post

@router.post('/{post_id}/likes',response_model=LikeRead,status_code=201)
async def add_like(post_id:uuid.UUID,data:LikeCreate, session:AsyncSession=Depends(get_session)):
    if data.post_id != post_id:
        raise HTTPException(status_code=400,detail="Post id does not match")

    result=await session.execute(select(Post).where(Post.id==post_id))
    post=result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404,detail="Post not found")
    user=await session.get(User,data.user_id)
    if not user:
        raise HTTPException(status_code=404,detail="User not found")

    existing_like=await session.execute(
        select(Like).where(Like.post_id==post_id,Like.user_id==data.user_id)
    )

    if existing_like.scalar_one_or_none():
       raise HTTPException(status_code=400,detail="Like already exists") 
    
    like=Like(user_id=data.user_id,post_id=post_id)
    session.add(like)
    await session.commit()
    await session.refresh(like)

    return LikeRead(**like.model_dump())

@router.post('/{post_id}/comments',response_model=CommentRead,status_code=201)
async def add_comment(post_id:uuid.UUID,data:CommentCreate, session:AsyncSession=Depends(get_session)):
    result=await session.execute(select(Post).where(Post.id==post_id))
    post=result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404,detail="Post not found")
    user=await session.get(User,data.user_id)
    if not user:
        raise HTTPException(status_code=404,detail="User not found")

    comment_data=data.model_dump()
    comment_data["post_id"]=post_id
    comment= Comment(**comment_data)
    session.add(comment)
    await session.commit()
    await session.refresh(comment) 
    
    return CommentRead(**comment.model_dump())
