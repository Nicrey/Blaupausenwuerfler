import os
import shutil
from os import listdir

from fuzzywuzzy import process, fuzz

from generator import Generator
from table import Table

path = ""
crawl_path = 'crawled_tables'
config_path = "config"
log_path = "log.txt"
sql_path = "sql"

GENERATOR_PRE = 'Generator'
MULTGENERATOR_PRE = 'MultiGenerator'
CONFIG_PRE = 'config'


def is_table(filename):
    if filename.startswith(GENERATOR_PRE) \
            or filename.startswith(MULTGENERATOR_PRE) \
            or filename.startswith(CONFIG_PRE):
        return False
    return True


def is_generator(filename):
    return filename.startswith(GENERATOR_PRE)


def is_multi_generator(filename):
    return filename.startswith(MULTGENERATOR_PRE)


def is_config(filename):
    return filename.startswith(CONFIG_PRE)


def parse_category_config():
    with open(f"{config_path}/config_categories", encoding='cp1252') as read:
        all_lines = read.readlines()
    sort_map = {}

    current_key = ''
    for line in all_lines:
        if line.startswith('###'):
            current_key = line[3:]
            sort_map[current_key] = []
        else:
            sort_map[current_key].append(line.replace('\n', ''))
    return sort_map


def find_best_match(name_list, input):
    if ' ' in input:
        res = process.extract(input.lower(), name_list, limit=10, scorer=fuzz.token_set_ratio)
    else:
        res = process.extract(input.lower(), name_list, limit=10)
    tops = sorted([r for r in res if r[1] == res[0][1]], key=lambda x: len(x[0]))
    return tops[0][0]


def ensure_directory(path):
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        pass
    os.mkdir(path)


def ensure_directories():
    print(config_path, path, log_path)
    print("Recreating directories")
    ensure_directory(config_path)
    ensure_directory(path)


def check_table_completeness(tables, sort_map):
    """
    Checks if all the tables mentioned in the category file,
    are also found in the final tables
    Checks also for missing entries for author/idea in all tables
    Logs it all to a logfile available via /log/
    :param tables: the parsed tables
    :param sort_map: the sort map based on the categories config file
    :return:
    """
    table_links = [table.link for table in tables]
    missing_tables = []
    # Check for missing tables
    for category in sort_map:
        for table_link in sort_map[category]:
            if table_link not in table_links:
                missing_tables.append((category, table_link))

    # Check for missing author/idea
    missing_idea = []
    missing_authors = []
    for table in tables:
        if not table.idea:
            missing_idea.append(table.link)
        elif len(table.idea) < 6:
            missing_idea.append(table.link)

        if not table.authors:
            missing_authors.append(table.link)
        elif table.authors.startswith('Mit') and len(table.authors) < 20:
            missing_authors.append(table.link)
        elif table.authors.startswith('Autor') and len(table.authors) < 13:
            missing_authors.append(table.link)


    # Write log
    with open(log_path, 'w', encoding='cp1252') as log_file:
        log_file.write("Fehlende Tabellen laut Index:\n")
        for category, table_link in missing_tables:
            category_clean = category.replace('\n', '')
            log_file.write(f"{category_clean} -> {table_link}\n")

        log_file.write("########################\n")
        log_file.write("Fehlender Ideengeber:\n")
        for table_link in missing_idea:
            log_file.write(f"{table_link}\n")

        log_file.write("#######################\n")
        log_file.write("Fehlende Autor:innen:\n")
        for table_link in missing_authors:
            log_file.write(f"{table_link}\n")


def read_tables(sort_map):
    print("Reading normal Tables")
    tables = [Table.read_table(f"{path}/{f}") for f in listdir(f"{path}/") if is_table(f)]
    print("Reading Generator-Tables")
    tables += [Generator.read_generator(f"{path}/{f}") for f in listdir(f"{path}/") if is_generator(f)]
    tables += [Generator.read_generator(f"{path}/{f}", tables) for f in listdir(f"{path}/") if
               is_multi_generator(f)]
    table_map = {}
    print("Sorting Tables")

    for cat in sort_map:
        table_map[cat] = []
        for table in tables:
            if table.link in sort_map[cat]:
                table_map[cat].append(table)
        table_map[cat] = sorted(table_map[cat], key=lambda x: (x.display_name, x.max_roll))
    print("Checking Tables")

    return tables, table_map


def read_last_crawl():
    with open(f"{config_path}/last_crawl.txt") as last_crawl:
        return last_crawl.readline()


def get_sql_query(file):
    with open(f"{sql_path}/{file}") as sql_file:
        lines = sql_file.readlines()
    return ' '.join(lines)
