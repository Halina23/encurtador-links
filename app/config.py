from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações lidas de variáveis de ambiente (ou do arquivo .env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Sem valor padrão: se faltar, a aplicação falha logo ao iniciar.
    database_url: str
    # Vazio: os links curtos usam o endereço pelo qual a requisição chegou
    # (útil quando o IP ou o domínio não são conhecidos de antemão).
    base_url: str = ""
    log_level: str = "INFO"


settings = Settings()
