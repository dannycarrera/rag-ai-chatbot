import asyncio
import logging
import os
import platform

from flask import Flask
from flask_cors import CORS
from langchain_redis import RedisVectorStore
from psycopg2.errors import DuplicateDatabase

import app.routes as routes
from app.config import get_config, get_flask_config, get_llm_config, get_redis_config
from app.db.db_manager import DbManager

# Config
config = get_config()
is_debug = config["IS_DEBUG"]
llm_config = get_llm_config()
flask_config = get_flask_config()

# Logging
log_path = os.path.join(config["LOG_FOLDER"], "log.log")
logging.basicConfig(
    level=(logging.DEBUG if is_debug else logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(log_path), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


async def async_main() -> None:
    app = Flask(__name__)
    CORS(app)

    # LLM
    llm = None
    embeddings = None
    if llm_config.llm == "llama":
        from langchain_ollama import ChatOllama, OllamaEmbeddings

        llm = ChatOllama(model="llama3.2", base_url=llm_config.url)
        embeddings = OllamaEmbeddings(model="llama3.2", base_url=llm_config.url)
    elif llm_config.llm == "openai":
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings

        llm = ChatOpenAI(model="gpt-4o-mini", api_key=llm_config.api_secret_key)
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large", api_key=llm_config.api_secret_key
        )
    else:
        raise ValueError("Unsupported llm type")

    # PSQL Setup
    with DbManager() as db_manager:
        try:
            db_manager.create_db()
        except DuplicateDatabase:
            pass
        except Exception as e:
            logger.error(e)

        try:
            await db_manager.setup_db()
        except Exception as e:
            logger.error(e)

        # Redis setup
        redis_config = get_redis_config()
        vector_store = RedisVectorStore(embeddings, config=redis_config)

        # Start flask
        try:
            routes.register_endpoints(app, llm, vector_store)
            app.run(host=flask_config.host, port=flask_config.port, debug=is_debug)
        except Exception as e:
            logger.error(e)


def main() -> None:
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    main()
