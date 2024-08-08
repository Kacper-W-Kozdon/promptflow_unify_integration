import os

from dotenv import load_dotenv

from promptflow.core import tool

try:
    from unify.utils import evaluate
except ImportError:

    def evaluate(*args, **kwargs):
        raise NotImplementedError


load_dotenv()
api_key = os.getenv("UNIFY_KEY")


# Unify client as the connection is a temporary solution before the final approach is chosen (CustomConnection?)
@tool
def evaluate_llms(models: list, prompt_set: list, api_key: str = api_key) -> str:
    """
    Evaluates the endpoint models on a prompt set for a step of a flow.

    :param models: models' endpoints to use
    :param prompt_set: list of prompts for evaluation
    :param api_key: api key to the Unify client
    """
    results = evaluate(dataset=prompt_set, endpoints=models, api_key=api_key)
    return results
