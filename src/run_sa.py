import argparse
import csv
import json
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from core import load_problem, render_text, value_fee
from sa import simulated_annealing

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SEEDS = [11, 22, 33]   # seed dicatat supaya hasil bisa diulang


def simpan_run(problem, hasil, nama, k, folder):
    data = dict(hasil)
    for kunci in ("initial_state", "final_state", "best_state"):
        data[kunci] = [list(p) for p in hasil[kunci]]
    data["kasus"] = nama
    with open(os.path.join(folder, f"{nama}_run{k}.json"), "w") as f:
        json.dump(data, f)

    with open(os.path.join(folder, f"{nama}_run{k}.txt"), "w") as f:
        f.write(f"=== {nama} run {k} (seed {hasil['params']['seed']}) ===\n\n")
        f.write(f"STATE AWAL (value_fee {value_fee(problem, hasil['initial_state'])})\n")
        f.write(render_text(problem, hasil["initial_state"]) + "\n\n")
        f.write(f"STATE AKHIR (value_fee {value_fee(problem, hasil['final_value'])})\n")
        f.write(render_text(problem, hasil["final_state"]) + "\n")


def plot_objective(hasil_list, nama, folder):
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for k, h in enumerate(hasil_list, 1):
        ax.plot(h["history"], linewidth=0.8, label=f"run {k} (akhir {h['final_value']})")
    ax.set_xlabel("iterasi")
    ax.set_ylabel("objective (total ShippingFee, juta)")
    ax.set_title(f"Simulated Annealing - {nama}: objective terhadap iterasi")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(folder, f"{nama}_objective.png"), dpi=150)
    plt.close(fig)


def plot_prob(hasil_list, nama, folder):
    fig, axes = plt.subplots(len(hasil_list), 1, figsize=(9, 3 * len(hasil_list)), sharex=True)
    if len(hasil_list) == 1:
        axes = [axes]
    for k, (ax, h) in enumerate(zip(axes, hasil_list), 1):
        xs = [i + 1 for i, p in enumerate(h["probs"]) if p is not None]
        ys = [p for p in h["probs"] if p is not None]
        ax.scatter(xs, ys, s=2, alpha=0.4)
        ax.set_ylabel(f"run {k}\ne^(dE/T)")
        ax.set_ylim(-0.02, 1.02)
        ax.grid(alpha=0.3)
    axes[-1].set_xlabel("iterasi")
    axes[0].set_title(f"Simulated Annealing - {nama}: e^(dE/T) terhadap iterasi")
    fig.tight_layout()
    fig.savefig(os.path.join(folder, f"{nama}_prob.png"), dpi=150)
    plt.close(fig)


def ringkas(nama, hasil_list):
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


def tulis_ringkasan(baris, folder):
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
        problem = load_problem(os.path.join(ROOT, "data", nama + ".json"))
        hasil_list = []
        for k, seed in enumerate(SEEDS, 1):
            h = simulated_annealing(problem, T0=args.T0, alpha=args.alpha,
                                    T_min=args.tmin, seed=seed)
            hasil_list.append(h)
            simpan_run(problem, h, nama, k, args.out)
            print(f"{nama} run {k}: akhir={h['final_value']} terbaik={h['best_value']} "
                  f"iter={h['iterations']} durasi={h['duration']:.2f}s "
                  f"stuck={h['stuck_freq']:.2f} local_opt={h['final_local_opt']}")
        plot_objective(hasil_list, nama, args.out)
        plot_prob(hasil_list, nama, args.out)
        semua.append(ringkas(nama, hasil_list))

    tulis_ringkasan(semua, args.out)
    print("\nRingkasan disimpan di", args.out)


if __name__ == "__main__":
    main()
