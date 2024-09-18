from typing import Any, List, Optional, Union

# Avoid circular dependencies: Use import 'from promptflow._internal' instead of 'from promptflow'
# since the code here is in promptflow namespace as well
from promptflow._internal import ToolProvider, register_apis, tool
from promptflow.contracts.types import PromptTemplate
from promptflow.tools.common import render_jinja_template  # noqa: F401
from promptflow.tools.common import post_process_chat_api_response, process_function_call, to_bool, validate_functions
from unify_llm_tool.tools.single_sign_on_tool import UnifyConnection

try:
    from promptflow.tools.common import build_messages
except ImportError:
    from promptflow.tools.common import parse_chat

    def build_messages(
        prompt: PromptTemplate,
        images: Union[None, List] = None,
    ) -> dict:
        # keep_trailing_newline=True is to keep the last \n in the prompt to avoid converting "user:\t\n" to "user:".
        chat_str = render_jinja_template(prompt, trim_blocks=True, keep_trailing_newline=True)
        messages = parse_chat(chat_str, images=images)

        return messages


class UnifyPF(ToolProvider):
    def __init__(self, connection: UnifyConnection):
        super().__init__()
        self._client = connection._connection_instance

    @tool
    def chat(
        self,
        prompt: PromptTemplate,
        temperature: float = 1.0,
        top_p: float = 1.0,
        # stream is a hidden to the end user, it is only supposed to be set by the executor.
        stream: bool = False,
        stop: Optional[list] = None,
        max_tokens: Optional[int] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        logit_bias: dict = {},  # noqa: W0102
        user: str = "",
        # function_call can be of type str or dict.
        function_call: object = None,
        functions: Optional[list] = None,
        # tool_choice can be of type str or dict.
        tool_choice: object = None,
        tools: Optional[list] = None,
        response_format: object = None,
        seed: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        messages = build_messages(prompt, **kwargs)
        stream = to_bool(stream)
        params = {
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "stream": stream,
        }

        # functions and function_call are deprecated and are replaced by tools and tool_choice.
        # if both are provided, tools and tool_choice are used and functions and function_call are ignored.
        if tools:
            # TODO: add validate_tools
            params["tools"] = tools
            # TODO: add validate_tool_choice
            params["tool_choice"] = tool_choice
        else:
            if functions:
                validate_functions(functions)
                params["functions"] = functions
                params["function_call"] = process_function_call(function_call)

        # to avoid vision model validation error for empty param values.
        if stop:
            params["stop"] = stop
        if max_tokens is not None and str(max_tokens).lower() != "inf":
            params["max_tokens"] = int(max_tokens)
        if logit_bias:
            params["logit_bias"] = logit_bias
        if response_format:
            params["response_format"] = response_format
        if seed is not None:
            params["seed"] = seed
        if presence_penalty is not None:
            params["presence_penalty"] = presence_penalty
        if frequency_penalty is not None:
            params["frequency_penalty"] = frequency_penalty
        if user:
            params["user"] = user

        completion = self._client.generate(**params)
        return post_process_chat_api_response(completion, stream, functions)


register_apis(UnifyPF)


@tool
def chat(
    connection: UnifyConnection,
    prompt: PromptTemplate,
    model: str = "",
    temperature: float = 1,
    top_p: float = 1,
    stream: bool = False,
    stop: Optional[list] = None,
    max_tokens: Optional[int] = None,
    presence_penalty: Optional[float] = None,
    frequency_penalty: Optional[float] = None,
    logit_bias: dict = {},  # noqa: W0102
    user: str = "",
    function_call: object = None,
    functions: Optional[list] = None,
    tool_choice: object = None,
    tools: Optional[list] = None,
    response_format: object = None,
    seed: Optional[int] = None,
    **kwargs: Any,
) -> str:
    return UnifyPF(connection).chat(
        prompt=prompt,
        model=model,
        temperature=temperature,
        top_p=top_p,
        stream=stream,
        stop=stop if stop else None,
        max_tokens=max_tokens,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
        logit_bias=logit_bias,
        user=user,
        function_call=function_call,
        functions=functions,
        tool_choice=tool_choice,
        tools=tools,
        response_format=response_format,
        seed=seed,
        **kwargs,
    )
