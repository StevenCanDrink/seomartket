from contextlib import asynccontextmanager
from fastapi import FastAPI
from pymongo import AsyncMongoClient
from beanie import init_beanie
import model.index as model
from model.user import User
import os


async def initiate_database():
    client = AsyncMongoClient(os.getenv("MONGO_URL"))
    await init_beanie(database=client.user_manage, document_models=model.__all__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Startup code
    await initiate_database()

    print("mongo-bunnycdn-jwt installed")
    # async for user in User.find_all():
    #     print(user)
    yield
    # Shutdown / cleanup code
