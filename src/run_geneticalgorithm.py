import csv
import os

from data_io import ROOT, load_problem, simpan_hasil
from geneticalgorithm import run_ga
from visual import gambar_state, plot_ga

OUTPUT = os.path.join(ROOT, "output")


def jalanin(problem, objective, populasi, iterasi, seed, run, folder):
    hasil = run_ga(problem, objective, populasi, iterasi, seed)
    nama = "ga_" + problem["name"] + "_" + objective + "_pop" + str(populasi) + \
           "_it" + str(iterasi) + "_run" + str(run)

    simpan_hasil(hasil, os.path.join(OUTPUT, folder, nama + ".json"))
    gambar = os.path.join(OUTPUT, "figures", folder)
    gambar_state(problem, hasil["initial_state"],
                 nama + " - state awal (" + str(hasil["initial_value"]) + ")",
                 os.path.join(gambar, nama + "_awal.png"))
    gambar_state(problem, hasil["final_state"],
                 nama + " - state akhir (" + str(hasil["final_value"]) + ")",
                 os.path.join(gambar, nama + "_akhir.png"))
    plot_ga(hasil, nama, os.path.join(gambar, nama + "_plot.png"))

    print(nama, "awal:", hasil["initial_value"], "akhir:", hasil["final_value"],
          "durasi:", round(hasil["duration_s"], 2), "detik")

    return {
        "folder": folder, "dataset": problem["name"], "objective": objective,
        "populasi": populasi, "iterasi": iterasi, "run": run, "seed": seed,
        "nilai_awal": hasil["initial_value"], "nilai_akhir": hasil["final_value"],
        "fee_akhir": hasil["final_fee"], "salah_zona": hasil["zone_violations"],
        "durasi_detik": round(hasil["duration_s"], 3),
    }


kasus_1 = load_problem("kasus_1")
kasus_multi = load_problem("kasus_multi")
ringkasan = []

for iterasi in [100, 200, 400]:
    for run, seed in [(1, 1), (2, 2), (3, 3)]:
        ringkasan.append(jalanin(kasus_1, "fee", 50, iterasi, seed, run, "ga/A_iterasi"))

for populasi in [20, 50, 100]:
    for run, seed in [(1, 4), (2, 5), (3, 6)]:
        ringkasan.append(jalanin(kasus_1, "fee", populasi, 200, seed, run, "ga/B_populasi"))

for run, seed in [(1, 1), (2, 2), (3, 3)]:
    ringkasan.append(jalanin(kasus_1, "eta", 50, 200, seed, run, "bonus_eta"))
for run, seed in [(1, 1), (2, 2), (3, 3)]:
    ringkasan.append(jalanin(kasus_multi, "fee", 50, 200, seed, run, "bonus_multi"))

with open(os.path.join(OUTPUT, "ga", "ringkasan_ga.csv"), "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=ringkasan[0].keys())
    writer.writeheader()
    writer.writerows(ringkasan)
print("ringkasan disimpan di output/ga/ringkasan_ga.csv")
