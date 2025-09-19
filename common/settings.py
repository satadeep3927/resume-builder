from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    LLM_BASE_URL: str = "https://api.githubcopilot.com"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4.1"

    COPILOT_ACCESS_TOKEN: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config = AppSettings()
