from typing import Dict, List, Optional, Sequence

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing_extensions import Annotated, TypedDict


class ChatMessage(BaseModel):
    """A chat message with multiple choice options if available"""

    content: str = Field(description="the message content")
    mc_options: Optional[List[str]] = Field(
        default=None,
        description="Possible answers for a multiple choice question",
    )

    def toJson(self) -> str:
        return self.model_dump_json(exclude_none=True)

    def toDict(self) -> Dict[str, object]:
        return {"content": self.content, "mc_options": self.mc_options}


### Statefully manage chat history ###
class ChatState(TypedDict):
    input: str
    chat_history: Annotated[Sequence[BaseMessage], add_messages]
    context: str
    answer: ChatMessage
