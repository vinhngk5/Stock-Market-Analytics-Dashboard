import os


class Settings:
    DB_USER = os.environ.get("POSTGRES_USER")
    DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    DB_NAME = os.environ.get("POSTGRES_DB")

    @property
    def conninfo(self):
        return f"host=db dbname={self.DB_NAME} user={self.DB_USER} password={self.DB_PASSWORD}"


settings = Settings()
