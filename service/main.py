# import library
from fastapi import FastAPI
from pydantic import BaseModel
from service.ai import ChoaAI

# create object app FastApi
app = FastAPI()
# create object AI LLM
choa = ChoaAI()


# class for data
class NeuroRequest(BaseModel):
    """Модель запроса для нейро-финансиста."""
    user_id: int
    note: str

# function '/'
@app.get('/')
def root():
    return {'message': 'Hello FastAPI'}

# function 'about'
@app.get('/about')
def about():
    return {'message': '초아, AI for finance'}

# function 'neuro'
@app.post('/api/neuro/')
async def neuro(request: NeuroRequest):
    return await choa.neuro_finansist(request.user_id, request.note)

