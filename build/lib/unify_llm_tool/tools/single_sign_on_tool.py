from typing import Dict, Optional, Any, List

import unify.clients
from unify import Unify
import unify

from promptflow.contracts.types import Secret
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
    api_key: Secret
    api_base: str = "https://api.unify.ai/v0"

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
        self.convert_to_strong_type()

    def convert_to_strong_type(self) -> Unify:
        """
        Creates an instance of Unify client.

        """

        module = self._Connection_kwargs.get("module")
        name = self._Connection_kwargs.get("name")
        return self._convert_to_custom_strong_type(module=module, to_class=name)


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
    connection: UnifyConnection,
    endpoint: Optional[str],
    model: Optional[str],
    provider: Optional[str],
    router: Optional[str],
) -> Unify:
    """Unify connection tool.

    :param endpoint: The endpoint to use.
    :type endpoint: str
    :param model: The model to use.
    :type model: str
    :param provider: The provider from the list of providers available for the model.
    :type provider: str
    """
    if new_endpoint := endpoint or router:
        connection.set_endpoint(new_endpoint)
        return connection
    if model and provider:
        connection.set_model(model)
        connection.set_provider(provider)
        return connection
