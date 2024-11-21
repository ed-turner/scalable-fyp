
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    DB_URI: str = Field(..., env="DB_URI")
    MLFLOW_URI: str = Field(..., env="MLFLOW_DB_URI")

    DATA_SOURCE_SCHEMA: str = Field("public", env="DATA_SOURCE_SCHEMA")
    ML_PREDICTIONS_SCHEMA: str = Field("ml_predictions", env="ML_PREDICTIONS_SCHEMA")
    DATA_INTERNAL_RANKING_SCHEMA: str = Field("ranking", env="DATA_INTERNAL_RANKING_SCHEMA")

