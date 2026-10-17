# baca file data dan simpan/baca hasil run ke json
import json
import os

from core import load_problem as baca_json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_problem(nama):
    # nama = "kasus_1" atau "kasus_multi", filenya ada di src/data/
    problem = baca_json(os.path.join(ROOT, "src", "data", nama + ".json"))
    problem["name"] = nama
    return problem


def simpan_hasil(hasil, path):
    # state berupa tuple, json ga punya tuple jadi diubah ke list dulu
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = dict(hasil)
    for key in ["initial_state", "final_state"]:
        data[key] = [list(p) for p in data[key]]
    with open(path, "w") as f:
        json.dump(data, f, indent=1)


def baca_hasil(path):
    with open(path) as f:
        data = json.load(f)
    for key in ["initial_state", "final_state"]:
        data[key] = tuple(tuple(p) for p in data[key])
    return data 