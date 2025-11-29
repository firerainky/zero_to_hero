from typing import Dict, List
from bespokelabs import curator
from pydantic import BaseModel, Field
import os

API_ENDPOINTS = {
    "bailian": {
        "url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "key": "sk-987eabba7cf9404d9bde119440ce561a",
        "model": "qwen3-max"
    },
    "internal/R1": {
        "url": "http://10.200.48.200:30600/v1",
        "key": "sk-H8RJWNGwqEmIfk2ushYsqWWCbrjdReoEOwxqB6GAS5kZkyk9",
        "model": "openai/deepseek-ai/DeepSeek-R1"
    },
    "internal/qwen-plus": {
        "url": "http://10.200.48.200:30600/v1",
        "key": "sk-H8RJWNGwqEmIfk2ushYsqWWCbrjdReoEOwxqB6GAS5kZkyk9",
        "model": "qwen-plus-2025-07-28"
    },
    "internal/v3": {
        "url": "http://10.200.48.200:30600/v1",
        "key": "sk-H8RJWNGwqEmIfk2ushYsqWWCbrjdReoEOwxqB6GAS5kZkyk9",
        "model": "deepseek-ai/DeepSeek-V3"
    },
    "Horayai": {
        "url": "https://sr-endpoint.horay.ai/openai/v1",
        "key": "sk-hzaoqnkkkubhulblxprriyhldguxphmydljwguivffwjvbwx",
        "model": "g5.1"
    }
}

api_conf = API_ENDPOINTS['internal/R1']

os.environ["OPENAI_BASE_URL"] = api_conf['url']  # base_url
os.environ["OPENAI_API_KEY"] = api_conf['key']  # api_key
os.environ["OPENAI_MODEL_NAME"] = api_conf['model']  # model_name

# Monkeypatch to fix structured output check for custom endpoints
# from bespokelabs.curator.request_processor.online.openai_online_request_processor import OpenAIOnlineRequestProcessor
# import openai
# import logging

# logger = logging.getLogger(__name__)


# Monkeypatch to bypass structured output check
# from bespokelabs.curator.request_processor.online.openai_online_request_processor import OpenAIOnlineRequestProcessor
# import logging

# logger = logging.getLogger(__name__)

# def check_structured_output_support_patched(self) -> bool:
#     return True

# OpenAIOnlineRequestProcessor.check_structured_output_support = check_structured_output_support_patched

# # Monkeypatch to fix actual API call model name
# from bespokelabs.curator.request_processor.openai_request_mixin import OpenAIRequestMixin
# from bespokelabs.curator.types.generic_request import GenericRequest

# def create_api_specific_request_online_patched(self, generic_request: GenericRequest) -> dict:
#     model_name = generic_request.model
#     if model_name.startswith("openai/"):
#         model_name = model_name[7:]
        
#     request = {
#         "model": model_name,
#         "messages": generic_request.messages,
#     }

#     if generic_request.response_format:
#         request["response_format"] = {
#             "type": "json_schema",
#             "json_schema": {
#                 "name": "output_schema",  # NOTE: not using 'strict': True
#                 "schema": generic_request.response_format,
#             },
#         }

#     for key, value in generic_request.generation_params.items():
#         request[key] = value
#     return request

# OpenAIRequestMixin.create_api_specific_request_online = create_api_specific_request_online_patched



class Topics(BaseModel):
    topics_list: List[str] = Field(description="A list of topics.")

class TopicGenerator(curator.LLM):
  response_format = Topics

  def prompt(self, subject):
    return f"Return 3 topics related to {subject}"

  def parse(self, input: str, response: Topics):
    return [{"topic": t} for t in response.topics_list]


class Poem(BaseModel):
    title: str = Field(description="The title of the poem.")
    poem: str = Field(description="The content of the poem.")

class Poet(curator.LLM):
    response_format = Poem

    def prompt(self, input: Dict) -> str:
        return f"Write two poems about {input['topic']}."

    def parse(self, input: Dict, response: Poem) -> Dict:
        return [{"title": response.title, "poem": response.poem}]

topic_generator = TopicGenerator(model_name=api_conf['model'], backend='openai')
poet = Poet(model_name=api_conf['model'], backend='openai')
# Start generation
topics = topic_generator("Mathematics")
# print("Generated Topics:")
# print(topics)
poems = poet(topics)
# print("Generated Poems:")
# print(poems)