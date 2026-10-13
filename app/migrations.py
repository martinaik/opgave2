# Import necessary modules
import logging
from pathlib import Path
from app.database import get_connection

# Set up logging
logger = logging.getLogger(__name__)

# Define the path to the migrations directory
MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"

def run_migrations() -> None:
    """ Runs database migrations that have not been applied yet. """

    # Create a table that tracks completed migrations
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

    # Find migration files in alphabetical order
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    # Apply each migration if it has not been applied yet
    for migration in migration_files:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM schema_migrations WHERE version = %s",
                    (migration.name,)
                )

                # Skip migrations that have already been applied
                if cur.fetchone():
                    logger.info(
                        "Migration %s has already been applied.",
                        migration.name
                    )
                    continue

                # Log that the migration is being applied
                logger.info("Applying migration %s.", migration.name)

                # Read and execute the migration
                sql = migration.read_text(encoding="utf-8")
                cur.execute(sql)

                # Record the migration in the same transaction
                cur.execute(
                    "INSERT INTO schema_migrations (version) VALUES (%s)",
                    (migration.name,)
                )

                # Log that the migration has been applied
                logger.info("Migration %s applied successfully.", migration.name)

# Run the migrations
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migrations()