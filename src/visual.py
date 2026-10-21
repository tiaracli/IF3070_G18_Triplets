import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from core import posisi_vehicle, value_fee, value_eta

UNGU = "#5D1C6A"
PINK = "#CA5995"
PEACH = "#FFB090"
KREM = "#FFF1D3"
ABU = "#E4DCE6"

JENIS = {
    "motor": ("M", "Motor", KREM, "black"),
    "sedan": ("S", "Sedan", PEACH, "black"),
    "suv": ("V", "SUV", PINK, "white"),
    "truk": ("T", "Truk", UNGU, "white"),
}


def tipe(id_kendaraan):
    return id_kendaraan.rstrip("0123456789")


def gambar_kapal(problem, state, judul, path):
    kapal = problem["ships"]
    kendaraan = problem["vehicles"]
    lebar = [4] + [k["w"] for k in kapal]

    fig, axes = plt.subplots(1, len(kapal) + 1, figsize=(4 + sum(lebar[1:]) * 0.85, 7.5),
                             gridspec_kw={"width_ratios": lebar})

    kiri = axes[0]
    kiri.axis("off")
    kiri.set_xlim(0, 4)
    kiri.set_ylim(0, 10)
    ukuran = {}
    for v in kendaraan:
        if tipe(v["id"]) not in ukuran:
            ukuran[tipe(v["id"])] = str(v["w"]) + " x " + str(v["l"])

    kiri.text(1.4, 9.4, "Jenis Kendaraan", ha="center", fontsize=11)
    kiri.text(3.3, 9.4, "Ukuran", ha="center", fontsize=11)
    y = 8.3
    for t in JENIS:
        huruf, nama, warna, tulisan = JENIS[t]
        kiri.add_patch(Rectangle((0.3, y), 2.2, 0.7, facecolor=warna))
        kiri.text(1.4, y + 0.35, huruf + " (" + nama + ")", ha="center", va="center",
                  color=tulisan, fontsize=10)
        kiri.text(3.3, y + 0.35, ukuran.get(t, "-"), ha="center", va="center", fontsize=10)
        y -= 1

    jumlah = 0
    for i in range(len(kendaraan)):
        if state[i][0] != -1:
            jumlah += 1

    nilai_eta = value_eta(problem, state)
    if nilai_eta == int(nilai_eta):
        nilai_eta = int(nilai_eta)

    info = ["Value Fee = " + str(value_fee(problem, state)),
            "Nilai ETA = " + str(nilai_eta),
            "Jumlah kendaraan = " + str(jumlah)]
    for k in range(len(kapal)):
        berat = 0
        for i in range(len(kendaraan)):
            if state[i][0] == k:
                berat += kendaraan[i]["weight"]
        if len(kapal) == 1:
            info.append("Berat kapal = " + str(berat))
        else:
            info.append("Berat kapal " + str(k + 1) + " = " + str(berat))

    y = 3.9
    for baris in info:
        kiri.text(0.3, y, baris, fontsize=10)
        y -= 0.55

    for k in range(len(kapal)):
        ax = axes[k + 1]
        W = kapal[k]["w"]
        L = kapal[k]["l"]

        isi = {}
        for i in range(len(kendaraan)):
            if state[i][0] != k:
                continue
            for sel in posisi_vehicle(kendaraan[i], state[i]):
                isi[sel] = kendaraan[i]["id"]

        for x in range(W):
            for yy in range(L):
                if (x, yy) in isi:
                    id_kendaraan = isi[(x, yy)]
                    huruf, nama, warna, tulisan = JENIS[tipe(id_kendaraan)]
                    label = huruf + id_kendaraan[len(tipe(id_kendaraan)):]
                    ax.add_patch(Rectangle((x, yy), 1, 1, facecolor=warna, edgecolor="black", linewidth=0.8))
                    ax.text(x + 0.5, yy + 0.5, label, ha="center", va="center", color=tulisan, fontsize=10)
                else:
                    ax.add_patch(Rectangle((x, yy), 1, 1, facecolor="white", edgecolor="black", linewidth=0.8))

        ax.add_patch(Rectangle((0, -0.5), W, 0.45, facecolor="#E1E4E8"))
        ax.text(W / 2, -1.1, "Pintu Masuk", ha="center", fontsize=11)
        if len(kapal) > 1:
            ax.text(W / 2, L + 0.3, "Kapal " + str(k + 1), ha="center", fontsize=11)

        ax.set_xlim(-0.1, W + 0.1)
        ax.set_ylim(-1.4, L + 0.8)
        ax.set_aspect("equal")
        ax.axis("off")

    fig.suptitle("Posisi Kendaraan Pada Kapal", fontsize=16, fontweight="bold", y=0.98)
    fig.text(0.5, 0.92, judul, ha="center", fontsize=11, fontweight="bold", color="black")
    fig.savefig(path, dpi=110, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def grafik_objective(riwayat, judul, path):
    plt.figure(figsize=(7, 3.6))
    plt.plot(riwayat, color=UNGU, linewidth=2)
    plt.xlabel("iterasi")
    plt.ylabel("nilai objective")
    plt.title(judul, color=UNGU)
    plt.grid(color=ABU)
    plt.savefig(path, dpi=110, bbox_inches="tight")
    plt.close()


def grafik_ga(riwayat_max, riwayat_rata, judul, path):
    plt.figure(figsize=(7, 3.6))
    plt.plot(riwayat_max, color=UNGU, linewidth=2, label="maksimum populasi")
    plt.plot(riwayat_rata, color=PINK, linewidth=2, label="rata-rata populasi")
    plt.xlabel("iterasi")
    plt.ylabel("nilai objective")
    plt.title(judul, color=UNGU)
    plt.grid(color=ABU)
    plt.legend(frameon=False)
    plt.savefig(path, dpi=110, bbox_inches="tight")
    plt.close()


def grafik_peluang(peluang, judul, path):
    x = [p[0] for p in peluang]
    y = [p[1] for p in peluang]
    plt.figure(figsize=(7, 3.6))
    plt.scatter(x, y, s=8, color=PINK, alpha=0.5)
    plt.ylim(-0.03, 1.03)
    plt.xlabel("iterasi")
    plt.ylabel("e^(dE/T)")
    plt.title(judul, color=UNGU)
    plt.grid(color=ABU)
    plt.savefig(path, dpi=110, bbox_inches="tight")
    plt.close()


def grafik_banding(daftar_riwayat, daftar_label, judul, path, tebal=3):
    warna = [UNGU, PINK, PEACH, UNGU]
    gaya = ["-", "-", "-", "--"]
    plt.figure(figsize=(7, 3.6))
    for i in range(len(daftar_riwayat)):
        plt.plot(daftar_riwayat[i], color=warna[i % 4], linestyle=gaya[i % 4],
                 linewidth=tebal - i * tebal / 5, label=daftar_label[i])
    plt.xlabel("iterasi")
    plt.ylabel("nilai objective")
    plt.title(judul, color=UNGU)
    plt.grid(color=ABU)
    plt.legend(frameon=False)
    plt.savefig(path, dpi=110, bbox_inches="tight")
    plt.close()


def grafik_restart(semua_riwayat, judul, path):
    plt.figure(figsize=(7, 3.6))
    awal = 0
    for i in range(len(semua_riwayat)):
        riwayat = semua_riwayat[i]
        x = list(range(awal, awal + len(riwayat)))
        plt.plot(x, riwayat, color=UNGU, linewidth=2)
        if i > 0:
            plt.axvline(awal, color=PINK, linestyle="--", linewidth=1)
        awal += len(riwayat)
    plt.xlabel("iterasi (garis putus-putus = restart)")
    plt.ylabel("nilai objective")
    plt.title(judul, color=UNGU)
    plt.grid(color=ABU)
    plt.savefig(path, dpi=110, bbox_inches="tight")
    plt.close()