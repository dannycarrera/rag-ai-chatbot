from typing import Any, Callable, Union

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.language_models import LanguageModelLike
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_core.runnables.config import RunnableConfig
from langchain_redis import RedisVectorStore
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import START, StateGraph
from redisvl.query.filter import Tag

from app.config import get_psql_url

from . import ChatState

### Contextualize question ###
contextualize_q_system_prompt = """
        Given a chat history and the latest user question
        which might reference context in the chat history,
        formulate a standalone question which can be understood
        without the chat history. Do NOT answer the question,
        just reformulate it if needed and otherwise return it as is.
    """
contextualize_chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)


class BaseSalesAgent:
    """The base class to create SalesAgents.

    Init args:
        llm: The LLM to use.
        vector_store: The RedisVectorStore to use.
        intro_prompt: The prompt to use for the AI introductory message.
        qa_prompt: The prompt to use for subsequent responses to human inputs.
    """
    def __init__(
        self,
        llm: LanguageModelLike,
        vector_store: RedisVectorStore,
        intro_prompt: PromptTemplate,
        qa_prompt: ChatPromptTemplate,
    ) -> None:
        self.llm = llm
        self.vector_store = vector_store
        self.intro_prompt = intro_prompt
        self.qa_prompt = qa_prompt

    async def _ainvoke(
        self,
        hostname: str,
        config: RunnableConfig,
        call_model: Callable[[ChatState], dict[str, Any]],
        input: str,
    ) -> Union[dict[str, Any], Any]:  # noqa: ANN401
        """Asynchronously create and invoke the graph.
        
        Args:
            hostname: The hostname of the url. Used to filter the vector store.
            config: The configuration for the graph.
            call_model: The function to call.
            input: The user's input.
        """
        # Retriever
        filter = Tag("hostname") == hostname
        retriever = self.vector_store.as_retriever(search_kwargs={"filter": filter})

        # Intro RAG Chain
        intro_chain = create_stuff_documents_chain(self.llm, self.intro_prompt)
        intro_rag_chain = create_retrieval_chain(retriever, intro_chain)

        history_aware_retriever = create_history_aware_retriever(
            self.llm, retriever, contextualize_chat_prompt
        )
        question_answer_chain = create_stuff_documents_chain(self.llm, self.qa_prompt)

        # QA RAG Chain
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        workflow = StateGraph(state_schema=ChatState)
        workflow.add_edge(START, "model")
        workflow.add_node("model", lambda state: call_model(intro_rag_chain, rag_chain, state))

        async with AsyncPostgresSaver.from_conn_string(get_psql_url()) as checkpointer:
            self.app = workflow.compile(checkpointer=checkpointer)

            result = await self.app.ainvoke(
                {"input": input},
                config=config,
            )
            return result
