"""Test all the modules related to data management"""
from modules.data.db_manager import DbManager

TABLE_NAME = "test_table"


def query_to_string(query_result: list) -> str:
    """Converts a query result in a well formatted string

    Args:
        query_result (list): query result to be converted

    Returns:
        str: the corrisponding string
    """
    result = []
    for row in query_result:
        row_result = ", ".join(str(value) for value in row.values())
        result.append(row_result)
    return "\n".join(result)


def test_get_db(db_results):
    """Tests the get_db function for the database
    """
    for remote in db_results['remote']:
        DbManager.use_remote_db = remote
        conn, cur = DbManager.get_db()

        assert conn is not None
        assert cur is not None


def test_query_from_string(db_results):
    """Tests the query_from_string function for the database
    """
    for remote in db_results['remote']:
        DbManager.use_remote_db = remote
        DbManager.query_from_string("""CREATE TABLE temp
                                    (
                                        id int NOT NULL,
                                        PRIMARY KEY (id)
                                    );""",
                                    """DROP TABLE temp;""")

        assert True


def test_select_from(db_results):
    """Tests the select_from function for the local database
    """
    for remote in db_results['remote']:
        DbManager.use_remote_db = remote
        query_result = DbManager.select_from(
            table_name=TABLE_NAME, select="id, name, surname")

        assert query_to_string(query_result) == db_results['select_from']


def test_select_from_where(db_results):
    """Tests the select_from_where function for the database
    """
    for remote in db_results['remote']:
        DbManager.use_remote_db = remote
        query_result = DbManager.select_from_where(
            table_name=TABLE_NAME, where="id = 2 or id = 3", select="id, name")

        assert query_to_string(query_result) == db_results['select_from_where']


def test_count_from_where(db_results):
    """Tests the count_from_where function for the database
    """
    for remote in db_results['remote']:
        DbManager.use_remote_db = remote
        query_result = DbManager.count_from_where(
            table_name=TABLE_NAME, where=" id > 1")

        assert query_result == db_results['count_from_where']
