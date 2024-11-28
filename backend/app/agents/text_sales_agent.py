from typing import Any, Dict, Union

import langchain
from langchain_core.language_models import LanguageModelLike
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_core.runnables import Runnable
from langchain_core.runnables.config import RunnableConfig
from langchain_redis import RedisVectorStore

from app.agents.base_sales_agent import BaseSalesAgent

from . import ChatState

langchain.debug = False

# These examples are not used in this agent. They were generated and used to populate
# the examples for json_sales_agent.py.
exmaple0 = """
Hi there! My name is Emily, and I'm so thrilled to have you shopping with us at HoloInvites today!

To help me find the perfect product or service for you, could you please tell me what type of 
occasion are you looking to celebrate with a special gift? Are you thinking of birthdays, holidays, 
or perhaps a milestone event?

A) Birthday
B) Holiday Season (Christmas, Hanukkah, etc.)
C) Graduation/ Achievement
D) Special Occasion (engagement, new baby, etc.)
"""
example1 = """
Hi there! My name is Alex, and I'm so excited to be your personal sales agent here at the Apple 
store today!

I'd love to help you find exactly what you're looking for. Can you tell me, are you in the market
for a new iPhone, an iPad, or maybe something else?

A) iPhone 16 Pro
B) iPad Air
C) AirPods 4
D) MacBook Air
"""
example2 = """
Hello and welcome to TWO MEN AND A TRUCK Canada! My name is Karen, and I'll be your sales agent
 today. We're thrilled to have you on our website!

To get started, can you tell me a little bit about what brings you here today? Are you planning a
move, looking for moving services, or perhaps considering storage options?

Please choose one of the following options:

A) I'm looking for local moving services
B) I need long-distance moving assistance
C) I want to pack and unpack my belongings
D) I have other questions about your services
"""

# Intro
intro_system_template = """
        You are a sales agent working for a website and your job
        is to help customer's find what they're looking for. Speak
        directly to the customer. You have an uplifting and energetic
        attitude.

        Start the conversation by first introducing yourself, be sure to
        include your name, and welcome the visitor to your store.
        
        Then in one sentence ask 1 question with 4 multiple choice options
        to determine what the I am looking for.

        Try to find relevant products or services to offer the customer.

        Use the following pieces of context:
       {context}
   """

intro_prompt = PromptTemplate(template=intro_system_template)

### Answer question ###
system_prompt = """
        You are a sales agent working for a website and your job
        is to help customer's find what they're looking for. Speak
        directly to the customer. You have an uplifting and energetic
        attitude.

        Try to find products, services or categories
        that the I am looking for. Use three sentences
        maximum and keep the answer concise.

        Use the following pieces of retrieved context to answer
        the question. If you don't know the answer, say that you
        don't know.
        "{context}"
    """
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)


class TextSalesAgent(BaseSalesAgent):
    """A SalesAgent that generates text responses.

    Init args:
        llm: The LLM to use.
        vector_store: The RedisVectorStore to use.
    """

    def __init__(self, llm: LanguageModelLike, vector_store: RedisVectorStore) -> None:
        super().__init__(llm, vector_store, intro_prompt, qa_prompt)

    def __call_model(
        self,
        intro_rag_chain: Runnable[Dict[str, Any], Any],
        rag_chain: Runnable[Dict[str, Any], Any],
        state: ChatState,
    ) -> dict[str, Any]:
        """Invoke the graph chain.

        Args:
            intro_rag_chain: The chain used to generate the introductory message.
            rag_chain: The chain used to generate subsequent responses to user inputs.
            state: The state of the conversation.
        """
        # # Check if chat history is empty to send the first AI message
        if not state["chat_history"]:
            init_state = ChatState(input="placeholder")
            initial_response = intro_rag_chain.invoke(init_state)
            return {
                "chat_history": [
                    AIMessage(initial_response["answer"]),
                ],
                "context": initial_response["context"],
                "answer": initial_response["answer"],
            }

        # Normal flow if chat history is present
        response = rag_chain.invoke(state)
        return {
            "chat_history": [
                HumanMessage(state["input"]),
                AIMessage(response["answer"]),
            ],
            "context": response["context"],
            "answer": response["answer"],
        }

    async def ainvoke(
        self, hostname: str, config: RunnableConfig, input: str
    ) -> Union[dict[str, Any], Any]:  # noqa: ANN401
        return await super(TextSalesAgent, self)._ainvoke(
            hostname, config, self.__call_model, input
        )
