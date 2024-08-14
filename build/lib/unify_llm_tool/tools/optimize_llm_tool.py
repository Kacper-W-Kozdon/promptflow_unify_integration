from typing import Optional, Sequence, Union

from unify import Unify

from promptflow.core import tool


# Unify client as the connection is a temporary solution before the final approach is chosen (CustomConnection?)
@tool
def optimize_llm(connection: Unify, config: Optional[dict], input_text: Union[str, Sequence] = " ") -> Union[dict, str]:
    """
    Selects the optimal model for a step of a flow.

    :param connection: Unify client to use for connection
    :type connection: Unify
    :param config: requirements for the optimization
    :type config: Optional[dict]
    :param input_text:
    :type input_text: Union[str, Sequence]
    """
    assert isinstance(connection.get_credit_balance(), (str, float, int))
    if not isinstance(config, dict):
        config = {}
    quality: str = config.get("quality", "1")
    cost: str = config.get("cost", "4.65e-03")
    time_to_first_token: str = config.get("time_to_first_token", "2.08e-05")
    inter_token_latency: str = config.get("inter_token_latency", "2.07e-03")
    endpoint: Union[list[str], str] = config.get("endpoint", None)
    model: Union[list[str], str] = config.get("model", None)
    provider: Union[list[str], str] = config.get("provider", None)

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
        router_listed: list = router.split("@")
        router_listed.insert(1, f"@model:{models}|")
        router = "".join(router_listed)
        connection.set_endpoint(router)
        response: str = connection.generate(input_text)
        endpoint: str = connection.endpoint
        return {"optimal_endpoint": endpoint, "response": response}

    if endpoint:
        connection.set_endpoint(endpoint)
    if not endpoint and all([model, provider]):
        connection.set_model(model)
        connection.set_provider(provider)

    response: str = connection.generate(input_text)
    endpoint: str = connection.endpoint
    return {"optimal_endpoint": endpoint, "response": response}
