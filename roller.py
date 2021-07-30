import os
from flask_cors import CORS
from dotenv import load_dotenv
from flask import Flask, request

from flask import session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import util
import controller

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
here = os.path.dirname(__file__)
load_dotenv(f"{here}/.env")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_server = os.getenv("DB_SERVER")
db_name = os.getenv('DB_NAME')
db_socket = os.getenv("DB_SOCKET")
user_pass = f'mysql+pymysql://{db_user}:{db_password}@'
app.config['SQLALCHEMY_DATABASE_URI'] = user_pass + db_server + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
Session(app)

cors = CORS(app)

util.path = os.getenv("BW_DATA_FOLDER")
util.config_path = os.getenv("BW_CONFIG_FOLDER")
util.log_path = os.getenv("BW_LOG_PATH")
util.sql_path = os.getenv("BW_SQL_PATH")

"""
    BEFORE EACH REQUEST
"""


@app.before_request
def before_request_func():
    controller.session_setup()


"""
    DEFAULT SITE
"""


@app.route("/")
def hello():
    return controller.render("", "main.html")


@app.route('/', methods=["GET", "POST"])
def button():
    table = request.form['tables']
    return controller.render(table, "main.html")


"""
    SEARCH VIEW 
"""


@app.route("/search/")
def hello_search():
    return controller.render("", "search.html")


@app.route('/search/', methods=["GET", "POST"])
def button_search():
    table_post = request.form['tables']
    return controller.render(table_post, "search.html")


"""
    LINK OVERVIEW
"""

@app.route("/links/")
def hello_links():
    return controller.render("", "links.html")

"""
    ONE TABLE VIEW
"""


@app.route("/<table>")
def hello_table(table):
    return controller.render(table, "embed_small.html")


@app.route('/<table>', methods=["GET", "POST"])
def button_table(table):
    return controller.render(table, "embed_small.html")


"""
    API CALLS
"""


@app.route("/api/<table>")
def api_call(table):
    if controller.get_table(table) is None:
        return "Unbekannte Tabelle. Bitte URL verbessern"
    text = controller.get_table(table).roll(-1)[1]
    return text


@app.route("/fuzzyapi/<table>")
def fuzzyapi_call(table):
    table = controller.get_table(table, fuzzy=True)
    if table is None:
        return "Unbekannte Tabelle. Bitte Anfrage verbessern"
    text = f"<i>Tabelle: {table.name}</i><br>"
    text += table.roll(-1)[1]
    return text


"""
    CONFIG CALLS
"""


@app.route('/table_update/', methods=["POST"])
def update_table_data():
    key = request.form['key']
    if key == os.getenv("UPDATE_KEY"):
        controller.update_tables()
        return "UPDATE SUCCESSFUL"
    else:
        return "PERMISSION DENIED (UPDATEKEY)"


@app.route('/log/')
def show_log():
    with open(util.log_path, encoding='cp1252') as log_file:
        lines = log_file.readlines()
    return '<br>'.join(lines)


"""
    TESTING
"""


@app.route('/refresh/')
def refresh_session():
    session.clear()
    return "Session cookies cleared"


@app.route('/session/')
def session_call():
    controller.session_setup()
    return 'ok'


@app.route('/session_get/')
def session_get():
    return '<br>'.join([x[0] for x in session['table_list']])


@app.route('/db/')
def db_test():
    try:
        controller.update_tables()
        return '<h1>It works.</h1>'
    except Exception as e:
        # see Terminal for description of the error
        print("\nThe error:\n" + str(e) + "\n")
        return '<h1>Something is broken.</h1>'


# print([table.name for table in tables])
if __name__ == "__main__":
    app.run(debug=True)

# OLD EMBEDS not needed anymore?
# @app.route('/embed/', methods=["GET", "POST"])
# def button_embed():
#     table = request.form['tables']
#     return render(table, "embed.html")
#
#
# @app.route('/embed_small/<table>', methods=["GET", "POST"])
# def button_embed_small(table):
#     return render(table, "embed_small.html")
#
#
# @app.route("/embed/")
# def hello_embed():
#     return render("", "embed.html")
#
#
# @app.route("/embed_small/<table>")
# def hello_embed_small(table):
#     return render(table, "embed_small.html")
