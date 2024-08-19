import os
from typing import Dict, List, Optional, Union

import unify
import unify.clients
from dotenv import load_dotenv
from unify import Unify

from promptflow._constants import ConnectionType
from promptflow.client import PFClient
from promptflow.connections import CustomConnection
from promptflow.contracts.types import Secret
from promptflow.core import tool

# Get a pf client to manage connections
pf = PFClient()


class UnifyClient(Unify):
    """Unify client.

    :param configs: The configs kv pairs.
    :type configs: Dict[str, str]
    :param secrets: The secrets kv pairs.
    :type secrets: Dict[str, str]
    :param name: Connection name
    :type name: str
    """

    def __init__(self, configs: dict = None, secrets: dict = None, **kwargs: dict):
        load_dotenv()
        api_key = (
            secrets.get("api_key")
            or kwargs.get("api_key")
            or configs.get("api_key")
            or os.getenv("UNIFY_API_KEY")
            or os.getenv("UNIFY_KEY")
        )
        endpoint = secrets.get("endpoint") or kwargs.get("endpoint") or configs.get("endpoint")
        model = secrets.get("model") or kwargs.get("model") or configs.get("model")
        provider = secrets.get("provider") or kwargs.get("provider") or configs.get("provider")
        super().__init__(endpoint=endpoint, model=model, provider=provider, api_key=api_key)


unify.clients.Unify = UnifyClient


# Unify client as the connection is a temporary solution before the final approach is chosen (CustomConnection?)

unify_connection_name: str = "unify_connection"


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

    api_key: Secret
    api_base: str = "https://api.unify.ai/v0"

    _default_endpoint: str = "gpt-4o@openai"

    TYPE = ConnectionType.CUSTOM.value
    _Connection_configs: Dict[str, str] = {
        "name": unify_connection_name,
        "module": "unify.clients",
        "type": "CustomConnection",
        "custom_type": "UnifyConnection",
        "package": "unify_integration",
    }

    _strong_configs: Dict[str, str] = {
        "api_base": "https://api.unify.ai/v0",
        "endpoint": "<user-input>",
        "model": "<user-input>",
        "provider": "<user-input>",
    }

    _strong_secrets: Dict[str, str] = {
        "unify_api_key": "<user-input>",
    }

    def __init__(
        self,
        secrets: Optional[Dict[str, str]] = None,
        configs: Optional[Dict[str, str]] = None,
        **kwargs: dict,
    ):
        self.connection_instance: Union[None, Unify] = Unify(endpoint=self._default_endpoint)
        if not secrets:
            _configs = {**self._strong_configs, **self._Connection_configs}
            super().__init__(secrets=self._strong_secrets, configs=_configs)
            self.convert_to_strong_type()
        else:
            if not configs:
                configs = {"api_base": "https://api.unify.ai/v0", "endpoint": self._default_endpoint}
            configs = {**self._Connection_configs, **configs}
            super().__init__(secrets=secrets, configs=configs, **kwargs)

    def convert_to_strong_type(self) -> Unify:
        """
        Creates an instance of Unify client.

        """

        module = self._Connection_configs.get("module")
        name = self._Connection_configs.get("name")
        self.connection_instance = self._convert_to_custom_strong_type(module=module, to_class=name)
        return self.connection_instance


def create_strong_unify_connection() -> Union[Unify, UnifyConnection]:
    """
    Creates a strong type connection for Unify
    """
    strong_unify_connection: Union[UnifyConnection, None] = None
    if unify_connection_name not in pf.connections.list():
        strong_unify_connection = UnifyConnection()
        pf.connections.create_or_update(strong_unify_connection)
    return strong_unify_connection


def list_endpoints(model: Optional[str], provider: Optional[str], api_key: Optional[str]) -> List[str]:
    """
    Lists endpoints available through Unify.

    :param model: If provided, filters the list of endpoints for the ones using the provided model.
    :type param: str
    :param provider: If provided, filters the list of endpoints for the ones using the provider.
    :type provider: str
    :param api_key: Unify API key
    :type api_key: str
    """
    try:
        return unify.list_endpoints(model=model, provider=provider, api_key=api_key)
    except ValueError:
        return unify.list_endpoints(model=model)


def list_models(provider: Optional[str], api_key: Optional[str]) -> List[str]:
    """
    Lists models available through Unify.

    :param provider: Provider for which to generate the list of the available models.
    :type provider: str
    :param api_key:
    :type api_key: str
    """
    try:
        return unify.list_models(provider=provider, api_key=api_key)
    except ValueError:
        return unify.list_models()


def list_providers(model: Optional[str], api_key: Optional[str]) -> List[str]:
    """
    Lists providers available through Unify.

    :param model: Model for which to generate the list of the available providers.
    :type provider: str
    :param api_key:
    :type api_key: str
    """
    try:
        return unify.list_providers(model=model, api_key=api_key)
    except ValueError:
        return unify.list_providers(model=model)


@tool
def single_sign_on(
    endpoint: Optional[str],
    model: Optional[str],
    provider: Optional[str],
    router: Optional[str],
    unify_api_key: Secret,
) -> Unify:
    """Unify connection tool.

    :param endpoint: The endpoint to use.
    :type endpoint: str
    :param model: The model to use.
    :type model: str
    :param provider: The provider from the list of providers available for the model.
    :type provider: str
    :param unify_api_key: The Unify API key
    """

    new_endpoint = endpoint or router or f"{model}@{provider}"

    configs: Dict[str, str] = {
        "endpoint": new_endpoint,
    }

    # Create the connection, note that all secret values will be scrubbed in the returned result
    connection = UnifyConnection(secrets={"api_key": unify_api_key}, configs=configs)
    pf.connections.create_or_update(connection)

    return connection
