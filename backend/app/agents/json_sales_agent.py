import logging
from typing import Any, Dict, Union

import langchain
from langchain_core.language_models import LanguageModelLike
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from langchain_core.runnables import Runnable
from langchain_core.runnables.config import RunnableConfig
from langchain_redis import RedisVectorStore

from app.agents.base_sales_agent import BaseSalesAgent

from . import ChatMessage, ChatState

logger = logging.getLogger(__name__)
langchain.debug = False

# Intro Prefix
intro_prefix = """
    You are a sales agent working for a website and your job
    is to help customer's find what they're looking for. Speak
    directly to the customer. You have an uplifting and energetic
    attitude.

    Start the conversation by first introducing yourself, be sure to
    include your name, and welcome the visitor to your store.

    Then in one sentence ask 1 question with 4 multiple choice options
    to determine what the I am looking for.

    Try to find relevant products or services to offer the customer.

    ### Format Response
    {format_instructions}

    Make sure the entire response fits inside the JSON object. Do not
    repeat the options in the content field.

    Here are some example responses:
"""

# Intro Examples
intro_exmaple0 = {
    "content": "Hi there! My name is Emily, and I'm so thrilled to have you shopping with us at "
    "HoloInvites today!\n\n"
    "To help me find the perfect product or service for you, could you please tell me what type of "
    "occasion are you looking to celebrate with a special gift? Are you thinking of birthdays, "
    "holidays, or perhaps a milestone event?",
    "mc_options": [
        "A) Birthday",
        "B) Holiday Season (Christmas, Hanukkah, etc.)",
        "C) Graduation/ Achievement",
        "D) Special Occasion (engagement, new baby, etc.)",
    ],
}

intro_exmaple1 = {
    "content": "Hi there! My name is Alex, and I'm so excited to be your personal sales agent here "
    "at the Apple store today!\n\n"
    "I'd love to help you find exactly what you're looking for. Can you tell me, are you in the "
    "market for a new iPhone, an iPad, or maybe something else?",
    "mc_options": ["A) iPhone 16 Pro", "B) iPad Air)", "C) AirPods 4", "D) MacBook Air"],
}

intro_exmaple2 = {
    "content": "Hello and welcome to TWO MEN AND A TRUCK Canada! My name is Karen, and I'll be "
    "your sales agent today. We're thrilled to have you on our website!\n\n"
    "To get started, can you tell me a little bit about what brings you here today? Are you "
    "planning a move, looking for moving services, or perhaps considering storage options?\n\n"
    "Please choose one of the following options:",
    "mc_options": [
        "A) I'm looking for local moving services",
        "B) I need long-distance moving assistance",
        "C) I want to pack and unpack my belongings",
        "D) I have other questions about your services",
    ],
}
intro_examples = [
    {"example": f"{{{intro_exmaple0}}}"},
    {"example": f"{{{intro_exmaple1}}}"},
    {"example": f"{{{intro_exmaple2}}}"},
]

example_template = "Example: {example}"
intro_example_prompt = PromptTemplate(input_variables=["example"], template=example_template)

# Intro Suffix
intro_suffix = """
    ### Contextualize
    Use the following pieces of context: \n{context}"""

output_parser = PydanticOutputParser(pydantic_object=ChatMessage)

intro_few_shot_prompt = FewShotPromptTemplate(
    examples=intro_examples,
    example_prompt=intro_example_prompt,
    prefix=intro_prefix,
    suffix=intro_suffix,
    partial_variables={"format_instructions": output_parser.get_format_instructions()},
)

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

# How many multiple choice options
MC_OPTION_LENGTH = 4


class JsonSalesAgent(BaseSalesAgent):
    """A SalesAgent that generates JSON responses.

    Init args:
        llm: The LLM to use.
        vector_store: The RedisVectorStore to use
    """

    def __init__(self, llm: LanguageModelLike, vector_store: RedisVectorStore) -> None:
        super().__init__(llm, vector_store, intro_few_shot_prompt, qa_prompt)

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
        json_result = None
        # Check if chat history is empty to send the first AI message
        if not state["chat_history"]:
            init_state = ChatState(input="placeholder")
            while json_result is None:
                try:
                    initial_response = intro_rag_chain.invoke(init_state)

                    # try parsing json and ensure 4 options
                    temp_result = output_parser.parse(initial_response["answer"])
                    if temp_result.mc_options and len(temp_result.mc_options) == MC_OPTION_LENGTH:
                        json_result = temp_result
                except Exception as e:
                    logger.warning(e)

            return {
                "chat_history": [
                    AIMessage(initial_response["answer"]),
                ],
                "context": initial_response["context"],
                "answer": json_result,
            }

        # Normal flow if chat history is present
        response = rag_chain.invoke(state)

        return {
            "chat_history": [
                HumanMessage(state["input"]),
                AIMessage(response["answer"]),
            ],
            "context": response["context"],
            "answer": ChatMessage(content=response["answer"]),
        }

    async def ainvoke(
        self, hostname: str, config: RunnableConfig, input: str
    ) -> Union[dict[str, Any], Any]:  # noqa: ANN401
        return await super(JsonSalesAgent, self)._ainvoke(
            hostname, config, self.__call_model, input
        )
