import logging
from typing import Any, Mapping, Sequence

import psycopg2
import redis
from langchain.indexes import SQLRecordManager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from peewee import PostgresqlDatabase
from psycopg2 import sql

from app.config import (
    get_psql_admin_config,
    get_psql_db_name,
    get_psql_url,
    get_redis_url,
)
from app.db.schema import WebSite, db_proxy

logger = logging.getLogger(__name__)


def _executeAdminCmd(sql: str, vars: Sequence[Any] | Mapping[str, Any] | None = None) -> None:
    psql_admin_config = get_psql_admin_config()
    conn = psycopg2.connect(
        database=psql_admin_config.db_name,
        user=psql_admin_config.user,
        password=psql_admin_config.password,
        host=psql_admin_config.host,
        port=psql_admin_config.port,
    )
    conn.autocommit = True

    cursor = conn.cursor()
    cursor.execute(sql, (vars,))

    # Closing the connection
    conn.close()


class DbManager:
    def __init__(self) -> None:
        self.psql_db_url = get_psql_url()

    def __enter__(self) -> "DbManager":
        self.db = PostgresqlDatabase(self.psql_db_url)
        db_proxy.initialize(self.db)
        return self

    # DB Admin
    def create_db(self) -> None:
        try:
            db_name = get_psql_db_name()
            sql = f""" CREATE database "{db_name}"; """
            _executeAdminCmd(sql)
            logger.info("Database has been created successfully!")
        except Exception:
            pass
        self.db = PostgresqlDatabase(get_psql_url())
        db_proxy.initialize(self.db)
        

    def drop_db(self) -> None:
        """Terminate connections and drop database"""
        db_name = get_psql_db_name()
        terminate_sql = sql.SQL("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = %s
                AND pid <> pg_backend_pid();
            """)
        drop_sql = f""" DROP database "{db_name}"; """
        _executeAdminCmd(terminate_sql, db_name)
        _executeAdminCmd(drop_sql)
        logger.info("Database has been dropped successfully.")

    async def setup_db(self) -> None:
        db = self.db
        """Create tables for peewee models, sqlrecordmanager and checkpointer"""
        if not db.is_connection_usable:
            db.connect()
        # peewee
        db.create_tables([WebSite])
        # documentloader/index
        record_manager = SQLRecordManager("namespace", db_url=self.psql_db_url)
        record_manager.create_schema()
        # checkpointer
        async with AsyncPostgresSaver.from_conn_string(self.psql_db_url) as checkpointer:
            await checkpointer.setup()

    def recreate_peewee_tables(self) -> None:
        db = self.db
        if not db.is_connection_usable:
            db.connect()
        db.drop_tables([WebSite])
        db.create_tables([WebSite])
        db.close()

    async def reset_dbs(self) -> None:
        db = self.db
        """Reset all data for or peewee models, sqlrecordmanager, checkpointer and redis"""
        # PSQL
        # peewee
        if not db.is_connection_usable:
            db.connect()

        WebSite.delete().execute()

        if db.is_connection_usable:
            db.close()

        async with AsyncPostgresSaver.from_conn_string(self.psql_db_url) as checkpointer:
            cursor = checkpointer.conn.cursor()
            try:
                # checkpointer
                await cursor.execute("DELETE FROM checkpoints")
                await cursor.execute("DELETE FROM checkpoint_writes")
                await cursor.execute("DELETE FROM checkpoint_blobs")

                # documentloader/index
                await cursor.execute("DELETE FROM upsertion_record")

                await checkpointer.conn.commit()
            except Exception as e:
                logger.error(e)

        # Redis
        redis_url = get_redis_url()
        redis_client = redis.Redis.from_url(redis_url)
        redis_client.flushall()

    def __exit__(self, exc_type, exc_value, traceback) -> None:  # noqa: ANN001
        self.db.close()
