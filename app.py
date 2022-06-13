from fastapi import FastAPI

app = FastAPI()

subjects = [
    {'name': 'Levi', 'cpf': 53260414568},
    {'name': 'Helen', 'cpf': 96283793568},
    {'name': 'Lavinia', 'cpf': 12345}
]

@app.get('/subjects')
def user_list():
    return {'subjects': subjects}

@app.get('/authenticate')
def authenticate():
    return {'result': 'ok'}
