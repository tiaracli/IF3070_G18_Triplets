import os
import random
import time
import webbrowser

from core import load_problem, value_fee, eta_value, count_misplaced_urgent, render_text
from neighbor import random_state, all_neighbors
from hill_climbing import (steepest_ascent, stochastic_hill_climbing,
                           sideways_hill_climbing, random_restart_hill_climbing)
from sa import simulated_annealing
from geneticalgorithm import genetic_algorithm
from data_io import path_data, path_output
from visual import gambar_kapal, grafik_objective, grafik_ga, grafik_peluang, grafik_restart

ALGORITMA = {
    "1": "Steepest Ascent Hill Climbing",
    "2": "Stochastic Hill Climbing",
    "3": "Sideways Move Hill Climbing",
    "4": "Random Restart Hill Climbing",
    "5": "Simulated Annealing",
    "6": "Genetic Algorithm",
}


def rapi(angka):
    if type(angka) == float and angka == int(angka):
        return str(int(angka))
    return str(angka)


def tanya_pilihan(judul, pilihan):
    print("\n" + judul)
    for kode in pilihan:
        print("  " + kode + ". " + pilihan[kode])
    kode = list(pilihan.keys())
    if len(kode) == 2:
        petunjuk = kode[0] + " atau " + kode[1]
    else:
        petunjuk = kode[0] + " sampai " + kode[-1]
    print("Ketik angka " + petunjuk + " lalu tekan Enter")
    while True:
        jawab = input("> ").strip()
        if jawab in pilihan:
            return jawab
        print("Pilihan tidak ada, ketik angka " + petunjuk)


def tanya_angka(judul, catatan, minimal, maksimal, bawaan):
    print("\n" + judul)
    print(catatan)
    print("Ketik angka dari " + rapi(minimal) + " sampai " + rapi(maksimal)
          + ", atau langsung tekan Enter untuk memakai " + rapi(bawaan))
    while True:
        jawab = input("> ").strip()
        if jawab == "":
            return bawaan
        try:
            if type(bawaan) == int:
                angka = int(jawab)
            else:
                angka = float(jawab)
        except ValueError:
            print("Harus berupa angka, coba lagi")
            continue
        if minimal <= angka <= maksimal:
            return angka
        print("Angka harus dari " + rapi(minimal) + " sampai " + rapi(maksimal) + ", coba lagi")


def tanya_ya_tidak(judul):
    print("\n" + judul)
    print("Ketik y untuk ya atau n untuk tidak")
    while True:
        jawab = input("> ").strip().lower()
        if jawab in ["y", "n"]:
            return jawab == "y"
        print("Cukup ketik y atau n")


def nilai(problem, state, objective):
    if objective == "eta":
        return eta_value(problem, state)
    return value_fee(problem, state)


def tanya_iterasi_hc():
    return tanya_angka("Berapa maksimal iterasi?",
                       "Satu iterasi berarti satu kali pindah ke tetangga yang lebih baik. "
                       "Pencarian bisa berhenti lebih awal kalau sudah tidak ada tetangga yang lebih baik.",
                       1, 1000, 500)


def jalankan(problem, pilihan, objective, seed):
    random.seed(seed)
    hasil = {}

    if pilihan in ["1", "2", "3", "4"]:
        iterasi = tanya_iterasi_hc()
        if pilihan == "3":
            batas = tanya_angka("Berapa maksimal sideways move?",
                                "Sideways move adalah pindah ke tetangga yang nilainya sama, "
                                "supaya pencarian tidak langsung berhenti di dataran (shoulder).",
                                0, 100, 20)
        if pilihan == "4":
            restart = tanya_angka("Berapa maksimal restart?",
                                  "Setiap restart mengulang pencarian dari state acak yang baru, "
                                  "lalu diambil hasil terbaik dari semua percobaan.",
                                  0, 50, 10)

        awal = random_state(problem)
        print("\nSedang berjalan...")
        mulai = time.time()
        if pilihan == "1":
            h = steepest_ascent(problem, awal, all_neighbors, objective, iterasi)
        elif pilihan == "2":
            h = stochastic_hill_climbing(problem, awal, all_neighbors, objective, iterasi)
        elif pilihan == "3":
            h = sideways_hill_climbing(problem, awal, all_neighbors, objective, iterasi, batas)
        else:
            h = random_restart_hill_climbing(problem, awal, all_neighbors, random_state,
                                             objective, restart, iterasi)
        hasil["durasi"] = time.time() - mulai
        hasil["awal"] = awal
        hasil["akhir"] = h["final_state"]
        hasil["riwayat"] = h["history"]
        hasil["iterasi"] = h["iterations"]
        if "sideways_moves" in h:
            hasil["sideways"] = h["sideways_moves"]
        if "all_histories" in h:
            hasil["semua_riwayat"] = h["all_histories"]
            hasil["restart"] = h["restart_scores"]

    elif pilihan == "5":
        T0 = tanya_angka("Berapa suhu awal (T0)?",
                         "Makin tinggi suhu awal, makin sering langkah yang lebih buruk diterima di awal pencarian.",
                         1.0, 1000.0, 100.0)
        alpha = tanya_angka("Berapa nilai alpha?",
                            "Alpha adalah pengali suhu di setiap iterasi. "
                            "Makin dekat ke 1, suhu turun makin pelan dan prosesnya makin lama.",
                            0.9, 0.9999, 0.9998)
        tmin = tanya_angka("Berapa suhu minimum?",
                           "Pencarian berhenti ketika suhu sudah turun di bawah angka ini.",
                           0.001, 10.0, 0.1)
        print("\nSedang berjalan...")
        h = simulated_annealing(problem, T0, alpha, tmin, seed=seed, objective=objective)
        hasil["durasi"] = h["duration"]
        hasil["awal"] = h["initial_state"]
        hasil["akhir"] = h["final_state"]
        hasil["riwayat"] = h["history"]
        hasil["iterasi"] = h["iterations"]
        hasil["stuck"] = h["stuck_freq"]
        peluang = []
        for i in range(len(h["probs"])):
            if h["probs"][i] is not None:
                peluang.append((i + 1, h["probs"][i]))
        hasil["peluang"] = peluang

    else:
        populasi = tanya_angka("Berapa jumlah populasi?",
                               "Populasi adalah banyaknya state yang diproses bersamaan di setiap generasi.",
                               2, 500, 50)
        iterasi = tanya_angka("Berapa jumlah iterasi?",
                              "Satu iterasi berarti satu generasi baru "
                              "(seleksi, crossover, dan mutasi).",
                              1, 1000, 200)
        print("\nSedang berjalan...")
        mulai = time.time()
        awal, akhir, riwayat_max, riwayat_rata = genetic_algorithm(problem, objective, populasi, iterasi)
        hasil["durasi"] = time.time() - mulai
        hasil["awal"] = awal
        hasil["akhir"] = akhir
        hasil["riwayat"] = riwayat_max
        hasil["rata"] = riwayat_rata
        hasil["iterasi"] = iterasi

    return hasil


def gabung(daftar):
    if len(daftar) == 1:
        return daftar[0]
    return ", ".join(daftar[:-1]) + " dan " + daftar[-1]


def isi_kapal(problem, state, k):
    jumlah = {"motor": 0, "sedan": 0, "suv": 0, "truk": 0}
    for i in range(len(problem["vehicles"])):
        if state[i][0] == k:
            jumlah[problem["vehicles"][i]["id"].rstrip("0123456789")] += 1
    teks = []
    for jenis in jumlah:
        if jumlah[jenis] > 0:
            nama = "SUV" if jenis == "suv" else jenis
            teks.append(str(jumlah[jenis]) + " " + nama)
    if not teks:
        return "belum ada kendaraan"
    return gabung(teks)


def jelaskan(problem, hasil, pilihan):
    akhir = hasil["akhir"]
    di_luar = 0
    for p in akhir:
        if p[0] == -1:
            di_luar += 1
    masuk = len(akhir) - di_luar

    print("\n---------- PENJELASAN VISUALISASI ----------")
    if len(problem["ships"]) == 1:
        print("Pada state final ada " + str(masuk) + " kendaraan yang masuk kapal, yaitu "
              + isi_kapal(problem, akhir, 0) + ", sedangkan " + str(di_luar)
              + " kendaraan lainnya tidak terangkut.")
    else:
        print("Pada state final kapal 1 berisi " + isi_kapal(problem, akhir, 0)
              + ", sedangkan kapal 2 berisi " + isi_kapal(problem, akhir, 1) + ".")
        print("Total ada " + str(masuk) + " kendaraan yang terangkut dan "
              + str(di_luar) + " kendaraan yang tidak terangkut.")

    if pilihan in ["1", "2"]:
        print("Grafik menunjukkan nilai objective di setiap iterasi. Garisnya naik setiap kali "
              "pencarian menemukan tetangga yang lebih baik, lalu berhenti ketika sudah tidak ada "
              "tetangga yang lebih baik.")
    elif pilihan == "3":
        print("Grafik menunjukkan nilai objective di setiap iterasi. Bagian garis yang datar adalah "
              "sideways move, yaitu saat pencarian pindah ke tetangga yang nilainya sama.")
    elif pilihan == "4":
        print("Grafik menunjukkan nilai objective dari semua restart. Garis putus-putus pink menandai "
              "awal restart baru, dan state final diambil dari restart yang nilainya paling tinggi.")
    elif pilihan == "5":
        print("Grafik objective naik turun di awal karena langkah yang lebih buruk masih sering "
              "diterima saat suhu tinggi, lalu makin stabil saat suhu turun.")
        print("Grafik peluang menunjukkan nilai e^(dE/T), yaitu peluang langkah yang lebih buruk "
              "diterima, dan nilainya makin kecil seiring suhu turun.")
    else:
        print("Garis ungu adalah nilai terbaik di populasi dan garis pink adalah rata-rata populasi "
              "di setiap iterasi. Kalau kedua garis makin dekat, artinya isi populasi makin mirip.")


def tampilkan(problem, hasil, objective):
    print("\n---------- STATE AWAL ----------")
    print("Nilai objective = " + rapi(nilai(problem, hasil["awal"], objective)))
    print(render_text(problem, hasil["awal"]))
    print("\n---------- STATE AKHIR ----------")
    print("Nilai objective = " + rapi(nilai(problem, hasil["akhir"], objective)))
    print(render_text(problem, hasil["akhir"]))

    print("\n---------- RINGKASAN ----------")
    print("Value fee akhir = " + str(value_fee(problem, hasil["akhir"])))
    print("Nilai Estimated Time of Arrival (ETA) akhir = " + rapi(eta_value(problem, hasil["akhir"])))
    print("Kendaraan mendesak di luar zona depan = " + str(count_misplaced_urgent(problem, hasil["akhir"])))
    print("Jumlah iterasi = " + str(hasil["iterasi"]))
    print("Durasi = " + str(round(hasil["durasi"], 3)) + " detik")
    if "sideways" in hasil:
        print("Jumlah sideways move = " + str(hasil["sideways"]))
    if "restart" in hasil:
        print("Jumlah restart = " + str(len(hasil["restart"]) - 1))
        print("Nilai akhir tiap restart = " + ", ".join(rapi(n) for n in hasil["restart"]))
    if "stuck" in hasil:
        print("Frekuensi stuck = " + str(round(hasil["stuck"], 3)))


def simpan_gambar(problem, hasil, judul):
    awal = path_output("demo", "awal.png")
    akhir = path_output("demo", "akhir.png")
    grafik = path_output("demo", "grafik.png")
    peluang = path_output("demo", "peluang.png")

    gambar_kapal(problem, hasil["awal"], judul + " (awal)", awal)
    gambar_kapal(problem, hasil["akhir"], judul + " (akhir)", akhir)
    if "rata" in hasil:
        grafik_ga(hasil["riwayat"], hasil["rata"], judul, grafik)
    elif "semua_riwayat" in hasil:
        grafik_restart(hasil["semua_riwayat"], judul, grafik)
    else:
        grafik_objective(hasil["riwayat"], judul, grafik)

    dibuka = [akhir, grafik]
    if "peluang" in hasil:
        grafik_peluang(hasil["peluang"], judul, peluang)
        dibuka.append(peluang)
    elif os.path.exists(peluang):
        os.remove(peluang)
    return dibuka


print("-----------------------------------------------")
print(" Tugas Besar 1")
print(" IF3070 Dasar Inteligensi Artifisial 2026/2027")
print(" Kelompok 18 Triplets")
print("-----------------------------------------------")

while True:
    data = tanya_pilihan("Kasus mana yang ingin didemokan?", {
        "1": "kasus_satu_kapal (terdiri dari 1 kapal dengan ukuran 8x8)",
        "2": "kasus_multi_kapal (terdiri dari 2 kapal dengan ukuran 8x8 dan 6x8)",
    })
    if data == "1":
        problem = load_problem(path_data("kasus_1"))
    else:
        problem = load_problem(path_data("kasus_multi"))

    pilihan = tanya_pilihan("Algoritma mana yang mau dijalankan?", ALGORITMA)

    jenis = tanya_pilihan("Objective function mana yang mau dipakai?", {
        "1": "Fee, total ShippingFee kendaraan yang diangkut",
        "2": "Estimated Time of Arrival (ETA), fee dengan potongan untuk kendaraan mendesak yang jauh dari pintu masuk",
    })
    objective = "fee"
    if jenis == "2":
        objective = "eta"

    seed = tanya_angka("Berapa seed yang mau dipakai?",
                       "Seed mengatur hasil acak. Seed yang sama akan selalu memberi hasil yang sama, "
                       "jadi percobaan bisa diulang.",
                       0, 9999, 1)

    hasil = jalankan(problem, pilihan, objective, seed)
    tampilkan(problem, hasil, objective)

    judul = ALGORITMA[pilihan] + ", seed " + str(seed)
    if objective == "eta":
        judul += ", objective Estimated Time of Arrival (ETA)"
    dibuka = simpan_gambar(problem, hasil, judul)
    print("\nGambar state awal, state akhir, dan grafik sudah disimpan di folder output/demo")

    if tanya_ya_tidak("Tampilkan visualisasi untuk state final?"):
        for path in dibuka:
            webbrowser.open("file://" + os.path.abspath(path))
        jelaskan(problem, hasil, pilihan)

    if not tanya_ya_tidak("Mau menjalankan algoritma lagi?"):
        print("\nSelesai, terima kasih")
        break