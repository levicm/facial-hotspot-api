import aiofiles
import typing

from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy import func

import database
import models, schemas, faces, cache

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "https://localhost",
    "https://localhost:8080",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency

@app.get("/")
def main():
    return RedirectResponse(url="/docs/")

@app.post('/db_create', response_model=schemas.Result)
def create_database():
    database.create_db()
    return schemas.Result(result='ok')

@app.post('/db_clear', response_model=schemas.Result)
def clear_database():
    database.clear_db()
    return schemas.Result(result='ok')

@app.post('/db_drop', response_model=schemas.Result)
def drop_database():
    database.drop_db()
    return schemas.Result(result='ok')

@app.post('/users', response_model=schemas.Result)
def user_add(puser: schemas.User, db: Session = Depends(database.get_db)):
    print('add_user')
    error = ''
    if (len(puser.photo) == 0):
        error = 'Foto não definida!'
    else:
        encodings = faces.extract_encodings(puser.get_photo_image())
        if (len(encodings) == 0):
            error = 'Nenhuma face encontrada na foto!'
        if (len(encodings) > 1):
            error = 'Mais de uma face encontrada na foto!'

    if (len(error) == 0):
        dbuser = add_user(puser, encodings[0], db)
        return schemas.Result(result='ok', user=dbuser)
    else:
        return schemas.Result(result='error', message=error)
        # raise HTTPException(status_code=404, detail=error)

def add_user(user, encoding, db):
    if (not user.id or len(user.id) == 0):
        user.id = get_next_id(db)
    print(user.id)
    model_user = models.User(id = user.id, name = user.name, email = user.email);
    model_user.encoding = faces.serialize(encoding)
    print(model_user)
    db.add(model_user)
    db.commit()
    cache.clear_cache()
    return model_user

def get_next_id(db):
    maxid_row = db.query(func.max(models.User.id)).first()
    print(maxid_row)
    print(type(maxid_row))
    if (len(maxid_row) > 0 and maxid_row[0]):
        return maxid_row[0] + 1
    else:
        return 1

async def create_image_file(user: schemas.User):
    print('create_image_file: ' + user.get_image_file_path())
    async with aiofiles.open(user.get_image_file_path(), 'wb') as out_file:
        await out_file.write(user.get_photo_image())

@app.post('/authenticate', response_model=schemas.Result)
def authenticate(puser: schemas.User, db: Session = Depends(database.get_db)):
    error = ''
    if (len(puser.photo) == 0):
        error = 'Foto não definida!'
    else:
        encodings = faces.extract_encodings(puser.get_photo_image())
        if (len(encodings) == 0):
            error = 'Nenhuma face encontrada na foto!'
        if (len(encodings) > 1):
            error = 'Mais de uma face encontrada na foto!'

    if len(error) == 0:
        # with open('./images/autenticando.jpg', 'wb') as out_file:
        #     out_file.write(user.get_photo_image())

        index = faces.match_face(cache.get_encoding_list(db), encodings[0])
        if index > -1:
            user_id = cache.get_user_id(index, db)
            dbuser = get_user_by_id(user_id, db)
            print(dbuser.name)
            return schemas.Result(result='ok', user=dbuser)
        else:
            error = 'Usuário não encontrado!'
    return schemas.Result(result='error', message=error)
    # raise HTTPException(status_code=404, detail='Usuário não encontrado!')

@app.get('/users', response_model=typing.List[schemas.User])
def user_list(db: Session = Depends(database.get_db)):
    records = db.query(models.User).all()
    return records

@app.get('/users/id/{user_id}', response_model=schemas.User)
def user_by_id(user_id: int, db: Session = Depends(database.get_db)):
    model_user = get_user_by_id(user_id, db)
    if (model_user): 
        return model_user
    else:
        raise HTTPException(status_code=404, detail='User not found!')

def get_user_by_id(user_id, db: Session):
    stmt = select(models.User).where(models.User.id.is_(user_id))
    return db.scalar(stmt);    

@app.get('/users/email/{email}', response_model=schemas.User)
def user_by_email(email: str, db: Session = Depends(database.get_db)):
    stmt = select(models.User).where(models.User.email.is_(email))
    model_user = db.scalar(stmt)
    if (model_user): 
        return model_user
    else:
        raise HTTPException(status_code=404, detail='User not found!')

@app.delete('/users/id/{user_id}', response_model=schemas.User)
def user_delete(user_id: int, db: Session = Depends(database.get_db)):
    print('user_delete')
    print(user_id)
    model_user = get_user_by_id(user_id, db)
    if (model_user): 
        db.delete(model_user)
        db.commit()
        cache.clear_cache()
        return model_user
    else:
        raise HTTPException(status_code=404, detail='User not found!')

