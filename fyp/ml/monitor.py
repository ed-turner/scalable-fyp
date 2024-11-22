import logging
import argparse
from datetime import datetime, UTC

from distributed import Client, LocalCluster

import dask.dataframe as dd

from fyp.settings import Settings
from fyp.data.db.queries import define_analysis_query

logger = logging.getLogger()
settings = Settings()

parser = argparse.ArgumentParser()

parser.add_argument("--execution_timestamp", type=str, required=True, default=lambda: datetime.now(UTC).isoformat())

args = parser.parse_args()

with LocalCluster() as cluster:
    with Client(cluster):
        ddf: dd.DataFrame = dd.read_sql_query(
            define_analysis_query(args.execution_timestamp),
            con=settings.DB_URI,
            index_col="rn",
            params={
                "sslmode": "require",
                "options": f"-csearch_path%3D{settings.DATA_SOURCE_SCHEMA}"
            }
        )

        ddf['created_at'] = datetime.now(UTC)

        ddf.to_sql(
        "fyp_current_ranking",
            uri=settings.DB_URI,
            schema=settings.ML_PREDICTIONS_SCHEMA,
            if_exists="append",
            parallel=True
        )