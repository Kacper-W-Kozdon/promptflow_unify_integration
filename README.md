# Unify integration for Prompt flow

## Introduction
This tool package provides access to [numerous endpoints](https://console.unify.ai/dashboard) and custom routers, with the option to employ dynamic routing to obtain responses from the best-suited model@provider for your task.

## Requirements
PyPI package: [`unify-integration`](https://pypi.org/project/unify-integration/).
- For local users:
    ```
    pip install unify-integration
    ```
    Recommended to be used with the [VS Code extension for Prompt flow](https://marketplace.visualstudio.com/items?itemName=prompt-flow.prompt-flow).

## Unify-specific inputs (optional)

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| cost | string | Cost-per-token for the endpoint. | No |
| quality | string | The quality value of the model based on [dataset evaluations](https://console.unify.ai/dashboard) done by the oracle model. | No |
| inter_token_latency | string | The delay before a new token is output. | No |
| time_to_first_token | string | The delay before the first token is generated | No |
| connection | CustomConnection | UnifyConnection using the [Unify client](https://github.com/unifyai/unify?tab=readme-ov-file#chatbot-agent) | No |
