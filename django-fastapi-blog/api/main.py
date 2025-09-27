from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import os
import sys
import django


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog_project.settings")
django.setup()

from blog.models import Post, Category, Comment
from django.contrib.auth.models import User
from django.db.models import Q

app = FastAPI(
    title="Blog API",
    descrpition="A high-performance blog API built with FastAPI and Django ORM",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PostBase(BaseModel):
    title: str
    slug: str
    content: str
    excerpt: Optional[str] = None
    status: str = "draft"
    category_id: Optional[int] = None


class PostCreate(PostBase):
    author_id: int


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    status: Optional[str] = None
    category_id: Optional[int] = None


class PostResponse(BaseModel):
    id: int
    title: str
    slug: str
    author: str
    category: Optional[str] = None
    content: str
    excerpt: str
    status: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    post_id: int
    author_id: int


class CommentResponse(CommentBase):
    id: int
    author: str
    created_at: datetime

    class Config:
        from_attributes = True


@app.get("/")
async def root():
    return {
        "message": "Blog API with FastAPI and Django ORM",
        "endpoints": {
            "posts": "/api/posts/",
            "categories": "/api/categories/",
            "comments": "/api/comments/",
            "docs": "/docs",
        },
    }


@app.get("/api/categories/", response_model=List[CategoryResponse])
async def get_categories():
    categories = Category.objects.all()
    return [
        CategoryResponse(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            description=cat.description,
            created_at=cat.created_at,
        )
        for cat in categories
    ]


@app.post("/api/categories/", response_model=CategoryResponse)
async def create_category(category: CategoryBase):
    try:
        new_category = Category.objects.create(
            name=category.name,
            slug=category.slug,
            description=category.description,
        )
        return CategoryResponse(
            id=new_category.id,
            name=new_category.name,
            slug=new_category.slug,
            description=new_category.description,
            created_at=new_category.created_at,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Post endpoints
@app.get("/api/posts/", response_model=List[PostResponse])
async def get_posts(
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by categoyr slug"),
    search: Optional[str] = Query(None, description="Filter by title and content"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    posts = Post.objects.select_related("author", "category").all()

    if status:
        posts = posts.filter(status=status)
    if category:
        posts = posts.filter(category_slug=category)
    if search:
        posts = posts.filter(Q(title__icontains=search) | Q(content__icontains=search))

    posts = posts[offset : offset + limit]

    return [
        PostResponse(
            id=post.id,
            title=post.title,
            slug=post.slug,
            author=post.author.username,
            category=post.category.name if post.categiry else None,
            content=post.content,
            excerpt=post.excerpt,
            status=post.status,
            created_at=post.created_at,
            updated_at=post.updated_at,
            published_at=post.published_at,
        )
        for post in posts
    ]


@app.get("/api/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int):
    try:
        post = Post.objects.select_related("author", "category").get(id=post_id)
        return PostResponse(
            id=post.id,
            title=post.title,
            slug=post.slug,
            author=post.author.username,
            category=post.category.name if post.categiry else None,
            content=post.content,
            excerpt=post.excerpt,
            status=post.status,
            created_at=post.created_at,
            updated_at=post.updated_at,
            published_at=post.published_at,
        )
    except Post.DoesNotExist:
        raise HTTPException(status_code=404, detail="Post not found")


@app.post("/api/posts", response_model=PostResponse)
async def create_post(post: PostCreate):
    try:
        author = User.objects.get(id=post.author_id)
        category = None
        if post.category_id:
            category = Category.objects.get(id=post.category_id)

        new_post = Post.objects.create(
            title=post.title,
            slug=post.slug,
            author=author,
            category=category,
            content=post.content,
            excerpt=post.excerpt,
            status=post.status,
        )

        return PostResponse(
            id=new_post.id,
            title=new_post.title,
            slug=new_post.slug,
            author=new_post.author.username,
            category=new_post.category.name if post.categiry else None,
            content=new_post.content,
            excerpt=new_post.excerpt,
            status=new_post.status,
            created_at=new_post.created_at,
            updated_at=new_post.updated_at,
            published_at=new_post.published_at,
        )
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="Author not found")
    except Category.DoesNotExist:
        raise HTTPException(status_code=404, detail="Category not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/posts/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post_update: PostUpdate):
    try:
        post = Post.objects.get(id=post_id)
        if post_update.title:
            post.title = post_update.title
        if post_update.content:
            post.content = post_update.content
        if post_update.excerpt:
            post.excerpt = post_update.excerpt
        if post_update.status:
            post.status = post_update.status
        if post_update.category_id:
            post.category = Category.objects.get(id=post_update.category_id)

        post.save()

        return PostResponse(
            id=post.id,
            title=post.title,
            slug=post.slug,
            author=post.author.username,
            category=post.category.name if post.categiry else None,
            content=post.content,
            excerpt=post.excerpt,
            status=post.status,
            created_at=post.created_at,
            updated_at=post.updated_at,
            published_at=post.published_at,
        )
    except Post.DoesNotExist:
        raise HTTPException(status_code=404, detail="Post not found")
    except Category.DoesNotExist:
        raise HTTPException(status_code=404, detail="Category not found")


@app.delete("/api/posts/{post_id}")
async def delete_post(post_id: int):
    try:
        post = Post.objects.get(id=post_id)
        post.delete()
        return {"message": "Post deleted successfully"}
    except Post.DoesNotExist:
        raise HTTPException(status_code=404, detail="Post not found")
