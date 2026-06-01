import pytest
from db.init import initialize_database


@pytest.mark.db
def test_initialize_fresh_db(postgres_connection):
    initialize_database(postgres_connection)  # должно пройти без ошибок
