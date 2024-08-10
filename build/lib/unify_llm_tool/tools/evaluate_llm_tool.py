import os
from collections import OrderedDict
from typing import List, Optional

import requests
import unify.utils
from dotenv import load_dotenv
from unify.utils import _res_to_list as res_to_list
from unify.utils import _validate_api_key as validate_api_key

from promptflow.core import tool

try:
    from unify.utils import evaluate
except ImportError:

    def evaluate(*args, **kwargs):
        raise NotImplementedError


load_dotenv()
_api_key = os.getenv("UNIFY_KEY")
_base_url = "https://api.unify.ai/v0"

# Unify client as the connection is a temporary solution before the final approach is chosen (CustomConnection?)


@tool
def benchmark_models(
    models: Optional[list], providers: Optional[list], api_key: Optional[str] = _api_key, router: bool = True
) -> OrderedDict:
    """
    Evaluates the endpoint models on a prompt set for a step of a flow.

    :param models: models' endpoints to use
    :param prompt_set: list of prompts for evaluation
    :param api_key: api key to the Unify client
    """
    if not router:
        api_key = validate_api_key(api_key)
        url: str = f"{_base_url}/v0/benchmarks"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        benchmark_list = OrderedDict()
        try:
            endpoints_list: List[str] = unify.utils.list_endpoints(model=models, provider=providers, api_key=api_key)
        except Exception:
            endpoints_list: List[str] = unify.utils.list_endpoints(model=models)

        for endpoint in endpoints_list:
            model, provider = endpoint.split("@")
            params: dict = {
                "model": model,
                "provider": provider,
            }
            benchmark = res_to_list(requests.get(url, headers=headers, params=params, timeout=10))
            benchmark_list[endpoint] = benchmark
    return benchmark_list
