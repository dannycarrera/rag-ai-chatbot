import datetime
import logging
from uuid import uuid4

from flask import Flask, jsonify, request
from langchain_core.language_models import LanguageModelLike
from langchain_redis import RedisVectorStore

from app.agents import ChatMessage
from app.agents.json_sales_agent import JsonSalesAgent
from app.config import get_passphrases
from app.url_processor import UrlProcessor

logging.basicConfig()
logger = logging.getLogger(__name__)


def register_endpoints(app: Flask, llm: LanguageModelLike, vector_store: RedisVectorStore) -> None:
    def __is_authorized(passphrase: str) -> bool:
        passphrases = get_passphrases()
        if passphrase in passphrases:
            return True
        return False

    @app.route("/api/heartbeat", methods=["GET"])
    def get_heartbeat() -> None:
        return jsonify({"server_time": datetime.datetime.now()})

    @app.route("/api/start_chat", methods=["POST"])
    async def post_start_chat() -> None:
        try:
            data = request.json
            logger.info({"data": data})
            passphrase = data.get("passphrase")
            if not __is_authorized(passphrase):
                logger.warning("Unauthorized request")
                return jsonify({"error": "Unauthorized access"}), 401

            # Scrape website
            url = data.get("url")
            urlProcessor = UrlProcessor(vector_store)
            hostname = await urlProcessor.processUrl(url)
            sales_agent = JsonSalesAgent(llm, vector_store)

            # Get initial ai message
            thread_id = str(uuid4())
            config = {"configurable": {"thread_id": thread_id}}
            init_result = await sales_agent.ainvoke(hostname, config, "")
            answer: ChatMessage = init_result["answer"]
            response = {"thread_id": thread_id, "message": answer.toDict()}
            json_result = jsonify(response)
        except Exception as e:
            if e.status_code and e.status_code == 429 and e.type == "insufficient_quota":
                logger.warning(e)
                return jsonify({"error": "Unauthorized access", "type": "insufficient_quota"}), 429
            else:
                logger.error(e)

        return json_result

    @app.route("/api/add_chat_message", methods=["POST"])
    async def post_add_chat_message() -> None:
        try:
            data = request.json
            logger.info({"data": data})
            passphrase = data.get("passphrase")
            if not __is_authorized(passphrase):
                logger.warning("Unauthorized request")
                return jsonify({"error": "Unauthorized access"}), 401

            hostname = data.get("hostname")
            thread_id = data.get("threadId")
            message = data.get("message")

            sales_agent = JsonSalesAgent(llm, vector_store)
            config = {"configurable": {"thread_id": thread_id}}
            result = await sales_agent.ainvoke(hostname, config, message)
            answer: ChatMessage = result["answer"]
            response = {"message": {"content": answer.content}}
            json_result = jsonify(response)
        except Exception as e:
            if e.status_code == 429 and e.type == "insufficient_quota":
                logger.warning(e)
                return jsonify({"error": "Unauthorized access", "type": "insufficient_quota"}), 429
            else:
                logger.error(e)

        return json_result
