import os
from typing import Any

from dotenv import load_dotenv
from langchain_redis import RedisConfig

load_dotenv()

# Check for required env vars
postgres_db = os.getenv("POSTGRES_DB")
if not postgres_db or postgres_db == "":
    raise ValueError("POSTGRES_DB environment variable is missing")
postgres_user = os.getenv("POSTGRES_USER")
if not postgres_user or postgres_user == "":
    raise ValueError("POSTGRES_USER environment variable is missing")
postgres_password = os.getenv("POSTGRES_PASSWORD")
if not postgres_password or postgres_password == "":
    raise ValueError("POSTGRES_PASSWORD environment variable is missing")

psql_host = os.getenv("PSQL_HOST")
if not psql_host or psql_host == "":
    raise ValueError("PSQL_HOST environment variable is missing")
psql_port = os.getenv("PSQL_PORT")
if not psql_port or psql_port == "":
    raise ValueError("PSQL_PORT environment variable is missing")
psql_admin_db_url = os.getenv("PSQL_ADMIN_DB_URL")
if not psql_admin_db_url or psql_admin_db_url == "":
    raise ValueError("PSQL_ADMIN_DB_URL environment variable is missing")
psql_db_name = os.getenv("PSQL_DB_NAME")
if not psql_db_name or psql_db_name == "":
    raise ValueError("PSQL_DB_NAME environment variable is missing")
psql_db_url = os.getenv("PSQL_DB_URL")
if not psql_db_url or psql_db_url == "":
    raise ValueError("PSQL_DB_URL environment variable is missing")

redis_url = os.getenv("REDIS_URL")
if not redis_url or redis_url == "":
    raise ValueError("REDIS_URL environment variable is missing")

llm = os.getenv("LLM")
if llm not in ["llama", "openai"]:
    raise ValueError("Valid options for the LLM environment variable are llama or openai")
llm_api_key = os.getenv("LLM_API_KEY")
if llm == "openai" and (not llm_api_key or llm_api_key == ""):
    raise ValueError("LLM is set to 'openai' but LLM_API_KEY environment variable is missing")

# Create config dict
config = {
    "POSTGRES_DB": postgres_db,
    "POSTGRES_USER": postgres_user,
    "POSTGRES_PASSWORD": postgres_password,
    "PSQL_HOST": psql_host,
    "PSQL_PORT": psql_port,
    "PSQL_ADMIN_DB_URL": psql_admin_db_url,
    "PSQL_DB_NAME": psql_db_name,
    "PSQL_DB_URL": psql_db_url,
    "REDIS_URL": redis_url,
    "LLM": llm,
    "LLM_URL": os.getenv("LLM_URL"),
    "LLM_API_KEY": llm_api_key,
    "HOST": os.getenv("HOST", "0.0.0.0"),
    "PORT": os.getenv("PORT", 5555),
    "URL_RECURSIVE_MAX_DEPTH": int(os.getenv("URL_RECURSIVE_MAX_DEPTH", 1)),
    "PASSPHRASES": os.getenv("PASSPHRASES", "").split(","),
    "LOG_FOLDER": os.getenv("LOG_FOLDER", "_logs"),
    "IS_DEBUG": os.getenv("IS_DEBUG", False) in ["1", "True", "true"],
}

DEFAULTS = {
    "HOST": "localhsot",
    "PORT": 5555,
    "URL_RECURSIVE_MAX_DEPTH": 1,
    "LOG_FOLDER": "_logs",
    "IS_DEBUG": False,
}

# apply defaults for missing config params
for key in DEFAULTS:
    if key not in config or config[key] is None:
        config[key] = DEFAULTS[key]

# check if log folder exists
if not os.path.isdir(config["LOG_FOLDER"]):
    os.mkdir(config["LOG_FOLDER"])


def get_config() -> dict[str, Any]:
    return config


# Config classes
class PSqlAdminConfig:
    def __init__(
        self, host: str, port: int, user: str, password: str, db_name: str, url: str
    ) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name
        self.url = url


class FlaskConfig:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port


class LlmConfig:
    def __init__(self, llm: str, url: str | None, api_secret_key: str | None) -> None:
        self.llm = llm
        self.url = url
        self.api_secret_key = api_secret_key


# Getters
def get_psql_admin_config() -> PSqlAdminConfig:
    psql_admin_config = PSqlAdminConfig(
        host=config["PSQL_HOST"],
        port=config["PSQL_PORT"],
        user=config["POSTGRES_USER"],
        password=config["POSTGRES_PASSWORD"],
        db_name=config["POSTGRES_DB"],
        url=config["PSQL_ADMIN_DB_URL"],
    )
    return psql_admin_config


def get_psql_db_name() -> str:
    return config["PSQL_DB_NAME"]


def get_psql_url() -> str:
    return config["PSQL_DB_URL"]


def get_redis_url() -> str:
    return config["REDIS_URL"]


def get_redis_config() -> RedisConfig:
    redis_config = RedisConfig(
        index_name="website",
        redis_url=config["REDIS_URL"],
        # from_existing=True,
        metadata_schema=[
            {
                "name": "source",
                "type": "text",
            },
            {
                "name": "hostname",
                "type": "tag",
            },
        ],
    )
    return redis_config


def get_llm_config() -> LlmConfig:
    llm_config = LlmConfig(
        llm=config["LLM"],
        url=config["LLM_URL"],
        api_secret_key=config["LLM_API_KEY"],
    )
    return llm_config


def get_flask_config() -> FlaskConfig:
    flask_config = FlaskConfig(host=config["HOST"], port=config["PORT"])
    return flask_config


def get_passphrases() -> bool:
    return config["PASSPHRASES"]


def get_log_folder() -> str:
    return config["LOG_FOLDER"]


def is_debug() -> bool:
    return config["IS_DEBUG"]
