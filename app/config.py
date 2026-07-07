from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field("HabitFlowByMe", validation_alias="APP_NAME")

    database_host: str = Field(validation_alias="DATABASE_HOST")
    database_port: int = Field(validation_alias="DATABASE_PORT")
    database_name: str = Field(validation_alias="DATABASE_NAME")
    database_user: str = Field(validation_alias="DATABASE_USER")
    database_password: str = Field(validation_alias="DATABASE_PASSWORD")

    secret_key: str = Field(validation_alias="SECRET_KEY")
    algorithm: str = Field("HS256", validation_alias="ALGORITHM")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}"
            f"/{self.database_name}"
        )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
