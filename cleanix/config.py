from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    postgres_host: str = Field("postgres", env="POSTGRES_HOST")
    postgres_port: int = Field(5432, env="POSTGRES_PORT")
    postgres_user: str
    postgres_pass: str
    postgres_db: str

    sql_queries_path: str = Field("/cleanix/sql", env="SQL_PATH")
    sql_init_path: str = Field("/cleanix/init_db/initdb.sql", env="INIT_DB_PATH")


class AuthConfig(BaseSettings):
    secret_key: str
    algorithm: str = Field("HS256", env="ALGORITHM")
    expiration_time_minutes: int = Field(60, env="EXPIRATION_TIME_MINUTES")


auth_config = AuthConfig()
