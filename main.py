import os
from secrets import compare_digest

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import models
import schemas
from auth import create_token, token_verify
from database import Base, engine, SessionLocal

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Blog API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")
    if not admin_username or not admin_password:
        raise HTTPException(
            status_code=503, detail="Admin login is not configured on the server"
        )

    username_matches = compare_digest(form_data.username, admin_username)
    password_matches = compare_digest(form_data.password, admin_password)
    if not (username_matches and password_matches):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    return {
        "access_token": create_token({"sub": admin_username}),
        "token_type": "bearer",
    }


@app.get("/")
def home():
    return {"message": "Welcome to the Blog API!"}


@app.post("/blogs/", response_model=schemas.BlogResponse)
def create_blog(
    blog: schemas.BlogCreate,
    db: Session = Depends(get_db),
    user=Depends(token_verify),
):
    new_blog = models.Blog(title=blog.title, content=blog.content)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@app.get("/blogs")
def get_blogs(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=5, ge=1, le=100),
    search: str = Query(default=""),
    db: Session = Depends(get_db),
):
    query = db.query(models.Blog)

    if search:
        query = query.filter(models.Blog.title.ilike(f"%{search}%"))
    total = query.count()
    blogs = query.offset((page - 1) * limit).limit(limit).all()
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "data": blogs,
    }


@app.get("/blog/{id}")
def get_one_blog(id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog Not found")
    return blog


@app.put("/blog/{id}", response_model=schemas.BlogResponse)
def update(
    id: int,
    blog: schemas.BlogCreate,
    db: Session = Depends(get_db),
    user=Depends(token_verify),
):
    existing_blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not existing_blog:
        raise HTTPException(status_code=404, detail="Blog Not found")
    existing_blog.title = blog.title
    existing_blog.content = blog.content
    db.commit()
    db.refresh(existing_blog)
    return existing_blog


@app.delete("/blog/{id}")
def delete_blog(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(token_verify),
):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog Not found")
    db.delete(blog)
    db.commit()
    return {"message": "Blog deleted successfully"}
