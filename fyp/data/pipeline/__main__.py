"""
The main module for the pipeline package.
"""
import logging


from distributed import Client, LocalCluster
import dask.dataframe as dd

from fyp.data.db.queries import define_training_data_query
from fyp.settings import Settings

logger = logging.getLogger()

settings = Settings()

# this is just assuming local development.  There is an option of using
# distribution in the cloud using remote instances
with LocalCluster() as cluster:
    with Client(cluster):
        logger.info("Executing query")
        ddf = dd.read_sql_query(
            define_training_data_query(),
            con=settings.DB_URI,
            index_col="rn",
            params={
                "sslmode": "require",
                "options": f"-csearch_path%3D{settings.DATA_SOURCE_SCHEMA}"
            }
        )

        dd.to_sql(
            ddf,
            "training_data",
            uri=settings.DB_URI,
            schema=settings.DATA_INTERNAL_RANKING_SCHEMA,
            if_exists="replace",
            parallel=True
        )

        logger.info("Execution is done")
