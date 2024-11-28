import redis
from langchain_redis import RedisVectorStore

from app.config import get_redis_config
from app.db.schema import WebSite
from app.url_processor import UrlProcessor
from tests.conftest import async_reset_dbs_fn

redis_config = get_redis_config()
redis_client = redis.Redis.from_url(redis_config.redis_url)



async def test_processUrl_hostname_only(async_reset_dbs: RedisVectorStore) -> None:
    vector_store = async_reset_dbs
    urlProcessor = UrlProcessor(vector_store)
    hostname = "holoinvites.com"
    await urlProcessor.processUrl(hostname)
    website = WebSite.get_or_none(WebSite.hostname == hostname)
    assert website
    assert redis_client.dbsize() == 1



async def test_processUrl_hostname_not_root(async_reset_dbs: RedisVectorStore) -> None:
    vector_store = async_reset_dbs
    urlProcessor = UrlProcessor(vector_store)
    url = "holoinvites.com/about-us"
    await urlProcessor.processUrl(url)
    website = WebSite.get_or_none(WebSite.hostname == "holoinvites.com")
    assert website
    assert redis_client.dbsize() == 1



async def test_processUrl(async_reset_dbs: RedisVectorStore) -> None:
    vector_store = async_reset_dbs
    urlProcessor = UrlProcessor(vector_store)
    url = "https://holoinvites.com"
    await urlProcessor.processUrl(url)
    website = WebSite.get_or_none(WebSite.base_url == url)
    assert website
    assert redis_client.dbsize() == 1



async def test_processUrl_not_root(async_reset_dbs: RedisVectorStore) -> None:
    vector_store = async_reset_dbs
    urlProcessor = UrlProcessor(vector_store)
    url = "https://holoinvites.com/about-us"
    await urlProcessor.processUrl(url)
    website = WebSite.get_or_none(WebSite.hostname == "holoinvites.com")
    assert website
    assert redis_client.dbsize() == 1



async def test_processUrl_multiple_sites(async_reset_dbs: RedisVectorStore) -> None:
    vector_store = async_reset_dbs
    urlProcessor = UrlProcessor(vector_store)

    url = "https://holoinvites.com"
    await urlProcessor.processUrl(url)
    website = WebSite.get_or_none(WebSite.base_url == url)
    assert website

    url = "https://twomenandatruck.ca"
    await urlProcessor.processUrl(url)
    website = WebSite.get_or_none(WebSite.base_url == url)
    assert website

    urlProcessor = UrlProcessor(vector_store)
    url = "https://apple.com"
    await urlProcessor.processUrl(url)
    website = WebSite.get_or_none(WebSite.base_url == url)
    assert website

    all_keys = redis_client.keys("*")
    assert len(all_keys) == 3
    for key in all_keys:
        vals = redis_client.hgetall(key)
        hostname_value = vals.get(b"hostname")
        decoded_hostname = hostname_value.decode("utf-8")
        match decoded_hostname:
            case "holoinvites.com":
                holoinvites_found = True
            case "twomenandatruck.ca":
                twomenandatruck = True
            case "apple.com":
                apple = True
            case _:
                raise "Unknown hostname"
    assert holoinvites_found is True
    assert twomenandatruck is True
    assert apple is True



async def test_processUrl_multiple_pages_same_site(async_reset_dbs: RedisVectorStore) -> None:
    vector_store = async_reset_dbs
    urlProcessor = UrlProcessor(vector_store)
    hostname = "holoinvites.com"
    url = f"https://{hostname}"
    await urlProcessor.processUrl(url, 2)
    website = WebSite.get_or_none(WebSite.base_url == url)
    assert website

    all_keys = redis_client.keys("*")
    assert len(all_keys) > 1
    for key in all_keys:
        vals = redis_client.hgetall(key)
        hostname_value = vals.get(b"hostname")
        decoded_hostname = hostname_value.decode("utf-8")
        assert decoded_hostname == hostname
    
    # Reset again. llama begins struggling to output json result when
    # multiple pages are scraped. This is usually last test to run and 
    # can cause infinite loop when trying to parse the response.
    await async_reset_dbs_fn()