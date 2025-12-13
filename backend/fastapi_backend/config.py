"""Configuration management using pydantic-settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
    )

    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")

    # Pinecone Configuration
    pinecone_api_key: str = Field(..., description="Pinecone API key")
    pinecone_environment: str = Field(
        default="us-east-1", 
        description="Pinecone region (e.g., us-east-1, eu-west-1). Will auto-create index if it doesn't exist."
    )
    pinecone_index_name: str = Field(
        default="learnify", 
        description="Pinecone index name (will be created automatically if it doesn't exist)"
    )

    # Application Configuration
    backend_host: str = Field(default="0.0.0.0", description="Backend host")
    backend_port: int = Field(default=8000, description="Backend port")
    log_level: str = Field(default="INFO", description="Logging level")

    # Embedding Model
    embedding_model: str = Field(
        default="text-embedding-3-small", description="OpenAI embedding model"
    )

    # LLM Configuration
    llm_model: str = Field(
        default="gpt-4o-mini", description="OpenAI LLM model"
    )
    llm_temperature: float = Field(
        default=0.7, description="Temperature for LLM generation"
    )

    # CORS Configuration
    cors_origins: list[str] = Field(
        default=["http://localhost:8501", "http://localhost:3000"],
        description="Allowed CORS origins",
    )

    @property
    def backend_url(self) -> str:
        """Get the backend URL."""
        return f"http://{self.backend_host}:{self.backend_port}"


# Global settings instance
settings = Settings()

