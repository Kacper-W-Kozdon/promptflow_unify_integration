import json
import os
from collections import OrderedDict
from importlib.metadata import version
from typing import List, Optional, Union

import requests
import unify.utils
from dotenv import load_dotenv
from unify.utils import _res_to_list as res_to_list
from unify.utils import _validate_api_key as validate_api_key

from promptflow.contracts.types import Secret
from promptflow.core import tool

load_dotenv()
_api_key = os.getenv("UNIFY_KEY")
_base_url = "https://api.unify.ai/v0"

# Unify client as the connection is a temporary solution before the final approach is chosen (CustomConnection?)


def get_benchmarks(endpoints_list: list, api_key: Union[Secret, str]) -> Union[OrderedDict, object, list]:
    """
    Retrieves the list of benchmarks for a list of endpoints

    :param endpoints_list: A list of endpoints in the format "<model>@<provider>".
    :type endpoints_list: list
    :param api_key: Unify API key
    :type api_key: Union[Secret, str]
    """
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    benchmark_list: Union[OrderedDict] = OrderedDict()
    url = f"{_base_url}/benchmarks"
    print(f"---ENDPOINTS---\n{endpoints_list}")
    for endpoint in endpoints_list:
        model, provider = tuple(endpoint.split("@"))
        params: dict = {
            "model": model,
            "provider": provider,
        }
        benchmark = res_to_list(requests.get(url, headers=headers, params=params, timeout=10))
        benchmark_list[endpoint] = benchmark
    return benchmark_list


@tool
def benchmark_models(
    models: Optional[list], providers: Optional[list], api_key: Union[str, Secret] = _api_key, router: bool = False
) -> Union[OrderedDict, object, dict]:
    """
    Provides the list of available endpoints or routers.
    If either models or providers are passed to the tool,
    it lists available endpoints for these models or providers.

    :param models: models' endpoints to use
    :type models: Optional[list]
    :param providers: list of prompts for evaluation
    :type providers: Optional[list]
    :param api_key: api key to the Unify client
    :type api_key: Union[str, Secret]
    :param router: if True, fetches the list of deployed routers with metadata; default: False
    :type router: bool
    """

    benchmark_list: Union[OrderedDict, object, list] = OrderedDict()
    api_key = validate_api_key(api_key)
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    if not router and version("unifyai") <= "0.8.5":
        assert isinstance(benchmark_list, OrderedDict)
        url: str = f"{_base_url}/endpoints"
        endpoints_params: dict = {
            "model": models,
            "provider": providers,
        }
        endpoints_list: List[str] = res_to_list(requests.get(url, headers=headers, params=endpoints_params, timeout=10))
        return get_benchmarks(endpoints_list=endpoints_list, api_key=api_key)
    elif not router and version("unifyai") > "0.8.5":
        try:
            endpoints_list = unify.list_endpoints(
                model=models, provider=providers, api_key=api_key
            )  # noqa: E1123, E501
        except (TypeError, ValueError):
            url = f"{_base_url}/endpoints"
            endpoints_params = {
                "model": models,
                "provider": providers,
            }
            endpoints_list = res_to_list(requests.get(url, headers=headers, params=endpoints_params, timeout=10))

        return get_benchmarks(endpoints_list=endpoints_list, api_key=api_key)

    url = f"{_base_url}/router/deploy/list"
    benchmark_list = requests.get(url, headers=headers, params=endpoints_params, timeout=10)
    ret: dict = {"value": benchmark_list, "name": "benchmarks"}
    ret_pickled = json.dumps(ret)
    return ret_pickled
