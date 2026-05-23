import json
from pathlib import Path

from PySide2.QtGui import QColor
from importlib.resources import files

def _load_config(file_path):
    with open(file_path, 'r') as config_file:
        content = config_file.read()
        data = json.loads(content)

    return data


def convert_data_to_color(data=None):
    if len(data) == 3:
        color = QColor(data[0], data[1], data[2])
    elif len(data) == 4:
        color = QColor(data[0], data[1], data[2], data[3])
    else:
        color = QColor(120, 120, 120)

    return color


def split_string(data: str, max_line_length: int):
    words = data.split(sep=" ")
    new_str = ""
    acum_length = 0
    for w in words:
        if acum_length + len(w) <= max_line_length:
            new_str += w + " "
            acum_length += len(w) + 1
        else:
            new_str = new_str.strip()
            new_str += "\n" + w + " "
            acum_length = len(w)

    return new_str.strip()


app_config = _load_config(files('co_razon.util').joinpath(Path('config.json')))
db_config = _load_config(files('co_razon.util').joinpath(Path('db_config.json')))
