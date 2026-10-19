import csv
import os

FOLDER_SRC = os.path.dirname(os.path.abspath(__file__))
FOLDER_OUTPUT = os.path.join(FOLDER_SRC, "..", "output")


def path_data(nama):
    return os.path.join(FOLDER_SRC, "data", nama + ".json")


def path_output(folder, nama_file):
    os.makedirs(os.path.join(FOLDER_OUTPUT, folder), exist_ok=True)
    return os.path.join(FOLDER_OUTPUT, folder, nama_file)


def simpan_csv(baris, folder, nama_file):
    with open(path_output(folder, nama_file), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=baris[0].keys())
        writer.writeheader()
        writer.writerows(baris)
