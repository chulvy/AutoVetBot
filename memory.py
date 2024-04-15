import json


class Memory:
    def __init__(self, filepath):
        self.filepath = filepath

    def get_data(self, key):
        try:
            with open(self.filepath, 'rt', encoding='utf-8') as f:
                return json.loads(f.read()).get(str(key))
        except FileNotFoundError:
            print('File not found')
            return None

    def add_data(self, key, value):
        try:
            with open(self.filepath, 'rt', encoding='utf-8') as f:
                data = json.loads(f.read())
        except FileNotFoundError:
            print('File not found. Creating new')
            data = {}

        try:
            data[str(key)] = value
        except TypeError as e:
            print(f"TypeError: {e}")
        with open(self.filepath, 'wt', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4, default=str)

    def del_data(self, key):
        try:
            with open(self.filepath, 'rt', encoding='utf-8') as f:
                data = json.loads(f.read())
        except FileNotFoundError:
            print('File not found')
            return None

        data.pop(str(key), None)
        with open(self.filepath, 'wt', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_all_data(self):
        try:
            with open(self.filepath, 'rt', encoding='utf-8') as f:
                return json.loads(f.read())
        except FileNotFoundError:
            print('File not found')
            return {}
