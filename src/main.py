import os
import random
import time
import webbrowser

from core import read_data, value_fee, value_eta, count_salahzona, show_layout
from neighbor import random_state, all_neighbors
from hill_climbing import (steepestascent_hc, stochastic_hc,
                           sideways_hc, randomrestart_hc)
from sa import simulated_annealing
from geneticalgorithm import genetic_algorithm
from data_io import lokasi_data, lokasi_output
from visual import visual_kapal, grafik_objective_kapal, visual_genetic_algorithm, grafik_prob, grafik_restart

ALGORITMA = {
    "1": "Steepest Ascent Hill Climbing",
    "2": "Stochastic Hill Climbing",
    "3": "Sideways Move Hill Climbing",
    "4": "Random Restart Hill Climbing",
    "5": "Simulated Annealing",
    "6": "Genetic Algorithm",
}

def rapikan_format_angka(angka):
    if type(angka) == float and angka == int(angka):
        return str(int(angka))
    return str(angka)

def pilih_case(judul, pilihan):
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

def insert_atribut(judul, catatan, minimal, maksimal, bawaan):
    print("\n" + judul)
    print(catatan)
    print("Ketik angka dari " + rapikan_format_angka(minimal) + " sampai " + rapikan_format_angka(maksimal)
          + ", atau langsung tekan Enter untuk memakai " + rapikan_format_angka(bawaan))
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
        print("Angka harus dari " + rapikan_format_angka(minimal) + " sampai " + rapikan_format_angka(maksimal) + ", coba lagi")

def pilih_output(judul):
    print("\n" + judul)
    print("Ketik y untuk ya atau n untuk tidak")
    while True:
        jawab = input("> ").strip().lower()
        if jawab in ["y", "n"]:
            return jawab == "y"
        print("Cukup ketik y atau n")


def nilai_objective(problem, state, objective):
    if objective == "eta":
        return value_eta(problem, state)
    return value_fee(problem, state)

def input_iterasi():
    return insert_atribut("Berapa maksimal iterasi?",
                       "Satu iterasi berarti satu kali pindah ke tetangga yang lebih baik. "
                       "Pencarian bisa berhenti lebih awal kalau sudah tidak ada tetangga yang lebih baik.",
                       1, 500, 500)

def run_algoritma(problem, pilihan, objective, seed):
    random.seed(seed)
    hasil = {}
    if pilihan in ["1", "2", "3", "4"]:
        iterasi = input_iterasi()
        if pilihan == "3":
            batas = insert_atribut("Berapa maksimal sideways move?",
                                "Sideways move adalah pindah ke tetangga yang nilainya sama, "
                                "supaya pencarian tidak langsung berhenti di dataran (shoulder).",
                                0, 20, 20)
        if pilihan == "4":
            restart = insert_atribut("Berapa maksimal restart?",
                                  "Setiap restart mengulang pencarian dari state acak yang baru, "
                                  "lalu diambil hasil terbaik dari semua percobaan.",
                                  0, 10, 10)
        awal = random_state(problem)
        print("\nSedang berjalan...")
        mulai = time.time()
        if pilihan == "1":
            h = steepestascent_hc(problem, awal, all_neighbors, objective, iterasi)
        elif pilihan == "2":
            h = stochastic_hc(problem, awal, all_neighbors, objective, iterasi)
        elif pilihan == "3":
            h = sideways_hc(problem, awal, all_neighbors, objective, iterasi, batas)
        else:
            h = randomrestart_hc(problem, awal, all_neighbors, random_state,
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
        T0 = insert_atribut("Berapa suhu awal (T0)?",
                         "Makin tinggi suhu awal, makin sering langkah yang lebih buruk diterima di awal pencarian.",
                         20.0, 300.0, 100.0)
        alpha = insert_atribut("Berapa nilai alpha?",
                            "Alpha adalah pengali suhu di setiap iterasi. "
                            "Makin dekat ke 1, suhu turun makin pelan dan prosesnya makin lama.",
                            0.5, 0.9999, 0.9998)
        tmin = insert_atribut("Berapa suhu minimum?",
                           "Pencarian berhenti ketika suhu sudah turun di bawah angka ini.",
                           0.01, 5.0, 0.1)
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
        populasi = insert_atribut("Berapa jumlah populasi?",
                               "Populasi adalah banyaknya state yang diproses bersamaan di setiap generasi.",
                               2, 500, 50)
        iterasi = insert_atribut("Berapa jumlah iterasi?",
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

def gabung_kalimat(daftar):
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
    return gabung_kalimat(teks)

def jelaskan_visualisasi_kapal(problem, hasil, pilihan):
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

def tampilkan_hasil(problem, hasil, objective):
    print("\n---------- STATE AWAL ----------")
    print("Nilai objective = " + rapikan_format_angka(nilai_objective(problem, hasil["awal"], objective)))
    print(show_layout(problem, hasil["awal"]))
    print("\n---------- STATE AKHIR ----------")
    print("Nilai objective = " + rapikan_format_angka(nilai_objective(problem, hasil["akhir"], objective)))
    print(show_layout(problem, hasil["akhir"]))

    print("\n---------- RINGKASAN ----------")
    print("Value fee akhir = " + str(value_fee(problem, hasil["akhir"])))
    print("Nilai Estimated Time of Arrival (ETA) akhir = " + rapikan_format_angka(value_eta(problem, hasil["akhir"])))
    print("Kendaraan mendesak di luar zona depan = " + str(count_salahzona(problem, hasil["akhir"])))
    print("Jumlah iterasi = " + str(hasil["iterasi"]))
    print("Durasi = " + str(round(hasil["durasi"], 3)) + " detik")
    if "sideways" in hasil:
        print("Jumlah sideways move = " + str(hasil["sideways"]))
    if "restart" in hasil:
        print("Jumlah restart = " + str(len(hasil["restart"]) - 1))
        print("Nilai akhir tiap restart = " + ", ".join(rapikan_format_angka(n) for n in hasil["restart"]))
    if "stuck" in hasil:
        print("Frekuensi stuck = " + str(round(hasil["stuck"], 3)))


def save_gambar(problem, hasil, judul):
    awal = lokasi_output("demo", "awal.png")
    akhir = lokasi_output("demo", "akhir.png")
    grafik = lokasi_output("demo", "grafik.png")
    peluang = lokasi_output("demo", "peluang.png")
    visual_kapal(problem, hasil["awal"], judul + " (awal)", awal)
    visual_kapal(problem, hasil["akhir"], judul + " (akhir)", akhir)
    if "rata" in hasil:
        visual_genetic_algorithm(hasil["riwayat"], hasil["rata"], judul, grafik)
    elif "semua_riwayat" in hasil:
        grafik_restart(hasil["semua_riwayat"], judul, grafik)
    else:
        grafik_objective_kapal(hasil["riwayat"], judul, grafik)
    dibuka = [akhir, grafik]
    if "peluang" in hasil:
        grafik_prob(hasil["peluang"], judul, peluang)
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
    data = pilih_case("Kasus mana yang ingin didemokan?", {
        "1": "kasus_satu_kapal (terdiri dari 1 kapal dengan ukuran 8x8)",
        "2": "kasus_multi_kapal (terdiri dari 2 kapal dengan ukuran 8x8 dan 6x8)",
    })
    if data == "1":
        problem = read_data(lokasi_data("kasus_1"))
    else:
        problem = read_data(lokasi_data("kasus_multi"))

    pilihan = pilih_case("Algoritma mana yang mau dijalankan?", ALGORITMA)
    jenis = pilih_case("Objective function mana yang mau dipakai?", {
        "1": "Fee, total ShippingFee kendaraan yang diangkut",
        "2": "Estimated Time of Arrival (ETA), fee dengan potongan untuk kendaraan mendesak yang jauh dari pintu masuk",
    })
    objective = "fee"
    if jenis == "2":
        objective = "eta"

    seed = insert_atribut("Berapa seed yang mau dipakai?",
                       "Seed mengatur hasil acak. Seed yang sama akan selalu memberi hasil yang sama, "
                       "jadi percobaan bisa diulang.",
                       0, 500, 1)
    hasil = run_algoritma(problem, pilihan, objective, seed)
    tampilkan_hasil(problem, hasil, objective)

    judul = ALGORITMA[pilihan] + ", seed " + str(seed)
    if objective == "eta":
        judul += ", objective Estimated Time of Arrival (ETA)"
    dibuka = save_gambar(problem, hasil, judul)
    print("\nGambar state awal, state akhir, dan grafik sudah disimpan di folder output/demo")
    if pilih_output("Tampilkan visualisasi untuk state final?"):
        for path in dibuka:
            webbrowser.open("file://" + os.path.abspath(path))
        jelaskan_visualisasi_kapal(problem, hasil, pilihan)

    if not pilih_output("Mau menjalankan algoritma lagi?"):
        print("\nSelesai, terima kasih")
        break
        