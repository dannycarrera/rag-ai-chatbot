import asyncio
import logging
import os
import platform

import pytest_asyncio
from langchain_redis import RedisVectorStore
from psycopg2.errors import DuplicateDatabase

from app.config import get_config, get_llm_config, get_redis_config
from app.db.db_manager import DbManager

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

config = get_config()
is_debug = config["IS_DEBUG"]
llm_config = get_llm_config()

log_path = os.path.join(config["LOG_FOLDER"], "tests.log")
logging.basicConfig(
    level=(logging.DEBUG if is_debug else logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(log_path), logging.StreamHandler()],
)

if llm_config.llm == "llama":
    from langchain_ollama import ChatOllama, OllamaEmbeddings

    llm = ChatOllama(model="llama3.2", base_url=llm_config.url)
    embeddings = OllamaEmbeddings(model="llama3.2")
elif llm_config.llm == "openai":
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings

    llm = ChatOpenAI(model="gpt-4o-mini", api_key=llm_config.api_secret_key)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=llm_config.api_secret_key)
else:
    raise ValueError("Unsupported llm type")


db_manager = DbManager()

# Make sure db and tables are created
try:
    db_manager.create_db()
except DuplicateDatabase:
    pass
asyncio.run(db_manager.setup_db())

redis_config = get_redis_config()
vector_store = RedisVectorStore(embeddings, config=redis_config)

async def async_reset_dbs_fn() -> RedisVectorStore:
    await db_manager.reset_dbs()
    redis_config = get_redis_config()
    vector_store = RedisVectorStore(embeddings, config=redis_config)
    return vector_store

@pytest_asyncio.fixture
async def async_reset_dbs() -> RedisVectorStore:
    return await async_reset_dbs_fn()
