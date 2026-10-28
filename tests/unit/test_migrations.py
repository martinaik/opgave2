# Import necessary modules
from unittest.mock import MagicMock, patch, call
from app.migrations import run_migrations

def create_mock_connection():
    """ Creates a mock database connection and cursor. """

    connection = MagicMock()
    cursor = MagicMock()

    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor

    return connection, cursor

def test_run_migrations_applies_new_migration(tmp_path):
    """ Tests that a new migration is executed and recorded. """

    migration_file = tmp_path / "001_initial_schema.sql"
    migration_file.write_text(
        "CREATE TABLE test_table (id INTEGER);",
        encoding="utf-8",
    )

    connection, cursor = create_mock_connection()
    cursor.fetchone.return_value = None

    with patch("app.migrations.get_connection", return_value=connection), \
         patch("app.migrations.MIGRATIONS_DIR", tmp_path):

        run_migrations()

    executed_sql = [
        call.args[0]
        for call in cursor.execute.call_args_list
    ]

    assert "CREATE TABLE test_table (id INTEGER);" in executed_sql
    assert any(
        "INSERT INTO schema_migrations" in sql
        for sql in executed_sql
    )

def test_run_migrations_skips_applied_migration(tmp_path):
    """ Tests that an already applied migration is skipped. """

    migration_file = tmp_path / "001_initial_schema.sql"
    migration_file.write_text(
        "CREATE TABLE test_table (id INTEGER);",
        encoding="utf-8",
    )

    connection, cursor = create_mock_connection()
    cursor.fetchone.return_value = (1,)

    with patch("app.migrations.get_connection", return_value=connection), \
         patch("app.migrations.MIGRATIONS_DIR", tmp_path):

        run_migrations()

    executed_sql = [
        call.args[0]
        for call in cursor.execute.call_args_list
    ]

    assert not any(
        "CREATE TABLE test_table" in sql
        for sql in executed_sql
    )
    assert not any(
        "INSERT INTO schema_migrations" in sql
        for sql in executed_sql
    )

def test_run_migrations_applies_files_in_order(tmp_path):
    """ Tests that migration files are applied alphabetically. """

    first = tmp_path / "001_first.sql"
    second = tmp_path / "002_second.sql"

    first.write_text("SELECT 1;", encoding="utf-8")
    second.write_text("SELECT 2;", encoding="utf-8")

    connection, cursor = create_mock_connection()
    cursor.fetchone.return_value = None

    with patch("app.migrations.get_connection", return_value=connection), \
         patch("app.migrations.MIGRATIONS_DIR", tmp_path):

        run_migrations()

    executed_sql = [
        call.args[0]
        for call in cursor.execute.call_args_list
    ]

    first_index = executed_sql.index("SELECT 1;")
    second_index = executed_sql.index("SELECT 2;")

    assert first_index < second_index

def test_run_migrations_logs_applied_migration(tmp_path, caplog):
    """ Tests that applying a migration is logged. """

    migration_file = tmp_path / "001_initial_schema.sql"
    migration_file.write_text("SELECT 1;", encoding="utf-8")

    connection, cursor = create_mock_connection()
    cursor.fetchone.return_value = None

    with (
        patch("app.migrations.get_connection", return_value=connection),
        patch("app.migrations.MIGRATIONS_DIR", tmp_path),
    ):
        with caplog.at_level("INFO"):
            run_migrations()

    assert "Applying migration 001_initial_schema.sql." in caplog.text
    assert "Migration 001_initial_schema.sql applied successfully." in caplog.text

def test_run_migrations_does_not_record_failed_migration(tmp_path):
    """ Tests that a failed migration is not recorded. """
    
    migration_file = tmp_path / "001_initial_schema.sql"
    migration_file.write_text("INVALID SQL;", encoding="utf-8")

    connection, cursor = create_mock_connection()
    cursor.fetchone.return_value = None
    cursor.execute.side_effect = [
        None,  # Create schema_migrations table
        None,  # Check whether migration was applied
        RuntimeError("Migration failed"),
    ]

    with (
        patch("app.migrations.get_connection", return_value=connection),
        patch("app.migrations.MIGRATIONS_DIR", tmp_path),
    ):
        try:
            run_migrations()
        except RuntimeError:
            pass
        else:
            raise AssertionError("Expected migration to fail")

    assert not any(
        "INSERT INTO schema_migrations" in str(call.args[0])
        for call in cursor.execute.call_args_list
    )