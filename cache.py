from sqlalchemy.orm import Session
import faces, models

user_id_list = [ ]
user_encoding_list = [ ]

def build_cache(db: Session):
    print('build_cache')
    user_id_list.clear()
    user_encoding_list.clear()
    records = db.query(models.User).all()
    for user in records:
        user_id_list.append(user.id)
        user_encoding_list.append(faces.desserialize(user.encoding))
    print(len(user_encoding_list))

def clear_cache():
    user_id_list.clear()
    user_encoding_list.clear()

def get_user_id_list(db: Session):
    if (len(user_id_list) == 0):
        build_cache(db)
    return user_id_list

def get_encoding_list(db: Session):
    if (len(user_encoding_list) == 0):
        build_cache(db)
    return user_encoding_list

def get_user_id(index, db:Session):
    return get_user_id_list(db)[index]
