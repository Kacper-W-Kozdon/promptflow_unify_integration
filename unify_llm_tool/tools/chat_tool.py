from typing import Union

from unify import Unify

from promptflow.client import PFClient
from promptflow.connections import CustomConnection
from promptflow.contracts.types import Secret  # noqa: F401
from promptflow.core import tool
from unify_llm_tool.tools.single_sign_on_tool import UnifyConnection, single_sign_on  # noqa: F401

pf = PFClient()


@tool
def basic_chat(connection: Union[CustomConnection, UnifyConnection, Unify]) -> str:
    """
    Basic chat tool for custom connections and endpoints.

    :param: connection: Custom connection to use for chatting.
    :type connection: CustomConnection
    :param message: Input message for the chat tool.
    :type message: string
    :param chat_history: History of the chat.
    :type chat_history: list
    """

    ret: str = ""
    return ret
