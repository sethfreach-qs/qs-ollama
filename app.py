import os
import sys
from dotenv import load_dotenv
import requests
import json
import time
from abc import ABC, abstractmethod


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        stop = time.perf_counter()
        print(f"Time taken: {stop-start:.2f} seconds")
        return result
    return wrapper


class APIClient(ABC):
    def __init__(self, model, base_url, headers={}):
        self.model = model
        self.base_url = base_url
        self.headers = headers

    @abstractmethod
    def get_data_payload(self, prompt):
        pass

    def fetch_prompt_response(self, prompt):
        data = self.get_data_payload(prompt)
        url = f"{self.base_url}/{self.endpoint}"
        response = requests.post(url=url, headers=self.headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


class OpenAIAPIClient(APIClient):
    def __init__(self, model, base_url=None, headers={}):
        OPENAI_API_KEY = os.getenv("OPENAIKEY")

        self.model = model
        self.base_url = "https://api.openai.com/"
        self.endpoint = "v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        }

    def get_data_payload(self, prompt):
        data = {
            "model": f"{self.model}",
            "messages": [{"role": "user", "content": f"{prompt}"}]
        }
        return json.dumps(data)


class OllamaAPIClient(APIClient):
    def __init__(self, model, base_url=None, headers={}):
        self.model = model
        self.base_url = "http://127.0.0.1:11434/"
        self.endpoint = "api/generate"
        self.headers = {
            "Content-Type": "application/json",
        }

    def get_data_payload(self, prompt):
        data = {
            "model": f"{self.model}",
            "prompt": f"{prompt}",
            "stream": False,
        }
        return json.dumps(data)


class DataParser:
    def parse(self, data):
        resp = data.get("response", None)
        if resp is not None:
            return json.dumps(resp, indent=4)

        resp = data.get("choices", None)
        if resp is not None:
            return json.dumps(resp[0]["message"]["content"], indent=4)

        return json.dumps(data, indent=4)


class Display:
    def show(self, parsed_data):
        print(parsed_data)


class APIService:
    def __init__(self, api_client, data_parser, display):
        self.api_client = api_client
        self.data_parser = data_parser
        self.display = display

    def run(self, prompt=None):
        data = self.api_client.fetch_prompt_response(prompt)
        parsed_data = self.data_parser.parse(data)
        self.display.show(parsed_data)


# run main program
@timer
def main(local=False):
    prompt = "Tell me a fairy tale story. Once upon a time"

    # read the api key from a .env file
    load_dotenv()

    if local:
        client = OllamaAPIClient("sheldon")
    else:
        client = OpenAIAPIClient("gpt-4o")

    data_parser = DataParser()
    display = Display()
    service = APIService(client, data_parser, display)

    service.run(prompt)


if __name__ == "__main__":
    arg1 = sys.argv[1] if len(sys.argv) > 1 else None
    if arg1 == "--local" or arg1 == "-l":
        main(True)
    else:
        main()
