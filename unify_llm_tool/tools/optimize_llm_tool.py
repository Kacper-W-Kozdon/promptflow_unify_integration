from typing import Optional, Sequence, Union

from unify import Unify

from promptflow.client import PFClient
from promptflow.contracts.types import Secret
from promptflow.core import tool
from unify_llm_tool.tools.single_sign_on_tool import UnifyConnection, single_sign_on

pf = PFClient()


# Unify client as the connection is a temporary solution before the final approach is chosen (CustomConnection?)
@tool
def optimize_llm(
    unify_api_key: Secret,  # noqa: W0613
    connection: Optional[Union[Unify, UnifyConnection]],
    quality: Optional[str],
    cost: Optional[str],
    time_to_first_token: Optional[str],
    inter_token_latency: Optional[str],
    endpoint: Optional[str],
    model: Optional[str],
    provider: Optional[str],
    input_text: Union[str, Sequence] = " ",
) -> Union[dict, str, tuple]:
    """
    Selects the optimal model for a step of a flow.

    :param unify_api_key:
    :type unify_api_key: Secret
    :param connection: Unify client to use for connection
    :type connection: Unify
    :param quality:
    :type quality: str
    :param cost:
    :type cost: str
    :param time_to_first_token:
    :type time_to_first_token: str
    :param inter_token_latency:
    :type inter_token_latency: str
    :param endpoint:
    :type endpoint: str
    :param model:
    :type model: str
    :param provider:
    :type provider: str
    :param input_text:
    :type input_text: Union[str, Sequence]
    """

    if not connection:
        connection = single_sign_on(endpoint=endpoint, model=model, provider=provider, unify_api_key=unify_api_key)
    assert connection.name == "unify_connection", "Incorrect connection base."
    connection_instance = connection.connection_instance if isinstance(connection, UnifyConnection) else connection

    router: str = f"router@q:{quality}|c:{cost}|t:{time_to_first_token}|i:{inter_token_latency}"

    if isinstance(endpoint, list):
        model = []
        provider = []
        for entry in endpoint:
            entry_model, entry_provider = tuple(entry.split("@"))
            model.append(entry_model)
            provider.append(entry_provider)
    if isinstance(provider, list):
        providers: str = ",".join(provider)
        router_listed: list = router.split("@")
        router_listed.insert(1, f"@provider:{providers}|")
        router = "".join(router_listed)
    if isinstance(model, list):
        models: str = ",".join(model)
        router_listed = router.split("@")
        router_listed.insert(1, f"@model:{models}|")
        router = "".join(router_listed)
        connection_instance.set_endpoint(router)
        response: str = connection_instance.generate(input_text)
        endpoint = connection_instance.endpoint
        return {"optimal_endpoint": endpoint, "response": response}

    if endpoint:
        connection_instance.set_endpoint(endpoint)
    if not endpoint and all([model, provider]):
        connection_instance.set_model(model)
        connection_instance.set_provider(provider)

    response = connection_instance.generate(input_text)
    endpoint = connection_instance.endpoint

    connection.configs["endpoint"] = endpoint
    pf.connections.create_or_update(connection)
    ret_endpoint: str = endpoint
    ret_response: str = response
    return {"value": ret_endpoint, "name": "optimal_endpoint"}, {"value": ret_response, "name": "response"}
