import argparse
import csv
import json
import os
import statistics

from core import read_data, show_layout, value_fee
from sa import simulated_annealing

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SEEDS = [11, 22, 33]      # seednya dicatat 


def simpan_result(problem, hasil, nama, k, folder):
    data = dict(hasil)
    for kunci in ("initial_state", "final_state", "best_state"):
        data[kunci] = [list(p) for p in hasil[kunci]]
    data["kasus"] = nama
    with open(os.path.join(folder, f"{nama}_run{k}.json"), "w") as f:
        json.dump(data, f)

    with open(os.path.join(folder, f"{nama}_run{k}.txt"), "w") as f:
        f.write(f"=== {nama} run {k} (seed {hasil['params']['seed']}) ===\n\n")
        f.write(f"STATE AWAL (value_fee {value_fee(problem, hasil['initial_state'])})\n")
        f.write(show_layout(problem, hasil["initial_state"]) + "\n\n")
        f.write(f"STATE AKHIR (value_fee {value_fee(problem, hasil['final_state'])})\n")
        f.write(show_layout(problem, hasil["final_state"]) + "\n")

def summary(nama, hasil_list):
    nilai = [h["final_value"] for h in hasil_list]
    return {
        "kasus": nama,
        "run": len(hasil_list),
        "nilai_akhir": " / ".join(str(v) for v in nilai),
        "rata2": round(statistics.mean(nilai), 1),
        "std": round(statistics.pstdev(nilai), 1),
        "terbaik": max(nilai),
        "iterasi": hasil_list[0]["iterations"],
        "durasi_rata2_detik": round(statistics.mean(h["duration"] for h in hasil_list), 2),
        "stuck_freq_rata2": round(statistics.mean(h["stuck_freq"] for h in hasil_list), 3),
        "worse_diterima_rata2": round(statistics.mean(h["worse_accepted"] for h in hasil_list)),
        "akhir_local_opt": f"{sum(h['final_local_opt'] for h in hasil_list)}/{len(hasil_list)}",
    }

def collect_summary(baris, folder):
    kolom = list(baris[0].keys())
    with open(os.path.join(folder, "ringkasan.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=kolom)
        w.writeheader()
        w.writerows(baris)
    with open(os.path.join(folder, "ringkasan.md"), "w") as f:
        f.write("| " + " | ".join(kolom) + " |\n")
        f.write("|" + "---|" * len(kolom) + "\n")
        for b in baris:
            f.write("| " + " | ".join(str(b[k]) for k in kolom) + " |\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kasus", nargs="+", default=["kasus_1", "kasus_multi"])
    ap.add_argument("--T0", type=float, default=100.0)
    ap.add_argument("--alpha", type=float, default=0.9998)
    ap.add_argument("--tmin", type=float, default=0.1)
    ap.add_argument("--out", default=os.path.join(ROOT, "output", "sa"))
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    semua = []
    for nama in args.kasus:
        problem = read_data(os.path.join(ROOT, "src", "data", nama + ".json"))
        hasil_list = []
        for k, seed in enumerate(SEEDS, 1):
            h = simulated_annealing(problem, T0=args.T0, alpha=args.alpha,
                                    T_min=args.tmin, seed=seed)
            hasil_list.append(h)
            simpan_result(problem, h, nama, k, args.out)
            print(f"{nama} run {k}: akhir={h['final_value']} terbaik={h['best_value']} "
                  f"iter={h['iterations']} durasi={h['duration']:.2f}s "
                  f"stuck={h['stuck_freq']:.2f} local_opt={h['final_local_opt']}")
        semua.append(summary(nama, hasil_list))

    collect_summary(semua, args.out)
    print("\nRingkasan disimpan di", args.out)


if __name__ == "__main__":
    main()
