from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"

    AVAILABLE_MODELS: str = ""

    HOST: str = "0.0.0.0"
    PORT: int = 8080

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def get_model_list(self) -> list[dict]:
        """返回可用模型列表，格式 [{id, name, default}]。"""
        if self.AVAILABLE_MODELS:
            models = []
            for entry in self.AVAILABLE_MODELS.split(","):
                entry = entry.strip()
                if not entry:
                    continue
                if "|" in entry:
                    mid, mname = entry.split("|", 1)
                else:
                    mid = mname = entry
                models.append({
                    "id": mid.strip(),
                    "name": mname.strip(),
                    "default": mid.strip() == self.LLM_MODEL,
                })
            return models
        return [{"id": self.LLM_MODEL, "name": self.LLM_MODEL, "default": True}]


settings = Settings()
