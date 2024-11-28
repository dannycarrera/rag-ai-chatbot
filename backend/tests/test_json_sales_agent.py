from uuid import uuid4

from langchain_redis import RedisVectorStore

from app.agents import ChatMessage
from app.agents.json_sales_agent import JsonSalesAgent
from app.url_processor import UrlProcessor
from tests.conftest import llm


async def test_initiate_chat_and_add_message(async_reset_dbs: RedisVectorStore) -> None:
    vector_store = async_reset_dbs

    hostname = "holoinvites.com"

    urlProcessor = UrlProcessor(vector_store)
    await urlProcessor.processUrl(hostname)

    sales_agent = JsonSalesAgent(llm, vector_store)

    config = {"configurable": {"thread_id": str(uuid4())}}
    intro_result = await sales_agent.ainvoke(hostname, config, "")
    intro_context: list = intro_result["context"]
    for document in intro_context:
        assert document.metadata["hostname"] == hostname

    intro: ChatMessage = intro_result["answer"]
    assert intro.content
    assert intro.mc_options
    assert intro.mc_options[0]
    assert intro.mc_options[1]
    assert intro.mc_options[2]
    assert intro.mc_options[3]

    second_result = await sales_agent.ainvoke(hostname, config, "Lets go with B")
    second_context: list = intro_result["context"]
    for document in second_context:
        assert document.metadata["hostname"] == hostname
    second_message: ChatMessage = second_result["answer"]
    assert second_message.content
