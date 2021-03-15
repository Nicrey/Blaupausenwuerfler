from fuzzywuzzy import process, fuzz

path = ""

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
    with open(f"{path}/config_categories") as read:
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
    tops = sorted([r for r  in res if r[1] == res[0][1]], key=lambda x: len(x[0]))
    return tops[0][0]
