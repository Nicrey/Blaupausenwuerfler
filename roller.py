import os
from os import listdir
from flask_cors import CORS
from dotenv import load_dotenv
from flask import Flask, render_template, request

import util
from generator import Generator
from table import Table


app = Flask(__name__)
cors = CORS(app)
load_dotenv()


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
    return render_template(html, option_list=map, text=text, misc=info, selected={'selected': table})



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


curr_value = -1
util.path = os.getenv("BW_DATA_FOLDER")
path = util.path
tables = [Table.read_table(f"{path}/{f}") for f in listdir(f"{path}/") if util.is_table(f)]
tables += [Generator.read_generator(f"{path}/{f}") for f in listdir(f"{path}/") if util.is_generator(f)]
tables += [Generator.read_generator(f"{path}/{f}", tables) for f in listdir(f"{path}/") if util.is_multi_generator(f)]
map = {}
sort_map = util.parse_category_config()
for cat in sort_map:
    map[cat] = []
    for table in tables:
        if table.link in sort_map[cat]:
            map[cat].append(table)
    map[cat] = sorted(map[cat], key=lambda x: (x.display_name, x.max_roll))
print([table.name for table in tables])
if __name__ == "__main__":
    app.run(debug=True)
