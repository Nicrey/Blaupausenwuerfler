import copy
import itertools
import random
import re


class TableWrapper:
    def __init__(self, name, table):
        self.name = name
        self.table = table
        self.lookup = False
        self.finished = True

    def roll(self):
        return self.table.roll(-1)


class GeneratorTable:
    def __init__(self, name, die, lookup):
        self.name = name
        self.die = die
        self.lookup = lookup
        self.max_roll = int(die.split('W')[1]) if not lookup else 0
        self.entries = {}

    def roll(self):
        return self.entries[str(random.randint(1, self.max_roll))]

    def add_entry(self, roll, entry):
        if self.lookup:
            self.entries[str(roll)] = entry.replace('\u2028', '').replace('\u0155', '')
        else:
            self.entries[str(int(roll))] = entry.replace('\u2028', '').replace('\u0155', '')


class TagHierarchy:
    def __init__(self, hierarchy_string):
        self.hierarchy = {symbol: i for i, symbol in enumerate(hierarchy_string.split('>'))}

    def combine_tags(self, s1: str, s2: str):
        return ''.join(sorted(s1 + s2, key=lambda x: self.hierarchy[x]))

    def rate(self, s):
        sum = 0
        for tag in s:
            sum += self.hierarchy[tag]
        return len(s) * max(self.hierarchy.values()) - sum


class Replacement:
    def __init__(self, adapt, values, adapt_value, modifier, hierarchy, subtables, name, result=None):
        self.adapt = adapt
        self.values = values
        self.adapt_value = adapt_value
        self.modifier = modifier
        self.result = result
        self.tag_hierarchy = hierarchy
        self.subtables = subtables
        self.name = name

    def is_finished(self):
        return self.result is not None

    def add_modifier(self, mod):
        self.adapt_value = self.tag_hierarchy.combine_tags(self.adapt_value, mod)
        self.modifier = self.tag_hierarchy.combine_tags(self.modifier, mod)

    def try_finish(self, current_i, replacements):
        if self.is_finished():
            return True
        if replacements[current_i + self.adapt].is_finished() or self.adapt == 0:
            if self.adapt != 0:
                self.adapt_value = self.tag_hierarchy.combine_tags(self.adapt_value,
                                                                   replacements[current_i + self.adapt].adapt_value)
                self.modifier = self.tag_hierarchy.combine_tags(self.modifier,
                                                                replacements[current_i + self.adapt].adapt_value)

            combs = [self.modifier[x:y] for x, y, in itertools.combinations(range(len(self.modifier) + 1), r=2)]
            for comb in sorted(combs, key=lambda x: (len(x), self.tag_hierarchy.rate(x)), reverse=True):
                if comb in self.values:
                    self.result = self.values[comb]
                    break
            if self.result is None:
                self.result = self.values['Default']
            while '{' in self.result:
                self.resolve_result()

    def resolve_result(self):
        sub_tables = re.findall(r'{(.*?)\}', self.result)
        for table in sub_tables:
            table_name, modifier, adapt = parse(table)
            result = self.subtables[table_name].roll()
            if isinstance(self.subtables[table_name], TableWrapper):
                self.result = self.result.replace('{' + table + '}', result[1], 1)
                continue
            adapt_value = result.split('***')[1] if '***' in result else ''
            self.adapt_value = self.tag_hierarchy.combine_tags(self.adapt_value, adapt_value)
            variants = {variant.split(':')[0]: variant.split(':')[1] for variant in re.findall(r'\[(.*?)\]', result)}
            variants['Default'] = result.split('[')[0].split('***')[0]
            combs = [self.modifier[x:y] for x, y, in itertools.combinations(range(len(self.modifier) + 1), r=2)]
            replace = False
            for comb in sorted(combs, key=lambda x: (len(x), self.tag_hierarchy.rate(x)), reverse=True):
                if comb in variants:
                    self.result = self.result.replace('{' + table + '}', variants[comb], 1)
                    replace = True
                    break
            if not replace:
                self.result = self.result.replace('{' + table + '}', variants['Default'], 1)


def parse(syntax):
    table_name = re.findall(r'(.*?)[~-]', syntax)[0] if '~' in syntax or '-' in syntax else syntax
    modifier = re.findall(r'.*~(.*?)$', syntax)[0].replace('-', '').replace('>', '') if '~' in syntax else ''
    if '->' in syntax:
        adapt = len(re.findall(r'.*-(.*?)$', syntax)[0])
    elif '-<' in syntax:
        adapt = -len(re.findall(r'.*-(.*?)$', syntax)[0])
    else:
        adapt = 0
    return table_name, modifier, adapt


class Generator:

    def __init__(self, link, name):
        self.link = link
        self.name = name
        self.idea = ''
        self.authors = ''
        self.main_table = None
        self.sub_tables = {}
        self.lookups = {}
        self.tag_hierarchy = {}
        self.display_name = name
        self.max_roll = 0

    def add_table(self, table):
        if table.lookup:
            self.lookups[table.name] = table
        else:
            self.sub_tables[table.name] = table

    def roll(self, _):
        # Current Value can be ignored since the same result will rarely be there, since there are a lot more options
        # Roll on Main Table
        syntax = self.main_table.roll()
        # Parse Result and Roll accordingly on subtables
        subtables = re.findall(r'\[(.*?)\]', syntax.split('|||')[0])
        replacements = []
        for table in subtables:
            replacement = self.roll_table(table)
            if replacement:
                replacements.append(self.roll_table(table))
            replacement = self.lookup_table(table)
            if replacement:
                replacements.append(self.lookup_table(table))

        variant_str = []
        if '|||' in syntax:
            variants = {}
            variant = syntax.split('|||')[1]
            variant_mod = variant[1]
            changed_tables = re.findall(r'\[(.*?)\]', variant[2:])
            combs = []
            for i in range(0, len(changed_tables)):
                combs += itertools.combinations(changed_tables, r=i + 1)
            for comb in combs:
                variants[comb] = copy.deepcopy(replacements)
                for repl in variants[comb]:
                    if repl.name in comb:
                        repl.add_modifier(variant_mod)
                finished = 0
                while finished < len(variants[comb]):
                    finished = 0
                    for i, replacement in enumerate(variants[comb]):
                        replacement.try_finish(i, variants[comb])
                        if replacement.is_finished():
                            finished += 1
                        else:
                            finished = 0

                base_syntax = syntax.split('|||')[0]
                for replacement in variants[comb]:
                    base_syntax = base_syntax.replace(f"[{replacement.name}]", replacement.result, 1)
                variant_str.append(f"{base_syntax[0].upper()}{base_syntax[1:]}")

        finished = 0
        while finished < len(replacements):
            finished = 0
            for i, replacement in enumerate(replacements):
                replacement.try_finish(i, replacements)
                if replacement.is_finished():
                    finished += 1
                else:
                    finished = 0
        syntax = syntax.split('|||')[0]
        for subtable, replacement in zip(subtables, replacements):
            syntax = syntax.replace(f"[{subtable}]", replacement.result, 1)
        if variant_str:
            str = f"{syntax[0].upper()}{syntax[1:]}<br><br><i>Alternativen:"
            for s in variant_str:
                str += f'<br>{s[0].upper()}{s[1:]}'
            return 1, f"{str}</i>"
        return 1, f"{syntax[0].upper()}{syntax[1:]}"

    def lookup_table(self, syntax):
        table_name, modifier, adapt = parse(syntax)
        if table_name not in self.lookups:
            return False
        return Replacement(adapt, self.lookups[table_name].entries, '', modifier, self.tag_hierarchy, self.sub_tables,
                           syntax)

    def roll_table(self, syntax):
        table_name, modifier, adapt = parse(syntax)
        if table_name not in self.sub_tables:
            return False
        result = self.sub_tables[table_name].roll()
        if isinstance(self.sub_tables[table_name], TableWrapper):
            return Replacement(0, [], '', '', self.tag_hierarchy, self.sub_tables, '', result[1])
        adapt_value = result.split('***')[1] if '***' in result else ''
        variants = {variant.split(':')[0]: variant.split(':')[1] for variant in re.findall(r'\[(.*?)\]', result)}
        variants['Default'] = result.split('[')[0].split('***')[0]
        return Replacement(adapt, variants, adapt_value, modifier, self.tag_hierarchy, self.sub_tables, syntax)

    def get_info(self):
        return f'''{self.idea + "<br>" if self.idea != "" else ""}{self.authors} <br> <a href="{self.link}">Komplette Tabelle</a>'''

    @staticmethod
    def read_table(lines: [str], tables: [] = None):
        import_t = False
        if '###' in lines[0]:
            lookup = False
        elif '|||' in lines[0]:
            lookup = True
        elif '§§§' in lines[0]:
            import_t = True
            lookup = False
        else:
            raise Exception('Error reading Generator Table, no valid start sequence')
        if lookup:
            name = lines[0].replace('|||', '')
            die = None
        elif import_t:
            table = [table for table in tables if table.name == lines[1]][0]
            return TableWrapper(lines[0].replace('§§§', ''), table), lines[2:]
        else:
            name = lines[0].replace('###', '')
            die = lines[1]
        table = GeneratorTable(name, die, lookup)
        i = 0
        for i, line in enumerate(lines[1:] if lookup else lines[2:]):
            if line.startswith('###'):
                break
            if line.startswith('|||'):
                break
            if line.startswith('§§§'):
                break
            table.add_entry(line.split('~~~')[0], line.split('~~~')[1])
        return table, lines[i + (1 if lookup else 2):]

    @staticmethod
    def read_generator(file, tables=None):
        with open(file, encoding='utf-8') as read:
            lines = [line.replace('\n', '') for line in read.readlines()]
        link = lines[0]
        name = lines[1]
        generator = Generator(link, name)
        generator.idea = lines[2]
        generator.authors = lines[3]
        generator.tag_hierarchy = TagHierarchy(lines[5])
        generator.main_table, remaining_lines = Generator.read_table(lines[6:], tables)
        while len(remaining_lines) > 1:
            table, remaining_lines = Generator.read_table(remaining_lines, tables)
            generator.add_table(table)
        return generator
