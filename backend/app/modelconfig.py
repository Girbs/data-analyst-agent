import json
import os
import re

from langchain_ollama import OllamaLLM
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class OpenAIInvokeAdapter:
    def __init__(self, client, model):
        self.client = client
        self.model = model

    def invoke(self, prompt: str) -> str:
        try:
            response = self.client.responses.create(model=self.model, input=prompt)
            if hasattr(response, "output_text") and response.output_text:
                return response.output_text
        except Exception:
            pass

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content



PROVIDER = "openai"  # Change to "openai" or "mistral" as needed
OPEN_AI_MODEL_NAME = "gpt-4o-mini"
MISTRAL_MODEL_NAME = "mistral-small-latest"
LLAMA_MODEL_NAME = "llama3.2"
TEMPERATURE = 0.7
NUM_PREDICT = 1000


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(config_path):
        return {}

    with open(config_path, "r", encoding="utf-8") as config_file:
        return json.load(config_file)


def get_model_name():
    selected_provider = (PROVIDER).lower()
    if selected_provider == "ollama":
        return LLAMA_MODEL_NAME
    if selected_provider == "openai":
        return OPEN_AI_MODEL_NAME
    if selected_provider == "mistral":
        return MISTRAL_MODEL_NAME
    raise ValueError("PROVIDER must be 'ollama', 'openai', or 'mistral'")


def get_clients(temperature=None, num_predict=None):
    selected_provider = (PROVIDER).lower()
    selected_model = get_model_name()
    selected_temperature = TEMPERATURE if temperature is None else temperature
    selected_num_predict = NUM_PREDICT if num_predict is None else num_predict
    config = load_config()

    if selected_provider == "ollama":
        llm = OllamaLLM(
            model=selected_model,
            temperature=selected_temperature,
            num_predict=selected_num_predict,
        )
        return selected_provider, selected_model, llm, None

    if OpenAI is None:
        raise RuntimeError("OpenAI package is not installed. Run: pip install openai")

    if selected_provider == "openai":
        api_key = config.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set in config.json or environment")
        api_base = config.get("OPENAI_API_BASE") or os.getenv("OPENAI_API_BASE")
        client = OpenAI(api_key=api_key, base_url=api_base) if api_base else OpenAI(api_key=api_key)
        llm = OpenAIInvokeAdapter(client, selected_model)
        return selected_provider, selected_model, llm, client

    if selected_provider == "mistral":
        api_key = config.get("MISTRAL_API_KEY") or os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise RuntimeError("MISTRAL_API_KEY is not set in config.json or environment")
        api_base = config.get("MISTRAL_API_BASE") or os.getenv("MISTRAL_API_BASE") or "https://api.mistral.ai/v1"
        client = OpenAI(api_key=api_key, base_url=api_base)
        llm = OpenAIInvokeAdapter(client, selected_model)
        return selected_provider, selected_model, llm, client

    raise ValueError("PROVIDER must be 'ollama', 'openai', or 'mistral'")

def extract_json(llm_output):
  json_text = re.search(r"\{.*\}", llm_output, re.DOTALL).group()
  result = json.loads(json_text)
  return result