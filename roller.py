import os
from flask_cors import CORS
from dotenv import load_dotenv
from flask import Flask, render_template, request

import util
from cloud_connection import get_existing_tables_from_cloud

app = Flask(__name__)
cors = CORS(app)


def get_table(name, fuzzy=False):
    print("GETTABLE", name, fuzzy)
    if fuzzy:
        name = util.find_best_match([table.name.lower() for table in tables], name)
    for table in tables:
        if table.name.lower() == name.lower():
            return table


def render(table, html):
    text = 'Tabelle wählen und würfeln.'
    info = ''
    if get_table(table) is not None:
        table_obj = get_table(table)
        text = table_obj.roll(-1)[1]
        info = table_obj.get_info()
    return render_template(html,
                           option_list=table_map,
                           text=text,
                           misc=info,
                           selected={'selected': table},
                           last_update=last_update,
                           base_bproller_url=os.getenv("SITE_URL"))


@app.route("/<table>")
def hello_table(table):
    return render(table, "main.html")


@app.route("/")
def hello():
    return render("", "main.html")


@app.route("/search/")
def hello_search():
    return render("", "search.html")


@app.route("/embed/")
def hello_embed():
    return render("", "embed.html")


@app.route("/embed_small/<table>")
def hello_embed_small(table):
    return render(table, "embed_small.html")


@app.route("/api/<table>")
def api_call(table):
    if get_table(table) is None:
        return "Unbekannte Tabelle. Bitte URL verbessern"
    text = get_table(table).roll(-1)[1]
    return text


@app.route("/fuzzyapi/<table>")
def fuzzyapi_call(table):
    table = get_table(table, fuzzy=True)
    if table is None:
        return "Unbekannte Tabelle. Bitte Anfrage verbessern"
    text = f"<i>Tabelle: {table.name}</i><br>"
    text += table.roll(-1)[1]
    return text


@app.route('/', methods=["GET", "POST"])
def button():
    table = request.form['tables']
    return render(table, "main.html")


@app.route('/<table>', methods=["GET", "POST"])
def button_table(table):
    table_post = request.form['tables']
    return render(table_post, "main.html")


@app.route('/search/', methods=["GET", "POST"])
def button_search():
    table_post = request.form['tables']
    return render(table_post, "search.html")


@app.route('/embed/', methods=["GET", "POST"])
def button_embed():
    table = request.form['tables']
    return render(table, "embed.html")


@app.route('/embed_small/<table>', methods=["GET", "POST"])
def button_embed_small(table):
    return render(table, "embed_small.html")


@app.route('/table_update/', methods=["POST"])
def update_table_data():
    key = request.form['key']
    if key == os.getenv("UPDATE_KEY"):
        get_existing_tables_from_cloud()
        global tables
        global table_map
        global sort_map
        sort_map = util.parse_category_config()
        tables, table_map = util.read_tables(sort_map)
        util.check_table_completeness(tables, sort_map)
        global last_update
        last_update = util.read_last_crawl()
        return "UPDATE INITIATED"
    else:
        return "PERMISSION DENIED (UPDATEKEY)"


@app.route('/log/')
def show_log():
    with open(util.log_path, encoding='cp1252') as log_file:
        lines = log_file.readlines()
    return '<br>'.join(lines)


here = os.path.dirname(__file__)
load_dotenv(f"{here}/.env")
curr_value = -1
util.path = os.getenv("BW_DATA_FOLDER")
path = util.path
util.config_path = os.getenv("BW_CONFIG_FOLDER")
util.log_path = os.getenv("BW_LOG_PATH")
if not os.path.isfile(f"{util.config_path}/last_crawl.txt"):
    util.ensure_directories()
    get_existing_tables_from_cloud()
else:
    print("Skipping File download, since last_crawl.txt exists.")
sort_map = util.parse_category_config()
tables, table_map = util.read_tables(sort_map)
last_update = util.read_last_crawl()

# print([table.name for table in tables])
if __name__ == "__main__":
    app.run(debug=True)
