from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)
#@router.get("/", response_model=List[schemas.Post])
@router.get("/", response_model=List[schemas.PostOut])
#def get_posts(db: Session = Depends(get_db)): #allows getting all posts regardless of login status
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] =""):   #only allows if user is logged in
    # cursor.execute("""SELECT * FROM posts """)
    # posts = cursor.fetchall()
    #posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all() #gets all posts from all users
    #posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all() #only grabs current users posts rather than all posts. 
    #posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        #models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
            #models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
            models.Post.title.contains(search)).limit(limit).offset(skip).all()
  
    return posts
    

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s,%s,%s) RETURNING * """,
    #                 (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    #print(post.model_dump())   #in the course model_dump() is dict() pydantic just changed the name. 
      #pydantic new .dict()
    #new_post = models.Post(title=post.title, content=post.content, published=post.published) # example of what **post.model_dump() actually contains.
    print(current_user.id)
    print(current_user.email)
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    #return {"data": new_post}
    return new_post

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db)): #removes current user req
#def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)): #notice that this requests id as an integer, fastapi will auto throw the proper errors to the frontend if a valid value isnt input.
    # cursor.execute("""SELECT * from posts WHERE id = %s """, (str(id)))
    # post = cursor.fetchone()
    #post = db.query(models.Post).filter(models.Post.id == id).first()

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    #if post.owner_id != current_user.id:
        #raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
        #response.status_code = status.HTTP_404_NOT_FOUND
        #return {'message': f"post with id: {id} was not found"}
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING *""", (str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    post_query.delete(synchronize_session=False)
    db.commit()
    #my_posts.pop(deleted_post) #sql
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s  WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
    # cursor.fetchone()
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()