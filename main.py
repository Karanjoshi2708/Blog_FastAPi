from email.policy import default

from fastapi import FastAPI , Depends , HTTPException , Query
from sqlalchemy.orm import Session
from database import engine , SessionLocal
import models , schemas
from auth import create_token , token_verify

models.Base.metadata.create_all(bind=engine)

app = FastAPI() 

#DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#Login API
@app.post("/login")
def login():
    return {
        "access_token" : create_token({"user" : "admin"}),
        "tokrn_type" : "bearer"
    }

#Home
@app.get("/") 
def home():
    return {"message": "Welcome to the Blog API!"}

#create a blog(protected)
@app.post("/blogs/", response_model=schemas.BlogResponse)
def create_blog(blog: schemas.BlogCreate, db: Session = Depends(get_db) , user = Depends(token_verify)):
    new_blog = models.Blog(title=blog.title, 
                content=blog.content)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)

    return new_blog

#Raed all blogs
@app.get("/blogs")
def get_blogs(
    page : int = 1 ,
    limit : int = 5, 
    search : str = Query(default="") ,
    db: Session = Depends(get_db)):

    query = db.query(models.Blog)

    #for searching
    if search:
        query=query.filter(models.Blog.title.ilike(f"%{search}%"))

    #for pagenation
    total = query.count()

    start = (page-1)*limit

    blogs = query.offset(start).limit(limit).all()


    return{
        "page":page,
        "limit":limit,
        "total":total ,
        "data" : blogs
    }

#Read one blog
@app.get("/blog/{id}")
def get_one_blog(id : int , db : Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not blog:
        raise HTTPException(status_code=404 , detail="Blog Not found")

    return blog


#Update blog api(protected)
@app.put("/blog/{id}" , response_model=schemas.BlogResponse)
def update(id : int ,blog : schemas.BlogCreate , db : Session = Depends(get_db) , user = Depends(token_verify)):
    existing_blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not existing_blog:
            raise HTTPException(status_code=404 , detail="Blog Not found")

    existing_blog.title = blog.title
    existing_blog.content = blog.content

    db.commit()
    db.refresh(existing_blog)
    
    return existing_blog

#delete blog api(protected)

@app.delete("/blog/{id}")
def blog(id : int  , db : Session = Depends(get_db) , user = Depends(token_verify)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    
    if not blog.first:
        raise HTTPException(status_code=404 , detail="Blog Not found")

    blog.delete()
    db.commit()

    return {
        "message" : "Blog deleted successfully"}

