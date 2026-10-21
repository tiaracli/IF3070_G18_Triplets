import random
import time

from core import read_data, value_fee, count_salahzona
from geneticalgorithm import genetic_algorithm, hitung_nilai
from data_io import path_data, path_output, simpan_csv
from visual import gambar_kapal, grafik_ga

kasus_1 = read_data(path_data("kasus_1"))
kasus_multi = read_data(path_data("kasus_multi"))

percobaan = [
    ("A", 50, 100),
    ("A", 50, 200),
    ("A", 50, 400),
    ("B", 20, 200),
    ("B", 50, 200),
    ("B", 100, 200),
]

hasil = []
for kode, populasi, iterasi in percobaan:
    for run in [1, 2, 3]:
        if kode == "A":
            random.seed(run)
        else:
            random.seed(run + 3)
        mulai = time.time()
        awal, akhir, riwayat_max, riwayat_rata = genetic_algorithm(kasus_1, "fee", populasi, iterasi)
        durasi = time.time() - mulai

        nama = kode + "_pop" + str(populasi) + "_iter" + str(iterasi) + "_run" + str(run)
        judul = "Genetic Algorithm populasi " + str(populasi) + ", iterasi " + str(iterasi) + ", run " + str(run)
        gambar_kapal(kasus_1, awal, judul + " (awal)", path_output("ga", nama + "_awal.png"))
        gambar_kapal(kasus_1, akhir, judul + " (akhir)", path_output("ga", nama + "_akhir.png"))
        grafik_ga(riwayat_max, riwayat_rata, judul, path_output("ga", nama + "_grafik.png"))

        hasil.append({
            "percobaan": kode,
            "populasi": populasi,
            "iterasi": iterasi,
            "run": run,
            "nilai_awal": value_fee(kasus_1, awal),
            "nilai_akhir": value_fee(kasus_1, akhir),
            "salah_zona": count_salahzona(kasus_1, akhir),
            "durasi_detik": round(durasi, 3),
        })
        print(nama, "awal =", value_fee(kasus_1, awal), "akhir =", value_fee(kasus_1, akhir))

simpan_csv(hasil, "ga", "hasil.csv")

bonus = []
for nama_bonus, problem, objective, keterangan in [("bonus_eta", kasus_1, "eta", "objective ETA"),
                                                  ("bonus_multi", kasus_multi, "fee", "kasus_multi_kapal")]:
    for run in [1, 2, 3]:
        random.seed(run)
        mulai = time.time()
        awal, akhir, riwayat_max, riwayat_rata = genetic_algorithm(problem, objective, 50, 200)
        durasi = time.time() - mulai

        nama = nama_bonus + "_run" + str(run)
        judul = "Genetic Algorithm " + keterangan + ", run " + str(run)
        gambar_kapal(problem, awal, judul + " (awal)", path_output("ga", nama + "_awal.png"))
        gambar_kapal(problem, akhir, judul + " (akhir)", path_output("ga", nama + "_akhir.png"))
        grafik_ga(riwayat_max, riwayat_rata, judul, path_output("ga", nama + "_grafik.png"))

        bonus.append({
            "bonus": nama_bonus,
            "run": run,
            "nilai_awal": hitung_nilai(problem, awal, objective),
            "nilai_akhir": hitung_nilai(problem, akhir, objective),
            "fee_akhir": value_fee(problem, akhir),
            "salah_zona": count_salahzona(problem, akhir),
            "durasi_detik": round(durasi, 3),
        })
        print(nama, "akhir =", hitung_nilai(problem, akhir, objective))

simpan_csv(bonus, "ga", "hasil_bonus.csv")
print("selesai, hasil ada di output/ga")