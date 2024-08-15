import os
from collections import OrderedDict
from typing import List, Optional, Union

import requests
import unify.utils
from dotenv import load_dotenv
from unify.utils import _res_to_list as res_to_list
from unify.utils import _validate_api_key as validate_api_key

from promptflow.core import tool

load_dotenv()
_api_key = os.getenv("UNIFY_KEY")
_base_url = "https://api.unify.ai/v0"

# Unify client as the connection is a temporary solution before the final approach is chosen (CustomConnection?)


@tool
def benchmark_models(
    models: Optional[list], providers: Optional[list], api_key: Optional[str] = _api_key, router: bool = False
) -> Union[OrderedDict, object]:
    """
    Provides the list of available endpoints or routers.
    If either models or providers are passed to the tool,
    it lists available endpoints for these models or providers.

    :param models: models' endpoints to use
    :type models: Optional[list]
    :param providers: list of prompts for evaluation
    :type providers: Optional[list]
    :param api_key: api key to the Unify client
    :type api_key: Optional[str]
    :param router: if True, fetches the list of deployed routers with metadata; default: False
    :type router: bool
    """
    benchmark_list: Union[OrderedDict, object] = OrderedDict()
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    api_key = validate_api_key(api_key)
    if not router:
        assert isinstance(benchmark_list, OrderedDict)

        url: str = f"{_base_url}/benchmarks"
        try:
            endpoints_list: List[str] = unify.utils.list_endpoints(
                model=models, provider=providers, api_key=api_key
            )  # noqa: E1123, E501
        except TypeError:
            endpoints_list = unify.utils.list_endpoints(model=models)

        for endpoint in endpoints_list:
            model, provider = endpoint.split("@")
            params: dict = {
                "model": model,
                "provider": provider,
            }
            benchmark = res_to_list(requests.get(url, headers=headers, params=params, timeout=10))
            benchmark_list[endpoint] = benchmark
        return benchmark_list

    url = f"{_base_url}/router/deploy/list"
    benchmark_list = requests.get(url, headers=headers, params=params, timeout=10)
    return benchmark_list
