import util
from roller import db
from table import Table


def setup_next_table():
    query = "DROP TABLE IF EXISTS roll_tables_next"
    db.session.execute(query)
    query = util.get_sql_query("create_tables_table.sql")
    db.session.execute(query)


def setup_config_table():
    query = "DROP TABLE IF EXISTS config_next"
    db.session.execute(query)
    query = util.get_sql_query("create_config_table.sql")
    db.session.execute(query)


def insert_table(table, category):
    table_json = table.to_json()
    table_json = table_json.replace("\\", "\\\\")
    table_json = table_json.replace("'", "\\'")
    table_name = table.name
    if isinstance(table, Table):
        table_type = "Table"
    else:
        table_type = "Generator"
    query = util.get_sql_query("insert_table.sql")
    query = query.replace("$$TABLE_NAME$$", table_name)
    query = query.replace("$$CATEGORY$$", category)
    query = query.replace("$$TABLE_JSON$$", table_json)
    query = query.replace("$$TABLE_TYPE$$", table_type)
    db.session.execute(query)


def insert_config(last_update):
    query = f"INSERT INTO config_next VALUES ('{last_update}')"
    db.session.execute(query)


def switch_schema(table_name):
    query = f"DROP TABLE IF EXISTS {table_name};"
    db.session.execute(query)
    query = util.get_sql_query("swap_schema.sql").replace("$$TABLE_NAME$$", table_name)
    db.session.execute(query)


def get_table_json_from_db(name):
    query = f"SELECT table_json, table_type FROM roll_tables WHERE table_name='{name}'"
    result = db.session.execute(query)
    return result.all()[0]


def get_table_list_from_db():
    query = f"SELECT table_name, table_category FROM roll_tables"
    result = db.session.execute(query)
    return result.all()


def get_last_update_from_db():
    query = f"SELECT last_update FROM config"
    result = db.session.execute(query)
    return result.all()[0][0]