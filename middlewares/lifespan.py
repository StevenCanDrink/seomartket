from contextlib import asynccontextmanager
from fastapi import FastAPI
from pymongo import AsyncMongoClient
from beanie import init_beanie
import model.index as model
from model.user import User
from auth.supabase import close_clients, get_client
import os


async def initiate_database_mongo():
    client = AsyncMongoClient(os.getenv("MONGO_URL"))
    await init_beanie(database=client.user_manage, document_models=model.__all__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Startup code
    get_client(use_anon_key=False)
    get_client(use_anon_key=True)
    print("supabase installed")
    # print("mongo-bunnycdn-jwt installed")
    # async for user in User.find_all():
    #     print(user)
    yield
    close_clients()
    # Shutdown / cleanup code
