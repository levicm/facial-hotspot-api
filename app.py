import aiofiles

from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy import func

from database import SessionLocal, engine
import models, schemas, faces

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

user_cache = [ ]
user_encoding_cache = [ ]

# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.get("/")
def main():
    return RedirectResponse(url="/docs/")

@app.post('/create_db')
def create_db(db: Session = Depends(get_db)):
    models.Base.metadata.create_all(bind=engine)
    return {'result': 'ok'}

@app.post('/clear_db')
def clear_db(db: Session = Depends(get_db)):
    models.Base.metadata.clear()
    return {'result': 'ok'}

@app.post('/drop_db')
def drop_db(db: Session = Depends(get_db)):
    models.Base.metadata.drop_all(bind=engine)
    return {'result': 'ok'}

@app.post('/users')
def user_add(user: schemas.User, db: Session = Depends(get_db)):
    print('add_user')
    error = ''
    if (len(user.photo) == 0):
        error = 'Foto não definida!'
    else:
        encodings = faces.extract_encodings(user.get_photo_image())
        if (len(encodings) == 0):
            error = 'Nenhuma face encontrada na foto!'
        if (len(encodings) > 1):
            error = 'Mais de uma face encontrada na foto!'

    if (len(error) == 0):
        add_user(user, encodings[0], db)
        return {'result': 'ok'}
    else:
        return {'result': 'error', 'message': error}
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
    add_to_cache(model_user, encoding, db)

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

@app.post('/authenticate')
def authenticate(user: schemas.User, db: Session = Depends(get_db)):
    error = ''
    if (len(user.photo) == 0):
        error = 'Foto não definida!'
    else:
        encodings = faces.extract_encodings(user.get_photo_image())
        if (len(encodings) == 0):
            error = 'Nenhuma face encontrada na foto!'
        if (len(encodings) > 1):
            error = 'Mais de uma face encontrada na foto!'

    if len(error) == 0:
        # with open('./images/autenticando.jpg', 'wb') as out_file:
        #     out_file.write(user.get_photo_image())

        index = faces.match_face(get_encoding_cache(db), encodings[0])
        if index > -1:
            user_id = get_user_cache(db)[index]
            user = get_user_by_id(user_id, db)
            print(user.name)
            return { 'result': 'ok', 'user': { 'id': user.id, 'name': user.name } }
        else:
            error = 'Usuário não encontrado!'
    return { 'result': 'error', 'message': error }
    # raise HTTPException(status_code=404, detail='Usuário não encontrado!')

@app.get('/users')
def user_list(db: Session = Depends(get_db)):
    records = db.query(models.User).all()
    return records

@app.get('/users/id/{user_id}', response_model=schemas.User)
def user_by_id(user_id: int, db: Session = Depends(get_db)):
    model_user = get_user_by_id(user_id, db)
    if (model_user): 
        return model_user
    else:
        raise HTTPException(status_code=404, detail='User not found!')

def get_user_by_id(user_id, db: Session):
    stmt = select(models.User).where(models.User.id.is_(user_id))
    return db.scalar(stmt);    

@app.get('/users/email/{email}', response_model=schemas.User)
def user_by_email(email: str, db: Session = Depends(get_db)):
    stmt = select(models.User).where(models.User.email.is_(email))
    model_user = db.scalar(stmt)
    if (model_user): 
        return model_user
    else:
        raise HTTPException(status_code=404, detail='User not found!')

def add_to_cache(user, encoding, db: Session):
    get_user_cache(db).append(user.id)
    get_encoding_cache(db).append(encoding)

def get_user_cache(db: Session):
    if (len(user_cache) == 0):
        build_cache(db)
    return user_cache

def get_encoding_cache(db: Session):
    if (len(user_encoding_cache) == 0):
        build_cache(db)
    return user_encoding_cache

def build_cache(db: Session):
    user_cache.clear()
    user_encoding_cache.clear()
    records = db.query(models.User).all()
    for user in records:
        user_cache.append(user.id)
        user_encoding_cache.append(faces.desserialize(user.encoding))
