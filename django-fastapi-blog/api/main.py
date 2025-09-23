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
