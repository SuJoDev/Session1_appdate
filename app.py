from typing import Annotated

import base64
import hmac
import hashlib
import json

from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from models.models import *
from shemas.shemas import *


DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/session2"
SECRET_KEY = "secret_key"

error_code = 1000

def score_error():
    global error_code
    error_code += 1
    return error_code

app = FastAPI()
security = HTTPBearer()

engine = create_async_engine(DATABASE_URL)
new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        return session
    
SessionDep = Annotated[AsyncSession, Depends(get_session)]

def decode(data):
    return base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip("=")

def create_token(payload):
    header = {"alg": "SH256", "typ": "JWT"}
    unexpected_token = decode(header) + "." + decode(payload)
    
    signature = hmac.new(SECRET_KEY.encode(), unexpected_token.encode(), hashlib.sha256).digest()
    signature = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    token = unexpected_token + "." + signature
    return token

async def get_user_from_db(session: SessionDep, username: str):
    result = await session.execute(select(UsersModel).where(UsersModel.name == username))
    return result.scalar_one_or_none()    

def deccode(token):
    header, payload, signature = token.split(".")
    decoded_payload = base64.urlsafe_b64decode(payload + "==").decode()
    return json.loads(decoded_payload)  

def verify_token(token):
    try:
        header, payload, signature = token.split(".")
        unsigned_token = f"{header}.{payload}"
        expected_signature = hmac.new(SECRET_KEY.encode(), unsigned_token.encode(), hashlib.sha256).digest()
        expected_signature = base64.urlsafe_b64encode(expected_signature).decode().rstrip("=")
        return expected_signature == signature
    except:
        return False

async def get_current_user( credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"timestamp": datetime.now().timestamp(), "message" : "Не найдены данные", "errorCode": score_error()}
        )
    
    paylod = deccode(token)
    
    if datetime.now().timestamp() > paylod["exp"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"timestamp": datetime.now().timestamp(), "message" : "Токен устарел", "errorCode": score_error()}
        )
        
    return paylod
    

@app.post("/api/v1/SignIn")
async def auth(session: SessionDep, user_form : UserShema):
    user = await get_user_from_db(session, user_form.name)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"timestamp": datetime.now().timestamp(), "message" : "Не найдены данные", "errorCode": score_error()}
        )

    if user.password != user_form.password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"timestamp": datetime.now().timestamp(), "message" : "Не найдены данные", "errorCode": score_error()}
        )   
        
    payload = {
        "user_id": user.id,
        "iat" : int(datetime.now().timestamp()),
        "exp" : int((datetime.now() + timedelta(minutes=30)).timestamp())
    }     
        
    token = create_token(payload)
    return token

@app.get("/api/v1/Stuffs")
async def get_stuff(session: SessionDep, curent_user: dict= Depends(get_current_user)):
    result = await session.execute(select(StuffModel).options(
        selectinload(StuffModel.depart),
        selectinload(StuffModel.room),
        selectinload(StuffModel.post),
        ).order_by(StuffModel.id))
    stuff = result.scalars().all()
    
    return [
        StuffShema(
            id=s.id,
            name=s.name,
            phone= s.phone,    
            birthday=s.birthday,
            depart=s.depart.depart_name if s.depart else None,
            post=s.post.post_name if s.post else None,
            room= s.room.room_name if s.room else None,
            email = s.email,
            other_info= s.other_info
        )
        for s in stuff
    ]

@app.get("/api/v1/Stuff/trainings")
async def get_stuff_trainings(session: SessionDep, depart_id: int, current_user: dict = Depends(get_current_user)):
    query = select(TrainingModel).join(
        CalendarEventsModel, CalendarEventsModel.training_id == TrainingModel.id).join(
        StuffModel, CalendarEventsModel.stuff_id == StuffModel.id
    ).where(StuffModel.depart_id == depart_id)
    
    result = await session.execute(query)
    result = result.scalars().all()
    
    if result != []:
        return result
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"timestamp": datetime.now().timestamp(), "message" : "Данные не найдены", "errorCode": score_error()}
        )
        
@app.post("/api/v1/post_post")
async def add_new_post(session: SessionDep, post_data: PostAddShema, current_user: dict = Depends(get_current_user)):
    new_post = PostModel(post_name = post_data.name)
    
    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)
    return{"data added"}