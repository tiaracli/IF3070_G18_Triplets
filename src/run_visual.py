import json
import os

from core import read_data
from data_io import FOLDER_OUTPUT, path_data, path_output
from visual import gambar_kapal, grafik_objective, grafik_peluang, grafik_banding, grafik_restart

NAMA_HC = {
    "steepest": "Steepest Ascent",
    "stochastic": "Stochastic",
    "sideways": "Sideways Move",
    "random_restart": "Random Restart",
}

NAMA_KASUS = {
    "kasus_1": "kasus_satu_kapal",
    "kasus_multi": "kasus_multi_kapal",
}


def ubah_state(state):
    return tuple(tuple(p) for p in state)


def baca_json(folder, nama_file):
    path = os.path.join(FOLDER_OUTPUT, folder, nama_file)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def visual_hc(problem, folder, nama_file):
    data = baca_json(folder, nama_file)
    if data is None:
        print(nama_file, "belum ada, jalankan run_hill_climbing.py dulu")
        return

    per_seed = {}
    for d in data:
        nama = d["algorithm"] + "_" + d["objective"] + "_seed" + str(d["seed"])
        judul = NAMA_HC[d["algorithm"]] + " Hill Climbing"
        if d["objective"] == "eta":
            judul += " objective ETA"
        judul += ", seed " + str(d["seed"])

        gambar_kapal(problem, ubah_state(d["initial_state"]), judul + " (awal)",
                     path_output(folder, nama + "_awal.png"))
        gambar_kapal(problem, ubah_state(d["final_state"]), judul + " (akhir)",
                     path_output(folder, nama + "_akhir.png"))
        if "all_histories" in d:
            grafik_restart(d["all_histories"], judul, path_output(folder, nama + "_grafik.png"))
        else:
            grafik_objective(d["history"], judul, path_output(folder, nama + "_grafik.png"))

        if d["seed"] not in per_seed:
            per_seed[d["seed"]] = []
        per_seed[d["seed"]].append(d)
        print(nama, "selesai")

    for seed in per_seed:
        riwayat = []
        label = []
        for d in per_seed[seed]:
            riwayat.append(d["history"])
            if d["algorithm"] == "random_restart":
                label.append("Random Restart (restart terbaik)")
            else:
                label.append(NAMA_HC[d["algorithm"]])
        judul = "Perbandingan varian Hill Climbing"
        if per_seed[seed][0]["objective"] == "eta":
            judul += " objective ETA"
        grafik_banding(riwayat, label, judul + ", seed " + str(seed),
                       path_output(folder, "banding_seed" + str(seed) + ".png"))


def gambar_sa(kasus):
    problem = read_data(path_data(kasus))
    riwayat = []
    label = []
    for k in range(1, 4):
        d = baca_json("sa", kasus + "_run" + str(k) + ".json")
        if d is None:
            print(kasus, "run", k, "belum ada, jalankan run_sa.py dulu")
            continue
        nama = kasus + "_run" + str(k)
        judul = "Simulated Annealing " + NAMA_KASUS[kasus] + ", run " + str(k)
        gambar_kapal(problem, ubah_state(d["initial_state"]), judul + " (awal)",
                     path_output("sa", nama + "_awal.png"))
        gambar_kapal(problem, ubah_state(d["final_state"]), judul + " (akhir)",
                     path_output("sa", nama + "_akhir.png"))
        grafik_objective(d["history"], judul, path_output("sa", nama + "_grafik.png"))

        peluang = []
        for i in range(len(d["probs"])):
            if d["probs"][i] is not None:
                peluang.append((i + 1, d["probs"][i]))
        grafik_peluang(peluang, judul, path_output("sa", nama + "_peluang.png"))

        riwayat.append(d["history"])
        label.append("run " + str(k))
        print(nama, "selesai")

    if riwayat:
        grafik_banding(riwayat, label, "Simulated Annealing " + NAMA_KASUS[kasus] + ", 3 run",
                       path_output("sa", kasus + "_banding.png"), 1)


problem = read_data(path_data("kasus_1"))
visual_hc(problem, "hc", "detail_hc.json")
visual_hc(problem, "bonus_eta", "detail_eta.json")
gambar_sa("kasus_1")
gambar_sa("kasus_multi")
print("selesai, gambar ada di output/hc, output/bonus_eta, output/sa")