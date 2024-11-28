from uuid import uuid4

from langchain_redis import RedisVectorStore

from app.agents.text_sales_agent import TextSalesAgent
from app.url_processor import UrlProcessor
from tests.conftest import llm


async def test_ainvoke(async_reset_dbs: RedisVectorStore) -> None:
    vector_store = async_reset_dbs

    hostname = "holoinvites.com"

    urlProcessor = UrlProcessor(vector_store)
    await urlProcessor.processUrl(hostname)

    sales_agent = TextSalesAgent(llm, vector_store)
    config = {"configurable": {"thread_id": str(uuid4())}}
    intro_result = await sales_agent.ainvoke(hostname, config, "")
    intro = intro_result["answer"]
    assert intro

    second_result = await sales_agent.ainvoke(hostname, config, "Lets go with B")
    second_message = second_result["answer"]
    assert second_message
