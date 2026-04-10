from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from pydantic import EmailStr   #insert at top of the file

class Token(SQLModel):
    access_token: str
    token_type: str

class UserCreate(SQLModel):
    username:str
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)

class UserResponse(SQLModel):
    id: Optional[int]
    username:str
    email: EmailStr

class UserBase(SQLModel,):
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    password: str
    role:str = ""

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    todos: list['Todo'] = Relationship(back_populates="user")

class AdminCreate(UserBase):
    role:str = "admin"

class RegularUserCreate(UserBase):
    role:str = "regular_user"

class UserBase(SQLModel,):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password: str

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    def check_password(self, plaintext_password:str):
        return PasswordHash.recommended().verify(password=plaintext_password, hash=self.password)

    user_comments:list['Comment'] = Relationship(back_populates = "user")#1
    user_reactions:list['Reactions'] = Relationship(back_populates = "user")#1

class Album(SQLModel, table = True):
      id: Optional[int] = Field(default=None, primary_key=True)
      name:Optional[str] = Field(default = "")
      artist:Optional[str]=Field(default = "")
      image:Optional[str]=Field(default = "")
      album_tracks:list['AlbumTrack'] = Relationship(back_populates = "album")#2



class AlbumTrack(SQLModel, table=  True):
      id: Optional[int] = Field(default=None, primary_key=True)
      track_title:Optional[str]
      album_id:int = Field(foreign_key = "album.id")
      
      album:Album = Relationship(back_populates= "album_tracks")#2

      album_comments:list['Comment'] = Relationship(back_populates = "albumtrack")#3
      albumtrack_reactions:list['Reactions'] = Relationship(back_populates = "albumtrack")#4

      def numComments(self):

       return len(self.album_comments)
      def reactions(self):
        return len(self.albumtrack_reactions)
      
class Comment(SQLModel, table = True):
      id: Optional[int] = Field(default=None, primary_key=True)
      user_id:int = Field(foreign_key = "user.id")
      albumtrack_id:int = Field(foreign_key = "albumtrack.id")
      text:str
      albumtrack:AlbumTrack = Relationship(back_populates = "album_comments")#3
      user:User = Relationship(back_populates = "user_comments")#1


class Reactions(SQLModel, table = True):
     user_id:int = Field(foreign_key = "user.id", primary_key = True)
     albumtracktrack_id:int = Field(foreign_key = "albumtrack.id", primary_key = True)
     
     likes:int =0
     dislikes:int =0
     albumtrack:AlbumTrack = Relationship(back_populates = "albumtrack_reactions")#4
     user:'User' = Relationship(back_populates = "user_reactions")#1
  
     def numLikes(self):
          return self.likes
     def numDislikes(self):
          return self.dislikes
     def like(self):
          self.likes+=1
     def dislike(self):
          self.dislikes+=1
class TodoCategory(SQLModel, table=True):
    category_id: int = Field(foreign_key="category.id", primary_key=True)
    todo_id: int = Field(foreign_key="todo.id", primary_key=True)

class Category(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")
    text:str

    todos:list['Todo'] = Relationship(back_populates="categories", link_model=TodoCategory)

class TodoCreate(SQLModel):
    text:str

class TodoResponse(SQLModel):
    id: Optional[int] = Field(primary_key=True, default=None)
    text:str
    done: bool = False

class TodoUpdate(SQLModel):
    text: Optional[str] = None
    done: Optional[bool] = None

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")
    text:str
    done: bool = False

    user: User = Relationship(back_populates="todos")
    categories:list['Category'] = Relationship(back_populates="todos", link_model=TodoCategory)

    def toggle(self):
        self.done = not self.done
    
    def get_cat_list(self):
        return ', '.join([category.text for category in self.categories])
