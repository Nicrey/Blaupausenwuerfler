import random


class Table:
    def __init__(self, name, die, link):
        self.name = name
        self.die = die
        self.max_roll = int(die.split('W')[1])
        self.entries = {}
        self.authors = ''
        self.link = link
        self.idea = ''
        self.is_table_table = False
        self.display_name = name.replace(die, '').strip() + f' ({die})'
        self.display_name = f"{self.display_name[0].upper()}{self.display_name[1:]}"

    def add_entry(self, roll, string):
        self.entries[str(int(roll))] = string.replace('\u2028', '').replace('\u0155', '')

    def add_authors(self, authors):
        self.authors = authors.replace('\n', '')

    def add_idea(self, idea):
        self.idea = idea.replace('\n', '')

    def roll(self, current):
        die = self.max_roll
        new_value = random.randint(1, die)
        while new_value == current:
            new_value = random.randint(1, die)
        if self.is_table_table:
            return new_value, str(new_value) + ':<br><br>' + "<table></tr>" + self.entries[str(new_value)] + "</table>"
        return new_value, self.entries[str(new_value)]


    @staticmethod
    def read_table(file):
        print(f"Reading Table {file}")
        with open(file, encoding='utf-8') as file:
            lines = file.readlines()
        link = lines[0].replace('\n', '')
        name = lines[1].replace('\n', '')
        idea = lines[2].replace('\n', '')
        authors = lines[3].replace('\n', '')
        die = lines[4].replace('\n', '')
        t = Table(name, die, link)
        t.add_idea(idea)
        t.add_authors(authors)
        entry = ''
        roll = ''
        for line in lines[5:]:
            if line == '':
                continue
            if '~~~' not in line:
                entry += '\n' + line.replace('\n', '')
            else:
                if roll != '':
                    t.add_entry(roll, entry)
                roll = line.split('~~~')[0]
                entry = line[len(roll) + 3:].replace('\n', '')
                if roll.startswith('T'):
                    t.is_table_table = True
                    roll = roll[1:]
        t.add_entry(roll, entry)
        return t

    def get_info(self):
        return f'''{self.idea + "<br>" if self.idea != "" else ""}{self.authors} <br> <a href="{self.link}">Komplette Tabelle</a>'''


