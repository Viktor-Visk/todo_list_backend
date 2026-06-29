import os
import json


def print_with_indent(value, indent=0):
    indentation = '\t' * indent
    print(f'{indentation}{value}')


class Entry:
    def __init__(self, title, entries=None, parent=None):
        self.title = title
        if entries is None:
            entries = []
        self.entries = entries
        self.parent = parent

    def add_entry(self, entry):
        self.entries.append(entry)
        entry.parent = self

    def print_entries(self, indent=0):
        print_with_indent(self, indent)
        for entry in self.entries:
            entry.print_entries(indent + 1)

    def json(self):
        res = {
            "title": self.title,
            "entries": [entry.json() for entry in self.entries]
        }
        return res

    @classmethod
    def from_json(cls, value: dict):
        new_entry = cls(value["title"])
        for item in value.get("entries", []):
            new_entry.add_entry(cls.from_json(item))
        return new_entry

    def __str__(self):
        return self.title

    def save(self, path):
        file_path = os.path.join(path, f'{self.title}.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.json(), f, indent=4)

    @classmethod
    def load(cls, filename):
        with open(filename, "r", encoding='utf-8') as f:
            data = json.load(f)
        return Entry.from_json(data)


class EntryManager:
    def __init__(self, data_path):
        self.data_path = data_path
        self.entries = []

    def load(self):
        if not os.path.isdir(self.data_path):
            os.makedirs(self.data_path)
        else:
            for filename in os.listdir(self.data_path):
                if filename.endswith('json'):
                    entry = Entry.load(os.path.join(self.data_path, filename))
                    self.entries.append(entry)
        return self

    def add_entry(self, title: str):
        self.entries.append(Entry(title))

    def save(self):
        for entry in self.entries:
            entry.save(self.data_path)

    def delete(self, entry_name: str) -> bool:
        """ Удаляет запись из списка и стирает её файл с диска """
        # Проверяем, является ли удаляемый элемент корневым (файлом)
        for entry in self.entries:
            if entry.title == entry_name:
                # Формируем путь и удаляем файл с диска
                filename = f"{entry.title}.json"
                file_path = os.path.join(self.data_path, filename)
                # Стираем файл в системе
                if os.path.isfile(file_path):
                    os.remove(file_path)
                # Удаляем объект из списка в памяти
                self.entries.remove(entry)
                return True

        def _delete_recursive(current_node) -> bool:
            # Пытаемся достать список дочерних элементов (как атрибут или как ключ словаря)
            children = getattr(current_node, "entries", None)
            if children is None and isinstance(current_node, dict):
                children = current_node.get("entries")

            if not children or not isinstance(children, list):
                return False

            # Проверяем прямых детей на текущем уровне
            for child in children:
                child_title = getattr(child, "title", None)
                if child_title is None and isinstance(child, dict):
                    child_title = child.get("title")

                if child_title == entry_name:
                    children.remove(child)
                    return True

            # Если на этом уровне не нашли, идем глубже по дереву
            for child in children:
                if _delete_recursive(child):
                    return True
            return False
        # Если файл целиком не удален, ищем элемент внутри дерева каждого Entry
        for entry in self.entries:
            if _delete_recursive(entry):
                # Сохраняем обновленную структуру обратно в файл
                entry.save(self.data_path)
                return True

        return False