import aiofiles

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy import func
import base64

from database import SessionLocal, engine
import database, models, schemas, faces, cache

class AuthenticationError(Exception):
    pass 

def create_database():
    database.create_db()
    return schemas.Result(result='ok')

def clear_database():
    database.clear_db()
    return schemas.Result(result='ok')

def drop_database():
    database.drop_db()

def create_database():
    models.Base.metadata.create_all(bind=engine)
    return schemas.Result(result='ok')

def get_image_bytes(photoBase64: str):
    return base64.b64decode(photoBase64.replace('data:image/jpeg;base64,', ''))

def get_image_file_path(user):
    return './images/' + str(user.id) + ';' + user.name + '.jpg'

async def create_image_file(user: schemas.User):
    print('create_image_file: ' + get_image_file_path(user))
    async with aiofiles.open(get_image_file_path(user), 'wb') as out_file:
        await out_file.write(get_image_bytes(user.photo))

def getDbSession():
    dbgen = database.get_session()
    return next(dbgen)

def add_user(user: schemas.User, db: Session = getDbSession()):
    image = get_image_bytes(user.photo)
    encodings = faces.extract_encodings(image)
    if (len(encodings) == 0):
        raise AuthenticationError('Nenhuma face encontrada na foto!')
    if (len(encodings) > 1):
        raise AuthenticationError('Mais de uma face encontrada na foto!')

    user.encoding = faces.serialize(encodings[0])
    print(user)

    # Not persisting photo yet 
    dbuser = models.User(id = user.id, name = user.name, email = user.email, encoding=user.encoding, phone=user.phone, phone2=user.phone2);
    db.add(dbuser)
    db.commit()

    cache.clear_cache()
    return dbuser

def get_next_id(db: Session = getDbSession()):
    maxid_row = db.query(func.max(models.User.id)).first()
    print(maxid_row)
    print(type(maxid_row))
    if (len(maxid_row) > 0 and maxid_row[0]):
        return maxid_row[0] + 1
    else:
        return 1

def authenticate(user: schemas.User, db: Session = getDbSession()):
    image = get_image_bytes(user.photo)
    encodings = faces.extract_encodings(image)
    if (len(encodings) == 0):
        raise AuthenticationError('Nenhuma face encontrada na foto!')
    if (len(encodings) > 1):
        raise AuthenticationError('Mais de uma face encontrada na foto!')

    index = faces.match_face(cache.get_encoding_list(db), encodings[0])
    if index > -1:
        user_id: int = cache.get_user_id(index, db)
        dbuser = get_user_by_id(user_id, db)
        print(dbuser.name)
        return dbuser 

def user_list(db: Session = getDbSession()):
    return db.query(models.User).all()

def get_user_by_id(user_id: int, db: Session = getDbSession()):
    stmt = select(models.User).where(models.User.id == user_id)
    return db.scalar(stmt);    

def get_user_by_email(email: str, db: Session = getDbSession()):
    stmt = select(models.User).where(models.User.email == email)
    return db.scalar(stmt)

def user_delete(user_id: int, db: Session = getDbSession()):
    user = get_user_by_id(user_id, db)
    if (user): 
        db.delete(user)
        db.commit()
        cache.clear_cache()
    return user

def update_user(puser: schemas.User, db: Session = getDbSession()):
    dbuser = get_user_by_id(puser.id, db)
    if (dbuser): 
        if puser.photo and len(puser.photo) > 0:
            image = get_image_bytes(puser.photo)
            encodings = faces.extract_encodings(image)
            if (len(encodings) == 0):
                raise AuthenticationError('Nenhuma face encontrada na foto!')
            if (len(encodings) > 1):
                raise AuthenticationError('Mais de uma face encontrada na foto!')
            dbuser.encoding = faces.serialize(encodings[0])
        if puser.name and len(puser.name) > 0:
            dbuser.name = puser.name
        if puser.email and len(puser.email) > 0:
            dbuser.email = puser.email
        if puser.phone and len(puser.phone) > 0:
            dbuser.phone = puser.phone
        if puser.phone2 and len(puser.phone2) > 0:
            dbuser.phone2 = puser.phone2

        print(dbuser)
        db.flush()
        db.commit()
        cache.clear_cache()
    else: 
        raise AuthenticationError('Usuário não encontrado: ' + str(puser.id))
    return dbuser