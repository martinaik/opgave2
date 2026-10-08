# Import necessary modules
from app.database import get_connection

def test_database_connection() -> None:
    """ Tests the database connection. """
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

        assert result[0] == 1

    finally:
        connection.close()