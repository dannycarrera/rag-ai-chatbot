from tests.conftest import db_manager


# DB Admin
def test_create_db() -> None:
    try:
        db_manager.drop_db()
    except Exception:
        pass
    db_manager.create_db()


def test_drop_db() -> None:
    db_manager.drop_db()

    # recreate for rest of tests
    db_manager.create_db()


# DB Manage
async def test_setup_db() -> None:
    try:
        db_manager.drop_db()
    except Exception:
        pass
    db_manager.create_db()
    await db_manager.setup_db()


def test_recreate_peewee_tables() -> None:
    db_manager.recreate_peewee_tables()


async def test_reset_dbs() -> None:
    await db_manager.reset_dbs()
