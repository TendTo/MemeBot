"""Test all the modules related to data management"""
from modules.data.db_manager import DbManager


def test_stupid():
    assert True


def test_local_db():
    db_manager = DbManager()
    db_manager.use_remote_db = False
    db_manager.query_from_file("data/db/db_test_local.sql")
    query_result = db_manager.select_from("test_table")
    db_manager.query_from_string("DROP TABLE IF EXISTS test_table;")

    result = ""
    for row in query_result:
        row_result = ", ".join(str(value) for value in row.values())
        result += row_result + "\n"

    assert result == "1, test, 2016-06-22 19:10:25-07\n"\
                    "2, test2, big fest\n"


def test_remote_db():
    db_manager = DbManager()
    db_manager.use_remote_db = True
    db_manager.query_from_file("data/db/db_test_remote.sql")
    query_result = db_manager.select_from("test_table")
    db_manager.query_from_string("DROP TABLE IF EXISTS test_table;")

    result = ""
    for row in query_result:
        row_result = ", ".join(str(value) for value in row.values())
        result += row_result + "\n"

    assert result == "1, test, 2016-06-22 19:10:25\n"\
                    "2, test2, 2020-06-22 19:10:25\n"
