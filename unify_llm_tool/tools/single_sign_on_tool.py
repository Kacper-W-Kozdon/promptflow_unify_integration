import json
import os
from typing import Any, Dict, List, Optional, Union

import unify
import unify.clients
from dotenv import load_dotenv
from unify import Unify

from promptflow._constants import ConnectionType
from promptflow.client import PFClient
from promptflow.connections import CustomConnection
from promptflow.contracts.types import Secret
from promptflow.core import tool
from promptflow.entities import OpenAIConnection

# Get a pf client to manage connections
pf = PFClient()
load_dotenv()


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
            secrets.get("unify_api_key")
            or kwargs.get("unify_api_key")
            or configs.get("unify_api_key")
            or os.getenv("UNIFY_API_KEY")
            or os.getenv("UNIFY_KEY")
        )
        endpoint: Union[str, None] = secrets.get("endpoint") or kwargs.get("endpoint") or configs.get("endpoint")
        model: Union[str, None] = None
        provider: Union[str, None] = None
        if not endpoint:
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

    name: str = "unify_connection"
    class_name = "UnifyConnection"
    TYPE = ConnectionType.CUSTOM.value

    _connection_instance: UnifyClient = None

    _default_endpoint: str = "gpt-4o@openai"

    _Connection_configs: Dict[str, str] = {
        "name": "unify_connection",
        "module": "unify.clients",
        "class": "Unify",
        "type": "CustomConnection",
        "custom_type": "UnifyConnection",
        "package": "unify_integration",
    }

    _strong_configs: Dict[str, str] = {
        "api_base": "https://api.unify.ai/v0",
        "endpoint": _default_endpoint,
    }

    _strong_secrets: Dict[str, str] = {
        "unify_api_key": "<user-input>",
    }

    def __init__(
        self,
        secrets: Optional[Dict[str, str]] = None,
        configs: Optional[Dict[str, str]] = None,
        convert_to_strong_type: bool = True,
        **kwargs: dict,
    ):
        self.connection_instance: Union[None, Unify] = Unify(
            endpoint=self._default_endpoint, api_key=secrets.get("unify_api_key")
        )

        if not secrets:
            _configs = {**self._strong_configs, **self._Connection_configs}
            super().__init__(name=self.name, secrets=self._strong_secrets, configs=_configs)
        else:
            if not configs:
                configs = {"api_base": "https://api.unify.ai/v0", "endpoint": self._default_endpoint}
            _configs = {**self._Connection_configs, **configs}
            super().__init__(name=self.name, secrets=secrets, configs=_configs, **kwargs)

        if convert_to_strong_type:
            self.convert_to_strong_type()

    @property
    def connection_instance(self) -> UnifyClient:
        return self._connection_instance

    @connection_instance.setter
    def connection_instance(self, instance: UnifyClient) -> None:
        self._connection_instance = instance

    def convert_to_strong_type(self) -> Unify:
        """
        Creates an instance of Unify client.

        """

        module = self._Connection_configs.get("module")
        name = self._Connection_configs.get("class")
        self.connection_instance = self._convert_to_custom_strong_type(module=module, to_class=name)
        return self.connection_instance


def create_strong_unify_connection() -> Union[Unify, UnifyConnection]:
    """
    Creates a strong type connection for Unify
    """

    _api_key: str = os.getenv("UNIFY_API_KEY") or os.getenv("UNIFY_KEY") or "<user-input>"
    strong_unify_connection: Union[UnifyConnection, None] = None
    if unify_connection_name not in pf.connections.list():
        secrets: Dict[str, str] = {"unify_api_key": _api_key}
        strong_unify_connection = UnifyConnection(secrets=secrets)
        pf.connections.create_or_update(strong_unify_connection)
    return strong_unify_connection


def validate_input(**inputs: Any) -> bool:
    """
    Validates that input is not null.

    :param input: Any input
    :type input: Any
    """
    return any([input not in ["", " ", None] for input in inputs.values()])


def list_endpoints(
    api_key: Union[str, Any, None] = None,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    find_endpoints_by: Optional[str] = None,
    **kwargs: Optional[Any],
) -> List[Dict[str, str]]:
    """
    Lists endpoints available through Unify.

    :param model: If provided, filters the list of endpoints for the ones using the provided model.
    :type param: str
    :param provider: If provided, filters the list of endpoints for the ones using the provider.
    :type provider: str
    :param api_key: Unify API key
    :type api_key: str
    :param find_endpoints_by: "model" or "provider"
    :type find_endpoints_by: str
    """
    ret = []
    api_key = api_key or kwargs.get("api_key")
    model = None if find_endpoints_by in ["provider", None] else (model or kwargs.get("model"))
    provider = None if find_endpoints_by in ["model", None] else (provider or kwargs.get("provider"))
    print(model, provider)
    endpoints = unify.list_endpoints(model=model, provider=provider, api_key=api_key)

    for endpoint in endpoints:
        ret.append({"value": endpoint})
    return ret


def list_models(api_key: Union[str, Any, None] = "", **kwargs: Optional[Any]) -> List[Dict[str, str]]:
    """
    Lists models available through Unify.

    :param api_key:
    :type api_key: str
    """
    ret = []
    api_key = api_key or kwargs.get("api_key")
    try:
        models = unify.list_models(api_key=api_key)
    except (ValueError, TypeError):
        models = unify.list_models()
    for model in models:
        ret.append({"value": model})
    return ret


def list_providers(api_key: Union[str, Any, None] = "", **kwargs: Optional[Any]) -> List[Dict[str, str]]:
    """
    Lists providers available through Unify.

    :param api_key:
    :type api_key: str
    """
    ret = []
    api_key = api_key or kwargs.get("api_key")
    try:
        providers = unify.list_providers(api_key=api_key)
    except (ValueError, TypeError):
        providers = unify.list_providers()
    for provider in providers:
        ret.append({"value": provider})
    return ret


@tool
def single_sign_on(
    unify_api_key: Secret,
    endpoint: Optional[str] = None,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    custom: Optional[str] = None,
    **kwargs: Optional[Any],  # noqa: W0613
) -> Union[Unify, Dict[str, Any]]:
    """Unify connection tool.

    :param endpoint: The endpoint to use.
    :type endpoint: str
    :param model: The model to use.
    :type model: str
    :param provider: The provider from the list of providers available for the model.
    :type provider: str
    :param custom: Custom endpoint or router. Works with optimize_llm_tool
    :type custom: str
    :param unify_api_key: The Unify API key
    :type unify_api_key: Secret
    """

    if custom:
        assert isinstance(custom, (str, dict)), "Custom endpoint formatted incorrectly"
        custom_endpoint = custom if isinstance(custom, str) else endpoint.get("optimal_endpoint")
    new_endpoint: str = endpoint or custom_endpoint or f"{model}@{provider}"

    configs: Dict[str, Union[str, None]] = {
        "endpoint": new_endpoint,
    }

    # Create the connection, note that all secret values will be scrubbed in the returned result
    connection = UnifyConnection(secrets={"unify_api_key": unify_api_key}, configs=configs)

    pf.connections.create_or_update(connection)

    connection_openai_base = OpenAIConnection(
        name="unify_connection_openai",
        api_key=f"{unify_api_key}",
        base_url=f"{connection.api_base}",
        model=f"{connection.connection_instance.endpoint}",
    )

    pf.connections.create_or_update(connection_openai_base)

    ret: dict = {"value": connection.__dict__.get("configs"), "name": "unify_connection"}
    ret_pickled = json.dumps(ret)

    return ret_pickled
