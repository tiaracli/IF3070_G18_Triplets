# visualisasi state kapal dan grafik GA pakai matplotlib
import os

import matplotlib
matplotlib.use("Agg")  # biar bisa simpan gambar tanpa buka jendela
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from core import (get_vehicle_size, value_fee, eta_value, count_misplaced_urgent,
                  ETA_URGENT)

WARNA = {"mini": "skyblue", "sedan": "lightgreen", "suv": "gold", "truk": "orange"}


def tipe(vid):
    # "truk2" -> "truk"
    return vid.rstrip("0123456789")


def gambar_state(problem, state, judul, path):
    kapal_list = problem["ships"]
    kendaraan = problem["vehicles"]
    n = len(kapal_list)

    # 1 kolom per kapal + 1 kolom buat keterangan
    fig, axes = plt.subplots(1, n + 1, figsize=(5 * n + 4, 6))

    for k in range(n):
        ax = axes[k]
        W = kapal_list[k]["w"]
        L = kapal_list[k]["l"]

        # zona depan (setengah kapal yang dekat ramp)
        ax.add_patch(Rectangle((0, 0), W, L // 2, color="aliceblue"))
        # pintu ramp di y = 0
        ax.plot([0, W], [0, 0], color="red", linewidth=5)
        ax.text(W / 2, -0.6, "PINTU RAMP", color="red", ha="center")

        berat = 0
        for i in range(len(kendaraan)):
            v = kendaraan[i]
            kapal, x, y, o = state[i]
            if kapal != k:
                continue
            w, l = get_vehicle_size(v, o)
            berat += v["weight"]
            # garis tebal = kendaraan mendesak
            tebal = 3 if v["eta"] <= ETA_URGENT else 1
            ax.add_patch(Rectangle((x, y), w, l, facecolor=WARNA[tipe(v["id"])],
                                   edgecolor="black", linewidth=tebal))
            ax.text(x + w / 2, y + l / 2, v["id"] + "\n" + o, ha="center",
                    va="center", fontsize=7)

        ax.set_xlim(0, W)
        ax.set_ylim(-1, L)
        ax.set_xticks(range(W + 1))
        ax.set_yticks(range(L + 1))
        ax.grid(True, color="lightgray")
        ax.set_aspect("equal")
        ax.set_title(kapal_list[k]["id"] + " (berat " + str(berat) + "/" +
                     str(kapal_list[k]["capacity"]) + ")")

    # keterangan di kolom terakhir
    info = axes[n]
    info.axis("off")
    di_luar = [kendaraan[i] for i in range(len(kendaraan)) if state[i][0] == -1]
    teks = "Fee total: " + str(value_fee(problem, state)) + "\n"
    teks += "Nilai ETA: " + str(eta_value(problem, state)) + "\n"
    teks += "Salah zona: " + str(count_misplaced_urgent(problem, state)) + "\n\n"
    teks += "Di luar kapal (" + str(len(di_luar)) + "):\n"
    for v in di_luar:
        teks += "- " + v["id"] + " fee " + str(v["fee"]) + ", eta " + str(v["eta"]) + "\n"
    teks += "\nGaris tebal = ETA <= " + str(ETA_URGENT)
    teks += "\nArsir biru = zona depan"
    info.text(0, 1, teks, va="top", fontsize=9)

    fig.suptitle(judul)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def plot_ga(hasil, judul, path):
    # objective maksimum dan rata-rata populasi vs iterasi
    plt.figure(figsize=(7, 4))
    plt.plot(hasil["history"], label="maksimum")
    plt.plot(hasil["extra"]["avg_history"], label="rata-rata populasi")
    plt.xlabel("iterasi (generasi)")
    plt.ylabel("objective")
    plt.title(judul)
    plt.legend()
    plt.grid(True)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.savefig(path, dpi=120)
    plt.close() 