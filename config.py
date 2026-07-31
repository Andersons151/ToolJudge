# class Config:
#     SECRET_KEY = "change-this"
#     SQLALCHEMY_DATABASE_URI = "sqlite:///toolbench.db"
#     SQLALCHEMY_TRACK_MODIFICATIONS = False


import os

class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-this")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URL",
        "sqlite:///local.db"
    )


class ProductionConfig(BaseConfig):
    DEBUG = False

    # SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_DATABASE_URI ="postgresql://tooljudge_db_user:BhHFjTc7espXyKqiuFf09gQs1L9UaEoi@dpg-d9m6j73m8hqs73a1kk00-a.frankfurt-postgres.render.com/tooljudge_db"


    if not SQLALCHEMY_DATABASE_URI:
        print("WARNING: DATABASE_URL missing — using SQLite fallback.")
        SQLALCHEMY_DATABASE_URI = "sqlite:///local.db"


def get_config():
    env = os.environ.get("FLASK_ENV", "development").lower()
    return ProductionConfig if env == "production" else DevelopmentConfig
