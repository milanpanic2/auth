from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    debug: bool = True
    db_host: str = "postgresql"
    db_port: str = "5432"
    db_name: str = "auth"
    db_user: str = "cluster_user"
    db_password: str = ""
    db_pool_size: str = "2"
    db_max_overflow: str = "3"
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440
    environment: str = "default"

    @property
    def database_url(self) -> str:
        return f"{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
