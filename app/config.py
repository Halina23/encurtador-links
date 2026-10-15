from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações lidas de variáveis de ambiente (ou do arquivo .env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Sem valor padrão: se faltar, a aplicação falha logo ao iniciar.
    database_url: str
    base_url: str = "http://localhost:8000"
    log_level: str = "INFO"


settings = Settings()
