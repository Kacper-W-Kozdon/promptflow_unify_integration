from typing import Dict, Optional

import unify.clients
from unify import Unify

from promptflow._constants import ConnectionType
from promptflow.connections import CustomConnection
from promptflow.core import tool


class UnifyClient(Unify):
    """Unify client.

    :param configs: The configs kv pairs.
    :type configs: Dict[str, str]
    :param secrets: The secrets kv pairs.
    :type secrets: Dict[str, str]
    :param name: Connection name
    :type nam
    """

    def __init__(self, configs: dict = None, secrets: dict = None, **kwargs: dict):
        api_key = secrets.get("api_key") or kwargs.get("api_key") or configs.get("api_key")
        endpoint = secrets.get("endpoint") or kwargs.get("endpoint") or configs.get("endpoint")
        model = secrets.get("model") or kwargs.get("model") or configs.get("model")
        provider = secrets.get("provider") or kwargs.get("provider") or configs.get("provider")
        super().__init__(endpoint=endpoint, model=model, provider=provider, api_key=api_key)


unify.clients.Unify = UnifyClient


# Unify client as the connection is a temporary solution before the final approach is chosen (CustomConnection?)


class UnifyConnection(CustomConnection):
    """Unify connection.

    :param configs: The configs kv pairs.
    :type configs: Dict[str, str]
    :param secrets: The secrets kv pairs.
    :type secrets: Dict[str, str]
    :param name: Connection name
    :type name: str
    :param kwargs: Additional keyword arguments
    :type kwargs: dict
    """

    TYPE = ConnectionType.CUSTOM.value
    _Connection_kwargs: dict = {
        "name": "UnifyConnection",
        "module": "unify.clients",
        "type": "Custom",
    }

    def __init__(
        self,
        secrets: Dict[str, str],
        configs: Optional[Dict[str, str]],
        **kwargs: dict,
    ):

        kwargs = {**kwargs, **self._Connection_kwargs}
        super().__init__(secrets=secrets, configs=configs, **kwargs)

    def connect(self) -> Unify:
        """
        Creates an instance of Unify client.

        """

        module = self._Connection_kwargs.get("module")
        name = self._Connection_kwargs.get("name")
        return self._convert_to_custom_strong_type(module=module, to_class=name)


@tool
def single_sign_on(configs: Optional[Dict[str, str]], secrets: Dict[str, str]) -> UnifyConnection:
    """Unify connection tool.

    :param configs: The configs kv pairs.
    :type configs: Dict[str, str]
    :param secrets: The secrets kv pairs.
    :type secrets: Dict[str, str]
    """
    connection = UnifyConnection(secrets=secrets, configs=configs)
    connection_instance = connection.connect()

    return connection_instance
