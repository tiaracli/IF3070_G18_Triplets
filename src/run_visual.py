import json
import os

from core import load_problem
from data_io import FOLDER_OUTPUT, path_data, path_output
from visual import gambar_kapal, grafik_objective, grafik_peluang


def ubah_state(state):
    return tuple(tuple(p) for p in state)


def baca_json(folder, nama_file):
    path = os.path.join(FOLDER_OUTPUT, folder, nama_file)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def gambar_hc(problem, folder, nama_file):
    data = baca_json(folder, nama_file)
    if data is None:
        print(nama_file, "belum ada, jalankan run_hill_climbing.py dulu")
        return
    for d in data:
        nama = d["algorithm"] + "_" + d["objective"] + "_seed" + str(d["seed"])
        judul = d["algorithm"] + " (" + d["objective"] + "), seed " + str(d["seed"])
        gambar_kapal(problem, ubah_state(d["initial_state"]), judul + " - awal",
                     path_output(folder, nama + "_awal.png"))
        gambar_kapal(problem, ubah_state(d["final_state"]), judul + " - akhir",
                     path_output(folder, nama + "_akhir.png"))
        grafik_objective(d["history"], judul, path_output(folder, nama + "_grafik.png"))
        print(nama, "selesai")


def gambar_sa(kasus):
    problem = load_problem(path_data(kasus))
    for k in range(1, 4):
        d = baca_json("sa", kasus + "_run" + str(k) + ".json")
        if d is None:
            print(kasus, "run", k, "belum ada, jalankan run_sa.py dulu")
            continue
        nama = kasus + "_run" + str(k)
        judul = "Simulated Annealing " + kasus + ", run " + str(k)
        gambar_kapal(problem, ubah_state(d["initial_state"]), judul + " - awal",
                     path_output("sa", nama + "_awal.png"))
        gambar_kapal(problem, ubah_state(d["final_state"]), judul + " - akhir",
                     path_output("sa", nama + "_akhir.png"))
        grafik_objective(d["history"], judul, path_output("sa", nama + "_grafik.png"))
        peluang = []
        for i in range(len(d["probs"])):
            if d["probs"][i] is not None:
                peluang.append((i + 1, d["probs"][i]))
        grafik_peluang(peluang, judul, path_output("sa", nama + "_peluang.png"))
        print(nama, "selesai")


problem = load_problem(path_data("kasus_1"))
gambar_hc(problem, "hc", "detail_hc.json")
gambar_hc(problem, "bonus_eta", "detail_eta.json")
gambar_sa("kasus_1")
gambar_sa("kasus_multi")
print("selesai, gambar ada di output/hc, output/bonus_eta, output/sa")
