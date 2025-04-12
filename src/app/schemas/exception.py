import json


class ApiException(Exception):
    def __init__(self, message: str):
        self.message = message

    def detail(self) -> str | None:
        print(self.message)
        try:
            data = json.loads(self.message)
        except json.decoder.JSONDecodeError:
            return None
        return data.get("message") if isinstance(data, dict) else None
