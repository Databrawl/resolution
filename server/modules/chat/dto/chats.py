from enum import Enum
from typing import List, Optional, Tuple, Union
from uuid import UUID

from pydantic import BaseModel

from modules.chat.dto.outputs import GetChatHistoryOutput
from modules.notification.entity.notification import Notification


class ChatMessage(BaseModel):
    model: str
    question: str
    # A list of tuples where each tuple is (speaker, text)
    history: List[Tuple[str, str]]
    temperature: float = 0.0
    max_tokens: int = 256
    use_summarization: bool = False
    chat_id: Optional[UUID] = None
    chat_name: Optional[str] = None


class ChatQuestion(BaseModel):
    question: str
    model: Optional[str]
    temperature: Optional[float]
    max_tokens: Optional[int]
    brain_id: Optional[UUID]
    prompt_id: Optional[UUID]


class ChatItemType(Enum):
    MESSAGE = "MESSAGE"
    NOTIFICATION = "NOTIFICATION"


class ChatItem(BaseModel):
    item_type: ChatItemType
    body: Union[GetChatHistoryOutput, Notification]
