import os

from flask import session, render_template

import database_handler
import util
from cloud_connection import get_existing_tables_from_cloud
from generator import Generator
from table import Table


def get_table(name, fuzzy=False):
    current_table = session.get('table', '')
    if current_table and current_table.name == name:
        return current_table
    print(f"Getting Table for input: {name}. Fuzzy: {fuzzy}", name, fuzzy)
    json, table_type = '', ''
    tables = session.get('tables', [])
    if fuzzy:
        name = util.find_best_match(tables, name)
    for table in tables:
        if table.lower() == name.lower():
            json, table_type = database_handler.get_table_json_from_db(name)
            break
    if json:
        print(f"Loading Table {name}.")
    else:
        print(f"No Table found for {name}.")
    if table_type == 'Table':
        current_table = Table.from_json(json)
        session['table'] = current_table
        return current_table
    if table_type == 'Generator':
        return Generator.from_json(json)


def update_tables():
    util.ensure_directories()
    get_existing_tables_from_cloud()
    sort_map = util.parse_category_config()
    tables, table_map = util.read_tables(sort_map)
    util.check_table_completeness(tables, sort_map)
    database_handler.setup_next_table()
    database_handler.setup_config_table()
    last_update = util.read_last_crawl()
    database_handler.insert_config(last_update)
    for category in table_map:
        for table in table_map[category]:
            database_handler.insert_table(table, category)
    database_handler.switch_schema("roll_tables")
    database_handler.switch_schema("config")
    from roller import db
    db.session.commit()


def session_setup():
    print("Session setup")
    if session.get('tables', []):
        return
    table_list = database_handler.get_table_list_from_db()
    session['tables'] = [table_tuple[0] for table_tuple in table_list]
    sort_map = {}
    for table,category in table_list:
        category = category.replace('\n', '')
        if not category in sort_map:
            sort_map[category] = []
        sort_map[category].append(table)
    session['sort_map'] = sort_map
    last_update = database_handler.get_last_update_from_db()
    session['last_update'] = last_update


def render(table, html):
    text = 'Tabelle wählen und würfeln.'
    info = ''
    if get_table(table) is not None:
        table_obj = get_table(table)
        text = table_obj.roll(-1)[1]
        info = table_obj.get_info()
    # print(session.get('sort_map'))
    return render_template(html,
                           option_list=session.get('sort_map', {}),
                           text=text,
                           misc=info,
                           selected={'selected': table},
                           last_update=session.get('last_update'),
                           base_bproller_url=os.getenv("SITE_URL"))
