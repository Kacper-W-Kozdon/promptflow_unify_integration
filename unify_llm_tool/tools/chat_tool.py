from typing import Any, Optional, Union

from promptflow.client import PFClient
from promptflow.connections import CustomConnection
from promptflow.core import tool
from unify_llm_tool.tools.single_sign_on_tool import UnifyConnection
from unify_llm_tool.tools.unifypf import chat

pf = PFClient()


@tool
def basic_chat(
    connection: Union[CustomConnection, UnifyConnection],
    prompt: str = "Hello.",
    chat_history: Optional[list] = [],
    **kwargs: Any,
) -> str:
    """
    Basic chat tool for custom connections and endpoints.

    :param: connection: Custom connection to use for chatting.
    :type connection: CustomConnection
    :param prompt: Input message for the chat tool.
    :type prompt: string
    :param chat_history: History of the chat.
    :type chat_history: list
    """

    return chat(connection=connection, prompt=prompt, chat_history=chat_history)
