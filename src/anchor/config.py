from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ANCHOR_", env_file=".env", extra="ignore")

    graph_host: str = "127.0.0.1"
    graph_port: int = 6379
    graph_name: str = "anchor_demo"
    erp_path: str = "data/anchor-erp.sqlite3"
    host: str = "127.0.0.1"
    port: int = 8765
    mode: str = "SIMULATION"
    max_stress_iterations: int = 8
    max_execution_attempts: int = 2


settings = Settings()
