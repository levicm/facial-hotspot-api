import typing

from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from sqlalchemy.orm import Session

import database, services, schemas

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

@app.get("/")
def main():
    return RedirectResponse(url="/docs/")

@app.post('/db_create', response_model=schemas.Result)
def create_database():
    services.create_database()
    return schemas.Result(result='ok')

@app.post('/db_clear', response_model=schemas.Result)
def clear_database():
    services.clear_database()
    return schemas.Result(result='ok')

@app.post('/db_drop', response_model=schemas.Result)
def drop_database():
    services.drop_database()
    return schemas.Result(result='ok')

@app.post('/users', response_model=schemas.Result)
def user_add(puser: schemas.User, db: Session = Depends(database.get_session)):
    print('user_add')
    try:
        if (not(puser.photo) or len(puser.photo) == 0):
            raise services.AuthenticationError('Foto não definida!')

        dbuser = services.add_user(puser, db)
        # puser.photo = None
        return schemas.Result(result='ok', user=dbuser)
    except services.AuthenticationError as e:
        return schemas.Result(result='error', message=str(e))
        # raise HTTPException(status_code=404, detail=error)

@app.put('/users', response_model=schemas.Result)
def user_update(puser: schemas.User, db: Session = Depends(database.get_session)):
    print('user_update')
    try:
        if not(puser.id):
            raise services.AuthenticationError('Identificação requerida!')

        dbuser = services.update_user(puser, db)
        # puser.photo = None
        return schemas.Result(result='ok', user=dbuser)
    except services.AuthenticationError as e:
        return schemas.Result(result='error', message=str(e))
        # raise HTTPException(status_code=404, detail=error)

@app.post('/authenticate', response_model=schemas.Result)
def authenticate(puser: schemas.User, db: Session = Depends(database.get_session)):
    print('authenticate')
    try:
        if (not(puser.photo) or len(puser.photo) == 0):
            raise services.AuthenticationError('Foto não definida!')
        dbuser = services.authenticate(puser)
        if not (dbuser):
            raise services.AuthenticationError('Usuário não encontrado!')

        return schemas.Result(result='ok', user=dbuser)
    except services.AuthenticationError as e:
        return schemas.Result(result='error', message=str(e))
    # raise HTTPException(status_code=404, detail='Usuário não encontrado!')

@app.get('/users', response_model=typing.List[schemas.User])
def user_list(db: Session = Depends(database.get_session)):
    return services.user_list(db)

@app.get('/users/id/{user_id}', response_model=schemas.User)
def user_by_id(user_id: int, db: Session = Depends(database.get_session)):
    user = services.get_user_by_id(user_id)
    if not (user): 
        raise HTTPException(status_code=404, detail='Usuário não encontrado!')
    return user

@app.get('/users/email/{email}', response_model=schemas.User)
def user_by_email(email: str, db: Session = Depends(database.get_session)):
    user = services.get_user_by_email(email)
    if not (user): 
        raise HTTPException(status_code=404, detail='Usuário não encontrado!')
    return user

@app.delete('/users/id/{user_id}', response_model=schemas.Result)
def user_delete(user_id: int, db: Session = Depends(database.get_session)):
    dbuser = services.user_delete(user_id, db)
    if not (dbuser): 
        raise HTTPException(status_code=404, detail='Usuário não encontrado!')
    return schemas.Result(result='ok', user=dbuser)
